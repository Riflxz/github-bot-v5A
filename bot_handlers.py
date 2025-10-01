"""
Telegram bot handlers for GitHub repository management
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from github_manager import GitHubManager
from config import Config

logger = logging.getLogger(__name__)

class BotHandlers:
    """Handler class for bot commands and messages"""
    
    def __init__(self):
        """Initialize bot handlers"""
        self.config = Config()
        self.github_manager = GitHubManager(self.config.GITHUB_TOKEN)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            # Validate GitHub token first
            if not self.github_manager.validate_token():
                await update.message.reply_text(
                    self.config.ERROR_MESSAGES['invalid_token'],
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Send welcome message
            welcome_text = self.config.WELCOME_MESSAGE
            welcome_text += f"\n{self.config.SUCCESS_MESSAGES['token_valid']}"
            
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(
                self.config.ERROR_MESSAGES['api_error']
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            await update.message.reply_text(
                self.config.HELP_MESSAGE,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text("Terjadi kesalahan saat menampilkan bantuan.")
    
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /info command - show all repositories"""
        try:
            # Validate token first
            if not self.github_manager.validate_token():
                await update.message.reply_text(
                    self.config.ERROR_MESSAGES['invalid_token']
                )
                return
            
            # Send "loading" message
            loading_msg = await update.message.reply_text("📡 Mengambil data repository...")
            
            # Get all repositories
            repos = self.github_manager.get_user_repos()
            
            if not repos:
                await loading_msg.edit_text(
                    "Belum ada repository di akun GitHub kamu atau terjadi kesalahan saat mengambil data."
                )
                return
            
            # Format and send repository list
            repo_list = self.github_manager.format_repository_list(repos)
            
            await loading_msg.edit_text(
                repo_list,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            await update.message.reply_text(
                self.config.ERROR_MESSAGES['api_error']
            )
    
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /del command - delete repository"""
        try:
            # Check if repository name is provided
            if not context.args:
                await update.message.reply_text(
                    "Cara pakai: /del [nama-repository]\n\nContoh: /del my-project"
                )
                return
            
            repo_name = context.args[0]
            
            # Validate token first
            if not self.github_manager.validate_token():
                await update.message.reply_text(
                    self.config.ERROR_MESSAGES['invalid_token']
                )
                return
            
            # Send confirmation message
            confirm_msg = await update.message.reply_text(
                f"🔄 Menghapus repository '{repo_name}'..."
            )
            
            # Check if repository exists
            repo_info = self.github_manager.get_repository_info(repo_name)
            if not repo_info:
                await confirm_msg.edit_text(
                    f"Repository '{repo_name}' tidak ditemukan di akun kamu."
                )
                return
            
            # Delete repository
            if self.github_manager.delete_repository(repo_name):
                await confirm_msg.edit_text(
                    f"✅ Repository '{repo_name}' berhasil dihapus!"
                )
            else:
                await confirm_msg.edit_text(
                    f"❌ Gagal menghapus repository '{repo_name}'. Periksa izin akses kamu."
                )
            
        except Exception as e:
            logger.error(f"Error in delete command: {e}")
            await update.message.reply_text(
                self.config.ERROR_MESSAGES['api_error']
            )
    
    async def project_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /inp command - get detailed project information"""
        try:
            # Check if repository name is provided
            if not context.args:
                await update.message.reply_text(
                    "Cara pakai: /inp [nama-repository]\n\nContoh: /inp my-project"
                )
                return
            
            repo_name = context.args[0]
            
            # Validate token first
            if not self.github_manager.validate_token():
                await update.message.reply_text(
                    self.config.ERROR_MESSAGES['invalid_token']
                )
                return
            
            # Send loading message
            loading_msg = await update.message.reply_text(
                f"📡 Mengambil info repository '{repo_name}'..."
            )
            
            # Get repository information
            repo_info = self.github_manager.get_repository_info(repo_name)
            if not repo_info:
                await loading_msg.edit_text(
                    f"Repository '{repo_name}' tidak ditemukan di akun kamu."
                )
                return
            
            # Get repository contents
            contents = self.github_manager.get_repository_contents(repo_name)
            
            # Format and send detailed information
            detailed_info = self.github_manager.format_repository_info(repo_info, contents)
            
            await loading_msg.edit_text(
                detailed_info,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in project info command: {e}")
            await update.message.reply_text(
                self.config.ERROR_MESSAGES['api_error']
            )
    
    async def create_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create command - create new repository"""
        try:
            # Check if repository name is provided
            if not context.args:
                await update.message.reply_text(
                    "Cara pakai: /create [nama-repository] [deskripsi]\n\nContoh: /create my-project \"Deskripsi project\""
                )
                return
            
            repo_name = context.args[0]
            description = ' '.join(context.args[1:]) if len(context.args) > 1 else ''
            
            # Validate token first
            if not self.github_manager.validate_token():
                await update.message.reply_text(
                    self.config.ERROR_MESSAGES['invalid_token']
                )
                return
            
            # Send creating message
            creating_msg = await update.message.reply_text(
                f"🔄 Membuat repository '{repo_name}'..."
            )
            
            # Create repository
            if self.github_manager.create_repository(repo_name, description):
                await creating_msg.edit_text(
                    f"✅ Repository '{repo_name}' berhasil dibuat!\n\n"
                    f"🌐 https://github.com/{self.github_manager.username}/{repo_name}"
                )
            else:
                await creating_msg.edit_text(
                    f"❌ Gagal membuat repository '{repo_name}'. "
                    f"Mungkin nama sudah digunakan atau ada masalah izin."
                )
            
        except Exception as e:
            logger.error(f"Error in create command: {e}")
            await update.message.reply_text(
                self.config.ERROR_MESSAGES['api_error']
            )
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command - alternative to /info"""
        await self.info_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages"""
        try:
            message_text = update.message.text.lower()
            
            # Check for common questions or help requests
            if any(word in message_text for word in ['help', 'bantuan', 'gimana', 'cara']):
                await update.message.reply_text(
                    "Ketik /help untuk lihat semua perintah yang bisa dipakai!"
                )
            elif any(word in message_text for word in ['repo', 'repository', 'project']):
                await update.message.reply_text(
                    "Ketik /info untuk lihat semua repository atau /inp [nama-repo] untuk info detail."
                )
            else:
                await update.message.reply_text(
                    "Maaf, gak ngerti pesan kamu. Ketik /help untuk bantuan."
                )
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "Terjadi kesalahan saat memproses pesan kamu."
            )
