"""Stage definitions for the command line Git trainer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable, Dict, List, Tuple


ValidationResult = Tuple[bool, str]
StageSetup = Callable[[Path], None]
StageValidator = Callable[[Path], ValidationResult]


@dataclass(frozen=True)
class Stage:
    stage_id: int
    title: str
    objective: str
    hint: str
    solution: str
    setup: StageSetup
    validate: StageValidator


def _git(repo_path: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return (proc.stdout or "") + (proc.stderr or "")


def _init_repo(repo_path: Path) -> None:
    _git(repo_path, "init", "-b", "main")
    _git(repo_path, "config", "user.name", "Git Learner")
    _git(repo_path, "config", "user.email", "learner@example.com")


def _head_message(repo_path: Path) -> str:
    return _git(repo_path, "log", "-1", "--pretty=%s").strip()


def _commit_count(repo_path: Path) -> int:
    return int(_git(repo_path, "rev-list", "--count", "HEAD").strip())


def _stash_count(repo_path: Path) -> int:
    lines = _git(repo_path, "stash", "list").strip().splitlines()
    return len([x for x in lines if x.strip()])


def _has_merge_commit(repo_path: Path) -> bool:
    return int(_git(repo_path, "rev-list", "--merges", "--count", "HEAD").strip()) > 0


def _branch_exists(repo_path: Path, name: str) -> bool:
    return bool(_git(repo_path, "branch", "--list", name).strip())


def _current_branch(repo_path: Path) -> str:
    return _git(repo_path, "rev-parse", "--abbrev-ref", "HEAD").strip()


def _file_contains(repo_path: Path, rel: str, text: str) -> bool:
    p = repo_path / rel
    return p.exists() and text in p.read_text(encoding="utf-8")


def _file_exists(repo_path: Path, rel: str) -> bool:
    return (repo_path / rel).exists()


def _working_tree_clean(repo_path: Path) -> bool:
    return not _git(repo_path, "status", "--porcelain").strip()


def _make_stage(
    stage_id: int,
    title: str,
    objective: str,
    hint: str,
    solution: str,
    setup: StageSetup,
    validate: StageValidator,
) -> Stage:
    return Stage(stage_id, title, objective, hint, solution, setup, validate)


def _setup_1(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "app.cfg").write_text("feature=false\nhotfix=false\n", encoding="utf-8")
    _git(repo_path, "add", "app.cfg")
    _git(repo_path, "commit", "-m", "Base config")
    _git(repo_path, "checkout", "-b", "hotfix")
    (repo_path / "app.cfg").write_text("feature=false\nhotfix=true\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Hotfix: enable runtime patch")
    _git(repo_path, "checkout", "main")


def _validate_1(repo_path: Path) -> ValidationResult:
    if not _file_contains(repo_path, "app.cfg", "hotfix=true"):
        return False, "app.cfg에 hotfix=true 반영 필요"
    if "Hotfix:" not in _head_message(repo_path):
        return False, "마지막 커밋 메시지에 Hotfix: 필요"
    return True, "완료"


def _setup_2(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "feature.py").write_text("FLAG = False\n", encoding="utf-8")
    _git(repo_path, "add", "feature.py")
    _git(repo_path, "commit", "-m", "Init feature")
    (repo_path / "feature.py").write_text("FLAG = True\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "WIP flag")
    (repo_path / "feature.py").write_text("FLAG = True\nMODE = 'safe'\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "WIP mode")


def _validate_2(repo_path: Path) -> ValidationResult:
    if _commit_count(repo_path) > 2:
        return False, "커밋을 2개 이하로 squash 하세요"
    if not _head_message(repo_path).startswith("Feature:"):
        return False, "마지막 커밋 메시지는 Feature: 로 시작"
    return True, "완료"


def _setup_3(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "README.md").write_text("mode=main\n", encoding="utf-8")
    _git(repo_path, "add", "README.md")
    _git(repo_path, "commit", "-m", "Base README")
    _git(repo_path, "checkout", "-b", "feature-ui")
    (repo_path / "README.md").write_text("mode=feature-ui\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "UI tweak")
    _git(repo_path, "checkout", "main")
    (repo_path / "README.md").write_text("mode=main-hardening\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Main hardening")


def _validate_3(repo_path: Path) -> ValidationResult:
    if not _has_merge_commit(repo_path):
        return False, "merge 커밋이 필요합니다"
    content = (repo_path / "README.md").read_text(encoding="utf-8")
    if "<<" in content or ">>" in content:
        return False, "충돌 마커가 남아 있습니다"
    return True, "완료"


def _setup_4(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "notes.txt").write_text("stable\n", encoding="utf-8")
    _git(repo_path, "add", "notes.txt")
    _git(repo_path, "commit", "-m", "Stable notes")
    (repo_path / "notes.txt").write_text("stable\nlost draft\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "WIP draft")


def _validate_4(repo_path: Path) -> ValidationResult:
    if _file_contains(repo_path, "notes.txt", "lost draft"):
        return False, "lost draft 를 제거하세요"
    if not _working_tree_clean(repo_path):
        return False, "작업 트리를 clean 상태로 만드세요"
    return True, "완료"


def _setup_5(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "service.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    _git(repo_path, "add", "service.py")
    _git(repo_path, "commit", "-m", "Service baseline")
    _git(repo_path, "checkout", "-b", "release")
    (repo_path / "service.py").write_text(
        "def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n",
        encoding="utf-8",
    )
    _git(repo_path, "commit", "-am", "Release prep")
    _git(repo_path, "checkout", "main")


def _validate_5(repo_path: Path) -> ValidationResult:
    if not _file_contains(repo_path, "service.py", "def sub"):
        return False, "release 변경분(def sub)을 반영하세요"
    if "fix" not in _head_message(repo_path).lower():
        return False, "마지막 커밋 메시지에 fix 포함"
    return True, "완료"


def _setup_6(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "auth.py").write_text("ENABLED = False\n", encoding="utf-8")
    _git(repo_path, "add", "auth.py")
    _git(repo_path, "commit", "-m", "Base auth")


def _validate_6(repo_path: Path) -> ValidationResult:
    if not _branch_exists(repo_path, "feature/auth"):
        return False, "feature/auth 브랜치를 만드세요"
    if _current_branch(repo_path) != "feature/auth":
        return False, "feature/auth 브랜치에서 작업하세요"
    if not _head_message(repo_path).startswith("Feature:"):
        return False, "커밋 메시지는 Feature: 로 시작"
    return True, "완료"


def _setup_7(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "api.py").write_text("timeout=30\n", encoding="utf-8")
    (repo_path / "worker.py").write_text("retry=1\n", encoding="utf-8")
    _git(repo_path, "add", "api.py", "worker.py")
    _git(repo_path, "commit", "-m", "Base services")


def _validate_7(repo_path: Path) -> ValidationResult:
    if _stash_count(repo_path) < 1:
        return False, "stash를 최소 1개 생성하세요"
    if not _file_contains(repo_path, "api.py", "timeout=60"):
        return False, "api.py에 timeout=60 변경을 남기세요"
    return True, "완료"


def _setup_8(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "CHANGELOG.md").write_text("v0.1.0\n", encoding="utf-8")
    _git(repo_path, "add", "CHANGELOG.md")
    _git(repo_path, "commit", "-m", "Prepare release")


def _validate_8(repo_path: Path) -> ValidationResult:
    tags = _git(repo_path, "tag", "--list", "v1.0.0").strip()
    if not tags:
        return False, "v1.0.0 태그를 만드세요"
    return True, "완료"


def _setup_9(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "svc.py").write_text("base=1\n", encoding="utf-8")
    _git(repo_path, "add", "svc.py")
    _git(repo_path, "commit", "-m", "Base service")
    _git(repo_path, "checkout", "-b", "feature-range")
    (repo_path / "svc.py").write_text("base=1\nlog=true\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Feature: add logging")
    (repo_path / "config.py").write_text("ENABLED=True\n", encoding="utf-8")
    _git(repo_path, "add", "config.py")
    _git(repo_path, "commit", "-m", "Feature: add config")
    (repo_path / "docs.txt").write_text("notes\n", encoding="utf-8")
    _git(repo_path, "add", "docs.txt")
    _git(repo_path, "commit", "-m", "Chore docs")
    _git(repo_path, "checkout", "main")


def _validate_9(repo_path: Path) -> ValidationResult:
    if not _file_exists(repo_path, "config.py"):
        return False, "config.py가 main에 있어야 합니다"
    if _has_merge_commit(repo_path):
        return False, "merge 없이 cherry-pick으로 해결하세요"
    return True, "완료"


def _setup_10(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "calc.py").write_text("def add(a,b):\n    return a + b\n", encoding="utf-8")
    _git(repo_path, "add", "calc.py")
    _git(repo_path, "commit", "-m", "Base calculator")
    (repo_path / "calc.py").write_text("def add(a,b):\n    return a + b + 1\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Bad commit: off by one")


def _validate_10(repo_path: Path) -> ValidationResult:
    if "Revert" not in _head_message(repo_path):
        return False, "git revert로 되돌리세요"
    if _file_contains(repo_path, "calc.py", "+ 1"):
        return False, "버그 코드(+1)가 남아 있습니다"
    return True, "완료"


def _setup_11(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "core.py").write_text("VERSION=1\n", encoding="utf-8")
    _git(repo_path, "add", "core.py")
    _git(repo_path, "commit", "-m", "Core baseline")
    _git(repo_path, "checkout", "-b", "old-base")
    (repo_path / "feature.py").write_text("mode='old'\n", encoding="utf-8")
    _git(repo_path, "add", "feature.py")
    _git(repo_path, "commit", "-m", "Old: first")
    _git(repo_path, "checkout", "-b", "feature")
    (repo_path / "feature.py").write_text("mode='new'\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Feature: start")
    (repo_path / "feature.py").write_text("mode='new-final'\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Feature: finalize")
    _git(repo_path, "checkout", "main")


def _validate_11(repo_path: Path) -> ValidationResult:
    if _current_branch(repo_path) != "feature":
        return False, "feature 브랜치에서 마무리하세요"
    log = _git(repo_path, "log", "--pretty=%s", "-n", "5")
    if "Old:" in log:
        return False, "old-base 커밋을 제외하고 옮겨야 합니다"
    if "Feature:" not in log:
        return False, "Feature 커밋이 유지되어야 합니다"
    return True, "완료"


def _setup_12(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "important.py").write_text("value='v1'\n", encoding="utf-8")
    _git(repo_path, "add", "important.py")
    _git(repo_path, "commit", "-m", "Important v1")
    (repo_path / "important.py").write_text("value='critical-v2'\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Important v2")
    (repo_path / "important.py").write_text("value='temporary-v3'\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Temporary v3")
    _git(repo_path, "reset", "--hard", "HEAD~2")


def _validate_12(repo_path: Path) -> ValidationResult:
    if not _file_contains(repo_path, "important.py", "critical-v2"):
        return False, "reflog를 이용해 v2 커밋을 복구하세요"
    return True, "완료"


def _setup_13(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "bug.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
    _git(repo_path, "add", "bug.py")
    _git(repo_path, "commit", "-m", "good base")
    (repo_path / "bug.py").write_text("def ok():\n    return 2\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "still good")
    (repo_path / "bug.py").write_text("def ok():\n    return 0  # BUG\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "introduce BUG")


def _validate_13(repo_path: Path) -> ValidationResult:
    if not _file_exists(repo_path, ".git/BISECT_LOG"):
        return False, "git bisect를 시작해 good/bad를 기록하세요"
    return True, "완료"


def _setup_14(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "app.py").write_text("def main():\n    return 'ok'\n", encoding="utf-8")
    _git(repo_path, "add", "app.py")
    _git(repo_path, "commit", "-m", "Prod baseline")


def _validate_14(repo_path: Path) -> ValidationResult:
    if not _branch_exists(repo_path, "hotfix"):
        return False, "worktree에서 hotfix 브랜치를 생성하세요"
    log = _git(repo_path, "log", "--pretty=%s", "-n", "5")
    if "Hotfix WT" not in log:
        return False, "Hotfix WT 커밋을 남기세요"
    return True, "완료"


def _setup_15(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "offline.md").write_text("# Offline\n", encoding="utf-8")
    _git(repo_path, "add", "offline.md")
    _git(repo_path, "commit", "-m", "Offline docs")


def _validate_15(repo_path: Path) -> ValidationResult:
    p = repo_path / "feature.bundle"
    if not p.exists() or p.stat().st_size == 0:
        return False, "feature.bundle 파일을 생성하세요"
    return True, "완료"


def _setup_16(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "docs.md").write_text("# Docs\n", encoding="utf-8")
    _git(repo_path, "add", "docs.md")
    _git(repo_path, "commit", "-m", "Add docs")


def _validate_16(repo_path: Path) -> ValidationResult:
    if not _file_exists(repo_path, ".git/refs/notes/team"):
        return False, "git notes --ref=team add ... 를 실행하세요"
    return True, "완료"


def _setup_17(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "data.txt").write_text("bad\n", encoding="utf-8")
    _git(repo_path, "add", "data.txt")
    _git(repo_path, "commit", "-m", "Bad data")
    (repo_path / "data.txt").write_text("good\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Good data")


def _validate_17(repo_path: Path) -> ValidationResult:
    ref_dir = repo_path / ".git" / "refs" / "replace"
    if not ref_dir.exists():
        return False, "git replace로 replace ref를 생성하세요"
    if not any(ref_dir.iterdir()):
        return False, "replace ref가 비어 있습니다"
    return True, "완료"


def _setup_18(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "config.yml").write_text("mode: main\n", encoding="utf-8")
    _git(repo_path, "add", "config.yml")
    _git(repo_path, "commit", "-m", "Base config")
    _git(repo_path, "checkout", "-b", "feature-merge")
    (repo_path / "config.yml").write_text("mode: feature\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Feature config")
    _git(repo_path, "checkout", "main")
    (repo_path / "config.yml").write_text("mode: main-stable\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Main stable config")


def _validate_18(repo_path: Path) -> ValidationResult:
    if not _has_merge_commit(repo_path):
        return False, "-X ours 옵션으로 merge 커밋을 만드세요"
    if not _file_contains(repo_path, "config.yml", "mode: main"):
        return False, "main 쪽 설정을 유지하세요"
    return True, "완료"


def _setup_19(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "cleanup.txt").write_text("todo\n", encoding="utf-8")
    _git(repo_path, "add", "cleanup.txt")
    _git(repo_path, "commit", "-m", "Base cleanup")
    _git(repo_path, "checkout", "-b", "feature-cleanup")
    (repo_path / "cleanup.txt").write_text("done\n", encoding="utf-8")
    _git(repo_path, "commit", "-am", "Cleanup done")
    _git(repo_path, "checkout", "main")


def _validate_19(repo_path: Path) -> ValidationResult:
    if _branch_exists(repo_path, "feature-cleanup"):
        return False, "merge 후 feature-cleanup 브랜치를 삭제하세요"
    if not _has_merge_commit(repo_path):
        return False, "먼저 feature-cleanup을 merge 하세요"
    return True, "완료"


def _setup_20(repo_path: Path) -> None:
    _init_repo(repo_path)
    (repo_path / "final.txt").write_text("v1\n", encoding="utf-8")
    _git(repo_path, "add", "final.txt")
    _git(repo_path, "commit", "-m", "Draft final")
    (repo_path / "final.txt").write_text("v2-ready\n", encoding="utf-8")
    _git(repo_path, "add", "final.txt")


def _validate_20(repo_path: Path) -> ValidationResult:
    if not _working_tree_clean(repo_path):
        return False, "staged 변경을 포함해 commit --amend로 정리하세요"
    if not _head_message(repo_path).startswith("Final:"):
        return False, "최종 커밋 메시지를 Final: 로 시작하세요"
    return True, "완료"


STAGES: List[Stage] = [
    _make_stage(
        1,
        "Cherry-pick Hotfix",
        "hotfix 브랜치 커밋을 main으로 cherry-pick 하세요.",
        "git log --oneline hotfix -> git cherry-pick <hash>",
        "git cherry-pick <hotfix-commit>",
        _setup_1,
        _validate_1,
    ),
    _make_stage(
        2,
        "Rebase Squash",
        "커밋을 2개 이하로 정리하고 마지막 메시지를 Feature:로 시작시키세요.",
        "git rebase -i HEAD~2 또는 HEAD~3",
        "git rebase -i ... 후 reword로 Feature: ...",
        _setup_2,
        _validate_2,
    ),
    _make_stage(
        3,
        "Conflict Merge",
        "feature-ui를 merge 하고 충돌 마커 없이 마무리하세요.",
        "git merge feature-ui -> 충돌 해결 -> add -> commit",
        "git merge feature-ui",
        _setup_3,
        _validate_3,
    ),
    _make_stage(
        4,
        "Reset Recovery",
        "draft를 제거하고 clean working tree로 마무리하세요.",
        "reset --soft/--mixed로 히스토리와 파일을 정리하세요.",
        "git reset --soft HEAD~1",
        _setup_4,
        _validate_4,
    ),
    _make_stage(
        5,
        "Release Hotfix",
        "release 변경을 반영하고 fix가 포함된 커밋을 남기세요.",
        "release 브랜치 작업 후 main 반영",
        "git checkout release -> commit -m 'fix: ...' -> main 반영",
        _setup_5,
        _validate_5,
    ),
    _make_stage(
        6,
        "Feature Branch Start",
        "feature/auth 브랜치에서 Feature: 커밋을 만드세요.",
        "git checkout -b feature/auth",
        "git checkout -b feature/auth && git commit -m 'Feature: ...'",
        _setup_6,
        _validate_6,
    ),
    _make_stage(
        7,
        "Stash Practice",
        "stash를 남기고 api.py timeout=60 상태를 확보하세요.",
        "api.py 수정 후 staged stash를 연습하세요.",
        "git add api.py && git stash push -m 'api timeout' && git stash apply",
        _setup_7,
        _validate_7,
    ),
    _make_stage(
        8,
        "Release Tag",
        "v1.0.0 태그를 생성하세요.",
        "git tag -a v1.0.0 -m 'release v1.0.0'",
        "git tag -a v1.0.0 -m 'release'",
        _setup_8,
        _validate_8,
    ),
    _make_stage(
        9,
        "Cherry-pick Range",
        "feature-range에서 필요한 커밋만 main으로 가져오세요.",
        "git cherry-pick <start>^..<end>",
        "git cherry-pick <feature-commit-range>",
        _setup_9,
        _validate_9,
    ),
    _make_stage(
        10,
        "Revert Bad Commit",
        "버그 커밋을 revert로 되돌리세요.",
        "git log --oneline 후 git revert <bad-hash>",
        "git revert <bad-commit>",
        _setup_10,
        _validate_10,
    ),
    _make_stage(
        11,
        "Rebase Onto",
        "feature 브랜치를 old-base 없이 재배치하세요.",
        "git rebase --onto main old-base feature",
        "git checkout feature && git rebase --onto main old-base feature",
        _setup_11,
        _validate_11,
    ),
    _make_stage(
        12,
        "Reflog Rescue",
        "reflog로 중요한 v2 상태를 복구하세요.",
        "git reflog 후 git reset --hard <hash>",
        "git reflog && git reset --hard <important-v2>",
        _setup_12,
        _validate_12,
    ),
    _make_stage(
        13,
        "Bisect Start",
        "bisect good/bad 기록을 남기세요.",
        "git bisect start -> bad -> good <hash>",
        "git bisect start",
        _setup_13,
        _validate_13,
    ),
    _make_stage(
        14,
        "Worktree Hotfix",
        "worktree에서 hotfix 브랜치 커밋(Hotfix WT)을 만드세요.",
        "git worktree add ../hotfix -b hotfix",
        "git worktree add ../hotfix -b hotfix && git commit -m 'Hotfix WT ...'",
        _setup_14,
        _validate_14,
    ),
    _make_stage(
        15,
        "Bundle Export",
        "offline 공유용 feature.bundle을 생성하세요.",
        "git bundle create feature.bundle HEAD",
        "git bundle create feature.bundle HEAD",
        _setup_15,
        _validate_15,
    ),
    _make_stage(
        16,
        "Notes Namespace",
        "team notes namespace에 note를 추가하세요.",
        "git notes --ref=team add -m 'review'",
        "git notes --ref=team add -m 'review'",
        _setup_16,
        _validate_16,
    ),
    _make_stage(
        17,
        "Replace Object",
        "git replace로 replace ref를 생성하세요.",
        "git log --oneline 후 git replace <old> <new>",
        "git replace <bad> <good>",
        _setup_17,
        _validate_17,
    ),
    _make_stage(
        18,
        "Merge Strategy Ours",
        "-X ours 옵션으로 merge하고 main 설정을 유지하세요.",
        "git merge -X ours feature-merge",
        "git merge -X ours feature-merge",
        _setup_18,
        _validate_18,
    ),
    _make_stage(
        19,
        "Merge Then Cleanup Branch",
        "feature-cleanup을 merge하고 브랜치를 삭제하세요.",
        "git merge feature-cleanup && git branch -d feature-cleanup",
        "git merge feature-cleanup && git branch -d feature-cleanup",
        _setup_19,
        _validate_19,
    ),
    _make_stage(
        20,
        "Final Amend",
        "staged 변경을 포함해 마지막 커밋을 amend하고 메시지를 Final:로 바꾸세요.",
        "git commit --amend",
        "git commit --amend -m 'Final: ...'",
        _setup_20,
        _validate_20,
    ),
]

STAGE_INFOS: Dict[int, str] = {
    1: (
        "Cherry-pick 상세:\n"
        "- 기능: 다른 브랜치의 특정 커밋 1개를 현재 브랜치로 복사 적용합니다.\n"
        "- 주 사용 시점: hotfix를 전체 merge 없이 main에 빠르게 반영할 때.\n"
        "- 주의: 같은 변경을 중복 적용하면 충돌/중복 커밋이 생길 수 있습니다."
    ),
    2: (
        "Rebase Squash 상세:\n"
        "- 기능: 여러 커밋을 정리(squash/reword)해 히스토리를 읽기 쉽게 만듭니다.\n"
        "- 주 사용 시점: PR 올리기 전 WIP 커밋을 정돈할 때.\n"
        "- 주의: 공유 브랜치의 공개 커밋 rebase는 협업 충돌을 유발할 수 있습니다."
    ),
    3: (
        "Merge Conflict 상세:\n"
        "- 기능: 두 브랜치의 변경을 합치며 충돌을 수동 해결합니다.\n"
        "- 주 사용 시점: 기능 브랜치를 main에 통합할 때.\n"
        "- 주의: 충돌 마커(<<<<, >>>>)가 파일에 남지 않게 마무리하세요."
    ),
    4: (
        "Reset Recovery 상세:\n"
        "- 기능: reset 모드로 커밋/스테이징/워킹트리 상태를 되돌립니다.\n"
        "- 주 사용 시점: 잘못된 커밋을 로컬에서 정리할 때.\n"
        "- 주의: --hard는 변경을 잃을 수 있으니 복구 가능성(reflog)까지 고려하세요."
    ),
    5: (
        "Release Hotfix 상세:\n"
        "- 기능: 릴리스 브랜치 변경을 안정적으로 가져와 수정 커밋을 남깁니다.\n"
        "- 주 사용 시점: 배포 직전/직후 긴급 수정 반영.\n"
        "- 주의: 메시지 규칙(fix 포함)으로 변경 의도를 명확히 남기세요."
    ),
    6: (
        "Feature Branch Start 상세:\n"
        "- 기능: 기능 전용 브랜치에서 독립적으로 개발 시작.\n"
        "- 주 사용 시점: main을 보호하며 병렬 작업할 때.\n"
        "- 주의: 브랜치 네이밍과 커밋 메시지 규칙을 초반부터 지키세요."
    ),
    7: (
        "Stash Practice 상세:\n"
        "- 기능: 작업 중 변경을 임시 저장(stash)하고 다시 적용합니다.\n"
        "- 주 사용 시점: 급한 브랜치 전환/리뷰 대응이 필요할 때.\n"
        "- 주의: stash apply/pop 이후 충돌 여부를 반드시 확인하세요."
    ),
    8: (
        "Release Tag 상세:\n"
        "- 기능: 특정 커밋에 버전 태그를 붙여 릴리스 기준점을 만듭니다.\n"
        "- 주 사용 시점: 배포 버전 고정, 롤백 기준 관리.\n"
        "- 주의: annotated tag를 사용하면 이력 추적이 더 명확합니다."
    ),
    9: (
        "Cherry-pick Range 상세:\n"
        "- 기능: 커밋 범위를 선택적으로 현재 브랜치에 복사 적용합니다.\n"
        "- 주 사용 시점: 기능 브랜치의 일부 커밋만 선별 반영할 때.\n"
        "- 주의: 범위 지정(start^..end) 실수 시 불필요한 커밋까지 들어올 수 있습니다."
    ),
    10: (
        "Revert 상세:\n"
        "- 기능: 기존 커밋을 취소하는 '새 커밋'을 생성합니다.\n"
        "- 주 사용 시점: 공유 브랜치에서 안전하게 변경을 되돌릴 때.\n"
        "- 주의: reset과 달리 히스토리는 보존됩니다."
    ),
    11: (
        "Rebase --onto 상세:\n"
        "- 기능: 특정 구간 커밋을 새 베이스로 재배치합니다.\n"
        "- 주 사용 시점: 잘못된 기반 브랜치에서 작업한 커밋을 구조적으로 옮길 때.\n"
        "- 주의: 기준 커밋(old-base) 지정이 틀리면 의도치 않은 재배치가 발생합니다."
    ),
    12: (
        "Reflog Rescue 상세:\n"
        "- 기능: 사라진 것처럼 보이는 HEAD 이동 이력을 reflog로 추적해 복구.\n"
        "- 주 사용 시점: reset --hard, 잘못된 rebase 후 복구할 때.\n"
        "- 주의: reflog는 로컬 기록이므로 오래 지나면 정리될 수 있습니다."
    ),
    13: (
        "Bisect Start 상세:\n"
        "- 기능: good/bad 기준으로 이진 탐색해 문제 커밋을 빠르게 찾습니다.\n"
        "- 주 사용 시점: 언제 버그가 들어왔는지 모를 때.\n"
        "- 주의: 판별 기준(테스트/검증)이 명확해야 정확도가 올라갑니다."
    ),
    14: (
        "Worktree Hotfix 상세:\n"
        "- 기능: 하나의 저장소에서 여러 브랜치를 별도 디렉토리로 동시 작업.\n"
        "- 주 사용 시점: main 작업 중 hotfix를 즉시 병행할 때.\n"
        "- 주의: 각 worktree의 현재 브랜치를 혼동하지 않도록 주의하세요."
    ),
    15: (
        "Bundle Export 상세:\n"
        "- 기능: 네트워크 없이 주고받을 수 있는 Git 번들 파일 생성.\n"
        "- 주 사용 시점: 오프라인/보안망 환경에서 이력 전달.\n"
        "- 주의: 필요한 ref 범위를 포함했는지 생성 후 검증하세요."
    ),
    16: (
        "Notes Namespace 상세:\n"
        "- 기능: 커밋 본문을 바꾸지 않고 notes로 메타데이터를 첨부.\n"
        "- 주 사용 시점: 리뷰 코멘트, 내부 추적 정보 분리 저장.\n"
        "- 주의: notes ref 공유(push) 규칙을 팀에 맞춰 설정하세요."
    ),
    17: (
        "Replace Object 상세:\n"
        "- 기능: 원본 객체를 바꾸지 않고 replace ref로 대체 객체를 참조.\n"
        "- 주 사용 시점: 히스토리 실험/임시 복구 검증.\n"
        "- 주의: 로컬 중심 기능이므로 협업 전 replace ref 전파 여부를 확인하세요."
    ),
    18: (
        "Merge Strategy Ours 상세:\n"
        "- 기능: 충돌 시 현재 브랜치(main) 변경을 우선 채택(-X ours).\n"
        "- 주 사용 시점: 통합은 하되 현재 안정 설정을 유지하고 싶을 때.\n"
        "- 주의: 상대 변경이 사라질 수 있어 의도 검토가 필요합니다."
    ),
    19: (
        "Merge Then Cleanup 상세:\n"
        "- 기능: merge 완료 후 작업 브랜치를 정리해 브랜치 생명주기 종료.\n"
        "- 주 사용 시점: 기능 반영 완료 후 저장소를 깔끔하게 유지할 때.\n"
        "- 주의: 삭제 전 원격/로컬 모두에서 반영 여부를 확인하세요."
    ),
    20: (
        "Final Amend 상세:\n"
        "- 기능: 마지막 커밋에 staged 변경을 합치고 메시지를 최종 정리.\n"
        "- 주 사용 시점: 리뷰 반영 후 마지막 커밋 품질 정리 단계.\n"
        "- 주의: 이미 공유된 커밋 amend는 히스토리 변경이므로 팀 합의가 필요합니다."
    ),
}


def get_stage(stage_id: int) -> Stage:
    for stage in STAGES:
        if stage.stage_id == stage_id:
            return stage
    raise ValueError(f"Unknown stage: {stage_id}")


def _safe_git(repo_path: Path, *args: str) -> str:
    try:
        return _git(repo_path, *args).strip()
    except subprocess.CalledProcessError:
        return ""


def _render_repo_snapshot(repo_path: Path) -> List[str]:
    current_branch = _safe_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    status_raw = _safe_git(repo_path, "status", "--short")
    branch_raw = _safe_git(repo_path, "branch", "--sort=refname")
    graph_raw = _safe_git(repo_path, "log", "--graph", "--decorate", "--oneline", "--all", "-n", "12")

    lines = [
        "브랜치 맵 (CLI UI):",
        "┌─ 저장소 스냅샷",
        f"│ 현재 브랜치: {current_branch}",
        f"│ 작업 트리: {'clean' if not status_raw else '변경 있음'}",
        "├─ 브랜치 목록",
    ]

    branches = [line.rstrip() for line in branch_raw.splitlines() if line.strip()]
    if branches:
        for branch in branches:
            lines.append(f"│ {branch}")
    else:
        lines.append("│ (브랜치 정보 없음)")

    lines.append("├─ 최근 커밋 그래프")
    graph_lines = [line.rstrip() for line in graph_raw.splitlines() if line.strip()]
    if graph_lines:
        for graph_line in graph_lines:
            lines.append(f"│ {graph_line}")
    else:
        lines.append("│ (커밋 그래프 없음)")
    lines.append("└─ tip: git log --graph --decorate --oneline --all")
    return lines


def get_stage_info(stage_id: int, mode: str = "brief", repo_path: Path | None = None) -> str:
    stage = get_stage(stage_id)
    default_info = (
        f"{stage.title} 상세:\n"
        f"- 목표: {stage.objective}\n"
        f"- 힌트: {stage.hint}\n"
        f"- 해법 예시: {stage.solution}"
    )
    raw_info = STAGE_INFOS.get(stage_id, default_info)
    lines = [line.strip() for line in raw_info.splitlines() if line.strip()]

    rendered = [
        f"[INFO] Stage {stage.stage_id} | {stage.title}",
        f"목표: {stage.objective}",
        "",
    ]
    for line in lines:
        if line.endswith("상세:"):
            continue
        if line.startswith("- "):
            rendered.append(f"• {line[2:]}")
        else:
            rendered.append(line)

    if mode == "full":
        rendered.extend(
            [
                "",
                "추천 커맨드:",
                f"• 힌트: {stage.hint}",
                f"• 해법 예시: {stage.solution}",
            ]
        )
        if repo_path is not None:
            rendered.extend(["", *_render_repo_snapshot(repo_path)])

    return "\n".join(rendered)
