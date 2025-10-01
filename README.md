# Telegram GitHub Bot

<p align="center">
  <img src="https://github.com/Riflxz/github-bot-v5A/raw/main/banner.jpg" alt="Banner" width="100%" />
</p>

A personal, private Telegram bot designed to automate the entire workflow of uploading projects to GitHub. Simply send a ZIP file, and the bot will create a repository, generate a professional README, and push all your files.

## Key Features

- **Fully Automated**: From receiving a file to a complete GitHub repository, the entire process is hands-free.
- **ZIP Upload**: Upload your entire project in a single `.zip` file directly through Telegram.
- **Smart README Generation**: Automatically analyzes your project to detect languages and frameworks, then generates a detailed `README.md`.
- **Repository Management**: Update existing repositories, change visibility (public/private), get repository info, and delete repositories directly via bot commands.
- **Dual Upload Modes**: Choose between `normal` mode (uses your existing README) or `template` mode (always generates a new one).
- **Privacy First**: The bot is locked to a single `OWNER_ID`, ensuring only you can use it.
- **Simplified Workflow**: Comes with a `Justfile` for easy, one-word commands like `just run` and `just install`.

---

## Getting Started

Setting up and running this bot is a simple three-step process. For a detailed walkthrough on acquiring tokens and setting up your environment, please refer to the **[Full Setup Guide](./SETUP.md)**.

### 1. Configure the Environment

First, you need to provide your API tokens. Copy the `.env.example` file to a new file named `.env` and fill in your credentials.

> **Note**: Detailed instructions for getting each token are in the [setup guide](./SETUP.md).

### 2. Install Dependencies

With your environment configured, install all the necessary Python packages using one simple command.

```bash
just install
```

### 3. Run the Bot

That's it! You can now start the bot.

```bash
just run
```

---

## Command Reference

This project uses two types of commands: **Bot Commands** (sent via Telegram) and **Development Commands** (run in your terminal).

### Bot Commands (Telegram)

| Command | Description |
| :--- | :--- |
| `/start` | Displays a welcome message and basic guide. |
| `/help` | Shows the bot usage guide and command list. |
| `/upload` | Upload a new project in **Normal** mode. |
| `/upload template` | Upload a new project in **Template** mode. |
| `/upd_repo [repo]` | Update an existing repository. |
| `/upd_repo template [repo]` | Update an existing repository in **Template** mode. |
| `/info` | View statistics and recent repositories. |
| `/del [repo]` | Deletes the specified repository. |
| `/inp [repo]` | Displays detailed information about a repository. |
| `/priv [repo]` | Sets a repository's visibility to **private**. |
| `/pblc [repo]` | Sets a repository's visibility to **public**. |

### Development Commands (`just`)

| Command | Description |
| :--- | :--- |
| `just run` | Starts the bot. |
| `just install` | Installs/re-installs all dependencies. |
| `just lint` | Checks the code for style issues and errors. |
| `just format` | Automatically formats the code. |
| `just check` | Runs both the linter and formatter. |

---

## Required ZIP Structure

For the bot to work correctly, your project files **must be in the root** of the ZIP file, not nested inside a folder.

```
✅ CORRECT:
project-name.zip
├── main.py
├── config.py
└── README.md

❌ INCORRECT:
project-name.zip
└── project-folder/  <-- DON'T DO THIS
    ├── main.py
    └── config.py
```

---

*Created by Riflxz.*
