import { useState, useCallback } from 'react';
import axios from 'axios';

// Types
import { GameSession, CommandRequest, CommandResponse, UserCreate } from '../types/game';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

interface UseGameSessionReturn {
  session: GameSession | null;
  isLoading: boolean;
  error: string | null;
  startSession: (user: UserCreate) => Promise<GameSession | null>;
  executeCommand: (request: CommandRequest) => Promise<CommandResponse | null>;
  getStageInfo: (stageId: number) => Promise<any>;
  getStageHelp: (stageId: number) => Promise<any>;
}

export const useGameSession = (): UseGameSessionReturn => {
  const [session, setSession] = useState<GameSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const startSession = useCallback(async (user: UserCreate): Promise<GameSession | null> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/session/start`, user);
      const newSession = response.data as GameSession;
      setSession(newSession);
      return newSession;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '게임 세션 시작에 실패했습니다';
      setError(errorMessage);
      console.error('Failed to start game session:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  const executeCommand = useCallback(async (request: CommandRequest): Promise<CommandResponse | null> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/command`, request);
      const result = response.data as CommandResponse;
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '명령 실행에 실패했습니다';
      setError(errorMessage);
      console.error('Failed to execute command:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  const getStageInfo = useCallback(async (stageId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/stages/${stageId}`);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '스테이지 정보를 가져오는데 실패했습니다';
      setError(errorMessage);
      console.error('Failed to get stage info:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  const getStageHelp = useCallback(async (stageId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/help/${stageId}`);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '도움말을 가져오는데 실패했습니다';
      setError(errorMessage);
      console.error('Failed to get stage help:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);
  
  return {
    session,
    isLoading,
    error,
    startSession,
    executeCommand,
    getStageInfo,
    getStageHelp
  };
};
