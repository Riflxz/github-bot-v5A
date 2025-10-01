# Setup Guide: Telegram GitHub Bot

A straightforward guide to setting up and running the Telegram GitHub Upload Bot.

## 1. Install `just`

This project uses `just`, a command runner, to simplify common tasks. You'll need to install it first.

- **macOS (Homebrew):**
  ```bash
  brew install just
  ```

- **Windows (Chocolatey/Scoop/Winget):**
  ```bash
  # Using Chocolatey
  choco install just
  
  # Using Scoop
  scoop install just

  # Using Winget
  winget install --id Casey.Just --exact
  ```

- **Linux (Package Manager):**
  ```bash
  # Debian/Ubuntu
  sudo apt install just

  # Fedora
  sudo dnf install just

  # Arch Linux
  sudo pacman -S just
  ```

- **Universal (Cargo):**
  If you have Rust installed, you can use Cargo:
  ```bash
  cargo install just
  ```

For more installation options, see the [official `just` documentation](https://github.com/casey/just#installation).

## 2. Create a Telegram Bot

1.  Open Telegram and search for **@BotFather**.
2.  Send the `/newbot` command.
3.  Follow the instructions to create a new bot.
4.  Save the **bot token** you receive.

## 3. Generate a GitHub Personal Access Token

1.  Log in to your GitHub account and go to **Settings**.
2.  Navigate to **Developer settings** → **Personal access tokens** → **Tokens (classic)**.
3.  Click **Generate new token**.
4.  Give the token a name and select the following scopes:
    - `repo` (Full control of private repositories)
    - `delete_repo` (Required for deleting repositories)
5.  Click **Generate token** and save the token.

## 4. Configure Your Environment

1.  Clone or download this repository to your local machine.
2.  Create a file named `.env` in the project's root directory.
3.  Add the following configuration details to the `.env` file. Replace the placeholder values with your actual credentials.

    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
    GITHUB_TOKEN=your_github_personal_access_token_here
    OWNER_ID=your_telegram_user_id_here
    ```

    - **`TELEGRAM_BOT_TOKEN`**: The token you got from BotFather.
    - **`GITHUB_TOKEN`**: Your GitHub Personal Access Token.
    - **`OWNER_ID`**: Your personal Telegram User ID. This ensures only you can use the bot. You can get your ID from a bot like **@userinfobot**.

## 5. Install Dependencies

With `just` installed, you can now install the required Python packages with a simple command.

```bash
just install
```

This will read the `requirements.txt` file and install everything for you.

## 6. Run the Bot

Once the dependencies are installed and your `.env` file is configured, you can start the bot using `just`.

```bash
just run
```

The bot should now be running and responsive on Telegram. You can interact with it through the private chat you have with your bot.

## Available Commands (`just`)

Here are the commands defined in the `Justfile` for easier project management:

- `just list`: Lists all available commands.
- `just install`: Installs Python dependencies.
- `just run`: Starts the bot.
- `just lint`: Lints the code for errors and style issues.
- `just format`: Formats the code automatically.
- `just check`: Runs both the linter and formatter.
