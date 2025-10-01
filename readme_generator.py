"""
README.md generator for uploaded projects
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ReadmeGenerator:
    """Generate README.md content based on project structure"""
    
    def __init__(self):
        self.language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.vue': 'Vue.js',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.r': 'R',
            '.m': 'Objective-C',
            '.sh': 'Shell',
            '.bat': 'Batch',
            '.ps1': 'PowerShell'
        }
    
    def analyze_project(self, project_dir: str) -> Dict:
        """Analyze project structure and determine main language/framework"""
        analysis = {
            'languages': {},
            'frameworks': [],
            'files': [],
            'directories': [],
            'main_language': None,
            'project_type': None
        }
        
        # Count files by extension
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_dir)
                analysis['files'].append(relative_path)
                
                # Get file extension
                _, ext = os.path.splitext(file)
                if ext in self.language_extensions:
                    language = self.language_extensions[ext]
                    analysis['languages'][language] = analysis['languages'].get(language, 0) + 1
        
        # Determine main language
        if analysis['languages']:
            analysis['main_language'] = max(analysis['languages'], key=analysis['languages'].get)
        
        # Detect frameworks and project types
        analysis['frameworks'] = self._detect_frameworks(project_dir, analysis['files'])
        analysis['project_type'] = self._detect_project_type(project_dir, analysis['files'])
        
        return analysis
    
    def _detect_frameworks(self, project_dir: str, files: List[str]) -> List[str]:
        """Detect frameworks used in the project"""
        frameworks = []
        
        # Check for common framework files
        framework_indicators = {
            'package.json': ['Node.js', 'npm'],
            'requirements.txt': ['Python'],
            'Pipfile': ['Python', 'Pipenv'],
            'setup.py': ['Python'],
            'composer.json': ['PHP', 'Composer'],
            'Gemfile': ['Ruby'],
            'go.mod': ['Go'],
            'Cargo.toml': ['Rust'],
            'pom.xml': ['Java', 'Maven'],
            'build.gradle': ['Java', 'Gradle'],
            'pubspec.yaml': ['Dart', 'Flutter'],
            'vue.config.js': ['Vue.js'],
            'angular.json': ['Angular'],
            'next.config.js': ['Next.js'],
            'nuxt.config.js': ['Nuxt.js'],
            'gatsby-config.js': ['Gatsby'],
            'webpack.config.js': ['Webpack'],
            'vite.config.js': ['Vite'],
            'tsconfig.json': ['TypeScript'],
            'tailwind.config.js': ['Tailwind CSS'],
            'postcss.config.js': ['PostCSS']
        }
        
        for file in files:
            filename = os.path.basename(file)
            if filename in framework_indicators:
                frameworks.extend(framework_indicators[filename])
        
        # Check package.json for specific frameworks
        package_json_path = os.path.join(project_dir, 'package.json')
        if os.path.exists(package_json_path):
            try:
                import json
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                
                framework_packages = {
                    'react': 'React',
                    'vue': 'Vue.js',
                    'angular': 'Angular',
                    'express': 'Express.js',
                    'koa': 'Koa.js',
                    'fastify': 'Fastify',
                    'nest': 'NestJS',
                    'svelte': 'Svelte',
                    'solid-js': 'Solid.js',
                    'lit': 'Lit',
                    'bootstrap': 'Bootstrap',
                    'bulma': 'Bulma',
                    'material-ui': 'Material-UI',
                    'ant-design': 'Ant Design',
                    'chakra-ui': 'Chakra UI'
                }
                
                for package, framework in framework_packages.items():
                    if any(package in dep for dep in dependencies.keys()):
                        frameworks.append(framework)
            except:
                pass
        
        return list(set(frameworks))
    
    def _detect_project_type(self, project_dir: str, files: List[str]) -> Optional[str]:
        """Detect the type of project"""
        # Check for specific project indicators
        if 'package.json' in [os.path.basename(f) for f in files]:
            return 'Web Application'
        elif any(f.endswith('.py') for f in files):
            if 'requirements.txt' in [os.path.basename(f) for f in files]:
                return 'Python Application'
            elif 'manage.py' in [os.path.basename(f) for f in files]:
                return 'Django Application'
            elif 'app.py' in [os.path.basename(f) for f in files] or 'main.py' in [os.path.basename(f) for f in files]:
                return 'Python Application'
        elif any(f.endswith('.java') for f in files):
            return 'Java Application'
        elif any(f.endswith(('.cpp', '.c')) for f in files):
            return 'C/C++ Application'
        elif any(f.endswith('.go') for f in files):
            return 'Go Application'
        elif any(f.endswith('.rs') for f in files):
            return 'Rust Application'
        elif any(f.endswith('.php') for f in files):
            return 'PHP Application'
        elif any(f.endswith('.rb') for f in files):
            return 'Ruby Application'
        
        return 'Application'
    
    def generate_readme(self, project_dir: str, project_name: str) -> str:
        """Generate README.md content"""
        analysis = self.analyze_project(project_dir)
        
        # Build README content
        readme_content = f"# {project_name}\n\n"
        
        # Project description
        if analysis['project_type']:
            readme_content += f"A {analysis['project_type']}"
            if analysis['main_language']:
                readme_content += f" built with {analysis['main_language']}"
            readme_content += ".\n\n"
        else:
            readme_content += "Project uploaded via Telegram Bot.\n\n"
        
        # Technologies used
        if analysis['languages'] or analysis['frameworks']:
            readme_content += "## Technologies Used\n\n"
            
            if analysis['languages']:
                readme_content += "**Languages:**\n"
                for language, count in sorted(analysis['languages'].items(), key=lambda x: x[1], reverse=True):
                    readme_content += f"- {language}\n"
                readme_content += "\n"
            
            if analysis['frameworks']:
                readme_content += "**Frameworks/Libraries:**\n"
                for framework in analysis['frameworks']:
                    readme_content += f"- {framework}\n"
                readme_content += "\n"
        
        # Project structure
        readme_content += "## Project Structure\n\n"
        readme_content += "```\n"
        readme_content += f"{project_name}/\n"
        
        # Show directory structure
        dirs = set()
        for file in analysis['files']:
            dir_path = os.path.dirname(file)
            if dir_path and dir_path != '.':
                dirs.add(dir_path)
        
        # Sort directories and files
        sorted_dirs = sorted(dirs)
        sorted_files = sorted([f for f in analysis['files'] if os.path.dirname(f) == ''])
        
        # Add directories
        for dir_path in sorted_dirs:
            readme_content += f"├── {dir_path}/\n"
        
        # Add root files
        for i, file in enumerate(sorted_files):
            if i == len(sorted_files) - 1 and not sorted_dirs:
                readme_content += f"└── {file}\n"
            else:
                readme_content += f"├── {file}\n"
        
        readme_content += "```\n\n"
        
        # Installation and usage
        readme_content += "## Getting Started\n\n"
        
        # Add installation instructions based on project type
        if 'package.json' in [os.path.basename(f) for f in analysis['files']]:
            readme_content += "### Prerequisites\n\n"
            readme_content += "- Node.js (v14 or higher)\n"
            readme_content += "- npm or yarn\n\n"
            readme_content += "### Installation\n\n"
            readme_content += "```bash\n"
            readme_content += "# Clone the repository\n"
            readme_content += f"git clone https://github.com/your-username/{project_name}.git\n"
            readme_content += f"cd {project_name}\n\n"
            readme_content += "# Install dependencies\n"
            readme_content += "npm install\n"
            readme_content += "# or\n"
            readme_content += "yarn install\n"
            readme_content += "```\n\n"
            readme_content += "### Usage\n\n"
            readme_content += "```bash\n"
            readme_content += "# Start the application\n"
            readme_content += "npm start\n"
            readme_content += "# or\n"
            readme_content += "yarn start\n"
            readme_content += "```\n\n"
        
        elif 'requirements.txt' in [os.path.basename(f) for f in analysis['files']]:
            readme_content += "### Prerequisites\n\n"
            readme_content += "- Python 3.7+\n"
            readme_content += "- pip\n\n"
            readme_content += "### Installation\n\n"
            readme_content += "```bash\n"
            readme_content += "# Clone the repository\n"
            readme_content += f"git clone https://github.com/your-username/{project_name}.git\n"
            readme_content += f"cd {project_name}\n\n"
            readme_content += "# Install dependencies\n"
            readme_content += "pip install -r requirements.txt\n"
            readme_content += "```\n\n"
            readme_content += "### Usage\n\n"
            readme_content += "```bash\n"
            readme_content += "# Run the application\n"
            readme_content += "python main.py\n"
            readme_content += "```\n\n"
        
        else:
            readme_content += "### Installation\n\n"
            readme_content += "```bash\n"
            readme_content += "# Clone the repository\n"
            readme_content += f"git clone https://github.com/your-username/{project_name}.git\n"
            readme_content += f"cd {project_name}\n"
            readme_content += "```\n\n"
            readme_content += "### Usage\n\n"
            readme_content += "Follow the specific instructions for your project type.\n\n"
        
        # Contributing section
        readme_content += "## Contributing\n\n"
        readme_content += "1. Fork the repository\n"
        readme_content += "2. Create your feature branch (`git checkout -b feature/amazing-feature`)\n"
        readme_content += "3. Commit your changes (`git commit -m 'Add some amazing feature'`)\n"
        readme_content += "4. Push to the branch (`git push origin feature/amazing-feature`)\n"
        readme_content += "5. Open a Pull Request\n\n"
        
        # License section
        readme_content += "## License\n\n"
        readme_content += "This project is licensed under the MIT License - see the LICENSE file for details.\n\n"
        
        # Footer
        readme_content += "---\n\n"
        readme_content += "*Project uploaded via Telegram Bot*\n"
        
        return readme_content