# Bot Dockerfile - uses uv for dependency management
FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy pyproject.toml for dependency installation
COPY pyproject.toml ./

# Install dependencies using uv (no lock file in bot directory)
RUN uv sync --no-dev

# Copy bot source code
COPY bot.py config.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the bot
CMD ["uv", "run", "python", "bot.py"]
