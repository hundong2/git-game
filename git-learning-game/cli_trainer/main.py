"""CLI entrypoint for Git trainer."""

from __future__ import annotations

import argparse
import os
import sys

from .doctor import format_doctor_report, run_doctor
from .engine import GitTrainer
from .storage import append_session, format_leaderboard
from .stages import STAGES


def _print_stage(stage_id: int) -> None:
    stage = STAGES[stage_id - 1]
    print(f"\n[Stage {stage.stage_id}] {stage.title}")
    print(f"- Objective: {stage.objective}")


def cmd_list() -> int:
    for stage in STAGES:
        print(f"{stage.stage_id}. {stage.title} - {stage.objective}")
    return 0


def cmd_doctor() -> int:
    print(format_doctor_report(run_doctor()))
    return 0


def cmd_leaderboard(limit: int) -> int:
    print(format_leaderboard(limit=limit))
    return 0


def cmd_play(start_stage: int, player: str) -> int:
    trainer = GitTrainer(stage_id=start_stage)
    print("Git Trainer CLI")
    print("내장 명령: :help :hint :solution :status :next :reset :repo :leaderboard :quit")
    _print_stage(trainer.stage_id)

    exit_code = 0
    try:
        while True:
            prompt = f"git-trainer(s{trainer.stage_id})> "
            line = input(prompt).strip()
            if not line:
                continue
            if line == ":quit":
                break
            if line == ":help":
                print("git 명령어를 입력하거나 내장 명령(:hint/:next 등)을 사용하세요.")
                continue
            if line == ":repo":
                print(trainer.repo_path)
                continue
            if line == ":leaderboard":
                print(format_leaderboard(limit=10))
                continue
            if line == ":status":
                print(trainer.status())
                continue
            if line == ":hint":
                trainer.mark_hint_used()
                print(trainer.stage.hint)
                continue
            if line == ":solution":
                trainer.mark_solution_used()
                print(trainer.stage.solution)
                continue
            if line == ":reset":
                trainer.reset_current_stage()
                print("스테이지 환경을 초기화했습니다.")
                _print_stage(trainer.stage_id)
                continue
            if line == ":next":
                ok, msg = trainer.advance()
                print(msg)
                if ok and msg == "모든 스테이지 완료":
                    print(
                        f"수고하셨습니다. commands={trainer.stats.commands}, "
                        f"hints={trainer.stats.hints}, solutions={trainer.stats.solutions}"
                    )
                    break
                _print_stage(trainer.stage_id)
                continue
            if line == ":doctor":
                print(format_doctor_report(run_doctor()))
                continue

            print(trainer.run_command(line))
            ok, msg = trainer.stage.validate(trainer.repo_path)
            if ok:
                print(f"[완료 조건 충족] {msg} (:next 로 이동)")
    except KeyboardInterrupt:
        print("\n종료합니다.")
        exit_code = 130
    finally:
        summary = trainer.build_session_summary(player=player)
        path = append_session(summary)
        print(
            "세션 저장 완료:",
            f"player={summary['player']}",
            f"score={summary['score']}",
            f"stages={summary['completed_stage_count']}/{summary['total_stage_count']}",
            f"log={path}",
        )
        trainer.cleanup()
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interactive Git command line trainer")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list stages")
    sub.add_parser("doctor", help="run environment checks")
    leaderboard = sub.add_parser("leaderboard", help="show top scores")
    leaderboard.add_argument("--limit", type=int, default=10, help="max rows")
    play = sub.add_parser("play", help="start interactive trainer")
    play.add_argument("--stage", type=int, default=1, help="stage number to start from")
    play.add_argument("--player", type=str, default=os.getenv("USER", "anonymous"), help="player name")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        return cmd_list()
    if args.command == "doctor":
        return cmd_doctor()
    if args.command == "leaderboard":
        return cmd_leaderboard(args.limit)
    if args.command == "play":
        if args.stage < 1 or args.stage > len(STAGES):
            print(f"Invalid stage: {args.stage}", file=sys.stderr)
            return 2
        return cmd_play(args.stage, args.player)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
