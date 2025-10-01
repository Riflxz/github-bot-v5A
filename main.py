#!/usr/bin/env python3
"""
Private Telegram Bot for Automated GitHub Project Uploads
"""

import asyncio
import logging
import os
import zipfile
import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

from config import Config
from github_handler import GitHubHandler
from readme_generator import ReadmeGenerator

# Load environment variables
load_dotenv()

# Configure logging

logger = logging.getLogger(__name__)

# Global counter for uploaded projects
upload_counter = 0

class TelegramBot:
    def __init__(self):
        self.config = Config()
        self.github_handler = GitHubHandler(self.config.GITHUB_TOKEN)
        self.readme_generator = ReadmeGenerator()
        self.last_message_time = {}
        self.rate_limit_seconds = 2  # Allow 1 message every 2 seconds per user

    def _is_authorized_and_not_rate_limited(self, update: Update) -> bool:
        """Single check for authorization and rate limiting."""
        if not update.effective_user:
            return False
            
        user_id = update.effective_user.id

        # 1. Authorization Check: Silently ignore non-owners
        if user_id != self.config.OWNER_ID:
            return False

        # 2. Rate Limit Check (only for the owner)
        current_time = time.time()
        last_time = self.last_message_time.get(user_id, 0)

        if (current_time - last_time) < self.rate_limit_seconds:
            logger.warning(f"Rate limit exceeded for owner {user_id}")
            return False  # Silently ignore spam

        self.last_message_time[user_id] = current_time
        return True
    
    def _check_zip_structure(self, extract_dir: str) -> bool:
        """
        Check if ZIP structure is correct (files directly in root).
        Returns True if structure is correct, False if nested.
        """
        contents = os.listdir(extract_dir)
        
        # If there's only one item and it's a directory, structure is wrong
        if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
            return False
        
        return True
    
    def _fix_zip_structure(self, extract_dir: str) -> None:
        """Fix ZIP structure by moving files from nested folder to root"""
        contents = os.listdir(extract_dir)
        
        if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
            nested_dir = os.path.join(extract_dir, contents[0])
            
            # Move all files from nested directory to root
            for item in os.listdir(nested_dir):
                src = os.path.join(nested_dir, item)
                dst = os.path.join(extract_dir, item)
                shutil.move(src, dst)
            
            # Remove empty nested directory
            os.rmdir(nested_dir)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        
        welcome_message = """
🤖 **Bot GitHub Upload Otomatis**

Halo! Bot ini bisa bantu kamu upload project ke GitHub secara otomatis.

**Fitur:**
• Upload project dari file ZIP
• Buat repository GitHub otomatis
• Generate README.md profesional
• Support 2 mode upload (normal & template)

**Cara upload project:**
1. Ketik `/upload` atau `/upload template`
2. Kirim file ZIP berisi project kamu
3. Bot akan otomatis buat repository dan upload semua file

**Struktur ZIP yang benar:**
```
✅ BENAR:
nama-project.zip
├── main.py
├── config.py
└── README.md

❌ SALAH:
nama-project.zip
└── folder-project/
    ├── main.py
    ├── config.py
    └── README.md
```

**File project harus langsung di root ZIP, bukan dalam folder!**

Ketik /help untuk lihat semua perintah yang bisa dipakai.
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        
        help_message = """
📋 **Panduan Penggunaan Bot**

**Perintah yang Tersedia:**

/start - Tampilkan sambutan dan informasi bot
/help - Panduan penggunaan bot
/upload - Upload project baru ke GitHub
/upload template - Upload project baru dengan README template
/upd_repo [nama-repo] - Update repository yang sudah ada
/upd_repo template [nama-repo] - Update repo dengan README template
/priv [nama-repo] - Ubah repository menjadi private
/pblc [nama-repo] - Ubah repository menjadi public
/info - Lihat statistik upload
/del [nama-repo] - Hapus repository
/inp [nama-repo] - Info detail repository

**Mode Upload:**

🔹 **Mode Normal** (`/upload`)
• Jika ZIP berisi README.md → gunakan yang dari ZIP
• Jika ZIP tidak ada README.md → buat README basic

🔹 **Mode Template** (`/upload template`)
• Selalu gunakan template README profesional dari bot
• Ganti README.md yang ada di ZIP (jika ada)

**Cara Upload Project:**
1. Ketik `/upload` atau `/upload template`
2. Kirim file ZIP yang berisi project kamu
3. Bot akan secara otomatis:
   • Ekstrak file ZIP
   • Buat repository GitHub baru
   • Generate/gunakan README.md sesuai mode
   • Upload semua file ke repository

**Catatan:**
• Nama repository akan sama dengan nama file ZIP
• Semua file dalam ZIP akan diupload ke root repository
• Maksimal ukuran file: 20MB
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown'
        )
    
    async def upload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /upload command"""
        if not self._is_authorized_and_not_rate_limited(update):
            return

        # Clear any previous state
        context.user_data.pop('mode', None)
        context.user_data.pop('update_repo_name', None)

        # Check if user wants template mode
        command_text = update.message.text.strip()
        use_template = command_text.lower() == '/upload template'
        context.user_data['use_template'] = use_template
        context.user_data['mode'] = 'upload' # Set the mode to upload

        if use_template:
            upload_message = """
📤 **Mode Upload Template Aktif**

Silakan kirim file ZIP yang berisi project kamu.

**Mode Template:** README.md akan dibuat menggunakan template profesional dari source code, mengganti README.md yang ada di ZIP (jika ada).

**Format yang didukung:** .zip
**Ukuran maksimal:** 20MB
            """
        else:
            upload_message = """
📤 **Mode Upload Aktif**

Silakan kirim file ZIP yang berisi project kamu.

**Mode Normal:** Jika ZIP berisi README.md, akan digunakan yang dari ZIP. Jika tidak ada, akan dibuat README.md basic.

**Format yang didukung:** .zip
**Ukuran maksimal:** 20MB
            """
        
        await update.message.reply_text(
            upload_message,
            parse_mode='Markdown'
        )
    
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /info command"""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        
        # Get repository list
        repos = await self.github_handler.get_repositories()
        
        if repos:
            repo_info = f"📊 **Statistik GitHub:**\n\n"
            repo_info += f"📁 Total repository: {len(repos)}\n"
            repo_info += f"📤 Upload melalui bot: {upload_counter}\n\n"
            repo_info += "🔗 **5 Repository Terbaru:**\n"
            
            for i, repo in enumerate(repos[:5], 1):
                repo_info += f"{i}. {repo['name']}\n"
                repo_info += f"   📝 {repo.get('description', 'No description')}\n"
                repo_info += f"   🌟 {repo['stargazers_count']} stars\n\n"
        else:
            repo_info = "Belum ada repository di akun GitHub kamu."
        
        await update.message.reply_text(repo_info, parse_mode='Markdown')
    
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /del command"""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        
        if not context.args:
            await update.message.reply_text(
                "Cara pakai: /del [nama-repository]\n\nContoh: /del my-project"
            )
            return
        
        repo_name = context.args[0]
        
        # Send confirmation message
        confirm_msg = await update.message.reply_text(
            f"🔄 Menghapus repository '{repo_name}'..."
        )
        
        success = await self.github_handler.delete_repository(repo_name)
        
        if success:
            await confirm_msg.edit_text(
                f"✅ Repository '{repo_name}' berhasil dihapus!"
            )
        else:
            await confirm_msg.edit_text(
                f"❌ Gagal menghapus repository '{repo_name}'. Pastikan nama repository benar."
            )

    async def private_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /priv command to make a repository private."""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        await self._toggle_repo_visibility(update, context, private=True)

    async def public_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pblc command to make a repository public."""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        await self._toggle_repo_visibility(update, context, private=False)

    async def _toggle_repo_visibility(self, update: Update, context: ContextTypes.DEFAULT_TYPE, private: bool) -> None:
        """Generic handler to toggle repository visibility."""
        # Auth check is done by the calling commands
        command = "priv" if private else "pblc"
        if not context.args:
            await update.message.reply_text(f"Cara pakai: /{command} [nama-repository]")
            return

        repo_name = context.args[0]
        visibility_text = "private" if private else "public"
        
        loading_msg = await update.message.reply_text(f"🔄 Mengubah repository '{repo_name}' menjadi {visibility_text}...")

        # Check if repo exists
        repo_info = await self.github_handler.get_repository_info(repo_name)
        if not repo_info:
            await loading_msg.edit_text(f"❌ Repository '{repo_name}' tidak ditemukan.")
            return

        success = await self.github_handler.set_repository_visibility(repo_name, private=private)

        if success:
            await loading_msg.edit_text(f"✅ Repository '{repo_name}' berhasil diubah menjadi {visibility_text}.")
        else:
            await loading_msg.edit_text(f"❌ Gagal mengubah visibilitas repository '{repo_name}'.")
    
    async def project_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /inp command"""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        
        if not context.args:
            await update.message.reply_text(
                "Cara pakai: /inp [nama-repository]\n\nContoh: /inp my-project"
            )
            return
        
        repo_name = context.args[0]
        
        # Send loading message
        loading_msg = await update.message.reply_text(
            f"📡 Mengambil info repository '{repo_name}'..."
        )
        
        repo_info = await self.github_handler.get_repository_info(repo_name)
        
        if repo_info:
            info_text = f"📊 **Info Repository: {repo_info['name']}**\n\n"
            info_text += f"📝 **Deskripsi:** {repo_info.get('description', 'No description')}\n"
            info_text += f"🌟 **Stars:** {repo_info['stargazers_count']}\n"
            info_text += f"🍴 **Forks:** {repo_info['forks_count']}\n"
            info_text += f"👁️ **Watchers:** {repo_info['watchers_count']}\n"
            info_text += f"📏 **Size:** {repo_info['size']} KB\n"
            info_text += f"🔒 **Private:** {'Yes' if repo_info['private'] else 'No'}\n"
            info_text += f"💻 **Language:** {repo_info.get('language', 'Unknown')}\n"
            info_text += f"🔗 **URL:** {repo_info['html_url']}\n"
            
            await loading_msg.edit_text(info_text, parse_mode='Markdown')
        else:
            await loading_msg.edit_text(
                f"Repository '{repo_name}' tidak ditemukan di akun kamu."
            )
    
    async def update_repo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /upd_repo command"""
        if not self._is_authorized_and_not_rate_limited(update):
            return

        # Clear any previous state
        context.user_data.pop('mode', None)
        context.user_data.pop('update_repo_name', None)

        if not context.args:
            await update.message.reply_text(
                "Cara pakai: /upd_repo [nama-repository]\n\nContoh: /upd_repo my-project"
            )
            return

        repo_name = context.args[0]

        # Check if repository exists
        loading_msg = await update.message.reply_text(f"Mengecek repository '{repo_name}'...")
        repo_info = await self.github_handler.get_repository_info(repo_name)

        if not repo_info:
            await loading_msg.edit_text(
                f"❌ Repository '{repo_name}' tidak ditemukan di akun GitHub kamu."
            )
            return

        # Set update mode in user context
        context.user_data['mode'] = 'update'
        context.user_data['update_repo_name'] = repo_name
        
        # Also check for template mode
        use_template = 'template' in update.message.text.lower()
        context.user_data['use_template'] = use_template

        await loading_msg.edit_text(
            f"✅ **Mode Update Aktif** untuk repository **'{repo_name}'**\n"
            f"📄 Mode README: {'Template' if use_template else 'Normal'}\n\n"
            "Silakan kirim file ZIP yang berisi konten baru untuk project ini.",
            parse_mode='Markdown'
        )

    async def run_update_workflow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, repo_name: str, use_template: bool):
        """Runs the full workflow for updating a repository."""
        document = update.message.document
        processing_msg = await update.message.reply_text(
            f"🔄 **Memperbarui repository '{repo_name}'**\n\n"
            f"📥 Mengunduh file ZIP..."
        )

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, document.file_name)
                extract_dir = os.path.join(temp_dir, 'extracted')

                # Download and extract
                file = await context.bot.get_file(document.file_id)
                await file.download_to_drive(zip_path)
                await processing_msg.edit_text(
                    f"🔄 **Memperbarui repository '{repo_name}'**\n\n"
                    f"✅ ZIP diunduh\n"
                    f"📂 Mengekstrak file..."
                )
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                if not self._check_zip_structure(extract_dir):
                    self._fix_zip_structure(extract_dir)

                # Clear repository contents
                await processing_msg.edit_text(
                    f"🔄 **Memperbarui repository '{repo_name}'**\n\n"
                    f"✅ File diekstrak\n"
                    f"🗑️ Membersihkan repository..."
                )
                cleared = await self.github_handler.clear_repository_contents(repo_name)
                if not cleared:
                    await processing_msg.edit_text(
                        f"❌ **Gagal membersihkan repository '{repo_name}'**\n\n"
                        "Mungkin ada masalah dengan izin akses atau API GitHub. Proses update dibatalkan."
                    )
                    return

                # Generate README if needed
                project_name_for_readme = repo_name
                if use_template:
                    readme_content = self.readme_generator.generate_readme(extract_dir, project_name_for_readme)
                    readme_path = os.path.join(extract_dir, 'README.md')
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                elif not os.path.exists(os.path.join(extract_dir, 'README.md')):
                    readme_content = f"# {project_name_for_readme}\n\nProject updated via Telegram Bot\n"
                    readme_path = os.path.join(extract_dir, 'README.md')
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)

                # Upload new files
                await processing_msg.edit_text(
                    f"🔄 **Memperbarui repository '{repo_name}'**\n\n"
                    f"✅ Repository dibersihkan\n"
                    f"📤 Mengunggah file baru..."
                )
                success = await self.github_handler.upload_files(repo_name, extract_dir)

                if success:
                    repo_url = f"https://github.com/{await self.github_handler.get_username()}/{repo_name}"
                    await processing_msg.edit_text(
                        f"🎉 **Update Berhasil!**\n\n"
                        f"📁 Project: {repo_name}\n"
                        f"🔗 Repository: {repo_url}\n"
                        f"📄 Mode README: {'Template' if use_template else 'Normal'}"
                    )
                else:
                    await processing_msg.edit_text(
                        f"❌ **Update Gagal**\n\n"
                        "Gagal mengunggah file baru. Repository mungkin dalam keadaan kosong."
                    )

        except Exception as e:
            logger.error(f"Error processing update: {str(e)}")
            await processing_msg.edit_text(
                f"❌ **Error saat memproses update**\n\n"
                f"Terjadi kesalahan: {str(e)}"
            )
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle document (ZIP file) uploads"""
        if not self._is_authorized_and_not_rate_limited(update):
            return

        document = update.message.document
        mode = context.user_data.get('mode')

        # --- Update Workflow ---
        if mode == 'update':
            repo_name = context.user_data.get('update_repo_name')
            use_template = context.user_data.get('use_template', False)
            
            # Clean up context data
            context.user_data.pop('mode', None)
            context.user_data.pop('update_repo_name', None)
            context.user_data.pop('use_template', None)

            if not repo_name:
                await update.message.reply_text("Terjadi kesalahan: nama repository untuk di-update tidak ditemukan.")
                return
            
            await self.run_update_workflow(update, context, repo_name, use_template)
            return

        # --- Create Workflow (Original Logic) ---
        if mode != 'upload':
            await update.message.reply_text(
                "Untuk mengunggah atau memperbarui, silakan gunakan perintah /upload atau /upd_repo terlebih dahulu."
            )
            return
        
        # Check if it's a ZIP file
        if not document.file_name.endswith('.zip'):
            await update.message.reply_text(
                "❌ Hanya file ZIP yang didukung. Silakan upload file .zip"
            )
            return
        
        # Check file size
        if document.file_size > self.config.MAX_FILE_SIZE:
            await update.message.reply_text(
                f"❌ File terlalu besar. Maksimal ukuran: {self.config.MAX_FILE_SIZE // (1024*1024)}MB"
            )
            return
        
        # Get project name from ZIP filename
        project_name = document.file_name.replace('.zip', '')
        
        # Check if template mode is enabled
        use_template = context.user_data.get('use_template', False)
        
        # Clean up context data
        context.user_data.pop('mode', None)
        context.user_data.pop('use_template', None)

        # Send processing message
        processing_msg = await update.message.reply_text(
            f"🔄 **Memproses upload project '{project_name}'**\n\n"
            f"📥 Mengunduh file ZIP...\n"
            f"📂 Mode: {'Template' if use_template else 'Normal'}"
        )
        
        try:
            # Download the file
            file = await context.bot.get_file(document.file_id)
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, document.file_name)
                extract_dir = os.path.join(temp_dir, 'extracted')
                
                # Download ZIP file
                await file.download_to_drive(zip_path)
                
                await processing_msg.edit_text(
                    f"🔄 **Memproses upload project '{project_name}'**\n\n"
                    f"✅ File ZIP berhasil diunduh\n"
                    f"📂 Mengekstrak file..."
                )
                
                # Extract ZIP file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Check and fix ZIP structure if needed
                if not self._check_zip_structure(extract_dir):
                    self._fix_zip_structure(extract_dir)
                
                await processing_msg.edit_text(
                    f"🔄 **Memproses upload project '{project_name}'**\n\n"
                    f"✅ File ZIP berhasil diunduh\n"
                    f"✅ File berhasil diekstrak\n"
                    f"🔄 Membuat repository GitHub..."
                )
                
                # Create GitHub repository
                repo_created = await self.github_handler.create_repository(
                    project_name,
                    f"Project uploaded via Telegram Bot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                if not repo_created:
                    await processing_msg.edit_text(
                        f"❌ **Gagal membuat repository '{project_name}'**\n\n"
                        f"Repository dengan nama tersebut mungkin sudah ada atau ada masalah dengan GitHub API."
                    )
                    return
                
                await processing_msg.edit_text(
                    f"🔄 **Memproses upload project '{project_name}'**\n\n"
                    f"✅ File ZIP berhasil diunduh\n"
                    f"✅ File berhasil diekstrak\n"
                    f"✅ Repository GitHub berhasil dibuat\n"
                    f"🔄 Mengupload file..."
                )
                
                # Generate README if needed
                if use_template:
                    readme_content = self.readme_generator.generate_readme(extract_dir, project_name)
                    readme_path = os.path.join(extract_dir, 'README.md')
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                elif not os.path.exists(os.path.join(extract_dir, 'README.md')):
                    # Create basic README if not exists
                    readme_content = f"# {project_name}\n\nProject uploaded via Telegram Bot\n"
                    readme_path = os.path.join(extract_dir, 'README.md')
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                
                # Upload files to repository
                success = await self.github_handler.upload_files(project_name, extract_dir)
                
                if success:
                    global upload_counter
                    upload_counter += 1
                    
                    repo_url = f"https://github.com/{await self.github_handler.get_username()}/{project_name}"
                    
                    await processing_msg.edit_text(
                        f"🎉 **Upload Berhasil!**\n\n"
                        f"📁 Project: {project_name}\n"
                        f"🔗 Repository: {repo_url}\n"
                        f"📂 Mode: {'Template' if use_template else 'Normal'}\n"
                        f"📊 Total upload: {upload_counter}"
                    )
                else:
                    await processing_msg.edit_text(
                        f"❌ **Upload Gagal**\n\n"
                        f"Repository berhasil dibuat tapi gagal upload file. Coba lagi nanti."
                    )
                
        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            await processing_msg.edit_text(
                f"❌ **Error saat memproses upload**\n\n"
                f"Terjadi kesalahan: {str(e)}"
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle non-command messages"""
        if not self._is_authorized_and_not_rate_limited(update):
            return
        
        message_text = update.message.text.lower()
        
        # Check for common questions or help requests
        if any(word in message_text for word in ['help', 'bantuan', 'gimana', 'cara']):
            await update.message.reply_text(
                "Ketik /help untuk lihat semua perintah yang bisa dipakai!"
            )
        elif any(word in message_text for word in ['upload', 'project']):
            await update.message.reply_text(
                "Ketik /upload untuk upload project atau /upload template untuk mode template."
            )
        else:
            await update.message.reply_text(
                "Maaf, gak ngerti pesan kamu. Ketik /help untuk bantuan."
            )


def main():
    """Main function to run the bot"""
    
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Create bot instance
    bot = TelegramBot()
    
    # Create application
    app = Application.builder().token(bot_token).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", bot.start_command))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("upload", bot.upload_command))
    app.add_handler(CommandHandler("upd_repo", bot.update_repo_command))
    app.add_handler(CommandHandler("info", bot.info_command))
    app.add_handler(CommandHandler("del", bot.delete_command))
    app.add_handler(CommandHandler("priv", bot.private_command))
    app.add_handler(CommandHandler("pblc", bot.public_command))
    app.add_handler(CommandHandler("inp", bot.project_info_command))
    app.add_handler(MessageHandler(filters.Document.ALL, bot.handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    logger.info("Bot started successfully")
    
    # Run the bot
    app.run_polling(allowed_updates=["message"])


if __name__ == '__main__':
    main()
