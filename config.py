"""
Configuration file for the Telegram GitHub Upload Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class containing all bot settings"""
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # GitHub Personal Access Token
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    # Owner Telegram ID (only this user can use the bot)
    OWNER_ID = int(os.getenv('OWNER_ID'))
    
    # GitHub API Base URL
    GITHUB_API_BASE = 'https://api.github.com'
    
    # Maximum file size for uploads (20MB)
    MAX_FILE_SIZE = 20 * 1024 * 1024
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = ['.zip']
    
    # Default commit message
    DEFAULT_COMMIT_MESSAGE = 'Initial commit via Telegram Bot'
    
    # GitHub username (will be fetched from API)
    GITHUB_USERNAME = None
