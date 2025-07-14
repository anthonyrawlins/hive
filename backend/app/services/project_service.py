"""
Project Service for integrating with local project directories and GitHub.
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import markdown
from app.models.project import Project

class ProjectService:
    def __init__(self):
        self.projects_base_path = Path("/home/tony/AI/projects")
        self.github_token = self._get_github_token()
        self.github_api_base = "https://api.github.com"
    
    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from Docker secret or secrets file."""
        try:
            # Try Docker secret first (more secure)
            docker_secret_path = Path("/run/secrets/github_token")
            if docker_secret_path.exists():
                return docker_secret_path.read_text().strip()
            
            # Try gh-token from filesystem (fallback)
            gh_token_path = Path("/home/tony/AI/secrets/passwords_and_tokens/gh-token")
            if gh_token_path.exists():
                return gh_token_path.read_text().strip()
            
            # Try GitHub token from filesystem
            github_token_path = Path("/home/tony/AI/secrets/passwords_and_tokens/github-token")
            if github_token_path.exists():
                return github_token_path.read_text().strip()
            
            # Fallback to GitLab token if GitHub token doesn't exist
            gitlab_token_path = Path("/home/tony/AI/secrets/passwords_and_tokens/claude-gitlab-token")
            if gitlab_token_path.exists():
                return gitlab_token_path.read_text().strip()
        except Exception as e:
            print(f"Error reading GitHub token: {e}")
        return None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects from the local filesystem."""
        projects = []
        
        if not self.projects_base_path.exists():
            return projects
        
        for project_dir in self.projects_base_path.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                project_data = self._analyze_project_directory(project_dir)
                if project_data:
                    projects.append(project_data)
        
        # Sort by last modified date
        projects.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return projects
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific project by ID (directory name)."""
        project_path = self.projects_base_path / project_id
        if not project_path.exists() or not project_path.is_dir():
            return None
        
        return self._analyze_project_directory(project_path)
    
    def _analyze_project_directory(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a project directory and extract metadata."""
        try:
            project_id = project_path.name
            
            # Skip if this is the hive project itself
            if project_id == 'hive':
                return None
            
            # Get basic file info
            stat = project_path.stat()
            created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
            updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Read PROJECT_PLAN.md if it exists
            project_plan_path = project_path / "PROJECT_PLAN.md"
            project_plan_content = ""
            description = ""
            if project_plan_path.exists():
                project_plan_content = project_plan_path.read_text(encoding='utf-8')
                description = self._extract_description_from_plan(project_plan_content)
            
            # Read TODOS.md if it exists
            todos_path = project_path / "TODOS.md"
            todos_content = ""
            if todos_path.exists():
                todos_content = todos_path.read_text(encoding='utf-8')
            
            # Check for GitHub repository
            git_config_path = project_path / ".git" / "config"
            github_repo = None
            if git_config_path.exists():
                github_repo = self._extract_github_repo(git_config_path)
            
            # Determine project status
            status = self._determine_project_status(project_path, todos_content)
            
            # Extract tags from content
            tags = self._extract_tags(project_plan_content, project_path)
            
            # Get workflow count (look for workflow-related files)
            workflow_count = self._count_workflows(project_path)
            
            # Build project data
            project_data = {
                "id": project_id,
                "name": self._format_project_name(project_id),
                "description": description or f"Project in {project_id}",
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
                "tags": tags,
                "github_repo": github_repo,
                "workflow_count": workflow_count,
                "has_project_plan": project_plan_path.exists(),
                "has_todos": todos_path.exists(),
                "file_count": len(list(project_path.rglob("*"))),
                "metadata": {
                    "project_plan_path": str(project_plan_path) if project_plan_path.exists() else None,
                    "todos_path": str(todos_path) if todos_path.exists() else None,
                    "directory_size": self._get_directory_size(project_path)
                }
            }
            
            return project_data
            
        except Exception as e:
            print(f"Error analyzing project directory {project_path}: {e}")
            return None
    
    def _extract_description_from_plan(self, content: str) -> str:
        """Extract description from PROJECT_PLAN.md content."""
        lines = content.split('\n')
        description_lines = []
        in_description = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for overview, description, or objective sections
            if re.match(r'^#+\s*(overview|description|objective|project\s+description)', line, re.IGNORECASE):
                in_description = True
                continue
            elif line.startswith('#') and in_description:
                break
            elif in_description and not line.startswith('#'):
                description_lines.append(line)
                if len(description_lines) >= 2:  # Limit to first 2 lines
                    break
        
        description = ' '.join(description_lines).strip()
        
        # If no description found, try to get from the beginning
        if not description:
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('```'):
                    description = line
                    break
        
        return description[:200] + "..." if len(description) > 200 else description
    
    def _extract_github_repo(self, git_config_path: Path) -> Optional[str]:
        """Extract GitHub repository URL from git config."""
        try:
            config_content = git_config_path.read_text()
            
            # Look for GitHub remote URL
            for line in config_content.split('\n'):
                if 'github.com' in line and ('url =' in line or 'url=' in line):
                    url = line.split('=', 1)[1].strip()
                    
                    # Extract repo name from URL
                    if 'github.com/' in url:
                        repo_part = url.split('github.com/')[-1]
                        if repo_part.endswith('.git'):
                            repo_part = repo_part[:-4]
                        return repo_part
                        
        except Exception:
            pass
        return None
    
    def _determine_project_status(self, project_path: Path, todos_content: str) -> str:
        """Determine project status based on various indicators."""
        # Check for recent activity (files modified in last 30 days)
        recent_activity = False
        thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 60 * 60)
        
        try:
            for file_path in project_path.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime > thirty_days_ago:
                    recent_activity = True
                    break
        except Exception:
            pass
        
        # Check TODOS for status indicators
        if todos_content:
            content_lower = todos_content.lower()
            if any(keyword in content_lower for keyword in ['completed', 'done', 'finished']):
                if not recent_activity:
                    return "archived"
            if any(keyword in content_lower for keyword in ['in progress', 'active', 'working']):
                return "active"
        
        # Check for deployment files
        deployment_files = ['Dockerfile', 'docker-compose.yml', 'deploy.sh', 'package.json']
        has_deployment = any((project_path / f).exists() for f in deployment_files)
        
        if recent_activity:
            return "active"
        elif has_deployment:
            return "inactive"
        else:
            return "draft"
    
    def _extract_tags(self, content: str, project_path: Path) -> List[str]:
        """Extract tags based on content and file analysis."""
        tags = []
        
        if content:
            content_lower = content.lower()
            
            # Technology tags
            tech_tags = {
                'python': ['python', '.py'],
                'javascript': ['javascript', 'js', 'node'],
                'typescript': ['typescript', 'ts'],
                'react': ['react', 'jsx'],
                'docker': ['docker', 'dockerfile'],
                'ai': ['ai', 'ml', 'machine learning', 'neural', 'model'],
                'web': ['web', 'frontend', 'backend', 'api'],
                'automation': ['automation', 'workflow', 'n8n'],
                'infrastructure': ['infrastructure', 'deployment', 'devops'],
                'mobile': ['mobile', 'ios', 'android', 'swift'],
                'data': ['data', 'database', 'sql', 'analytics'],
                'security': ['security', 'auth', 'authentication']
            }
            
            for tag, keywords in tech_tags.items():
                if any(keyword in content_lower for keyword in keywords):
                    tags.append(tag)
        
        # File-based tags
        files = list(project_path.rglob("*"))
        file_extensions = [f.suffix.lower() for f in files if f.is_file()]
        
        if '.py' in file_extensions:
            tags.append('python')
        if '.js' in file_extensions or '.ts' in file_extensions:
            tags.append('javascript')
        if any(f.name == 'Dockerfile' for f in files):
            tags.append('docker')
        if any(f.name == 'package.json' for f in files):
            tags.append('node')
        
        return list(set(tags))  # Remove duplicates
    
    def _count_workflows(self, project_path: Path) -> int:
        """Count workflow-related files in the project."""
        workflow_patterns = [
            '*.yml', '*.yaml',  # GitHub Actions, Docker Compose
            '*.json',  # n8n workflows, package.json
            'workflow*', 'Workflow*',
            '*workflow*'
        ]
        
        count = 0
        for pattern in workflow_patterns:
            count += len(list(project_path.rglob(pattern)))
        
        return min(count, 20)  # Cap at reasonable number
    
    def _format_project_name(self, project_id: str) -> str:
        """Format project directory name into a readable project name."""
        # Convert kebab-case and snake_case to Title Case
        name = project_id.replace('-', ' ').replace('_', ' ')
        return ' '.join(word.capitalize() for word in name.split())
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size
    
    def get_project_metrics(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metrics for a project."""
        project_path = self.projects_base_path / project_id
        if not project_path.exists():
            return None
        
        # Get GitHub issues count if repo exists
        github_repo = None
        git_config_path = project_path / ".git" / "config"
        if git_config_path.exists():
            github_repo = self._extract_github_repo(git_config_path)
        
        github_issues = 0
        github_open_issues = 0
        if github_repo and self.github_token:
            try:
                issues_data = self._get_github_issues(github_repo)
                github_issues = len(issues_data)
                github_open_issues = len([i for i in issues_data if i['state'] == 'open'])
            except Exception:
                pass
        
        # Count workflows
        workflow_count = self._count_workflows(project_path)
        
        # Analyze TODO file
        todos_path = project_path / "TODOS.md"
        completed_tasks = 0
        total_tasks = 0
        if todos_path.exists():
            todos_content = todos_path.read_text()
            # Count checkboxes
            total_tasks = len(re.findall(r'- \[[ x]\]', todos_content))
            completed_tasks = len(re.findall(r'- \[x\]', todos_content))
        
        # Get last activity
        last_activity = None
        try:
            latest_file = None
            latest_time = 0
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    mtime = file_path.stat().st_mtime
                    if mtime > latest_time:
                        latest_time = mtime
                        latest_file = file_path
            
            if latest_file:
                last_activity = datetime.fromtimestamp(latest_time).isoformat()
        except Exception:
            pass
        
        return {
            "total_workflows": workflow_count,
            "active_workflows": max(0, workflow_count - 1) if workflow_count > 0 else 0,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "github_issues": github_issues,
            "github_open_issues": github_open_issues,
            "task_completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "last_activity": last_activity
        }
    
    def _get_github_issues(self, repo: str) -> List[Dict]:
        """Fetch GitHub issues for a repository."""
        if not self.github_token:
            return []
        
        try:
            url = f"{self.github_api_base}/repos/{repo}/issues"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching GitHub issues for {repo}: {e}")
        
        return []
    
    def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get tasks for a project (from GitHub issues and TODOS.md)."""
        tasks = []
        
        # Get GitHub issues
        project_path = self.projects_base_path / project_id
        git_config_path = project_path / ".git" / "config"
        if git_config_path.exists():
            github_repo = self._extract_github_repo(git_config_path)
            if github_repo:
                github_issues = self._get_github_issues(github_repo)
                for issue in github_issues:
                    tasks.append({
                        "id": f"gh-{issue['number']}",
                        "title": issue['title'],
                        "description": issue.get('body', ''),
                        "status": "open" if issue['state'] == 'open' else "closed",
                        "type": "github_issue",
                        "created_at": issue['created_at'],
                        "updated_at": issue['updated_at'],
                        "url": issue['html_url'],
                        "labels": [label['name'] for label in issue.get('labels', [])]
                    })
        
        # Get TODOS from TODOS.md
        todos_path = project_path / "TODOS.md"
        if todos_path.exists():
            todos_content = todos_path.read_text()
            todo_items = self._parse_todos_markdown(todos_content)
            tasks.extend(todo_items)
        
        return tasks
    
    def _parse_todos_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse TODOS.md content into structured tasks."""
        tasks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for checkbox items
            checkbox_match = re.match(r'- \[([x ])\]\s*(.+)', line)
            if checkbox_match:
                is_completed = checkbox_match.group(1) == 'x'
                task_text = checkbox_match.group(2)
                
                tasks.append({
                    "id": f"todo-{i}",
                    "title": task_text,
                    "description": "",
                    "status": "completed" if is_completed else "open",
                    "type": "todo",
                    "created_at": None,
                    "updated_at": None,
                    "url": None,
                    "labels": []
                })
        
        return tasks
    
    # === Bzzz Integration Methods ===
    
    def get_bzzz_active_repositories(self) -> List[Dict[str, Any]]:
        """Get list of repositories enabled for Bzzz consumption from database."""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        active_repos = []
        
        try:
            print("DEBUG: Attempting to connect to database...")
            # Connect to database
            conn = psycopg2.connect(
                host="192.168.1.27",
                port=5433,
                database="hive",
                user="hive",
                password="hivepass"
            )
            print("DEBUG: Database connection successful")
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Query projects where bzzz_enabled is true
                print("DEBUG: Executing query for bzzz-enabled projects...")
                cursor.execute("""
                    SELECT id, name, description, git_url, git_owner, git_repository, 
                           git_branch, bzzz_enabled, ready_to_claim, private_repo, github_token_required
                    FROM projects 
                    WHERE bzzz_enabled = true AND git_url IS NOT NULL
                """)
                
                db_projects = cursor.fetchall()
                print(f"DEBUG: Found {len(db_projects)} bzzz-enabled projects in database")
                
                for project in db_projects:
                    print(f"DEBUG: Processing project {project['name']} (ID: {project['id']})")
                    # For each enabled project, check if it has bzzz-task issues
                    project_id = project['id']
                    github_repo = f"{project['git_owner']}/{project['git_repository']}"
                    print(f"DEBUG: Checking GitHub repo: {github_repo}")
                    
                    # Check for bzzz-task issues
                    bzzz_tasks = self._get_github_bzzz_tasks(github_repo)
                    has_tasks = len(bzzz_tasks) > 0
                    print(f"DEBUG: Found {len(bzzz_tasks)} bzzz-task issues, has_tasks={has_tasks}")
                    
                    active_repos.append({
                        "project_id": project_id,
                        "name": project['name'],
                        "git_url": project['git_url'],
                        "owner": project['git_owner'],
                        "repository": project['git_repository'],
                        "branch": project['git_branch'] or "main",
                        "bzzz_enabled": project['bzzz_enabled'],
                        "ready_to_claim": has_tasks,
                        "private_repo": project['private_repo'],
                        "github_token_required": project['github_token_required']
                    })
            
            conn.close()
            print(f"DEBUG: Returning {len(active_repos)} active repositories")
            
        except Exception as e:
            print(f"Error fetching bzzz active repositories: {e}")
            import traceback
            print(f"DEBUG: Exception traceback: {traceback.format_exc()}")
            # Fallback to filesystem method if database fails
            return self._get_bzzz_active_repositories_filesystem()
        
        return active_repos
    
    def _get_github_bzzz_tasks(self, github_repo: str) -> List[Dict[str, Any]]:
        """Fetch GitHub issues with bzzz-task label for a repository."""
        if not self.github_token:
            return []
        
        try:
            url = f"{self.github_api_base}/repos/{github_repo}/issues"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            params = {
                "labels": "bzzz-task",
                "state": "open"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching bzzz-task issues for {github_repo}: {e}")
        
        return []
    
    def _get_bzzz_active_repositories_filesystem(self) -> List[Dict[str, Any]]:
        """Fallback method using filesystem scan for bzzz repositories."""
        active_repos = []
        
        # Get all projects and filter for those with GitHub repos
        all_projects = self.get_all_projects()
        
        for project in all_projects:
            github_repo = project.get('github_repo')
            if not github_repo:
                continue
                
            # Check if project has bzzz-task issues (indicating Bzzz readiness)
            project_id = project['id']
            bzzz_tasks = self.get_bzzz_project_tasks(project_id)
            
            # Only include projects that have bzzz-task labeled issues
            if bzzz_tasks:
                # Parse GitHub repo URL
                repo_parts = github_repo.split('/')
                if len(repo_parts) >= 2:
                    owner = repo_parts[0]
                    repository = repo_parts[1]
                    
                    active_repos.append({
                        "project_id": hash(project_id) % 1000000,  # Simple numeric ID for compatibility
                        "name": project['name'],
                        "git_url": f"https://github.com/{github_repo}",
                        "owner": owner,
                        "repository": repository,
                        "branch": "main",  # Default branch
                        "bzzz_enabled": True,
                        "ready_to_claim": len(bzzz_tasks) > 0,
                        "private_repo": False,  # TODO: Detect from GitHub API
                        "github_token_required": False  # TODO: Implement token requirement logic
                    })
        
        return active_repos
    
    def get_bzzz_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get GitHub issues with bzzz-task label for a specific project."""
        project_path = self.projects_base_path / project_id
        if not project_path.exists():
            return []
        
        # Get GitHub repository
        git_config_path = project_path / ".git" / "config"
        if not git_config_path.exists():
            return []
        
        github_repo = self._extract_github_repo(git_config_path)
        if not github_repo:
            return []
        
        # Fetch issues with bzzz-task label
        if not self.github_token:
            return []
        
        try:
            url = f"{self.github_api_base}/repos/{github_repo}/issues"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            params = {
                "labels": "bzzz-task",
                "state": "open"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                issues = response.json()
                
                # Convert to Bzzz format
                bzzz_tasks = []
                for issue in issues:
                    # Check if already claimed (has assignee)
                    is_claimed = bool(issue.get('assignees'))
                    
                    bzzz_tasks.append({
                        "number": issue['number'],
                        "title": issue['title'],
                        "description": issue.get('body', ''),
                        "state": issue['state'],
                        "labels": [label['name'] for label in issue.get('labels', [])],
                        "created_at": issue['created_at'],
                        "updated_at": issue['updated_at'],
                        "html_url": issue['html_url'],
                        "is_claimed": is_claimed,
                        "assignees": [assignee['login'] for assignee in issue.get('assignees', [])],
                        "task_type": self._determine_task_type(issue)
                    })
                
                return bzzz_tasks
                
        except Exception as e:
            print(f"Error fetching bzzz-task issues for {github_repo}: {e}")
        
        return []
    
    def _determine_task_type(self, issue: Dict) -> str:
        """Determine the task type from GitHub issue labels and content."""
        labels = [label['name'].lower() for label in issue.get('labels', [])]
        title_lower = issue['title'].lower()
        body_lower = (issue.get('body') or '').lower()
        
        # Map common labels to task types
        type_mappings = {
            'bug': ['bug', 'error', 'fix'],
            'feature': ['feature', 'enhancement', 'new'],
            'documentation': ['docs', 'documentation', 'readme'],
            'refactor': ['refactor', 'cleanup', 'optimization'],
            'testing': ['test', 'testing', 'qa'],
            'infrastructure': ['infra', 'deployment', 'devops', 'ci/cd'],
            'security': ['security', 'vulnerability', 'auth'],
            'ui/ux': ['ui', 'ux', 'frontend', 'design']
        }
        
        for task_type, keywords in type_mappings.items():
            if any(keyword in labels for keyword in keywords) or \
               any(keyword in title_lower for keyword in keywords) or \
               any(keyword in body_lower for keyword in keywords):
                return task_type
        
        return 'general'
    
    def claim_bzzz_task(self, project_id: str, task_number: int, agent_id: str) -> str:
        """Register task claim with Hive system."""
        # For now, just log the claim - in future this would update a database
        claim_id = f"{project_id}-{task_number}-{agent_id}"
        print(f"Bzzz task claimed: Project {project_id}, Task #{task_number}, Agent {agent_id}")
        
        # TODO: Store claim in database with timestamp
        # TODO: Update GitHub issue assignee if GitHub token has write access
        
        return claim_id
    
    def update_bzzz_task_status(self, project_id: str, task_number: int, status: str, metadata: Dict[str, Any]) -> None:
        """Update task status in Hive system."""
        print(f"Bzzz task status update: Project {project_id}, Task #{task_number}, Status: {status}")
        print(f"Metadata: {metadata}")
        
        # TODO: Store status update in database
        # TODO: Update GitHub issue status/comments if applicable
        
        # Handle escalation status
        if status == "escalated":
            print(f"Task escalated for human review: {metadata}")
            # TODO: Trigger N8N webhook for human escalation