import json

from cli_trainer.doctor import parse_git_version
from cli_trainer.engine import GitTrainer, is_command_allowed, should_repeat_stage
from cli_trainer.stages import STAGES, get_stage_info
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


def test_stage_info_contains_cherry_pick_use_case():
    info = get_stage_info(1)
    assert "Cherry-pick" in info
    assert "주 사용 시점" in info


def test_stage_info_full_mode_contains_recommended_commands():
    info = get_stage_info(1, mode="full")
    assert "추천 커맨드:" in info
    assert "힌트:" in info
    assert "해법 예시:" in info


def test_stage_info_full_mode_renders_branch_ui_when_repo_available():
    trainer = GitTrainer(stage_id=1)
    try:
        info = get_stage_info(1, mode="full", repo_path=trainer.repo_path)
    finally:
        trainer.cleanup()

    assert "브랜치 맵 (CLI UI):" in info
    assert "현재 브랜치:" in info
    assert "최근 커밋 그래프" in info
    assert "git log --graph --decorate --oneline --all" in info


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
