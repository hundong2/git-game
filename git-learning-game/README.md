# 🎮 Git Learning Game

An interactive game to master Git commands from basic to expert level through hands-on practice with real Git repositories.

## ✨ Features

- 🎯 **50 Progressive Stages**: From basic commits to advanced history rewriting
- 🌳 **Real-time Git Visualization**: Interactive branch graphs with D3.js
- 👥 **Team Collaboration Simulation**: Practice with realistic teammate interactions
- 🏆 **Online Leaderboards**: Compete with others and track your progress
- 💻 **Terminal Interface**: Full-featured terminal with command history and autocomplete
- 💡 **Built-in Help System**: Hints, tips, and detailed explanations for each stage
- 🚀 **Docker Ready**: One-command deployment with docker-compose
- ⚡ **Real-time Updates**: WebSocket-powered live collaboration experience

## 🔧 포트 설정 방법

### 방법 1: 시작 스크립트 사용 (Docker)

```bash
# 기본 포트 (3001)
./start-game.sh

# 커스텀 포트
./start-game.sh [GAME_PORT] [API_PORT] [DB_PORT] [REDIS_PORT]
./start-game.sh 8080 8001 5433 6380
```

### 방법 2: 환경변수 사용

```bash
# 환경변수로 포트 지정
GAME_PORT=8080 GAME_API_PORT=8001 docker-compose up -d

# .env 파일에 설정
echo "GAME_PORT=8080" >> .env
echo "GAME_API_PORT=8001" >> .env
```

### 방법 3: docker-compose.yml 직접 수정

```yaml
services:
  nginx:
    ports:
      - "8080:80"  # 원하는 포트로 변경
  git-learning-game:
    ports:
      - "8001:8000"  # API 포트 변경
```

### 개발 모드 포트 설정

```bash
# 개발 서버 포트 지정
./run-dev.sh 8001 3001  # 백엔드:8001, 프론트엔드:3001

# 또는 환경변수로
export REACT_APP_API_URL=http://localhost:8001
PORT=3001 npm start
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python) - High-performance API framework
- SQLAlchemy + PostgreSQL - Robust data persistence
- GitPython - Real Git repository manipulation
- WebSocket - Real-time communication
- Redis - Caching and session management

**Frontend:**
- React 18 + TypeScript - Modern UI framework
- D3.js - Interactive Git graph visualization
- Xterm.js - Full-featured terminal emulator
- Styled Components - CSS-in-JS styling
- Framer Motion - Smooth animations
- Zustand - Lightweight state management

**DevOps:**
- Docker + Docker Compose - Containerized deployment
- Nginx - Reverse proxy and load balancing

## 🚀 Quick Start

### Option 0: Command Line Trainer (New)

```bash
cd git-learning-game

# 환경 점검
./git-trainer.sh doctor

# 스테이지 목록
./git-trainer.sh list

# 학습 시작
./git-trainer.sh play

# 리더보드
./git-trainer.sh leaderboard
```

내장 명령:
- `:hint` 힌트 보기 (해당 스테이지 1회 재도전 트리거)
- `:solution` 정답 보기 (해당 스테이지 1회 재도전 트리거)
- `:status` 현재 완료 조건 확인
- `:next` 완료 조건 충족 시 다음 스테이지 이동
- `:reset` 현재 스테이지 초기화
- `:doctor` 환경 점검
- `:leaderboard` 로컬 최고 점수 보기

CLI 학습앱 특징:
- 20개 실전형 스테이지 (기본/중급/고급 Git 명령 흐름)
- 힌트/해답 사용 시 동일 스테이지 1회 재도전 정책
- 세션 로그 자동 저장 (`./.git-trainer/sessions.jsonl`, `GIT_TRAINER_HOME`로 변경 가능)
- 스테이지 해설 가이드: `CLI_STAGE_GUIDE.md`

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/git-learning-game.git
cd git-learning-game

# 기본 포트로 시작 (http://localhost:3001)
./start-game.sh

# 또는 커스텀 포트로 시작
./start-game.sh 8080 8001  # 게임:8080, API:8001

# 또는 직접 docker-compose 사용
docker-compose up -d
```

### Option 2: Local Development

```bash
# 개발 모드 (기본: 백엔드:8000, 프론트엔드:3000)
./run-dev.sh

# 커스텀 포트로 개발 모드
./run-dev.sh 8001 3001  # 백엔드:8001, 프론트엔드:3001

# 또는 수동으로 설정
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 새 터미널에서
cd frontend && npm install
REACT_APP_API_URL=http://localhost:8000 PORT=3000 npm start
```

## 🎯 Game Progression

### 🟢 Basic Level (Stages 1-15)
Foundation skills that every developer needs:
- **Interactive Rebase**: Squashing, reordering, editing commits
- **Cherry-picking**: Selecting specific commits with conflict resolution
- **Advanced Stashing**: Named stashes, partial staging
- **Reset Modes**: Understanding --soft, --mixed, --hard
- **Merge Conflicts**: Complex multi-file conflict resolution

### 🟡 Intermediate Level (Stages 16-35)
Professional workflows and advanced techniques:
- **Rebase --onto**: Transplanting commit ranges
- **Reflog Recovery**: Finding and recovering lost work
- **Git Bisect**: Binary search debugging
- **Worktree Management**: Multiple working directories
- **Submodule Operations**: Managing external dependencies
- **Rerere**: Recorded resolution for repeated conflicts

### 🔴 Advanced Level (Stages 36-50)
Expert-level Git mastery:
- **History Rewriting**: git filter-repo, removing sensitive data
- **Object Replacement**: git replace for fixing history
- **Bundle Operations**: Sharing repositories offline
- **Custom Merge Strategies**: Advanced merge configurations
- **Git Hooks**: Automation and workflow enforcement
- **Notes System**: Metadata and annotations

## 🗺️ Game Features

### 🌳 Visual Git Graph
- Real-time branch visualization
- Interactive commit exploration
- Color-coded branch types
- Working directory status display

### 💻 Terminal Interface
- Full bash-like terminal experience
- Command history and autocomplete
- Git command validation
- Helpful error messages and suggestions

### 👥 Team Collaboration
- Simulated teammate activities
- Real-time notifications
- Realistic merge conflicts
- Multi-user workflow scenarios

### 🏆 Progress Tracking
- Individual stage timing
- Command efficiency metrics
- Achievement system
- Global leaderboards

## 📊 API Endpoints

```
POST   /api/session/start      - Start new game session
POST   /api/command            - Execute git command
GET    /api/stages/{id}        - Get stage information
GET    /api/stages             - List all stages
GET    /api/help/{stage_id}    - Get stage help
GET    /api/leaderboard        - Get rankings
WS     /ws/{session_id}        - WebSocket connection
```

## 🎮 Screenshots

*Coming soon - showing the game interface, git visualization, and terminal*

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Adding New Stages

1. Define stage in `backend/stages.py`
2. Add validator function
3. Create initial repository state
4. Add help documentation
5. Test thoroughly

### CLI Stage Contribution

1. Edit `cli_trainer/stages.py`
2. Add/adjust tests in `tests/test_cli_trainer.py`
3. Run `python3 -m pytest -q`
4. Verify local run: `./git-trainer.sh play`

## 🐛 Issues & Support

Please report bugs and feature requests on [GitHub Issues](https://github.com/your-repo/git-learning-game/issues).

## 📦 Deployment

### Production Docker Deployment

```bash
# Production environment
cp .env.example .env
# Edit .env with production values

docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `.env.example` for all available configuration options.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 💯 Credits

Built with ❤️ by developers who believe learning should be fun and interactive.

---

**Ready to master Git?** 🚀 [Start playing now!](http://localhost:80)
