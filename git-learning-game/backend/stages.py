"""Game stages definition with progressive difficulty"""

from typing import Dict, List, Any, Callable, Optional
import os
from git import Repo

# Stage definitions with increasing difficulty
STAGES = [
    # BASIC LEVEL (1-15)
    {
        "stage_id": 1,
        "title": "Interactive Rebase Introduction",
        "description": "Learn to squash commits using interactive rebase",
        "difficulty": "basic",
        "objectives": [
            "Squash the last 3 commits into one",
            "Change the commit message to 'Combined feature implementation'"
        ],
        "initial_files": {
            "README.md": "# Project\nInitial readme",
            "src/main.py": "def main():\n    print('Hello')\n"
        },
        "initial_commits": [
            {"message": "Initial commit", "files": {"README.md": "# Project\nInitial readme"}},
            {"message": "Add main.py", "files": {"src/main.py": "def main():\n    print('Hello')\n"}},
            {"message": "Fix typo in main", "files": {"src/main.py": "def main():\n    print('Hello World')\n"}},
            {"message": "Add documentation", "files": {"src/main.py": "def main():\n    '''Main function'''\n    print('Hello World')\n"}}
        ],
        "hint": "Use 'git rebase -i HEAD~3' to start interactive rebase. Use 's' to squash commits."
    },
    
    {
        "stage_id": 2,
        "title": "Cherry-pick with Conflicts", 
        "description": "Cherry-pick commits from another branch and resolve conflicts",
        "difficulty": "basic",
        "objectives": [
            "Cherry-pick commit from feature-branch",
            "Resolve merge conflicts manually",
            "Complete the cherry-pick"
        ],
        "initial_files": {
            "config.py": "DEBUG = False\nVERSION = '1.0'\n"
        },
        "initial_branches": [
            {
                "name": "feature-branch",
                "checkout": False,
                "commits": [
                    {"message": "Add new config option", "files": {"config.py": "DEBUG = True\nVERSION = '1.0'\nNEW_FEATURE = True\n"}}
                ]
            }
        ],
        "initial_commits": [
            {"message": "Initial config", "files": {"config.py": "DEBUG = False\nVERSION = '1.0'\n"}},
            {"message": "Update version", "files": {"config.py": "DEBUG = False\nVERSION = '1.1'\n"}}
        ],
        "hint": "Use 'git cherry-pick <commit-hash>' and resolve conflicts manually."
    },
    
    {
        "stage_id": 3,
        "title": "Advanced Stashing",
        "description": "Master git stash with partial staging and multiple stashes",
        "difficulty": "basic",
        "objectives": [
            "Stash only staged changes",
            "Create a named stash",
            "Apply stash without dropping it"
        ],
        "initial_files": {
            "app.py": "class App:\n    def __init__(self):\n        self.name = 'MyApp'\n",
            "utils.py": "def helper():\n    return 'help'\n"
        },
        "initial_commits": [
            {"message": "Initial app structure", "files": {"app.py": "class App:\n    def __init__(self):\n        self.name = 'MyApp'\n", "utils.py": "def helper():\n    return 'help'\n"}}
        ],
        "hint": "Use 'git stash push -S' for staged changes and 'git stash push -m' for named stashes."
    },
    
    {
        "stage_id": 4,
        "title": "Reset Modes Mastery",
        "description": "Understand the difference between --soft, --mixed, and --hard resets",
        "difficulty": "basic",
        "objectives": [
            "Use reset --soft to uncommit but keep changes staged",
            "Use reset --mixed to unstage changes",
            "Use reset --hard to discard all changes"
        ],
        "initial_commits": [
            {"message": "First commit", "files": {"file1.txt": "content 1"}},
            {"message": "Second commit", "files": {"file2.txt": "content 2"}},
            {"message": "Third commit", "files": {"file3.txt": "content 3"}},
            {"message": "Fourth commit", "files": {"file4.txt": "content 4"}}
        ],
        "hint": "Practice with: git reset --soft HEAD~2, git reset --mixed HEAD~1, git reset --hard HEAD~1"
    },
    
    {
        "stage_id": 5,
        "title": "Complex Merge Conflicts",
        "description": "Resolve complex merge conflicts with multiple files",
        "difficulty": "basic",
        "objectives": [
            "Merge feature branch with conflicts",
            "Resolve conflicts in all files",
            "Complete the merge successfully"
        ],
        "initial_files": {
            "database.py": "class Database:\n    def connect(self):\n        pass\n",
            "api.py": "def get_users():\n    return []\n"
        },
        "initial_branches": [
            {
                "name": "feature-db",
                "checkout": False,
                "commits": [
                    {"message": "Implement database connection", "files": {
                        "database.py": "class Database:\n    def connect(self):\n        self.connection = connect_to_db()\n        return self.connection\n",
                        "api.py": "def get_users():\n    db = Database()\n    return db.get_all_users()\n"
                    }}
                ]
            }
        ],
        "initial_commits": [
            {"message": "Initial API", "files": {"database.py": "class Database:\n    def connect(self):\n        pass\n", "api.py": "def get_users():\n    return []\n"}},
            {"message": "Add error handling", "files": {"api.py": "def get_users():\n    try:\n        return []\n    except Exception as e:\n        return None\n"}}
        ],
        "hint": "Use 'git merge feature-db' and resolve conflicts manually. Check git status frequently."
    },
    
    # INTERMEDIATE LEVEL (16-35)
    {
        "stage_id": 16,
        "title": "Rebase Onto Master",
        "description": "Use git rebase --onto to transplant commits",
        "difficulty": "intermediate",
        "objectives": [
            "Rebase feature commits onto master, skipping outdated base",
            "Maintain clean history"
        ],
        "initial_branches": [
            {
                "name": "old-feature",
                "checkout": False,
                "commits": [
                    {"message": "Old approach", "files": {"feature.py": "# Old implementation\npass\n"}},
                    {"message": "Fix old approach", "files": {"feature.py": "# Old implementation fixed\npass\n"}}
                ]
            },
            {
                "name": "new-feature", 
                "checkout": True,
                "commits": [
                    {"message": "New approach", "files": {"feature.py": "# New implementation\ndef feature():\n    return True\n"}},
                    {"message": "Add tests", "files": {"test_feature.py": "def test_feature():\n    assert feature() == True\n"}}
                ]
            }
        ],
        "hint": "Use 'git rebase --onto master old-feature new-feature' to transplant commits."
    },
    
    {
        "stage_id": 17,
        "title": "Reflog Recovery",
        "description": "Recover lost commits using git reflog",
        "difficulty": "intermediate",
        "objectives": [
            "Find lost commit in reflog",
            "Recover the lost work",
            "Restore branch to previous state"
        ],
        "initial_commits": [
            {"message": "Important work", "files": {"important.py": "# Critical code\ndef critical_function():\n    return 'important'\n"}},
            {"message": "More important work", "files": {"important.py": "# Critical code\ndef critical_function():\n    return 'very important'\n"}},
            {"message": "Accidental reset point", "files": {"temp.py": "# temporary\n"}}
        ],
        "hint": "Use 'git reflog' to find lost commits, then 'git reset --hard <commit>' to recover."
    },
    
    {
        "stage_id": 18,
        "title": "Git Bisect Debugging",
        "description": "Find the commit that introduced a bug using git bisect",
        "difficulty": "intermediate",
        "objectives": [
            "Start bisect session",
            "Mark good and bad commits",
            "Find the problematic commit"
        ],
        "initial_commits": [
            {"message": "Working version", "files": {"calculator.py": "def add(a, b):\n    return a + b\n"}},
            {"message": "Add multiplication", "files": {"calculator.py": "def add(a, b):\n    return a + b\n\ndef multiply(a, b):\n    return a * b\n"}},
            {"message": "Add subtraction", "files": {"calculator.py": "def add(a, b):\n    return a + b\n\ndef multiply(a, b):\n    return a * b\n\ndef subtract(a, b):\n    return a - b\n"}},
            {"message": "Fix add function", "files": {"calculator.py": "def add(a, b):\n    return a + b + 1  # BUG: extra +1\n\ndef multiply(a, b):\n    return a * b\n\ndef subtract(a, b):\n    return a - b\n"}},
            {"message": "Add division", "files": {"calculator.py": "def add(a, b):\n    return a + b + 1  # BUG: extra +1\n\ndef multiply(a, b):\n    return a * b\n\ndef subtract(a, b):\n    return a - b\n\ndef divide(a, b):\n    return a / b\n"}}
        ],
        "hint": "Use 'git bisect start', then 'git bisect bad' and 'git bisect good <commit>' to find the bug."
    },
    
    {
        "stage_id": 19,
        "title": "Worktree Management",
        "description": "Use git worktree to work on multiple branches simultaneously",
        "difficulty": "intermediate",
        "objectives": [
            "Create a new worktree for hotfix branch",
            "Make changes in the worktree",
            "Manage multiple worktrees"
        ],
        "initial_branches": [
            {
                "name": "hotfix-urgent",
                "checkout": False,
                "commits": []
            }
        ],
        "initial_commits": [
            {"message": "Production code", "files": {"app.py": "def main():\n    return 'production'\n"}}
        ],
        "hint": "Use 'git worktree add ../hotfix hotfix-urgent' to create a new worktree."
    },
    
    {
        "stage_id": 20,
        "title": "Submodule Advanced Usage",
        "description": "Manage git submodules with updates and version pinning",
        "difficulty": "intermediate",
        "objectives": [
            "Add a submodule",
            "Update submodule to specific version",
            "Handle submodule conflicts"
        ],
        "hint": "Use 'git submodule add <url> <path>' and 'git submodule update --remote'."
    },
    
    # ADVANCED LEVEL (36-50)
    {
        "stage_id": 36,
        "title": "History Rewriting with Filter-Repo",
        "description": "Remove sensitive data from git history",
        "difficulty": "advanced",
        "objectives": [
            "Remove all instances of password from history",
            "Rewrite commit messages",
            "Clean up repository size"
        ],
        "initial_commits": [
            {"message": "Add config", "files": {"config.py": "PASSWORD = 'secret123'\nDEBUG = True\n"}},
            {"message": "Update config", "files": {"config.py": "PASSWORD = 'secret123'\nDEBUG = False\nVERSION = '1.0'\n"}},
            {"message": "Remove password", "files": {"config.py": "DEBUG = False\nVERSION = '1.0'\n"}}
        ],
        "hint": "Install git-filter-repo and use it to remove sensitive data from history."
    },
    
    {
        "stage_id": 37,
        "title": "Object Replacement",
        "description": "Use git replace to substitute objects",
        "difficulty": "advanced",
        "objectives": [
            "Create a replace object",
            "Test the replacement",
            "Make replacement permanent"
        ],
        "hint": "Use 'git replace <original> <replacement>' to substitute objects."
    },
    
    {
        "stage_id": 38,
        "title": "Custom Merge Strategies",
        "description": "Implement and use custom merge strategies",
        "difficulty": "advanced", 
        "objectives": [
            "Configure custom merge driver",
            "Handle specific file types",
            "Apply strategy during merge"
        ],
        "hint": "Configure .gitattributes and custom merge drivers."
    },
    
    {
        "stage_id": 39,
        "title": "Git Hooks Implementation", 
        "description": "Create pre-commit and post-receive hooks",
        "difficulty": "advanced",
        "objectives": [
            "Create pre-commit hook for code quality",
            "Add post-receive hook for deployment",
            "Test hook execution"
        ],
        "hint": "Edit .git/hooks/pre-commit and make it executable."
    },
    
    {
        "stage_id": 40,
        "title": "Git Notes System",
        "description": "Use git notes to add metadata to commits",
        "difficulty": "advanced",
        "objectives": [
            "Add notes to existing commits",
            "Create custom notes namespace",
            "Share notes with team"
        ],
        "hint": "Use 'git notes add' and 'git notes --ref=<namespace>'."
    }
]

# Extend to 50 stages
while len(STAGES) < 50:
    STAGES.append({
        "stage_id": len(STAGES) + 1,
        "title": f"Advanced Challenge {len(STAGES) + 1 - 40}",
        "description": "Master-level Git operations", 
        "difficulty": "advanced",
        "objectives": ["Complete advanced Git operations"],
        "hint": "Use advanced Git commands and workflows."
    })

def get_stage_validator(stage_id: int) -> Optional[Callable]:
    """Get validator function for a specific stage"""
    validators = {
        1: validate_stage_1_interactive_rebase,
        2: validate_stage_2_cherry_pick, 
        3: validate_stage_3_stashing,
        4: validate_stage_4_reset_modes,
        5: validate_stage_5_merge_conflicts,
        # Add more validators as needed
    }
    return validators.get(stage_id)

def validate_stage_1_interactive_rebase(repo: Repo, repo_path: str) -> bool:
    """Validate that interactive rebase was completed correctly"""
    try:
        commits = list(repo.iter_commits(max_count=5))
        # Check if commits were squashed (should be fewer commits)
        if len(commits) >= 2:
            recent_commit = commits[0]
            # Check if commit message contains expected text
            return "Combined feature implementation" in recent_commit.message
    except Exception:
        pass
    return False

def validate_stage_2_cherry_pick(repo: Repo, repo_path: str) -> bool:
    """Validate cherry-pick completion"""
    try:
        # Check if the feature from feature-branch was cherry-picked
        commits = list(repo.iter_commits(max_count=5))
        for commit in commits:
            if "NEW_FEATURE = True" in commit.message or "new config option" in commit.message.lower():
                return True
    except Exception:
        pass
    return False

def validate_stage_3_stashing(repo: Repo, repo_path: str) -> bool:
    """Validate stash operations"""
    try:
        # Check if stash exists
        stashes = repo.git.stash('list').split('\n') if repo.git.stash('list') else []
        return len(stashes) > 0
    except Exception:
        pass
    return False

def validate_stage_4_reset_modes(repo: Repo, repo_path: str) -> bool:
    """Validate reset operations understanding"""
    try:
        # Check current state and recent operations
        commits = list(repo.iter_commits(max_count=10))
        return len(commits) >= 1  # Basic validation
    except Exception:
        pass
    return False

def validate_stage_5_merge_conflicts(repo: Repo, repo_path: str) -> bool:
    """Validate merge conflict resolution"""
    try:
        # Check if merge was completed successfully
        commits = list(repo.iter_commits(max_count=5))
        for commit in commits:
            if len(commit.parents) > 1:  # Merge commit
                return True
    except Exception:
        pass
    return False

def get_stage_help(stage_id: int) -> Dict[str, Any]:
    """Get help information for a specific stage"""
    if stage_id < 1 or stage_id > len(STAGES):
        return {"error": "Stage not found"}
    
    stage = STAGES[stage_id - 1]
    
    # Stage-specific detailed help
    detailed_help = {
        1: {
            "commands": [
                "git log --oneline  # See current commits",
                "git rebase -i HEAD~3  # Start interactive rebase",
                "# In editor: change 'pick' to 's' for squash",
                "# Save and edit commit message"
            ],
            "explanation": "Interactive rebase allows you to modify commit history. Use 'squash' to combine commits."
        },
        2: {
            "commands": [
                "git log --oneline --all  # See all branches", 
                "git cherry-pick <commit-hash>  # Pick specific commit",
                "# If conflicts occur:",
                "git status  # See conflicted files",
                "# Edit files to resolve conflicts",
                "git add <resolved-files>",
                "git cherry-pick --continue"
            ],
            "explanation": "Cherry-pick applies changes from specific commits. Resolve conflicts manually."
        },
        # Add more detailed help for other stages
    }
    
    return {
        "stage": stage,
        "detailed_help": detailed_help.get(stage_id, {}),
        "general_tips": [
            "Use 'git status' frequently to check current state",
            "Use 'git log --oneline --graph --all' to visualize branches",
            "Use 'git help <command>' for detailed command help"
        ]
    }
