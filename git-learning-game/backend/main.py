from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio
from typing import List, Optional, Dict, Any
import uuid

from game_engine import GitGameEngine
from models import GameSession, User, LeaderboardEntry
from websocket_manager import WebSocketManager

app = FastAPI(title="Git Learning Game API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./git_game.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# WebSocket manager
manager = WebSocketManager()

# Pydantic models
class CommandRequest(BaseModel):
    command: str
    session_id: str

class CommandResponse(BaseModel):
    output: str
    git_state: Dict[str, Any]
    stage_completed: bool
    next_stage: Optional[int] = None
    error: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str

class GameStageInfo(BaseModel):
    stage_id: int
    title: str
    description: str
    difficulty: str
    objectives: List[str]
    hint: Optional[str] = None

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize game engines for each session
game_sessions: Dict[str, GitGameEngine] = {}

@app.on_event("startup")
async def startup_event():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("🎮 Git Learning Game API started!")

@app.get("/")
async def root():
    return {"message": "Git Learning Game API", "status": "running"}

@app.post("/api/session/start")
async def start_game_session(user: UserCreate, db: Session = Depends(get_db)):
    """Start a new game session"""
    session_id = str(uuid.uuid4())
    
    # Create new game engine instance
    game_engine = GitGameEngine(session_id)
    game_sessions[session_id] = game_engine
    
    # Initialize first stage
    initial_state = game_engine.get_current_state()
    
    return {
        "session_id": session_id,
        "current_stage": 1,
        "git_state": initial_state,
        "message": "게임이 시작되었습니다! 첫 번째 스테이지를 시작하세요."
    }

@app.post("/api/command", response_model=CommandResponse)
async def execute_command(request: CommandRequest, db: Session = Depends(get_db)):
    """Execute git command and return result"""
    if request.session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    game_engine = game_sessions[request.session_id]
    
    try:
        result = await game_engine.execute_command(request.command)
        
        # Broadcast updates to connected clients
        await manager.broadcast_to_session(
            request.session_id, 
            {
                "type": "command_executed",
                "command": request.command,
                "result": result
            }
        )
        
        return CommandResponse(
            output=result["output"],
            git_state=result["git_state"],
            stage_completed=result["stage_completed"],
            next_stage=result.get("next_stage")
        )
    
    except Exception as e:
        return CommandResponse(
            output="",
            git_state=game_engine.get_current_state(),
            stage_completed=False,
            error=str(e)
        )

@app.get("/api/stages/{stage_id}", response_model=GameStageInfo)
async def get_stage_info(stage_id: int):
    """Get information about a specific stage"""
    from stages import STAGES
    
    if stage_id < 1 or stage_id > len(STAGES):
        raise HTTPException(status_code=404, detail="Stage not found")
    
    stage = STAGES[stage_id - 1]
    return GameStageInfo(**stage)

@app.get("/api/stages")
async def get_all_stages():
    """Get list of all stages"""
    from stages import STAGES
    return {"stages": STAGES, "total_stages": len(STAGES)}

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    """Get leaderboard with top players"""
    # This would query the actual database
    # For now, return mock data
    return {
        "leaderboard": [
            {"username": "GitMaster", "total_time": 1234.56, "stages_completed": 50, "rank": 1},
            {"username": "CodeNinja", "total_time": 1456.78, "stages_completed": 48, "rank": 2},
            {"username": "RebaseKing", "total_time": 1567.89, "stages_completed": 45, "rank": 3},
        ]
    }

@app.get("/api/help/{stage_id}")
async def get_stage_help(stage_id: int):
    """Get help and hints for a specific stage"""
    from stages import get_stage_help
    help_info = get_stage_help(stage_id)
    return help_info

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message["type"] == "simulate_teammate":
                # Simulate teammate actions
                if session_id in game_sessions:
                    game_engine = game_sessions[session_id]
                    await game_engine.simulate_teammate_action()
                    
                    # Broadcast the update
                    await manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "teammate_action",
                            "git_state": game_engine.get_current_state()
                        }
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
