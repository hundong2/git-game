"""Database models for the Git Learning Game"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

Base = declarative_base()

class User(Base):
    """User model for authentication and progress tracking"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Game progress
    total_stages_completed = Column(Integer, default=0)
    current_stage = Column(Integer, default=1)
    total_play_time = Column(Float, default=0.0)  # in seconds
    best_completion_time = Column(Float)  # best time for all stages
    
class GameSession(Base):
    """Individual game session tracking"""
    __tablename__ = "game_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    user_id = Column(Integer, nullable=True)  # Can be anonymous
    username = Column(String(50), nullable=True)
    
    # Session info
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime)
    current_stage = Column(Integer, default=1)
    stages_completed = Column(Integer, default=0)
    total_commands = Column(Integer, default=0)
    
    # Performance metrics
    session_duration = Column(Float)  # total session time in seconds
    average_stage_time = Column(Float)
    fastest_stage_time = Column(Float)
    slowest_stage_time = Column(Float)
    
    # Session state (JSON field for flexibility)
    session_data = Column(JSON)  # Store git state, progress, etc.
    
class StageCompletion(Base):
    """Track completion of individual stages"""
    __tablename__ = "stage_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    
    # Stage info
    stage_id = Column(Integer, nullable=False)
    stage_title = Column(String(200))
    difficulty = Column(String(20))  # basic, intermediate, advanced
    
    # Performance
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    completion_time = Column(Float)  # time to complete stage in seconds
    commands_used = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    
    # Success metrics
    attempts = Column(Integer, default=1)
    first_try_success = Column(Boolean, default=True)
    
class LeaderboardEntry(Base):
    """Leaderboard rankings for competitive aspect"""
    __tablename__ = "leaderboard"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=True)
    
    # Overall performance
    total_completion_time = Column(Float, nullable=False)  # total time for all 50 stages
    stages_completed = Column(Integer, nullable=False)
    total_commands = Column(Integer, nullable=False)
    average_stage_time = Column(Float)
    
    # Ranking metrics
    rank = Column(Integer)
    score = Column(Float)  # calculated score based on time, efficiency, etc.
    
    # Achievement tracking
    perfect_stages = Column(Integer, default=0)  # stages completed without hints
    speedrun_achievements = Column(Integer, default=0)  # stages under time limit
    
    # Timestamps
    achieved_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
class Achievement(Base):
    """Game achievements and badges"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(36), nullable=True)
    
    # Achievement details
    achievement_type = Column(String(50), nullable=False)  # "speedrun", "no_hints", "first_try", etc.
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text)
    stage_id = Column(Integer, nullable=True)  # specific to a stage, or null for global
    
    # Achievement data
    earned_at = Column(DateTime, default=func.now())
    achievement_data = Column(JSON)  # flexible data for achievement details
    
class GitCommand(Base):
    """Track all git commands executed for analytics"""
    __tablename__ = "git_commands"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    stage_id = Column(Integer, nullable=False)
    
    # Command details
    command = Column(Text, nullable=False)  # the actual git command
    command_type = Column(String(50))  # "git", "ls", "cat", etc.
    git_subcommand = Column(String(50))  # "commit", "rebase", "merge", etc.
    
    # Execution results
    executed_at = Column(DateTime, default=func.now())
    execution_time = Column(Float)  # command execution time in seconds
    success = Column(Boolean, default=True)
    output = Column(Text)  # command output
    error_message = Column(Text)  # error if any
    
    # Context
    git_state_before = Column(JSON)  # git repo state before command
    git_state_after = Column(JSON)   # git repo state after command

# Helper functions for database operations
def calculate_score(completion_time: float, stages_completed: int, total_commands: int, hints_used: int = 0) -> float:
    """Calculate player score based on performance metrics"""
    base_score = 1000.0
    
    # Time penalty (faster is better)
    time_factor = max(0.1, 1.0 - (completion_time / 3600.0))  # 1 hour baseline
    
    # Efficiency bonus (fewer commands is better)
    command_factor = max(0.1, 1.0 - (total_commands / 1000.0))  # 1000 commands baseline
    
    # Completion bonus
    completion_factor = stages_completed / 50.0
    
    # Hints penalty
    hints_penalty = max(0.0, 1.0 - (hints_used * 0.05))  # 5% penalty per hint
    
    score = base_score * time_factor * command_factor * completion_factor * hints_penalty
    return round(score, 2)

def get_achievement_criteria() -> Dict[str, Dict[str, Any]]:
    """Define achievement criteria"""
    return {
        "speed_demon": {
            "name": "Speed Demon", 
            "description": "Complete a stage in under 30 seconds",
            "condition": lambda stage_time: stage_time < 30.0
        },
        "git_ninja": {
            "name": "Git Ninja",
            "description": "Complete 10 stages without using hints",
            "condition": "custom"  # Requires custom logic
        },
        "rebase_master": {
            "name": "Rebase Master", 
            "description": "Complete all rebase-related stages perfectly",
            "condition": "custom"
        },
        "conflict_resolver": {
            "name": "Conflict Resolver",
            "description": "Resolve 5 merge conflicts successfully", 
            "condition": "custom"
        },
        "perfectionist": {
            "name": "Perfectionist",
            "description": "Complete all 50 stages with perfect scores",
            "condition": "custom"
        }
    }
