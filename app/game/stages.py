import os
import subprocess
from dataclasses import dataclass, field
from typing import Callable, List, Dict

def run_git_command(command: str, cwd: str) -> str:
    """Runs a git command and returns its output."""
    try:
        process = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, check=True)
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""

# --- Stage Setup Functions ---

def setup_stage1(cwd: str):
    """Create a file for the user to commit."""
    with open(os.path.join(cwd, "README.md"), "w") as f:
        f.write("# Git Learning Game\n\nWelcome!")

# --- Stage Check Functions ---

def check_stage1(cwd: str) -> bool:
    """Check if there is at least one commit."""
    log = run_git_command("git log --oneline", cwd)
    return log != ""

def check_stage2(cwd: str) -> bool:
    """Check if the local main is in sync with remote main."""
    local_hash = run_git_command("git rev-parse main", cwd)
    remote_hash = run_git_command("git rev-parse origin/main", cwd)
    return local_hash != "" and local_hash == remote_hash

# --- Stage Definitions ---

@dataclass
class Stage:
    id: int
    title: str
    description: str
    hint: str
    setup: Callable[[str], None] = field(default=lambda cwd: None)
    check: Callable[[str], bool] = field(default=lambda cwd: False)

STAGES: List[Stage] = [
    Stage(
        id=1,
        title="첫 번째 커밋 만들기",
        description="저장소에 첫 번째 커밋을 만들어봅시다. `README.md` 파일이 이미 생성되어 있습니다. 이 파일을 스테이징하고('add') 커밋('commit')하세요.",
        hint="`git add <file>`로 파일을 스테이징하고, `git commit -m 'Your message'`로 커밋합니다.",
        setup=setup_stage1,
        check=check_stage1,
    ),
    Stage(
        id=2,
        title="원격 저장소에 푸시하기",
        description="로컬 커밋을 원격 저장소('origin')에 푸시하여 작업을 공유하세요. 앞으로 이 원격 저장소는 다른 팀원들과의 협업 공간이 될 것입니다.",
        hint="`git push origin <branch-name>` 명령어를 사용하세요. 기본 브랜치 이름은 'main'입니다.",
        check=check_stage2,
    ),
]

STAGES_BY_ID: Dict[int, Stage] = {stage.id: stage for stage in STAGES}

def get_stage(stage_id: int) -> Stage | None:
    return STAGES_BY_ID.get(stage_id)
