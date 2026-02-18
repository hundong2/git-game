"""Runtime engine for interactive Git training."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Tuple
import uuid

from .stages import STAGES, Stage, get_stage


ALLOWED_COMMANDS = {
    "git",
    "ls",
    "pwd",
    "cat",
    "find",
    "grep",
    "sed",
    "head",
    "tail",
    "wc",
    "echo",
}


def is_command_allowed(command: str) -> bool:
    command = command.strip()
    if not command:
        return False
    if any(op in command for op in ("&&", "||", ";", "|", "$(", "`")):
        return False
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if not tokens:
        return False
    return tokens[0] in ALLOWED_COMMANDS


def should_repeat_stage(help_used: bool, already_repeated: bool) -> bool:
    return help_used and not already_repeated


@dataclass
class SessionStats:
    commands: int = 0
    hints: int = 0
    solutions: int = 0
    completed: List[int] = field(default_factory=list)


class GitTrainer:
    def __init__(self, stage_id: int = 1):
        self.stats = SessionStats()
        self.session_id = str(uuid.uuid4())
        self.started_at = datetime.now(timezone.utc)
        self.stage_id = stage_id
        self.stage: Stage = get_stage(stage_id)
        self._stage_repeated = False
        self._help_used_in_stage = False
        self._tmp_root = Path(tempfile.mkdtemp(prefix="git_trainer_"))
        self.repo_path: Path = self._tmp_root / "repo"
        self._setup_stage(stage_id)

    def cleanup(self) -> None:
        shutil.rmtree(self._tmp_root, ignore_errors=True)

    def _setup_stage(self, stage_id: int) -> None:
        self.stage_id = stage_id
        self.stage = get_stage(stage_id)
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self.stage.setup(self.repo_path)
        self._help_used_in_stage = False

    def mark_hint_used(self) -> None:
        self.stats.hints += 1
        self._help_used_in_stage = True

    def mark_solution_used(self) -> None:
        self.stats.solutions += 1
        self._help_used_in_stage = True

    def reset_current_stage(self) -> None:
        self._setup_stage(self.stage_id)

    def advance(self) -> Tuple[bool, str]:
        ok, reason = self.stage.validate(self.repo_path)
        if not ok:
            return False, reason

        self.stats.completed.append(self.stage_id)
        if should_repeat_stage(self._help_used_in_stage, self._stage_repeated):
            self._stage_repeated = True
            self._setup_stage(self.stage_id)
            return True, "힌트/해답 사용으로 같은 스테이지를 1회 재도전합니다."

        self._stage_repeated = False
        if self.stage_id >= len(STAGES):
            return True, "모든 스테이지 완료"

        next_stage = self.stage_id + 1
        self._setup_stage(next_stage)
        return True, f"스테이지 {next_stage} 시작"

    def status(self) -> str:
        ok, reason = self.stage.validate(self.repo_path)
        state = "완료 조건 충족" if ok else "진행 중"
        return f"[Stage {self.stage.stage_id}] {self.stage.title} - {state} ({reason})"

    def run_command(self, command: str) -> str:
        self.stats.commands += 1
        if not is_command_allowed(command):
            return "허용되지 않은 명령어입니다. 단일 git/조회 명령만 사용하세요."

        proc = subprocess.run(
            command,
            cwd=self.repo_path,
            shell=True,
            executable="/bin/sh",
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return out.strip() or "(no output)"

    def build_session_summary(self, player: str) -> Dict[str, Any]:
        ended_at = datetime.now(timezone.utc)
        duration = (ended_at - self.started_at).total_seconds()
        completed_unique = sorted(set(self.stats.completed))
        completed_count = len(completed_unique)
        score = max(
            0,
            int(
                (completed_count * 120)
                + max(0, 250 - (self.stats.commands * 2))
                + max(0, 300 - int(duration))
                - (self.stats.hints * 5)
                - (self.stats.solutions * 10)
            ),
        )
        return {
            "session_id": self.session_id,
            "player": player,
            "started_at": self.started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "duration_seconds": round(duration, 2),
            "commands": self.stats.commands,
            "hints": self.stats.hints,
            "solutions": self.stats.solutions,
            "completed_stage_ids": completed_unique,
            "completed_stage_count": completed_count,
            "total_stage_count": len(STAGES),
            "score": score,
        }
