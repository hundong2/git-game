"""Environment diagnostics for Git trainer."""

from __future__ import annotations

from dataclasses import dataclass
import platform
import shutil
import subprocess
import tempfile
from typing import List, Optional


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    details: str
    fix: Optional[str] = None


def parse_git_version(raw: str) -> Optional[tuple[int, int, int]]:
    parts = raw.strip().replace("git version", "").strip().split(".")
    nums: List[int] = []
    for token in parts:
        token = "".join(ch for ch in token if ch.isdigit())
        if not token:
            break
        nums.append(int(token))
        if len(nums) == 3:
            break
    if len(nums) < 2:
        return None
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)  # type: ignore[return-value]


def run_doctor() -> List[CheckResult]:
    results: List[CheckResult] = []

    git_path = shutil.which("git")
    if not git_path:
        results.append(
            CheckResult(
                name="git binary",
                ok=False,
                details="git 명령어를 찾지 못했습니다.",
                fix="Git을 설치한 뒤 PATH에 추가하세요.",
            )
        )
        return results

    results.append(CheckResult(name="git binary", ok=True, details=f"found at {git_path}"))

    ver_proc = subprocess.run(["git", "--version"], capture_output=True, text=True, check=False)
    version_raw = (ver_proc.stdout or ver_proc.stderr or "").strip()
    version = parse_git_version(version_raw)
    if ver_proc.returncode == 0 and version:
        min_version = (2, 30, 0)
        if version >= min_version:
            results.append(CheckResult(name="git version", ok=True, details=version_raw))
        else:
            results.append(
                CheckResult(
                    name="git version",
                    ok=False,
                    details=f"{version_raw} (권장: >= {min_version[0]}.{min_version[1]})",
                    fix="Git을 최신 버전으로 업데이트하세요.",
                )
            )
    else:
        results.append(
            CheckResult(
                name="git version",
                ok=False,
                details="git 버전을 확인하지 못했습니다.",
                fix="git --version 명령이 정상 동작하는지 확인하세요.",
            )
        )

    for key in ("user.name", "user.email"):
        proc = subprocess.run(
            ["git", "config", "--global", "--get", key], capture_output=True, text=True, check=False
        )
        value = (proc.stdout or "").strip()
        if proc.returncode == 0 and value:
            results.append(CheckResult(name=f"global {key}", ok=True, details=value))
        else:
            results.append(
                CheckResult(
                    name=f"global {key}",
                    ok=False,
                    details="설정되지 않음",
                    fix=f"git config --global {key} \"<value>\"",
                )
            )

    try:
        with tempfile.TemporaryDirectory(prefix="git_trainer_doctor_"):
            pass
        results.append(CheckResult(name="temp dir writable", ok=True, details="ok"))
    except OSError as exc:
        results.append(
            CheckResult(
                name="temp dir writable",
                ok=False,
                details=str(exc),
                fix="TMPDIR 권한을 확인하거나 쓰기 가능한 위치를 지정하세요.",
            )
        )

    results.append(
        CheckResult(
            name="platform",
            ok=True,
            details=f"{platform.system()} {platform.release()} ({platform.machine()})",
        )
    )

    return results


def format_doctor_report(results: List[CheckResult]) -> str:
    lines = ["Git Trainer Doctor Report"]
    for item in results:
        marker = "OK" if item.ok else "FAIL"
        lines.append(f"- [{marker}] {item.name}: {item.details}")
        if item.fix and not item.ok:
            lines.append(f"  fix: {item.fix}")
    fails = sum(1 for x in results if not x.ok)
    lines.append(f"Summary: {len(results) - fails} passed, {fails} failed")
    return "\n".join(lines)

