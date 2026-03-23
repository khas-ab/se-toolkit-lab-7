# LMS Telegram Bot - Development Plan

## Overview

This document outlines the implementation plan for the LMS Telegram Bot across four tasks. The bot provides students with access to their learning management system through Telegram, supporting both slash commands and natural language queries via an LLM.

## Task 1: Scaffold and Testable Architecture

**Goal:** Create a bot skeleton with testable handlers that work without Telegram.

**Approach:**
- Separate handlers from Telegram transport layer (separation of concerns)
- Implement `--test` mode in `bot.py` for offline testing
- Create placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Use `pydantic-settings` for configuration loading from `.env.bot.secret`

**Key Pattern:** Handlers are pure functions that take input and return text. They can be called from `--test` mode, unit tests, or Telegram — same logic, different entry points.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:**
- Create `services/api_client.py` with Bearer token authentication
- Implement real API calls in handlers (replace placeholders)
- Handle API errors gracefully (timeouts, auth failures, not found)
- Add `/health` endpoint that actually checks backend status

**Key Pattern:** API client encapsulates HTTP details. Handlers call `await api_client.get_labs()` without worrying about URLs or auth headers. Environment variables (`LMS_API_BASE_URL`, `LMS_API_KEY`) configure the client.

## Task 3: LLM Intent Routing

**Goal:** Enable natural language queries like "what labs are available?"

**Approach:**
- Create `services/llm_client.py` for LLM API calls
- Define tool descriptions for each handler (what it does, when to use it)
- Use LLM to parse user intent and select the appropriate tool
- The LLM decides which handler to call based on tool descriptions

**Key Pattern:** Tool descriptions drive LLM behavior. Quality of descriptions > prompt engineering. If the LLM picks the wrong tool, improve the description — don't add regex routing.

## Task 4: Docker Deployment

**Goal:** Deploy the bot in a container alongside the backend.

**Approach:**
- Create `Dockerfile` for the bot
- Add bot service to `docker-compose.yml`
- Configure container networking (use service names, not `localhost`)
- Set up health checks and restart policies

**Key Pattern:** Containers communicate via Docker network service names. The bot connects to `http://backend:42002` not `localhost:42002`.

## File Structure

```
bot/
├── bot.py              # Entry point (--test + Telegram modes)
├── config.py           # Environment configuration
├── handlers/
│   ├── __init__.py
│   └── command_handlers.py  # Pure handler functions
├── services/           # Task 2+: API and LLM clients
│   ├── api_client.py
│   └── llm_client.py
├── pyproject.toml      # Dependencies
└── PLAN.md             # This file
```

## Testing Strategy

1. **Test mode:** `uv run bot.py --test "/command"` for quick iteration
2. **Unit tests:** Test handlers directly (no Telegram mocking needed)
3. **Integration tests:** Run bot in Telegram and verify responses

## Acceptance Criteria

- `--test` mode works for all commands
- Handlers have no Telegram imports
- Config loads from `.env.bot.secret`
- `uv sync` succeeds without errors
