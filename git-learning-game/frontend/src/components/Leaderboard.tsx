import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const Container = styled.div`
  padding: ${props => props.theme.spacing.xxl};
  max-width: 1000px;
  margin: 0 auto;
  height: calc(100vh - 80px);
  overflow-y: auto;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.primary};
`;

const LeaderboardTable = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid ${props => props.theme.colors.border};
`;

const TableHeader = styled.div`
  display: grid;
  grid-template-columns: 60px 1fr 120px 120px 100px;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.backgroundSecondary};
  font-weight: bold;
  color: ${props => props.theme.colors.primary};
  font-size: 0.9rem;
`;

const TableRow = styled(motion.div)`
  display: grid;
  grid-template-columns: 60px 1fr 120px 120px 100px;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.border};
  
  &:hover {
    background: ${props => props.theme.colors.background};
  }
`;

const RankBadge = styled.div<{ rank: number }>`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  background: ${props => 
    props.rank === 1 ? '#ffd700' :
    props.rank === 2 ? '#c0c0c0' :
    props.rank === 3 ? '#cd7f32' :
    props.theme.colors.backgroundSecondary
  };
  color: ${props => props.rank <= 3 ? '#000' : props.theme.colors.text};
`;

const mockLeaderboard = [
  { username: 'GitMaster', totalTime: 1234.56, stagesCompleted: 50, rank: 1, score: 987.5 },
  { username: 'CodeNinja', totalTime: 1456.78, stagesCompleted: 48, rank: 2, score: 876.3 },
  { username: 'RebaseKing', totalTime: 1567.89, stagesCompleted: 45, rank: 3, score: 765.2 },
  { username: 'MergeQueen', totalTime: 1678.90, stagesCompleted: 42, rank: 4, score: 654.1 },
  { username: 'CommitGod', totalTime: 1789.01, stagesCompleted: 40, rank: 5, score: 543.0 },
];

const Leaderboard: React.FC = () => {
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}:${minutes.toString().padStart(2, '0')}`;
  };
  
  return (
    <Container>
      <Title>🏆 Leaderboard</Title>
      
      <LeaderboardTable
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <TableHeader>
          <div>Rank</div>
          <div>Player</div>
          <div>Total Time</div>
          <div>Stages</div>
          <div>Score</div>
        </TableHeader>
        
        {mockLeaderboard.map((entry, index) => (
          <TableRow
            key={entry.username}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <RankBadge rank={entry.rank}>#{entry.rank}</RankBadge>
            <div style={{ fontWeight: 'bold' }}>{entry.username}</div>
            <div>{formatTime(entry.totalTime)}</div>
            <div>{entry.stagesCompleted}/50</div>
            <div>{entry.score.toFixed(1)}</div>
          </TableRow>
        ))}
      </LeaderboardTable>
    </Container>
  );
};

export default Leaderboard;
