import json

from cli_trainer.doctor import parse_git_version
from cli_trainer.engine import is_command_allowed, should_repeat_stage
from cli_trainer.stages import STAGES
from cli_trainer.storage import append_session, leaderboard


def test_parse_git_version_ok():
    assert parse_git_version("git version 2.43.1") == (2, 43, 1)
    assert parse_git_version("git version 2.39") == (2, 39, 0)


def test_parse_git_version_invalid():
    assert parse_git_version("unknown") is None


def test_command_filter():
    assert is_command_allowed("git status")
    assert is_command_allowed("ls -la")
    assert not is_command_allowed("python3 -c 'print(1)'")
    assert not is_command_allowed("git status && rm -rf /")
    assert not is_command_allowed("git status | cat")


def test_retry_policy():
    assert should_repeat_stage(help_used=True, already_repeated=False)
    assert not should_repeat_stage(help_used=False, already_repeated=False)
    assert not should_repeat_stage(help_used=True, already_repeated=True)


def test_stage_count():
    assert len(STAGES) >= 20


def test_leaderboard_best_score_per_player(tmp_path, monkeypatch):
    monkeypatch.setenv("GIT_TRAINER_HOME", str(tmp_path))
    append_session({"player": "alice", "score": 100, "completed_stage_count": 3, "total_stage_count": 20, "commands": 10, "duration_seconds": 50})
    append_session({"player": "alice", "score": 200, "completed_stage_count": 5, "total_stage_count": 20, "commands": 20, "duration_seconds": 80})
    append_session({"player": "bob", "score": 150, "completed_stage_count": 4, "total_stage_count": 20, "commands": 11, "duration_seconds": 60})

    rows = leaderboard(limit=10)
    assert rows[0]["player"] == "alice"
    assert rows[0]["score"] == 200
    assert rows[1]["player"] == "bob"

    raw = (tmp_path / "sessions.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(raw) == 3
    json.loads(raw[0])
