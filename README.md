# Git Learning Game

CLI 환경에 익숙하지 않은 사용자들이 Git의 핵심 명령어와 협업 워크플로우를 쉽고 재미있게 배울 수 있도록 설계된 인터랙티브 웹 게임입니다.

## ✨ 주요 기능 (Features)

- **실시간 인터랙티브 터미널**: 웹 브라우저에서 직접 Git 명령어를 입력하고 결과를 즉시 확인할 수 있습니다.
- **동적 Git 상태 대시보드**: 화면 상단에서 `git status`, `git log`, `git branch`의 결과를 실시간으로 시각화하여 현재 상태를 쉽게 파악할 수 있습니다.
- **격리된 학습 환경**: 각 사용자 세션마다 독립된 로컬 및 원격 저장소가 제공되어, 다른 사용자에게 영향을 주지 않고 마음껏 실험할 수 있습니다.
- **단계별 학습 시스템 (Staging System)**: `commit`, `push`와 같은 기본 명령어부터 시작하여 점진적으로 학습할 수 있는 스테이지를 제공합니다.
- **랭킹 시스템**: 모든 스테이지를 클리어하는 데 걸린 시간을 측정하여 순위를 기록하고 조회할 수 있습니다.
- **도움말 기능**: `help` 명령어를 통해 각 스테이지의 목표를 해결하기 위한 힌트를 얻을 수 있습니다.

## 🛠️ 기술 스택 (Tech Stack)

- **Backend**: Python, FastAPI
- **Real-time Communication**: python-socketio
- **Frontend**: HTML, CSS, JavaScript, xterm.js
- **Containerization**: Docker

## 🚀 시작하기 (Getting Started)

이 프로젝트를 실행하는 방법에는 두 가지가 있습니다: **로컬 환경에서 직접 실행**하거나 **Docker를 사용**하는 방법입니다.

### 1. 로컬 환경에서 직접 실행

```bash
# 1. 이 저장소를 클론합니다.
git clone https://github.com/your-username/git-game.git
cd git-game

# 2. (권장) 가상 환경을 생성하고 활성화합니다.
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 3. 필요한 패키지를 설치합니다.
pip install -r requirements.txt

# 4. Uvicorn 서버를 실행합니다.
# --reload 옵션은 코드 변경 시 서버를 자동으로 재시작해줍니다.
uvicorn app.main:app --reload
```

### 2. Docker를 사용하여 실행

Docker가 설치되어 있어야 합니다.

```bash
# 1. 이 저장소를 클론합니다.
git clone https://github.com/your-username/git-game.git
cd git-game

# 2. Docker 이미지를 빌드합니다.
docker build -t git-game .

# 3. 빌드된 이미지를 사용하여 컨테이너를 실행합니다.
docker run -p 8000:8000 git-game
```

두 방법 모두 성공적으로 실행했다면, 웹 브라우저에서 `http://localhost:8000` 주소로 접속하여 게임을 시작할 수 있습니다.

## 🎮 게임 방법 (How to Play)

- **UI**:
  - **상단 패널**: 현재 Git 저장소의 상태(`status`, `log`, `branch`)를 보여주는 대시보드입니다.
  - **하단 패널**: 명령어를 입력하는 터미널입니다.
- **기본 명령어**:
  - `help`: 현재 스테이지에 대한 힌트를 봅니다.
  - `name <your_name>`: 랭킹에 표시될 사용자 이름을 설정합니다.
  - `ranking`: 게임 클리어 시간 순위를 확인합니다.

## 🏗️ 개발 절차 (Development Process)

1.  **프로젝트 기획 및 설정**: FastAPI와 Socket.IO를 기반으로 프로젝트 구조를 설계하고, Dockerfile 및 기본 의존성을 설정했습니다.
2.  **핵심 기능 구현**: 실시간 터미널과 Git 상태 대시보드를 갖춘 기본 UI/UX를 구현하고, 사용자의 명령어를 격리된 환경에서 안전하게 실행하는 로직을 개발했습니다.
3.  **게임 시스템 추가**: 단계별 학습을 위한 스테이지 시스템과 `help` 명령어를 추가했습니다.
4.  **고급 기능 구현**: 게임의 재미와 동기 부여를 위해 랭킹 시스템을 도입하고, `rebase`와 같은 고급 시나리오를 위한 기반으로 원격 저장소 시뮬레이션 환경을 구축했습니다.
5.  **문서화**: 사용자가 프로젝트를 쉽게 이해하고 사용할 수 있도록 `README.md`를 작성했습니다.