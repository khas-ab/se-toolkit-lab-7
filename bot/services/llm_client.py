"""LLM client with tool calling support."""

import json
import sys
from typing import Any

import httpx
from config import settings


# Tool definitions for all 9 backend endpoints
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List all labs and tasks available in the system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "List all enrolled learners and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return (default 10)"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh data from the autochecker system",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt that encourages tool use
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System.
You have access to tools that fetch data about labs, learners, scores, and analytics.

When the user asks a question:
1. First, think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Once you have the data, summarize it in a clear, helpful way

If the user's message is a greeting or doesn't require data, respond naturally without using tools.
If the user's message is unclear, ask for clarification about what they want to know.

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_scores: Score distribution for a lab
- get_pass_rates: Pass rates per task in a lab
- get_timeline: Submission timeline for a lab
- get_groups: Group performance in a lab
- get_top_learners: Top students in a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker
"""


class LlmClient:
    """Client for LLM API with tool calling support."""

    def __init__(self):
        self.base_url = settings.llm_api_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_api_model
        self.timeout = 30.0  # seconds

    def _get_headers(self) -> dict[str, str]:
        """Return headers with Bearer token authentication."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Send a chat request to the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
        
        Returns:
            LLM response dict
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError(
                    "LLM authentication failed (HTTP 401). "
                    "Check LLM_API_KEY in .env.bot.secret or restart the OAuth proxy."
                ) from e
            raise
        except httpx.TimeoutException:
            raise RuntimeError(
                f"LLM timeout after {self.timeout}s. The service may be overloaded."
            )
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"Cannot connect to LLM at {self.base_url}. "
                "Check that the LLM service is running."
            ) from e

    def route(self, user_message: str, debug: bool = False) -> str:
        """Route a user message through the LLM with tool calling.
        
        This implements the tool calling loop:
        1. Send message + tools to LLM
        2. If LLM returns tool calls, execute them
        3. Feed results back to LLM
        4. Repeat until LLM produces final answer
        
        Args:
            user_message: The user's input message
            debug: If True, print debug info to stderr
        
        Returns:
            The LLM's final response
        """
        # Initialize conversation with system prompt and user message
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM with current conversation state
            response = self.chat(messages, tools=TOOL_DEFINITIONS)
            
            # Get the assistant's message
            choice = response["choices"][0]
            assistant_message = choice["message"]
            
            # Add assistant's message to conversation
            messages.append(assistant_message)
            
            # Check if LLM wants to call tools
            tool_calls = assistant_message.get("tool_calls", [])
            
            if not tool_calls:
                # No tool calls - LLM produced final answer
                return assistant_message.get("content", "I don't have a response.")
            
            # Execute tool calls and collect results
            tool_results = []
            for tool_call in tool_calls:
                function = tool_call["function"]
                tool_name = function["name"]
                tool_args = json.loads(function["arguments"] or "{}")
                tool_call_id = tool_call.get("id", f"call_{tool_name}")
                
                if debug:
                    print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                
                # Execute the tool
                result = self._execute_tool(tool_name, tool_args)
                result["_tool_call_id"] = tool_call_id
                tool_results.append(result)
                
                if debug:
                    print(f"[tool] Result: {len(str(result))} chars", file=sys.stderr)
            
            if debug:
                print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
            
            # Feed tool results back to LLM
            for tool_result in tool_results:
                messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_result),
                    "tool_call_id": tool_result["_tool_call_id"],
                })
        
        # Max iterations reached
        return "I'm having trouble processing your request. Please try rephrasing."

    def _execute_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool and return the result.
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
        
        Returns:
            Tool result as a dict
        """
        from services.api_client import api_client, ApiError
        
        try:
            if tool_name == "get_items":
                result = api_client.get_items()
            elif tool_name == "get_learners":
                result = api_client.get_learners()
            elif tool_name == "get_scores":
                result = api_client.get_scores(args["lab"])
            elif tool_name == "get_pass_rates":
                result = api_client.get_pass_rates(args["lab"])
            elif tool_name == "get_timeline":
                result = api_client.get_timeline(args["lab"])
            elif tool_name == "get_groups":
                result = api_client.get_groups(args["lab"])
            elif tool_name == "get_top_learners":
                result = api_client.get_top_learners(args["lab"], args.get("limit", 10))
            elif tool_name == "get_completion_rate":
                result = api_client.get_completion_rate(args["lab"])
            elif tool_name == "trigger_sync":
                result = api_client.trigger_sync()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
            
            # Wrap list results in a dict for JSON serialization
            if isinstance(result, list):
                return {"data": result}
            return result
        except ApiError as e:
            return {"error": str(e)}


# Global LLM client instance
llm_client = LlmClient()
