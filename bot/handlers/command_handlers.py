"""Command handlers - pure functions that take input and return text."""


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
/scores <lab_id> - Get scores for a lab"""


def handle_health() -> str:
    """Handle /health command - check backend health."""
    # TODO: Task 2 - call backend API
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command - list available labs."""
    # TODO: Task 2 - call backend API
    return "Available labs: (placeholder)"


def handle_scores(lab_id: str = "") -> str:
    """Handle /scores command - get scores for a lab.
    
    Args:
        lab_id: The lab identifier (e.g., 'lab-04')
    """
    # TODO: Task 2 - call backend API
    if lab_id:
        return f"Scores for {lab_id}: (placeholder)"
    return "Please specify a lab ID, e.g., /scores lab-04"
