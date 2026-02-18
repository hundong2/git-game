# git-game

메인 프로젝트는 `git-learning-game/` 디렉터리에 있습니다.

이 문서는 "설치 방법"과 "실행 방법"을 빠르게 따라할 수 있도록 정리한 안내서입니다.

## 1) 사전 준비

필수 도구:
- `git`
- `python3` (권장 3.11+)
- `pip`
- `node` / `npm` (웹 UI 실행 시)
- `docker` / `docker compose` (Docker 실행 시)
- `make` (권장, 없어도 실행 가능)

버전 확인:

```bash
git --version
python3 --version
pip --version
node --version
npm --version
docker --version
docker compose version
make --version
```

## 2) 프로젝트 준비

```bash
git clone <YOUR_REPO_URL>
cd git-game
```

이 저장소 루트에는 `Makefile`이 있고, 실제 앱 코드는 `git-learning-game/` 아래에 있습니다.

## 3) CLI 학습앱 설치/실행 (가장 빠른 시작)

### 방법 A. Make 사용 (추천)

루트(`git-game/`)에서 실행:

```bash
# 환경 점검
make doctor

# 스테이지 목록
make list

# 플레이 시작 (플레이어명/시작 스테이지 지정 가능)
make play PLAYER=your_name STAGE=1

# 리더보드
make leaderboard LIMIT=10

# 사용 가능한 명령 확인
make help
```

### 방법 B. 스크립트 직접 실행

```bash
cd git-learning-game

# 1) 환경 점검
./git-trainer.sh doctor

# 2) 스테이지 목록 확인
./git-trainer.sh list

# 3) 학습 시작
./git-trainer.sh play --player your_name --start-stage 1

# 4) 점수 확인
./git-trainer.sh leaderboard --limit 10
```

플레이 중 내장 명령:
- `:status` 현재 스테이지 완료 조건 확인
- `:hint` 힌트 보기 (같은 스테이지 1회 재도전 트리거)
- `:solution` 해답 보기 (같은 스테이지 1회 재도전 트리거)
- `:next` 다음 스테이지 이동
- `:reset` 현재 스테이지 초기화
- `:leaderboard` 리더보드 보기
- `:quit` 종료

## 4) 웹 버전 설치/실행

웹 버전은 `backend`(FastAPI) + `frontend`(React)로 동작합니다.

### 방법 A. Docker로 실행 (권장)

```bash
cd git-learning-game

# 기본 포트: 게임 UI 3001, API 8000(컨테이너 내부 설정에 따라 reverse proxy로 접근)
./start-game.sh
```

실행 후 접속:
- `http://localhost:3001`

종료:

```bash
cd git-learning-game
docker compose down
```

### 방법 B. 로컬 개발 모드

```bash
cd git-learning-game
./run-dev.sh
```

기본 포트:
- 프론트엔드: `http://localhost:3000`
- 백엔드 API: `http://localhost:8000`

커스텀 포트:

```bash
cd git-learning-game
./run-dev.sh 8001 3001
```

### 방법 C. 수동 실행 (백엔드/프론트 분리)

백엔드:

```bash
cd git-learning-game/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

프론트엔드(새 터미널):

```bash
cd git-learning-game/frontend
npm install
REACT_APP_API_URL=http://localhost:8000 PORT=3000 npm start
```

## 5) 테스트 실행

CLI 트레이너 테스트:

```bash
cd git-learning-game
python3 -m pytest -q
```

## 6) 자주 발생하는 문제

- `make: command not found`
  - `make` 설치 후 재시도하거나, `./git-trainer.sh ...`로 직접 실행하세요.
- `Permission denied: ./git-trainer.sh`
  - `chmod +x git-learning-game/git-trainer.sh` 실행 후 재시도하세요.
- `npm install` 또는 `npm start` 실패
  - Node 버전을 확인하고(`node --version`), `git-learning-game/frontend`에서 다시 실행하세요.
- Docker 포트 충돌
  - `./start-game.sh 8080 8001 5433 6380`처럼 포트를 변경해서 실행하세요.

## 7) 추가 문서

- 상세 기능/아키텍처: `git-learning-game/README.md`
- CLI 스테이지 가이드: `git-learning-game/CLI_STAGE_GUIDE.md`
