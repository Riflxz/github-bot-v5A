"""
GitHub API handler for repository creation and file uploads
"""

import aiohttp
import asyncio
import base64
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class GitHubHandler:
    """Handle GitHub API operations"""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        self.username = None
    
    async def get_username(self) -> Optional[str]:
        """Get GitHub username from API"""
        if self.username:
            return self.username
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/user',
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.username = user_data['login']
                        return self.username
                    else:
                        logger.error(f"Failed to get GitHub username: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting GitHub username: {str(e)}")
            return None
    
    async def create_repository(self, repo_name: str, description: str = "") -> bool:
        """Create a new repository"""
        try:
            data = {
                'name': repo_name,
                'description': description,
                'private': False,
                'auto_init': False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.api_base}/user/repos',
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 201:
                        logger.info(f"Repository '{repo_name}' created successfully")
                        return True
                    elif response.status == 422:
                        logger.error(f"Repository '{repo_name}' already exists")
                        return False
                    else:
                        logger.error(f"Failed to create repository: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error creating repository: {str(e)}")
            return False
    
    async def upload_files(self, repo_name: str, source_dir: str) -> bool:
        """Upload all files from source directory to repository"""
        try:
            username = await self.get_username()
            if not username:
                return False
            
            # Get all files recursively
            files_to_upload = []
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, source_dir)
                    files_to_upload.append((file_path, relative_path))
            
            # Upload files one by one
            success_count = 0
            total_files = len(files_to_upload)
            
            async with aiohttp.ClientSession() as session:
                for file_path, relative_path in files_to_upload:
                    try:
                        # Read file content
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # Encode to base64
                        encoded_content = base64.b64encode(file_content).decode('utf-8')
                        
                        # Prepare data
                        data = {
                            'message': f'Add {relative_path}',
                            'content': encoded_content
                        }
                        
                        # Upload file
                        url = f'{self.api_base}/repos/{username}/{repo_name}/contents/{relative_path}'
                        async with session.put(
                            url,
                            headers=self.headers,
                            json=data
                        ) as response:
                            if response.status in [200, 201]:
                                success_count += 1
                                logger.info(f"Uploaded: {relative_path}")
                            else:
                                logger.error(f"Failed to upload {relative_path}: {response.status}")
                    
                    except Exception as e:
                        logger.error(f"Error uploading {relative_path}: {str(e)}")
            
            logger.info(f"Upload complete: {success_count}/{total_files} files uploaded")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error uploading files: {str(e)}")
            return False
    
    async def get_repositories(self) -> List[Dict]:
        """Get all repositories for the authenticated user"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/user/repos',
                    headers=self.headers,
                    params={'per_page': 100, 'sort': 'updated', 'direction': 'desc'}
                ) as response:
                    if response.status == 200:
                        repos = await response.json()
                        return repos
                    else:
                        logger.error(f"Failed to get repositories: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error getting repositories: {str(e)}")
            return []
    
    async def delete_repository(self, repo_name: str) -> bool:
        """Delete a repository"""
        try:
            username = await self.get_username()
            if not username:
                return False
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f'{self.api_base}/repos/{username}/{repo_name}',
                    headers=self.headers
                ) as response:
                    if response.status == 204:
                        logger.info(f"Repository '{repo_name}' deleted successfully")
                        return True
                    else:
                        logger.error(f"Failed to delete repository: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error deleting repository: {str(e)}")
            return False
    
    async def get_repository_info(self, repo_name: str) -> Optional[Dict]:
        """Get detailed information about a repository"""
        try:
            username = await self.get_username()
            if not username:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_base}/repos/{username}/{repo_name}',
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        repo_info = await response.json()
                        return repo_info
                    else:
                        logger.error(f"Failed to get repository info: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            return None

    async def get_repository_contents(self, repo_name: str, path: str = "") -> Optional[List[Dict]]:
        """Get repository contents at a specific path"""
        try:
            username = await self.get_username()
            if not username:
                return None
            
            url = f'{self.api_base}/repos/{username}/{repo_name}/contents/{path}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    # 404 is okay, means directory doesn't exist or is empty
                    elif response.status == 404:
                        logger.warning(f"Path '{path}' not found in repo '{repo_name}'.")
                        return []
                    else:
                        logger.error(f"Failed to get contents for {repo_name} at path {path}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting repository contents: {str(e)}")
            return None

    async def delete_file(self, repo_name: str, file_path: str, sha: str) -> bool:
        """Delete a file from a repository"""
        try:
            username = await self.get_username()
            if not username:
                return False
            
            url = f'{self.api_base}/repos/{username}/{repo_name}/contents/{file_path}'
            data = {
                'message': f'chore: delete {os.path.basename(file_path)}',
                'sha': sha
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        logger.info(f"Deleted file: {file_path}")
                        return True
                    else:
                        logger.error(f"Failed to delete file {file_path}: {response.status} - {await response.text()}")
                        return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    async def clear_repository_contents(self, repo_name: str) -> bool:
        """Deletes all file contents of a repository recursively."""
        logger.info(f"Starting to clear contents of repository '{repo_name}'")
        try:
            files_to_delete = []
            
            async def find_files_recursively(path=""):
                contents = await self.get_repository_contents(repo_name, path)
                if not contents:
                    return

                for item in contents:
                    if item['type'] == 'file':
                        files_to_delete.append({'path': item['path'], 'sha': item['sha']})
                    elif item['type'] == 'dir':
                        await find_files_recursively(item['path'])

            await find_files_recursively()

            if not files_to_delete:
                logger.info(f"Repository '{repo_name}' is already empty.")
                return True

            logger.info(f"Found {len(files_to_delete)} files to delete.")

            # Run deletions sequentially for stability and better logging
            all_deleted = True
            for file_info in files_to_delete:
                success = await self.delete_file(repo_name, file_info['path'], file_info['sha'])
                if not success:
                    all_deleted = False
                    logger.error(f"Stopping deletion process for '{repo_name}' due to an error.")
                    break

            if all_deleted:
                logger.info(f"Successfully cleared contents of repository '{repo_name}'")
                return True
            else:
                logger.error(f"Failed to clear all files in repository '{repo_name}'")
                return False

        except Exception as e:
            logger.error(f"An error occurred while clearing repository: {str(e)}")
            return False

    async def set_repository_visibility(self, repo_name: str, private: bool) -> bool:
        """Sets the visibility of a repository."""
        try:
            username = await self.get_username()
            if not username:
                return False

            url = f'{self.api_base}/repos/{username}/{repo_name}'
            data = {'private': private}

            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        visibility = "private" if private else "public"
                        logger.info(f"Repository '{repo_name}' visibility set to {visibility}")
                        return True
                    else:
                        logger.error(f"Failed to set visibility for {repo_name}: {response.status} - {await response.text()}")
                        return False
        except Exception as e:
            logger.error(f"Error setting repository visibility: {str(e)}")
            return False