# Default task, runs when no task is specified
default: list

# List available commands
list:
    @just --list

# Install dependencies from requirements.txt
install:
    @echo "Installing dependencies..."
    pip install -r requirements.txt
    @echo "Dependencies installed."

# Run the bot
run:
    @echo "Starting the bot..."
    python3 main.py

# Lint the code with ruff
lint:
    @echo "Linting code with ruff..."
    ruff check .

# Format the code with ruff
format:
    @echo "Formatting code with ruff..."
    ruff format .

# A combined command to check and format the code
check: lint format
    @echo "All checks and formatting passed."
