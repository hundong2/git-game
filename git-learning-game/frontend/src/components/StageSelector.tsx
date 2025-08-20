import React from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const Container = styled.div`
  padding: ${props => props.theme.spacing.xxl};
  max-width: 1200px;
  margin: 0 auto;
  height: calc(100vh - 80px);
  overflow-y: auto;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.primary};
`;

const StageGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const StageCard = styled(motion.div)<{ difficulty: string }>`
  background: ${props => props.theme.colors.surface};
  border: 2px solid ${props => 
    props.difficulty === 'basic' ? props.theme.colors.success :
    props.difficulty === 'intermediate' ? props.theme.colors.warning :
    props.theme.colors.error
  };
  border-radius: 8px;
  padding: ${props => props.theme.spacing.lg};
  cursor: pointer;
  
  &:hover {
    background: ${props => props.theme.colors.background};
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
`;

const StageNumber = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const StageTitle = styled.h3`
  margin-bottom: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.text};
`;

const StageDescription = styled.p`
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.md};
  line-height: 1.4;
`;

const DifficultyBadge = styled.span<{ difficulty: string }>`
  background: ${props => 
    props.difficulty === 'basic' ? props.theme.colors.success :
    props.difficulty === 'intermediate' ? props.theme.colors.warning :
    props.theme.colors.error
  };
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
  text-transform: uppercase;
`;

const mockStages = [
  { id: 1, title: 'Interactive Rebase', description: 'Learn to squash and reorder commits', difficulty: 'basic' },
  { id: 2, title: 'Cherry-pick Conflicts', description: 'Handle conflicts while cherry-picking', difficulty: 'basic' },
  { id: 3, title: 'Advanced Stashing', description: 'Master git stash with multiple stashes', difficulty: 'basic' },
  { id: 16, title: 'Rebase Onto', description: 'Transplant commits with rebase --onto', difficulty: 'intermediate' },
  { id: 17, title: 'Reflog Recovery', description: 'Recover lost commits using reflog', difficulty: 'intermediate' },
  { id: 36, title: 'History Rewriting', description: 'Remove sensitive data from history', difficulty: 'advanced' },
];

const StageSelector: React.FC = () => {
  const navigate = useNavigate();
  
  const handleStageSelect = (stageId: number) => {
    // In a real app, you'd set the starting stage and navigate to game
    navigate('/game');
  };
  
  return (
    <Container>
      <Title>📚 Stage Selection</Title>
      
      <StageGrid>
        {mockStages.map((stage, index) => (
          <StageCard
            key={stage.id}
            difficulty={stage.difficulty}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleStageSelect(stage.id)}
          >
            <StageNumber>Stage {stage.id}</StageNumber>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <StageTitle>{stage.title}</StageTitle>
              <DifficultyBadge difficulty={stage.difficulty}>
                {stage.difficulty}
              </DifficultyBadge>
            </div>
            <StageDescription>{stage.description}</StageDescription>
            
            <div style={{ 
              fontSize: '0.8rem',
              color: '#8b949e',
              borderTop: '1px solid #30363d',
              paddingTop: '8px',
              marginTop: '12px'
            }}>
              Click to start this stage
            </div>
          </StageCard>
        ))}
      </StageGrid>
    </Container>
  );
};

export default StageSelector;
