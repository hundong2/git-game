// Game-related types

export interface Commit {
  hash: string;
  short_hash: string;
  message: string;
  author: string;
  date: string;
  parents: string[];
}

export interface Branch {
  name: string;
  is_current: boolean;
  commit: string;
}

export interface GitStatus {
  modified: string[];
  staged: string[];
  untracked: string[];
}

export interface GitState {
  branches: Branch[];
  commits: Commit[];
  status: GitStatus;
  current_branch: string;
  stage: number;
  total_stages: number;
  session_id: string;
}

export interface Stage {
  stage_id: number;
  title: string;
  description: string;
  difficulty: 'basic' | 'intermediate' | 'advanced';
  objectives: string[];
  hint?: string;
}

export interface StageHelp {
  stage: Stage;
  detailed_help: {
    commands: string[];
    explanation: string;
  };
  general_tips: string[];
}

export interface GameSession {
  session_id: string;
  current_stage: number;
  git_state: GitState;
  message: string;
}

export interface CommandRequest {
  command: string;
  session_id: string;
}

export interface CommandResponse {
  output: string;
  git_state: GitState;
  stage_completed: boolean;
  next_stage?: number;
  error?: string;
  command_count?: number;
}

export interface User {
  id?: number;
  username: string;
  email: string;
  created_at?: string;
  total_stages_completed: number;
  current_stage: number;
  total_play_time: number;
  best_completion_time?: number;
}

export interface UserCreate {
  username: string;
  email: string;
}

export interface LeaderboardEntry {
  username: string;
  user_id?: number;
  total_completion_time: number;
  stages_completed: number;
  total_commands: number;
  average_stage_time: number;
  rank: number;
  score: number;
  perfect_stages: number;
  speedrun_achievements: number;
  achieved_at: string;
}

export interface Achievement {
  id: number;
  user_id?: number;
  session_id?: string;
  achievement_type: string;
  achievement_name: string;
  description: string;
  stage_id?: number;
  earned_at: string;
  achievement_data: Record<string, any>;
}

export interface TeammateAction {
  type: 'teammate_commit' | 'teammate_push' | 'teammate_merge' | 'teammate_rebase';
  teammate: string;
  action: string;
  timestamp?: number;
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  session_id?: string;
  timestamp?: number;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Game Statistics
export interface GameStats {
  total_sessions: number;
  total_commands: number;
  average_completion_time: number;
  most_difficult_stage: number;
  popular_commands: string[];
  success_rate: number;
}

export interface StageStats {
  stage_id: number;
  completion_rate: number;
  average_time: number;
  average_commands: number;
  common_mistakes: string[];
  success_strategies: string[];
}

// UI State types
export interface UIState {
  theme: 'dark' | 'light';
  fontSize: 'small' | 'medium' | 'large';
  showAnimations: boolean;
  soundEnabled: boolean;
  showHints: boolean;
}

export interface GameConfig {
  autoSave: boolean;
  showTeammateActivity: boolean;
  difficultyLevel: 'beginner' | 'intermediate' | 'expert';
  enableTimers: boolean;
  showDetailedFeedback: boolean;
}

// Error types
export interface GameError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';
export type GamePhase = 'menu' | 'playing' | 'completed' | 'paused';
export type StageResult = 'success' | 'failed' | 'skipped' | 'in-progress';
