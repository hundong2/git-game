import os
import shutil
import tempfile
import subprocess
import json
import asyncio
import random
import shlex
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from git import Repo, GitCommandError
from stages import STAGES, get_stage_validator, get_stage_retry_policy, validate_stage_by_rules

class GitGameEngine:
    """Core game engine that simulates Git operations"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_stage = 1
        self.start_time = datetime.now()
        self.stage_start_time = datetime.now()
        self.completed_stages = []
        self.total_commands = 0
        self.help_usage_by_stage = {}
        self.repeated_stages = set()
        
        # Create temporary git repository for this session
        self.temp_dir = tempfile.mkdtemp(prefix=f"git_game_{session_id}_")
        self.repo_path = os.path.join(self.temp_dir, "game_repo")
        
        # Initialize the game repository
        self._init_repository()
        
        # Simulate teammate actions
        self.teammates = ["alice", "bob", "charlie", "diana"]
        self.teammate_actions_enabled = False
        
    def _init_repository(self):
        """Initialize the game repository with initial state"""
        os.makedirs(self.repo_path)
        self.repo = Repo.init(self.repo_path)
        
        # Configure git user for this session
        with self.repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Game Player")
            git_config.set_value("user", "email", "player@git-game.com")
        
        # Create initial files and commits
        self._setup_initial_state()

    def _reset_repository(self):
        """Reset repository to the current stage's initial state."""
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)
        self._init_repository()
    
    def _setup_initial_state(self):
        """Setup initial repository state based on current stage"""
        stage_config = STAGES[self.current_stage - 1]
        
        # Create initial files
        for filename, content in stage_config.get("initial_files", {}).items():
            file_path = os.path.join(self.repo_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Make initial commits if specified
        if "initial_commits" in stage_config:
            for commit_info in stage_config["initial_commits"]:
                if "files" in commit_info:
                    for filename, content in commit_info["files"].items():
                        file_path = os.path.join(self.repo_path, filename)
                        with open(file_path, 'w') as f:
                            f.write(content)
                        self.repo.index.add([filename])
                
                self.repo.index.commit(commit_info["message"])
        
        # Create initial branches if specified
        if "initial_branches" in stage_config:
            try:
                original_branch = self.repo.active_branch.name
            except Exception:
                original_branch = None

            for branch_info in stage_config["initial_branches"]:
                branch_name = branch_info["name"]
                branch = self.repo.create_head(branch_name)
                should_checkout = branch_info.get("checkout", False) or bool(branch_info.get("commits"))
                if should_checkout:
                    branch.checkout()
                    
                # Add commits to this branch if specified
                if "commits" in branch_info:
                    for commit_info in branch_info["commits"]:
                        for filename, content in commit_info["files"].items():
                            file_path = os.path.join(self.repo_path, filename)
                            with open(file_path, 'w') as f:
                                f.write(content)
                        self.repo.index.add([filename])
                    self.repo.index.commit(commit_info["message"])

                if not branch_info.get("checkout", False) and original_branch:
                    self.repo.git.checkout(original_branch)

    def _extract_command_segments(self, command: str) -> List[List[str]]:
        """Split a shell command into segments based on shell operators."""
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            return []

        segments: List[List[str]] = []
        current: List[str] = []
        separators = {"|", "&&", "||", ";"}

        for token in tokens:
            if token in separators:
                if current:
                    segments.append(current)
                    current = []
                continue
            current.append(token)

        if current:
            segments.append(current)

        return segments

    def _is_command_allowed(self, command: str) -> bool:
        """Allow common shell commands and full git command set."""
        if not command.strip():
            return False

        segments = self._extract_command_segments(command)
        if not segments:
            return False

        allowed_commands = {
            "git",
            "ls",
            "pwd",
            "cat",
            "grep",
            "find",
            "tree",
            "head",
            "tail",
            "wc",
            "sort",
            "uniq",
            "cut",
            "tr",
            "xargs",
            "echo",
            "printf",
            "touch",
            "mkdir",
            "rm",
            "mv",
            "cp",
            "stat",
            "diff",
            "patch",
            "basename",
            "dirname",
            "file",
            "which",
            "whoami",
            "date",
            "sed",
            "awk",
            "less",
            "more",
        }

        blocked_commands = {
            "sudo",
            "su",
            "ssh",
            "scp",
            "curl",
            "wget",
            "apt",
            "apt-get",
            "apk",
            "yum",
            "dnf",
            "brew",
            "pip",
            "npm",
            "node",
            "python",
            "python3",
            "ruby",
            "perl",
            "bash",
            "sh",
            "zsh",
            "fish",
            "kill",
            "pkill",
            "systemctl",
            "service",
        }

        env_assignment = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

        for segment in segments:
            tokens = segment[:]
            while tokens and env_assignment.match(tokens[0]):
                tokens = tokens[1:]

            if not tokens:
                continue

            cmd = tokens[0]
            if cmd in blocked_commands:
                return False
            if cmd not in allowed_commands:
                return False

        return True
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a git command and return the result"""
        self.total_commands += 1
        
        try:
            if not os.path.exists(self.repo_path):
                self._init_repository()

            if not self._is_command_allowed(command):
                return {
                    "output": "Command not allowed in game terminal.",
                    "git_state": self.get_current_state(),
                    "stage_completed": False,
                    "error": "Command not allowed"
                }
            
            # Execute command in a shell to support pipes and compound commands
            env = os.environ.copy()
            env["HOME"] = self.repo_path
            env["GIT_WORK_TREE"] = self.repo_path

            result = subprocess.run(
                command,
                shell=True,
                executable="/bin/sh",
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            output = (result.stdout or "") + (result.stderr or "")
            
            # Refresh repo object to get latest state
            self.repo = Repo(self.repo_path)
            
            # Check if stage is completed
            stage_completed = self._check_stage_completion()
            next_stage = None
            
            if stage_completed:
                completion_time = datetime.now() - self.stage_start_time
                self.completed_stages.append({
                    "stage": self.current_stage,
                    "completion_time": completion_time.total_seconds(),
                    "commands_used": self.total_commands,
                    "repeat_triggered": self._should_repeat_stage(self.current_stage)
                })
                
                if self._should_repeat_stage(self.current_stage):
                    self._repeat_current_stage()
                    next_stage = self.current_stage
                elif self.current_stage < len(STAGES):
                    self.current_stage += 1
                    next_stage = self.current_stage
                    self.stage_start_time = datetime.now()
                    self._reset_repository()
            
            return {
                "output": output,
                "git_state": self.get_current_state(),
                "stage_completed": stage_completed,
                "next_stage": next_stage,
                "command_count": self.total_commands
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "Command timed out",
                "git_state": self.get_current_state(),
                "stage_completed": False,
                "error": "Command execution timed out"
            }
        except Exception as e:
            return {
                "output": f"Error: {str(e)}",
                "git_state": self.get_current_state(),
                "stage_completed": False,
                "error": str(e)
            }
    
    def _check_stage_completion(self) -> bool:
        """Check if current stage objectives are completed"""
        rules_result = validate_stage_by_rules(self.current_stage, self.repo, self.repo_path)
        if rules_result is not None:
            return rules_result

        validator = get_stage_validator(self.current_stage)
        if validator:
            return validator(self.repo, self.repo_path)
        return False

    def register_help_usage(self, stage_id: int, help_type: str):
        """Record hint/solution usage to enforce retry policy."""
        if help_type not in ("hint", "solution"):
            return
        usage = self.help_usage_by_stage.setdefault(stage_id, {"hint": False, "solution": False})
        usage[help_type] = True

    def _should_repeat_stage(self, stage_id: int) -> bool:
        policy = get_stage_retry_policy(stage_id)
        if policy.get("on_hint_or_solution") != "repeat_same_stage_once":
            return False
        if stage_id in self.repeated_stages:
            return False
        usage = self.help_usage_by_stage.get(stage_id, {})
        return bool(usage.get("hint") or usage.get("solution"))

    def _repeat_current_stage(self):
        """Reset the current stage once after hint/solution usage."""
        self.repeated_stages.add(self.current_stage)
        self.stage_start_time = datetime.now()
        self._reset_repository()
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current git repository state for UI visualization"""
        try:
            # Get branch information
            branches = []
            for branch in self.repo.branches:
                branches.append({
                    "name": branch.name,
                    "is_current": branch == self.repo.active_branch,
                    "commit": str(branch.commit)
                })
            
            # Get commit history
            commits = []
            try:
                for commit in list(self.repo.iter_commits(max_count=20)):
                    commits.append({
                        "hash": str(commit),
                        "short_hash": str(commit)[:8],
                        "message": commit.message.strip(),
                        "author": commit.author.name,
                        "date": commit.authored_datetime.isoformat(),
                        "parents": [str(p) for p in commit.parents]
                    })
            except:
                pass
            
            # Get working directory status
            status = {
                "modified": [item.a_path for item in self.repo.index.diff(None)],
                "staged": [item.a_path for item in self.repo.index.diff("HEAD")],
                "untracked": self.repo.untracked_files
            }
            
            # Get current branch name
            current_branch = self.repo.active_branch.name if self.repo.active_branch else "HEAD"
            
            return {
                "branches": branches,
                "commits": commits,
                "status": status,
                "current_branch": current_branch,
                "stage": self.current_stage,
                "total_stages": len(STAGES),
                "session_id": self.session_id
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "stage": self.current_stage,
                "total_stages": len(STAGES),
                "session_id": self.session_id
            }
    
    async def simulate_teammate_action(self):
        """Simulate a random teammate making changes"""
        if not self.teammate_actions_enabled:
            return
        
        teammate = random.choice(self.teammates)
        actions = [
            self._teammate_commit,
            self._teammate_branch,
            self._teammate_merge
        ]
        
        action = random.choice(actions)
        await action(teammate)
    
    def _teammate_commit(self, teammate: str):
        """Simulate teammate making a commit"""
        try:
            # Create or modify a file
            filename = f"{teammate}_feature.txt"
            file_path = os.path.join(self.repo_path, filename)
            
            content = f"Feature by {teammate}\nTimestamp: {datetime.now()}\n"
            with open(file_path, 'a') as f:
                f.write(content)
            
            self.repo.index.add([filename])
            
            # Configure teammate as author temporarily
            with self.repo.config_writer() as config:
                config.set_value("user", "name", teammate.title())
                config.set_value("user", "email", f"{teammate}@company.com")
            
            self.repo.index.commit(f"Add feature by {teammate}")
            
            # Restore original config
            with self.repo.config_writer() as config:
                config.set_value("user", "name", "Game Player")
                config.set_value("user", "email", "player@git-game.com")
                
        except Exception as e:
            print(f"Error in teammate commit: {e}")
    
    def _teammate_branch(self, teammate: str):
        """Simulate teammate creating a branch"""
        try:
            branch_name = f"{teammate}-feature-{random.randint(1000, 9999)}"
            if branch_name not in [b.name for b in self.repo.branches]:
                self.repo.create_head(branch_name)
        except Exception as e:
            print(f"Error in teammate branch: {e}")
    
    def _teammate_merge(self, teammate: str):
        """Simulate teammate merging (rarely)"""
        # Only occasionally simulate merges to avoid conflicts
        if random.random() < 0.1:  # 10% chance
            try:
                branches = [b for b in self.repo.branches if b.name.startswith(teammate)]
                if branches and self.repo.active_branch.name == "main":
                    branch_to_merge = branches[0]
                    self.repo.git.merge(branch_to_merge.name, no_ff=True)
            except Exception as e:
                print(f"Error in teammate merge: {e}")
    
    def cleanup(self):
        """Cleanup temporary repository"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp dir: {e}")
    
    def __del__(self):
        self.cleanup()
