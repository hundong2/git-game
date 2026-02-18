"""Game stages definition with progressive difficulty"""

from typing import Dict, List, Any, Callable, Optional
import os
from git import Repo

# Default retry policy if a stage does not override it.
DEFAULT_RETRY_POLICY = {
    "on_hint_or_solution": "repeat_same_stage_once",
    "recording": "new_session_with_repeat_flag",
}

# Simple, structured validation rules for stage completion.
SUPPORTED_VALIDATION_RULES = {
    "head_message_contains",
    "commit_message_contains",
    "commit_count_at_most",
    "file_contains",
    "file_exists",
    "no_merge_commits",
    "has_merge_commits",
    "stash_count_at_least",
    "branch_exists",
    "branch_is_current",
    "worktree_clean",
}

# Stage definitions with increasing difficulty
STAGES = [
    # BASIC LEVEL (1-15)
    {
        "stage_id": 1,
        "title": "Cherry-pick Hotfix",
        "description": "Cherry-pick a teammate hotfix and resolve conflicts",
        "difficulty": "basic",
        "story": {
            "context": "A teammate pushed a hotfix that must be applied quickly.",
            "teammate": "Mina (backend)",
            "incident": "Your local changes touch the same config lines."
        },
        "objectives": [
            "Cherry-pick the hotfix commit from the hotfix branch",
            "Resolve any conflicts manually",
            "Keep the hotfix commit message"
        ],
        "constraints": [
            "No merge commits",
            "Do not use cherry-pick --no-commit"
        ],
        "initial_files": {
            "config.py": "DEBUG = False\nVERSION = '1.1'\n"
        },
        "initial_commits": [
            {"message": "Baseline config", "files": {"config.py": "DEBUG = False\nVERSION = '1.0'\n"}},
            {"message": "Update debug format", "files": {"config.py": "DEBUG = False  # stable\nVERSION = '1.1'\n"}}
        ],
        "initial_branches": [
            {
                "name": "hotfix",
                "checkout": False,
                "commits": [
                    {"message": "Hotfix: enable debug temporarily", "files": {"config.py": "DEBUG = True\nVERSION = '1.0'\n"}}
                ]
            }
        ],
        "hint": "Use 'git cherry-pick <commit-hash>' and resolve conflicts manually.",
        "solution": "git cherry-pick <hotfix-commit> -> resolve -> git add <files> -> git cherry-pick --continue",
        "validation": {
            "must_have": [
                {"type": "file_contains", "path": "config.py", "value": "DEBUG = True"},
                {"type": "commit_message_contains", "value": "Hotfix:"}
            ],
            "must_not_have": [
                {"type": "has_merge_commits"}
            ]
        }
    },
    
    {
        "stage_id": 2,
        "title": "Rebase Squash Cleanup",
        "description": "Clean up a messy commit history before review",
        "difficulty": "basic",
        "story": {
            "context": "Your PR has too many small commits.",
            "teammate": "Joon (reviewer)",
            "incident": "You must squash and rename commits before review."
        },
        "objectives": [
            "Squash the last 4 commits into 2 commits",
            "Set the final commit message to start with 'Feature:'"
        ],
        "constraints": [
            "No merge commits",
            "Use interactive rebase"
        ],
        "initial_commits": [
            {"message": "Add feature flag", "files": {"feature.py": "FLAG = False\n"}},
            {"message": "WIP: tweak flag", "files": {"feature.py": "FLAG = True\n"}},
            {"message": "Refactor flag logic", "files": {"feature.py": "def enabled():\n    return True\n"}},
            {"message": "Fix typo", "files": {"feature.py": "def enabled():\n    return True\n"}}
        ],
        "hint": "Use 'git rebase -i HEAD~4' and squash commits down to two.",
        "solution": "git rebase -i HEAD~4 -> squash -> set message to 'Feature: ...'",
        "validation": {
            "must_have": [
                {"type": "head_message_contains", "value": "Feature:"},
                {"type": "commit_count_at_most", "value": 2, "max_count": 10}
            ],
            "must_not_have": [
                {"type": "has_merge_commits"}
            ]
        }
    },
    
    {
        "stage_id": 3,
        "title": "Reset and Recover",
        "description": "Use reset modes to recover from an accidental commit",
        "difficulty": "basic",
        "story": {
            "context": "You committed draft text by mistake.",
            "teammate": "Kai (editor)",
            "incident": "You need to undo commits without losing good content."
        },
        "objectives": [
            "Use reset --soft and --mixed to adjust history",
            "Keep the final notes content intact",
            "End with a clean working tree"
        ],
        "constraints": [
            "Do not use reset --hard"
        ],
        "initial_commits": [
            {"message": "Add notes", "files": {"notes.txt": "keep\n"}},
            {"message": "WIP: add draft", "files": {"notes.txt": "keep\nlost draft\n"}},
            {"message": "Cleanup draft", "files": {"notes.txt": "keep\n"}}
        ],
        "hint": "Use 'git reset --soft HEAD~1' to uncommit and keep changes staged.",
        "solution": "git reset --soft HEAD~1 -> git reset --mixed HEAD~1 -> clean up notes.txt",
        "validation": {
            "must_have": [
                {"type": "file_contains", "path": "notes.txt", "value": "keep"},
                {"type": "worktree_clean"}
            ],
            "must_not_have": [
                {"type": "file_contains", "path": "notes.txt", "value": "lost draft"}
            ]
        }
    },
    
    {
        "stage_id": 4,
        "title": "Stash Partial Changes",
        "description": "Stash only staged changes and re-apply them",
        "difficulty": "basic",
        "story": {
            "context": "A bug report arrived while you were mid-task.",
            "teammate": "Sohee (support)",
            "incident": "You need to stash only the staged fixes."
        },
        "objectives": [
            "Stash only staged changes",
            "Create a named stash",
            "Apply the stash without dropping it"
        ],
        "constraints": [
            "Do not use stash pop"
        ],
        "initial_files": {
            "app.py": "class App:\n    def __init__(self):\n        self.name = 'MyApp'\n",
            "utils.py": "def helper():\n    return 'help'\n"
        },
        "initial_commits": [
            {"message": "Initial app structure", "files": {"app.py": "class App:\n    def __init__(self):\n        self.name = 'MyApp'\n", "utils.py": "def helper():\n    return 'help'\n"}}
        ],
        "hint": "Use 'git stash push -S -m <name>' for staged changes.",
        "solution": "git add <files> -> git stash push -S -m <name> -> git stash apply",
        "validation": {
            "must_have": [
                {"type": "stash_count_at_least", "value": 1}
            ]
        }
    },
    
    {
        "stage_id": 5,
        "title": "Simple Conflict Merge",
        "description": "Resolve a single-file conflict in a merge",
        "difficulty": "basic",
        "story": {
            "context": "Two teammates updated the same UI setting.",
            "teammate": "Ari (frontend)",
            "incident": "Merging causes a conflict in a single file."
        },
        "objectives": [
            "Merge the feature branch",
            "Resolve the conflict",
            "Complete the merge successfully"
        ],
        "constraints": [
            "Do not use rebase"
        ],
        "initial_branches": [
            {
                "name": "feature-ux",
                "checkout": False,
                "commits": [
                    {"message": "Update button style", "files": {"ui.txt": "button: secondary\nlayout: grid\n"}}
                ]
            }
        ],
        "initial_commits": [
            {"message": "Base UI config", "files": {"ui.txt": "button: primary\nlayout: list\n"}},
            {"message": "Update layout", "files": {"ui.txt": "button: primary\nlayout: grid\n"}}
        ],
        "hint": "Use 'git merge feature-ux' and resolve the conflict in ui.txt.",
        "solution": "git merge feature-ux -> resolve -> git add ui.txt -> git commit",
        "validation": {
            "must_have": [
                {"type": "has_merge_commits"}
            ]
        }
    },

    {
        "stage_id": 6,
        "title": "Rebase --onto",
        "description": "Transplant feature commits onto the latest main",
        "difficulty": "intermediate",
        "story": {
            "context": "A feature branch started from an outdated base.",
            "teammate": "Jae (tech lead)",
            "incident": "You must move only the feature commits onto main."
        },
        "objectives": [
            "Rebase feature commits onto main, skipping the old base",
            "Keep a clean history"
        ],
        "constraints": [
            "No merge commits"
        ],
        "initial_commits": [
            {"message": "Core baseline", "files": {"core.py": "VERSION = 1\n"}}
        ],
        "initial_branches": [
            {
                "name": "old-base",
                "checkout": True,
                "commits": [
                    {"message": "Old baseline", "files": {"feature.py": "mode = 'old'\n"}},
                    {"message": "Old baseline fix", "files": {"feature.py": "mode = 'old-fixed'\n"}}
                ]
            },
            {
                "name": "feature",
                "checkout": True,
                "commits": [
                    {"message": "Feature: start", "files": {"feature.py": "mode = 'new'\n"}},
                    {"message": "Feature: finalize", "files": {"feature.py": "mode = 'new-final'\n"}}
                ]
            }
        ],
        "hint": "Use 'git rebase --onto main old-base feature'.",
        "solution": "git rebase --onto main old-base feature",
        "validation": {
            "must_have": [
                {"type": "branch_is_current", "name": "feature"},
                {"type": "commit_message_contains", "value": "Feature:"},
                {"type": "no_merge_commits"}
            ],
            "must_not_have": [
                {"type": "commit_message_contains", "value": "Old baseline"}
            ]
        }
    },

    {
        "stage_id": 7,
        "title": "Reflog Rescue",
        "description": "Recover lost work using git reflog",
        "difficulty": "intermediate",
        "story": {
            "context": "A reset hid a critical commit.",
            "teammate": "Nari (PM)",
            "incident": "You need to restore the previous state."
        },
        "objectives": [
            "Find the lost commit in reflog",
            "Restore the branch to include the lost work"
        ],
        "constraints": [
            "No history rewriting tools"
        ],
        "initial_commits": [
            {"message": "Important work", "files": {"important.py": "# Critical code\ndef critical_function():\n    return 'important'\n"}},
            {"message": "More important work", "files": {"important.py": "# Critical code\ndef critical_function():\n    return 'very important'\n"}},
            {"message": "Accidental reset point", "files": {"important.py": "# Critical code\ndef critical_function():\n    return 'important'\n", "temp.py": "# temporary\n"}}
        ],
        "hint": "Use 'git reflog' to find the missing commit.",
        "solution": "git reflog -> git reset --hard <commit>",
        "validation": {
            "must_have": [
                {"type": "file_contains", "path": "important.py", "value": "very important"},
                {"type": "worktree_clean"}
            ]
        }
    },

    {
        "stage_id": 8,
        "title": "Cherry-pick Range",
        "description": "Cherry-pick a range of feature commits",
        "difficulty": "intermediate",
        "story": {
            "context": "Only part of a feature branch is approved.",
            "teammate": "Min (reviewer)",
            "incident": "You must pick only the approved range."
        },
        "objectives": [
            "Cherry-pick the approved commit range",
            "Keep history linear"
        ],
        "constraints": [
            "No merge commits"
        ],
        "initial_commits": [
            {"message": "Baseline service", "files": {"service.py": "value = 1\n"}}
        ],
        "initial_branches": [
            {
                "name": "feature-range",
                "checkout": False,
                "commits": [
                    {"message": "Feature: add logging", "files": {"service.py": "value = 1\nlog = True\n"}},
                    {"message": "Feature: add config", "files": {"config.py": "ENABLED = True\n"}},
                    {"message": "Fix: adjust logging", "files": {"service.py": "value = 1\nlog = 'verbose'\n"}}
                ]
            }
        ],
        "hint": "Use 'git cherry-pick <start>^..<end>' for a range.",
        "solution": "git cherry-pick <start>^..<end>",
        "validation": {
            "must_have": [
                {"type": "commit_message_contains", "value": "Feature:"},
                {"type": "file_exists", "path": "config.py"},
                {"type": "no_merge_commits"}
            ]
        }
    },

    {
        "stage_id": 9,
        "title": "Bisect Bug Hunt",
        "description": "Locate a bug-introducing commit with git bisect",
        "difficulty": "intermediate",
        "story": {
            "context": "A regression was introduced recently.",
            "teammate": "Hana (QA)",
            "incident": "You must find the faulty commit quickly."
        },
        "objectives": [
            "Start a bisect session",
            "Identify the commit that introduced the bug",
            "Checkout the bad commit"
        ],
        "constraints": [
            "Avoid manual resets while bisecting"
        ],
        "initial_commits": [
            {"message": "Working version", "files": {"calculator.py": "def add(a, b):\n    return a + b\n"}},
            {"message": "Add multiplication", "files": {"calculator.py": "def add(a, b):\n    return a + b\n\ndef multiply(a, b):\n    return a * b\n"}},
            {"message": "Add subtraction", "files": {"calculator.py": "def add(a, b):\n    return a + b\n\ndef multiply(a, b):\n    return a * b\n\ndef subtract(a, b):\n    return a - b\n"}},
            {"message": "Fix add function", "files": {"calculator.py": "def add(a, b):\n    return a + b + 1  # BUG: extra +1\n\ndef multiply(a, b):\n    return a * b\n\ndef subtract(a, b):\n    return a - b\n"}},
            {"message": "Add division", "files": {"calculator.py": "def add(a, b):\n    return a + b + 1  # BUG: extra +1\n\ndef multiply(a, b):\n    return a * b\n\ndef subtract(a, b):\n    return a - b\n\ndef divide(a, b):\n    return a / b\n"}}
        ],
        "hint": "Use 'git bisect start' then mark good/bad commits.",
        "solution": "git bisect start -> git bisect bad -> git bisect good <hash>",
        "validation": {
            "must_have": [
                {"type": "head_message_contains", "value": "Fix add function"}
            ]
        }
    },

    {
        "stage_id": 10,
        "title": "Worktree Hotfix",
        "description": "Create a worktree for a hotfix branch",
        "difficulty": "intermediate",
        "story": {
            "context": "A release is frozen, but a hotfix is needed.",
            "teammate": "Rin (release manager)",
            "incident": "Work on the hotfix in a separate worktree."
        },
        "objectives": [
            "Create a worktree for a hotfix branch",
            "Commit the hotfix change"
        ],
        "constraints": [
            "Do not modify the main branch directly"
        ],
        "initial_commits": [
            {"message": "Production app", "files": {"app.py": "def main():\n    return 'ok'\n"}}
        ],
        "hint": "Use 'git worktree add -b hotfix <path> hotfix'.",
        "solution": "git worktree add -b hotfix ../hotfix hotfix -> edit -> git commit",
        "validation": {
            "must_have": [
                {"type": "branch_exists", "name": "hotfix"}
            ]
        }
    },

    {
        "stage_id": 11,
        "title": "Filter-Repo Cleanup",
        "description": "Remove sensitive data from history",
        "difficulty": "advanced",
        "story": {
            "context": "A secret was committed to the repo.",
            "teammate": "Eun (security)",
            "incident": "You must remove the file from history."
        },
        "objectives": [
            "Remove secrets.txt from history",
            "Keep the rest of the repo intact"
        ],
        "constraints": [
            "Do not use git commit --amend"
        ],
        "initial_commits": [
            {"message": "Add readme", "files": {"README.md": "# Project\n"}},
            {"message": "Accidentally add secrets", "files": {"secrets.txt": "API_KEY=123\n"}}
        ],
        "hint": "Use 'git filter-repo --path secrets.txt --invert-paths'.",
        "solution": "git filter-repo --path secrets.txt --invert-paths",
        "validation": {
            "must_have": [
                {"type": "file_exists", "path": "README.md"}
            ],
            "must_not_have": [
                {"type": "file_exists", "path": "secrets.txt"}
            ]
        }
    },

    {
        "stage_id": 12,
        "title": "Replace Object",
        "description": "Use git replace to swap a bad commit temporarily",
        "difficulty": "advanced",
        "story": {
            "context": "A bad commit exists in history.",
            "teammate": "Yul (lead)",
            "incident": "You must replace it without rewriting history."
        },
        "objectives": [
            "Create a replacement object for a bad commit",
            "Verify the replacement ref exists"
        ],
        "constraints": [
            "Do not reset or rebase"
        ],
        "initial_commits": [
            {"message": "Add dataset", "files": {"data.txt": "bad\n"}},
            {"message": "Correct dataset", "files": {"data.txt": "good\n"}}
        ],
        "hint": "Use 'git replace <bad> <good>'.",
        "solution": "git replace <bad> <good>",
        "validation": {
            "must_have": [
                {"type": "file_exists", "path": ".git/refs/replace"}
            ]
        }
    },

    {
        "stage_id": 13,
        "title": "Bundle Exchange",
        "description": "Create a bundle to share commits offline",
        "difficulty": "advanced",
        "story": {
            "context": "You need to send changes without network access.",
            "teammate": "Sera (ops)",
            "incident": "Prepare a Git bundle for transfer."
        },
        "objectives": [
            "Create a bundle file with current commits",
            "Ensure the bundle is saved in the repo"
        ],
        "constraints": [
            "Do not push to any remote"
        ],
        "initial_commits": [
            {"message": "Add offline doc", "files": {"offline.md": "# Offline Mode\n"}}
        ],
        "hint": "Use 'git bundle create feature.bundle HEAD'.",
        "solution": "git bundle create feature.bundle HEAD",
        "validation": {
            "must_have": [
                {"type": "file_exists", "path": "feature.bundle"}
            ]
        }
    },

    {
        "stage_id": 14,
        "title": "Custom Merge Strategy",
        "description": "Merge using a custom strategy option",
        "difficulty": "advanced",
        "story": {
            "context": "A merge should prefer the current branch's config.",
            "teammate": "Doyeon (devops)",
            "incident": "Use a strategy option to keep current settings."
        },
        "objectives": [
            "Merge the feature branch with a custom strategy",
            "Keep the base config in config.yml"
        ],
        "constraints": [
            "Do not use a default merge"
        ],
        "initial_commits": [
            {"message": "Base config", "files": {"config.yml": "mode: base\n"}}
        ],
        "initial_branches": [
            {
                "name": "feature-merge",
                "checkout": False,
                "commits": [
                    {"message": "Feature config", "files": {"config.yml": "mode: feature\n", "feature.txt": "feature\n"}}
                ]
            }
        ],
        "hint": "Use 'git merge -X ours feature-merge'.",
        "solution": "git merge -X ours feature-merge",
        "validation": {
            "must_have": [
                {"type": "has_merge_commits"},
                {"type": "file_contains", "path": "config.yml", "value": "mode: base"}
            ]
        }
    },

    {
        "stage_id": 15,
        "title": "Notes Workflow",
        "description": "Add review notes in a custom namespace",
        "difficulty": "advanced",
        "story": {
            "context": "Review feedback must be attached without altering commits.",
            "teammate": "Sol (reviewer)",
            "incident": "Record notes under a shared namespace."
        },
        "objectives": [
            "Add a git note to the latest commit",
            "Use a custom notes namespace"
        ],
        "constraints": [
            "Do not amend commits"
        ],
        "initial_commits": [
            {"message": "Add docs", "files": {"docs.md": "# Docs\n"}}
        ],
        "hint": "Use 'git notes --ref=team add -m \"review\"'.",
        "solution": "git notes --ref=team add -m \"review\"",
        "validation": {
            "must_have": [
                {"type": "file_exists", "path": ".git/refs/notes/team"}
            ]
        }
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

def get_stage_retry_policy(stage_id: int) -> Dict[str, Any]:
    """Get retry policy for a stage, falling back to default."""
    if stage_id < 1 or stage_id > len(STAGES):
        return DEFAULT_RETRY_POLICY
    stage = STAGES[stage_id - 1]
    return stage.get("retry_policy", DEFAULT_RETRY_POLICY)

def _has_merge_commits(repo: Repo, max_count: int = 50) -> bool:
    for commit in repo.iter_commits(max_count=max_count):
        if len(commit.parents) > 1:
            return True
    return False

def _get_stash_count(repo: Repo) -> int:
    try:
        stash_list = repo.git.stash("list")
    except Exception:
        return 0
    if not stash_list:
        return 0
    return len([line for line in stash_list.split("\n") if line.strip()])

def _read_file(repo_path: str, path: str) -> Optional[str]:
    file_path = os.path.join(repo_path, path)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as handle:
        return handle.read()

def _evaluate_validation_rule(rule: Dict[str, Any], repo: Repo, repo_path: str) -> bool:
    rule_type = rule.get("type")
    if rule_type not in SUPPORTED_VALIDATION_RULES:
        return False

    if rule_type == "head_message_contains":
        value = rule.get("value", "")
        return value in repo.head.commit.message
    if rule_type == "commit_message_contains":
        value = rule.get("value", "")
        max_count = rule.get("max_count", 50)
        return any(value in commit.message for commit in repo.iter_commits(max_count=max_count))
    if rule_type == "commit_count_at_most":
        max_count = rule.get("max_count", 50)
        value = rule.get("value", max_count)
        return len(list(repo.iter_commits(max_count=max_count))) <= value
    if rule_type == "file_contains":
        path = rule.get("path", "")
        value = rule.get("value", "")
        content = _read_file(repo_path, path)
        return content is not None and value in content
    if rule_type == "file_exists":
        path = rule.get("path", "")
        return os.path.exists(os.path.join(repo_path, path))
    if rule_type == "no_merge_commits":
        return not _has_merge_commits(repo)
    if rule_type == "has_merge_commits":
        return _has_merge_commits(repo)
    if rule_type == "stash_count_at_least":
        value = rule.get("value", 1)
        return _get_stash_count(repo) >= value
    if rule_type == "branch_exists":
        name = rule.get("name", "")
        return any(branch.name == name for branch in repo.branches)
    if rule_type == "branch_is_current":
        name = rule.get("name", "")
        try:
            return repo.active_branch.name == name
        except Exception:
            return False
    if rule_type == "worktree_clean":
        return not repo.is_dirty(untracked_files=True)

    return False

def validate_stage_by_rules(stage_id: int, repo: Repo, repo_path: str) -> Optional[bool]:
    """Validate stage completion using structured rules if present."""
    if stage_id < 1 or stage_id > len(STAGES):
        return None
    stage = STAGES[stage_id - 1]
    rules = stage.get("validation")
    if not rules:
        return None

    must_have = rules.get("must_have", [])
    must_not_have = rules.get("must_not_have", [])

    for rule in must_have:
        if not _evaluate_validation_rule(rule, repo, repo_path):
            return False
    for rule in must_not_have:
        if _evaluate_validation_rule(rule, repo, repo_path):
            return False
    return True

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
                "git log --oneline --all  # See hotfix commits",
                "git cherry-pick <commit-hash>",
                "# Resolve conflicts if needed",
                "git add <resolved-files>",
                "git cherry-pick --continue"
            ],
            "explanation": "Cherry-pick applies a specific commit from another branch. Resolve conflicts by editing files and continuing."
        },
        2: {
            "commands": [
                "git log --oneline  # Check recent commits",
                "git rebase -i HEAD~4",
                "# In editor: squash to leave 2 commits",
                "# Save and update the final commit message"
            ],
            "explanation": "Interactive rebase lets you squash and rename commits to keep history clean."
        },
        3: {
            "commands": [
                "git log --oneline",
                "git reset --soft HEAD~1  # Uncommit but keep staged",
                "git reset --mixed HEAD~1  # Unstage changes",
                "git status"
            ],
            "explanation": "Use reset modes to move HEAD without losing the working tree changes."
        },
        4: {
            "commands": [
                "git add <files>",
                "git stash push -S -m \"partial\"",
                "git stash list",
                "git stash apply"
            ],
            "explanation": "Stash staged changes only, then apply them back without dropping."
        },
        5: {
            "commands": [
                "git merge feature-ux",
                "git status",
                "# Resolve ui.txt conflict",
                "git add ui.txt",
                "git commit"
            ],
            "explanation": "Resolve conflicts in the working tree and complete the merge."
        },
        # Add more detailed help for other stages
    }
    
    return {
        "stage": stage,
        "detailed_help": detailed_help.get(stage_id, {}),
        "solution": stage.get("solution"),
        "general_tips": [
            "Use 'git status' frequently to check current state",
            "Use 'git log --oneline --graph --all' to visualize branches",
            "Use 'git help <command>' for detailed command help"
        ]
    }
