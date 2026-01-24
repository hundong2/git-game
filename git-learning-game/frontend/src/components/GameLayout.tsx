import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

// Components
import GitGraph from './GitGraph';
import Terminal from './Terminal';
import StageInfo from './StageInfo';
import GameStats from './GameStats';
import TeammateActivity from './TeammateActivity';

// Hooks
import { useGameSession } from '../hooks/useGameSession';
import { useWebSocket } from '../hooks/useWebSocket';

// Store
import { useGameStore } from '../store/gameStore';

// Types
import { GitState, GameSession } from '../types/game';

const GameContainer = styled.div`
  display: flex;
  height: calc(100vh - 80px); /* Subtract header height */
  width: 100%;
  overflow: hidden;
`;

const LeftPanel = styled(motion.div)`
  width: 300px;
  background: ${props => props.theme.colors.backgroundSecondary};
  border-right: 1px solid ${props => props.theme.colors.border};
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const MainArea = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const GitVisualization = styled(motion.div)`
  height: 50%;
  background: ${props => props.theme.colors.background};
  border-bottom: 2px solid ${props => props.theme.colors.border};
  position: relative;
  overflow: hidden;
`;

const TerminalArea = styled(motion.div)`
  height: 50%;
  background: ${props => props.theme.colors.surface};
  position: relative;
`;

const RightPanel = styled(motion.div)`
  width: 280px;
  background: ${props => props.theme.colors.backgroundSecondary};
  border-left: 1px solid ${props => props.theme.colors.border};
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const PanelHeader = styled.div`
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surface};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  font-weight: bold;
  color: ${props => props.theme.colors.primary};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const LoadingOverlay = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(13, 17, 23, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
  z-index: 1000;
`;

const LoadingText = styled.div`
  color: ${props => props.theme.colors.primary};
  font-size: 1.2rem;
  font-weight: bold;
`;

const Spinner = styled(motion.div)`
  width: 40px;
  height: 40px;
  border: 3px solid ${props => props.theme.colors.border};
  border-top: 3px solid ${props => props.theme.colors.primary};
  border-radius: 50%;
`;

const GameLayout: React.FC = () => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [sessionId, setSessionId] = useState<string>('');
  
  // Game store
  const { 
    gameState, 
    currentStage,
    setGameState,
    setCurrentStage,
    isConnected,
    setConnected 
  } = useGameStore();
  
  // Custom hooks
  const { 
    session, 
    startSession, 
    executeCommand,
    isLoading: sessionLoading 
  } = useGameSession();
  
  const { 
    connect, 
    disconnect, 
    sendMessage,
    lastMessage,
    connectionStatus 
  } = useWebSocket(sessionId);
  
  // Initialize game session on component mount
  useEffect(() => {
    const initializeGame = async () => {
      try {
        setIsLoading(true);
        
        // Start new game session
        const newSession = await startSession({
          username: 'Player', // TODO: Get from auth
          email: 'player@example.com'
        });
        
        if (newSession) {
          setSessionId(newSession.session_id);
          setGameState(newSession.git_state);
          setCurrentStage(newSession.current_stage);
          
          // Connect WebSocket
          connect();
          
          toast.success('🎮 게임이 시작되었습니다!');
        }
      } catch (error) {
        console.error('Failed to initialize game:', error);
        toast.error('게임 초기화에 실패했습니다.');
      } finally {
        setIsLoading(false);
      }
    };
    
    initializeGame();
    
    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, []);
  
  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const message = JSON.parse(lastMessage.data);
      
      switch (message.type) {
        case 'command_executed':
          // Update game state after command execution
          if (message.result?.git_state) {
            setGameState(message.result.git_state);
          }
          break;
          
        case 'teammate_action':
          // Handle teammate simulation
          if (message.git_state) {
            setGameState(message.git_state);
          }
          toast.success(`👥 ${message.data?.teammate}이(가) ${message.data?.action}을(를) 수행했습니다`);
          break;
          
        case 'stage_completed':
          toast.success(`🎆 스테이지 ${message.stage} 완료!`);
          if (message.next_stage) {
            setCurrentStage(message.next_stage);
          }
          break;
          
        default:
          console.log('Unknown message type:', message.type);
      }
    }
  }, [lastMessage]);
  
  // Handle command execution
  const handleCommandExecution = async (command: string) => {
    if (!sessionId) {
      toast.error('게임 세션이 없습니다.');
      return;
    }
    
    try {
      const result = await executeCommand({
        command,
        session_id: sessionId
      });
      
      if (result) {
        setGameState(result.git_state);
        
        if (result.stage_completed) {
          toast.success('🎉 스테이지 완료!');
          if (result.next_stage) {
            setCurrentStage(result.next_stage);
          }
        }
        
        if (result.error) {
          toast.error(`오류: ${result.error}`);
        }
      }
    } catch (error) {
      console.error('Command execution failed:', error);
      toast.error('명령 실행에 실패했습니다.');
    }
  };
  
  // Simulate teammate activity
  const handleTeammateSimulation = () => {
    if (connectionStatus === 'Open') {
      sendMessage({
        type: 'simulate_teammate',
        session_id: sessionId
      });
    }
  };
  
  if (isLoading || sessionLoading) {
    return (
      <LoadingOverlay
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <Spinner
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
        <LoadingText>게임을 초기화하고 있습니다...</LoadingText>
      </LoadingOverlay>
    );
  }
  
  return (
    <GameContainer>
      {/* Left Panel - Stage Info & Stats */}
      <LeftPanel
        initial={{ x: -300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <PanelHeader>
          📚 스테이지 정보
        </PanelHeader>
        <StageInfo 
          stageId={currentStage} 
          sessionId={sessionId}
        />
        
        <PanelHeader>
          📊 게임 통계
        </PanelHeader>
        <GameStats 
          gameState={gameState}
          sessionId={sessionId}
        />
      </LeftPanel>
      
      {/* Main Area - Git Visualization & Terminal */}
      <MainArea>
        <GitVisualization
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <PanelHeader>
            🌳 Git Repository 상태
            <div style={{ marginLeft: 'auto', fontSize: '0.8rem', color: '#8b949e' }}>
              연결 상태: {connectionStatus === 'Open' ? '🟢 연결됨' : '🔴 연결 안됨'}
            </div>
          </PanelHeader>
          <GitGraph 
            gitState={gameState}
            onNodeClick={(commit) => console.log('Clicked commit:', commit)}
          />
        </GitVisualization>
        
        <TerminalArea
          ref={terminalRef}
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <PanelHeader>
            💻 터미널
            <div style={{ marginLeft: 'auto', fontSize: '0.8rem' }}>
              git commands, ls, cat, etc.
            </div>
          </PanelHeader>
          <Terminal
            onCommandExecute={handleCommandExecution}
            gameState={gameState}
          />
        </TerminalArea>
      </MainArea>
      
      {/* Right Panel - Teammate Activity */}
      <RightPanel
        initial={{ x: 300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <PanelHeader>
          👥 팀원 활동
          <button
            onClick={handleTeammateSimulation}
            style={{
              marginLeft: 'auto',
              background: 'none',
              border: 'none',
              color: '#00d2ff',
              cursor: 'pointer',
              fontSize: '1.2rem'
            }}
            title="팀원 활동 시뮬레이션"
          >
            ▶️
          </button>
        </PanelHeader>
        <TeammateActivity 
          sessionId={sessionId}
          lastMessage={lastMessage}
        />
      </RightPanel>
    </GameContainer>
  );
};

export default GameLayout;
