"""Persistent storage for session logs and leaderboard."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List


def data_home() -> Path:
    base = os.getenv("GIT_TRAINER_HOME")
    if base:
        return Path(base).expanduser()
    return Path.cwd() / ".git-trainer"


def sessions_path() -> Path:
    return data_home() / "sessions.jsonl"


def ensure_data_dir() -> Path:
    root = data_home()
    root.mkdir(parents=True, exist_ok=True)
    return root


def append_session(record: Dict[str, Any]) -> Path:
    ensure_data_dir()
    path = sessions_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True))
        f.write("\n")
    return path


def load_sessions() -> List[Dict[str, Any]]:
    path = sessions_path()
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    rows = load_sessions()
    best_by_player: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        player = str(row.get("player") or "anonymous")
        current = best_by_player.get(player)
        if current is None or int(row.get("score", 0)) > int(current.get("score", 0)):
            best_by_player[player] = row
    top = sorted(best_by_player.values(), key=lambda x: int(x.get("score", 0)), reverse=True)
    return top[:limit]


def format_leaderboard(limit: int = 10) -> str:
    rows = leaderboard(limit=limit)
    if not rows:
        return "No leaderboard data yet."
    lines = ["Git Trainer Leaderboard"]
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"{idx}. {row.get('player', 'anonymous')} "
            f"score={row.get('score', 0)} "
            f"stages={row.get('completed_stage_count', 0)}/{row.get('total_stage_count', 0)} "
            f"commands={row.get('commands', 0)} "
            f"duration={row.get('duration_seconds', 0)}s"
        )
    return "\n".join(lines)
