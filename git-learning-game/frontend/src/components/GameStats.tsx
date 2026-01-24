import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { GitState } from '../types/game';
import { useGameStore, usePerformanceStats } from '../store/gameStore';

interface GameStatsProps {
  gameState: GitState | null;
  sessionId: string;
}

const Container = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  overflow-y: auto;
`;

const StatCard = styled(motion.div)`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 4px;
  padding: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const StatTitle = styled.div`
  color: ${props => props.theme.colors.primary};
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const StatValue = styled.div`
  color: ${props => props.theme.colors.text};
  font-size: 1.2rem;
  font-weight: bold;
`;

const ProgressBar = styled.div<{ progress: number }>`
  width: 100%;
  height: 8px;
  background: ${props => props.theme.colors.surface};
  border-radius: 4px;
  margin: ${props => props.theme.spacing.sm} 0;
  overflow: hidden;
  
  &::after {
    content: '';
    display: block;
    height: 100%;
    width: ${props => props.progress}%;
    background: linear-gradient(90deg, #00d2ff, #0069da);
    transition: width 0.3s ease;
  }
`;

const GameStats: React.FC<GameStatsProps> = ({ gameState, sessionId }) => {
  const { currentStage, totalStages } = useGameStore();
  const { commandCount, hintsUsed, playTime, efficiency } = usePerformanceStats();
  
  const progress = (currentStage / totalStages) * 100;
  const formattedPlayTime = Math.floor(playTime / 60) + ':' + (Math.floor(playTime) % 60).toString().padStart(2, '0');
  
  return (
    <Container>
      <StatCard
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <StatTitle>🎯 Progress</StatTitle>
        <StatValue>{currentStage} / {totalStages}</StatValue>
        <ProgressBar progress={progress} />
        <div style={{ fontSize: '0.7rem', color: '#8b949e' }}>
          {progress.toFixed(1)}% Complete
        </div>
      </StatCard>
      
      <StatCard
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <StatTitle>⏱️ Play Time</StatTitle>
        <StatValue>{formattedPlayTime}</StatValue>
      </StatCard>
      
      <StatCard
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <StatTitle>⌨️ Commands Used</StatTitle>
        <StatValue>{commandCount}</StatValue>
      </StatCard>
      
      <StatCard
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      >
        <StatTitle>💡 Hints Used</StatTitle>
        <StatValue>{hintsUsed}</StatValue>
      </StatCard>
      
      {gameState && (
        <StatCard
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <StatTitle>🌳 Current Branch</StatTitle>
          <StatValue style={{ fontSize: '0.9rem' }}>
            {gameState.current_branch || 'main'}
          </StatValue>
        </StatCard>
      )}
      
      <StatCard
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.5 }}
      >
        <StatTitle>🏅 Efficiency</StatTitle>
        <StatValue style={{ fontSize: '0.9rem' }}>
          {efficiency > 0 ? efficiency.toFixed(1) : '0'} cmd/stage
        </StatValue>
      </StatCard>
    </Container>
  );
};

export default GameStats;
