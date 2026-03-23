"""Command handlers - pure functions that take input and return text."""

from services.api_client import api_client, ApiError


def handle_start() -> str:
    """Handle /start command - welcome message."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command - list available commands."""
    return """Available commands:
/start - Welcome message
/help - Show this help
/health - Check backend status
/labs - List available labs
/scores <lab_id> - Get scores for a lab (e.g., /scores lab-04)"""


def handle_health() -> str:
    """Handle /health command - check backend health."""
    try:
        items = api_client.get_items()
        item_count = len(items)
        return f"Backend is healthy. {item_count} items available."
    except ApiError as e:
        return f"Backend error: {str(e)}"


def handle_labs() -> str:
    """Handle /labs command - list available labs."""
    try:
        items = api_client.get_items()
        # Filter for labs only (type == "lab")
        labs = [item for item in items if item.get("type") == "lab"]
        
        if not labs:
            return "No labs available."
        
        lines = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown")
            lines.append(f"- {title}")
        
        return "\n".join(lines)
    except ApiError as e:
        return f"Failed to fetch labs: {str(e)}"


def handle_scores(lab_id: str = "") -> str:
    """Handle /scores command - get scores for a lab.
    
    Args:
        lab_id: The lab identifier (e.g., 'lab-04')
    """
    if not lab_id:
        return "Please specify a lab ID, e.g., /scores lab-04"
    
    try:
        pass_rates = api_client.get_pass_rates(lab_id)
        
        if not pass_rates:
            return f"No pass rate data available for {lab_id}."
        
        lines = [f"Pass rates for {lab_id}:"]
        for rate in pass_rates:
            task_name = rate.get("task", "Unknown task")
            avg_score = rate.get("avg_score", 0)
            attempts = rate.get("attempts", 0)
            lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
    except ApiError as e:
        return f"Failed to fetch scores for {lab_id}: {str(e)}"
