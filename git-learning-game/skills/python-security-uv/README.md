# python-security-uv 사용 가이드

이 문서는 `python-security-uv` 스킬의 설치, 사용, 삭제/재설치 방법과 동작 원리를 설명합니다.

## 설치

1) Codex 홈 디렉터리에서 스킬을 설치합니다.
   - 예: `~/.codex/skills/python-security-uv/`
2) 설치 후 Codex 세션에서 해당 스킬이 "Available skills"에 표시되는지 확인합니다.

### 설치 예시(로컬 경로 복사)

```sh
mkdir -p ~/.codex/skills
cp -R /Users/donghun2/workspace/git-game/git-learning-game/skills/python-security-uv \
  ~/.codex/skills/python-security-uv
```

### 설치 예시(Windows PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse -Force `
  "C:\path\to\python-security-uv" `
  "$env:USERPROFILE\.codex\skills\python-security-uv"
```

### 설치 예시(리포지토리 클론)

```sh
mkdir -p ~/.codex/skills
git clone https://github.com/hundong2/git-game.git /tmp/git-game
cp -R /tmp/git-game/skills/python-security-uv ~/.codex/skills/python-security-uv
rm -rf /tmp/git-game
```

## 사용 방법

- 프롬프트에서 스킬 이름을 명시하면 적용됩니다.
  - 예: `python-security-uv help`
  - 예: `$python-security-uv 테스트 실행 방법 알려줘`
- 스킬은 UV 환경에서의 파이썬 실행 규칙, .env 기반의 비밀키 처리, 보안 모범 사례를 안내합니다.
- 실제 코드 실행은 `uv run <module>` 및 관련 `uv` 태스크 사용을 우선합니다.

## 삭제 방법

1) Codex 홈 디렉터리의 스킬 폴더를 삭제합니다.
   - 예: `rm -rf ~/.codex/skills/python-security-uv`
2) Codex 세션을 다시 시작해 스킬 목록에서 제거되었는지 확인합니다.

### 삭제 예시(skill-installer 사용 후 정리)

`skill-installer`는 설치 전용이므로 삭제는 수동으로 진행합니다.

```sh
rm -rf ~/.codex/skills/python-security-uv
```

삭제 후 Codex를 재시작해 스킬이 목록에서 제거되었는지 확인합니다.

### 삭제 예시(Windows PowerShell)

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\python-security-uv"
```

## 재설치 방법

1) 기존 설치가 남아 있다면 먼저 삭제합니다.
2) 스킬 저장소/경로에서 다시 설치합니다.
3) Codex 세션을 재시작하여 스킬이 다시 로드되는지 확인합니다.

### 재설치 예시(skill-installer 사용)

```sh
rm -rf ~/.codex/skills/python-security-uv
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo hundong2/git-game \
  --path skills/python-security-uv
```

재설치 후 Codex를 재시작해 스킬이 목록에 다시 표시되는지 확인합니다.

### 재설치 예시(Windows PowerShell)

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\python-security-uv"
python "$env:USERPROFILE\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo hundong2/git-game `
  --path skills/python-security-uv
```

## skill-installer로 설치하는 방법

Codex에 내장된 `skill-installer` 스킬 스크립트를 사용할 수 있습니다. 네트워크 접근이 필요하며 설치 후 Codex를 재시작해야 합니다.

```sh
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo hundong2/git-game \
  --path skills/python-security-uv
```

## 동작 원리

- Codex는 세션 시작 시 스킬 디렉터리를 스캔하여 `SKILL.md`를 읽습니다.
- 사용자가 스킬 이름을 명시하거나 작업이 스킬 설명과 일치하면 스킬 지침을 적용합니다.
- 스킬 문서의 지침은 우선순위가 높아, 해당 작업 범위에서는 기본 행동을 덮어씁니다.
- `SKILL.md`에 추가 참조 파일(templates, scripts 등)이 있으면 필요할 때만 읽습니다.

## 참고

- 보안 민감 정보는 반드시 `.env`에만 저장하고 커밋하지 않습니다.
- UV 실행 규칙을 따라 `uv run` 및 `uv` 태스크를 사용합니다.
