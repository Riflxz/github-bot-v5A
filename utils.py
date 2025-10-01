"""
Utility functions for the Telegram GitHub Bot
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def validate_repo_name(name: str) -> bool:
    """
    Validate repository name according to GitHub rules
    
    Args:
        name: Repository name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name:
        return False
    
    # GitHub repository name rules
    # - Can contain alphanumeric characters and hyphens
    # - Cannot start or end with hyphen
    # - Cannot have consecutive hyphens
    # - Must be 1-100 characters long
    
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?$'
    
    if not re.match(pattern, name):
        return False
    
    if len(name) > 100:
        return False
    
    if '--' in name:
        return False
    
    return True

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_date(date_string: str) -> str:
    """
    Format ISO date string to human readable format
    
    Args:
        date_string: ISO format date string
        
    Returns:
        str: Formatted date string
    """
    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%d %B %Y, %H:%M')
    except:
        return "Unknown"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def escape_markdown(text: str) -> str:
    """
    Escape markdown special characters
    
    Args:
        text: Text to escape
        
    Returns:
        str: Escaped text
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def parse_command_args(text: str) -> List[str]:
    """
    Parse command arguments from text
    
    Args:
        text: Command text
        
    Returns:
        List[str]: List of arguments
    """
    # Simple argument parsing - split by spaces but respect quoted strings
    args = []
    current_arg = ""
    in_quotes = False
    
    for char in text:
        if char == '"' and not in_quotes:
            in_quotes = True
        elif char == '"' and in_quotes:
            in_quotes = False
            if current_arg:
                args.append(current_arg)
                current_arg = ""
        elif char == ' ' and not in_quotes:
            if current_arg:
                args.append(current_arg)
                current_arg = ""
        else:
            current_arg += char
    
    if current_arg:
        args.append(current_arg)
    
    return args

def get_file_type_icon(filename: str) -> str:
    """
    Get icon for file type based on extension
    
    Args:
        filename: Name of the file
        
    Returns:
        str: Icon emoji for file type
    """
    if not filename:
        return "📄"
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    icon_map = {
        'py': '🐍',
        'js': '📜',
        'html': '🌐',
        'css': '🎨',
        'json': '📋',
        'md': '📝',
        'txt': '📄',
        'yml': '⚙️',
        'yaml': '⚙️',
        'xml': '📄',
        'png': '🖼️',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'gif': '🖼️',
        'svg': '🖼️',
        'pdf': '📕',
        'doc': '📄',
        'docx': '📄',
        'zip': '📦',
        'tar': '📦',
        'gz': '📦',
    }
    
    return icon_map.get(extension, '📄')

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """
    Create ASCII progress bar
    
    Args:
        current: Current progress
        total: Total items
        length: Length of progress bar
        
    Returns:
        str: Progress bar string
    """
    if total == 0:
        return "█" * length
    
    filled_length = int(length * current / total)
    bar = "█" * filled_length + "░" * (length - filled_length)
    percentage = round(100 * current / total, 1)
    
    return f"{bar} {percentage}%"

def log_user_action(user_id: int, username: str, action: str, details: str = ""):
    """
    Log user actions for monitoring
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        action: Action performed
        details: Additional details
    """
    logger.info(f"User {user_id} (@{username}) performed: {action} - {details}")
