import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Types
import { GitState, GameSession, Stage, User } from '../types/game';

interface GameStore {
  // Game State
  gameState: GitState | null;
  currentStage: number;
  totalStages: number;
  sessionId: string | null;
  isConnected: boolean;
  
  // User State
  user: User | null;
  isAuthenticated: boolean;
  
  // UI State
  isLoading: boolean;
  showHelp: boolean;
  showLeaderboard: boolean;
  
  // Performance Tracking
  startTime: Date | null;
  commandCount: number;
  hintsUsed: number;
  completedStages: number[];
  
  // Actions
  setGameState: (state: GitState | null) => void;
  setCurrentStage: (stage: number) => void;
  setSessionId: (id: string | null) => void;
  setConnected: (connected: boolean) => void;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setShowHelp: (show: boolean) => void;
  setShowLeaderboard: (show: boolean) => void;
  
  // Game Actions
  incrementCommandCount: () => void;
  incrementHints: () => void;
  completeStage: (stageId: number) => void;
  resetGame: () => void;
  startTimer: () => void;
  getPlayTime: () => number;
}

export const useGameStore = create<GameStore>()((
  devtools(
    (set, get) => ({
      // Initial State
      gameState: null,
      currentStage: 1,
      totalStages: 50,
      sessionId: null,
      isConnected: false,
      
      user: null,
      isAuthenticated: false,
      
      isLoading: false,
      showHelp: false,
      showLeaderboard: false,
      
      startTime: null,
      commandCount: 0,
      hintsUsed: 0,
      completedStages: [],
      
      // Actions
      setGameState: (state) => set({ gameState: state }),
      
      setCurrentStage: (stage) => set({ currentStage: stage }),
      
      setSessionId: (id) => set({ sessionId: id }),
      
      setConnected: (connected) => set({ isConnected: connected }),
      
      setUser: (user) => set({ 
        user, 
        isAuthenticated: user !== null 
      }),
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      setShowHelp: (show) => set({ showHelp: show }),
      
      setShowLeaderboard: (show) => set({ showLeaderboard: show }),
      
      // Game Actions
      incrementCommandCount: () => set((state) => ({ 
        commandCount: state.commandCount + 1 
      })),
      
      incrementHints: () => set((state) => ({ 
        hintsUsed: state.hintsUsed + 1 
      })),
      
      completeStage: (stageId) => set((state) => {
        if (!state.completedStages.includes(stageId)) {
          return {
            completedStages: [...state.completedStages, stageId]
          };
        }
        return state;
      }),
      
      resetGame: () => set({
        gameState: null,
        currentStage: 1,
        sessionId: null,
        isConnected: false,
        startTime: null,
        commandCount: 0,
        hintsUsed: 0,
        completedStages: []
      }),
      
      startTimer: () => set({ startTime: new Date() }),
      
      getPlayTime: () => {
        const { startTime } = get();
        if (!startTime) return 0;
        return (new Date().getTime() - startTime.getTime()) / 1000;
      }
    }),
    {
      name: 'git-game-store'
    }
  )
));

// Selectors for computed values
export const useGameProgress = () => {
  const { currentStage, totalStages, completedStages } = useGameStore();
  return {
    progress: (completedStages.length / totalStages) * 100,
    currentStage,
    totalStages,
    completedCount: completedStages.length
  };
};

export const usePerformanceStats = () => {
  const { commandCount, hintsUsed, completedStages, getPlayTime } = useGameStore();
  const playTime = getPlayTime();
  
  return {
    commandCount,
    hintsUsed,
    playTime,
    efficiency: completedStages.length > 0 ? commandCount / completedStages.length : 0,
    averageTimePerStage: completedStages.length > 0 ? playTime / completedStages.length : 0
  };
};

export const useConnectionStatus = () => {
  const { isConnected, sessionId } = useGameStore();
  return {
    isConnected,
    hasSession: sessionId !== null,
    status: isConnected ? 'connected' : 'disconnected'
  };
};
