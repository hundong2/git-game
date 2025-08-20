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

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/git-learning-game.git
cd git-learning-game

# Start all services
docker-compose up -d

# Visit http://localhost:80
```

### Option 2: Local Development

```bash
# Backend setup
cd backend
pip install -r requirements.txt
cp ../.env.example .env
uvicorn main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm start
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
