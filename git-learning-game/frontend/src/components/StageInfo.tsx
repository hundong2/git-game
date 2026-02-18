import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useGameSession } from '../hooks/useGameSession';
import { Stage, StageHelp } from '../types/game';

interface StageInfoProps {
  stageId: number;
  sessionId: string;
}

const Container = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  overflow-y: auto;
`;

const StageHeader = styled(motion.div)`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const StageTitle = styled.h2`
  color: ${props => props.theme.colors.primary};
  font-size: 1.1rem;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const DifficultyBadge = styled.span<{ difficulty: string }>`
  background: ${props => 
    props.difficulty === 'basic' ? props.theme.colors.success :
    props.difficulty === 'intermediate' ? props.theme.colors.warning :
    props.theme.colors.error
  };
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
  text-transform: uppercase;
`;

const Description = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
  margin: ${props => props.theme.spacing.sm} 0;
  line-height: 1.4;
`;

const ObjectivesList = styled.ul`
  list-style: none;
  padding: 0;
  margin: ${props => props.theme.spacing.md} 0;
`;

const ObjectiveItem = styled.li`
  color: ${props => props.theme.colors.text};
  font-size: 0.85rem;
  margin: ${props => props.theme.spacing.sm} 0;
  padding-left: ${props => props.theme.spacing.md};
  position: relative;
  
  &:before {
    content: '✓';
    color: ${props => props.theme.colors.success};
    font-weight: bold;
    position: absolute;
    left: 0;
  }
`;

const HelpButton = styled(motion.button)`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  color: ${props => props.theme.colors.primary};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: ${props => props.theme.fonts.mono};
  margin-top: ${props => props.theme.spacing.md};
  width: 100%;
  
  &:hover {
    background: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.background};
  }
`;

const HelpPanel = styled(motion.div)`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 4px;
  padding: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.md};
  font-size: 0.8rem;
`;

const HelpCommand = styled.code`
  background: ${props => props.theme.colors.surface};
  padding: 2px 4px;
  border-radius: 2px;
  color: ${props => props.theme.colors.primary};
  font-family: ${props => props.theme.fonts.mono};
  font-size: 0.75rem;
`;

const LoadingSpinner = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.textSecondary};
`;

const StageInfo: React.FC<StageInfoProps> = ({ stageId, sessionId }) => {
  const [stage, setStage] = useState<Stage | null>(null);
  const [help, setHelp] = useState<StageHelp | null>(null);
  const [showHelp, setShowHelp] = useState(false);
  const [solution, setSolution] = useState<string | null>(null);
  const [showSolution, setShowSolution] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const { getStageInfo, getStageHelp } = useGameSession();
  
  useEffect(() => {
    const loadStageInfo = async () => {
      setLoading(true);
      try {
        const stageData = await getStageInfo(stageId);
        if (stageData) {
          setStage(stageData);
        }
      } catch (error) {
        console.error('Failed to load stage info:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadStageInfo();
  }, [stageId, getStageInfo]);
  
  const handleGetHelp = async () => {
    if (showHelp) {
      setShowHelp(false);
      return;
    }
    
    if (!help) {
      try {
        const helpData = await getStageHelp(stageId, sessionId, 'hint');
        if (helpData) {
          setHelp(helpData);
        }
      } catch (error) {
        console.error('Failed to load stage help:', error);
      }
    }
    
    setShowHelp(true);
  };

  const handleGetSolution = async () => {
    if (showSolution) {
      setShowSolution(false);
      return;
    }

    if (!solution) {
      try {
        const helpData = await getStageHelp(stageId, sessionId, 'solution');
        if (helpData?.solution) {
          setSolution(helpData.solution);
        } else {
          setSolution('해답이 준비되지 않았습니다.');
        }
      } catch (error) {
        console.error('Failed to load solution:', error);
        setSolution('해답을 불러오지 못했습니다.');
      }
    }

    setShowSolution(true);
  };
  
  if (loading) {
    return (
      <Container>
        <LoadingSpinner
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          ⏳ Loading stage info...
        </LoadingSpinner>
      </Container>
    );
  }
  
  if (!stage) {
    return (
      <Container>
        <p>Stage information not available</p>
      </Container>
    );
  }
  
  return (
    <Container>
      <StageHeader
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <StageTitle>Stage {stage.stage_id}: {stage.title}</StageTitle>
          <DifficultyBadge difficulty={stage.difficulty}>
            {stage.difficulty}
          </DifficultyBadge>
        </div>
        
        <Description>{stage.description}</Description>
        
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ color: '#00d2ff', fontSize: '0.9rem', marginBottom: '8px' }}>
            🎯 Objectives:
          </h4>
          <ObjectivesList>
            {stage.objectives.map((objective, index) => (
              <ObjectiveItem key={index}>{objective}</ObjectiveItem>
            ))}
          </ObjectivesList>
        </div>
        
        {stage.hint && (
          <div style={{ 
            background: '#1f2937',
            border: '1px solid #374151',
            borderRadius: '4px',
            padding: '12px',
            marginTop: '12px',
            fontSize: '0.8rem'
          }}>
            <strong style={{ color: '#fbbf24' }}>💡 Quick Hint:</strong>
            <br />
            {stage.hint}
          </div>
        )}
        
        <HelpButton
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleGetHelp}
        >
          {showHelp ? '🙈 Hide Detailed Help' : '🆘 Get Detailed Help'}
        </HelpButton>

        <HelpButton
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleGetSolution}
          style={{ marginTop: '8px' }}
        >
          {showSolution ? '🙈 Hide Solution' : '🧩 View Solution'}
        </HelpButton>
        
        {showHelp && help && (
          <HelpPanel
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <h4 style={{ color: '#00d2ff', marginBottom: '8px' }}>📚 Detailed Help:</h4>
            
            {help.detailed_help?.explanation && (
              <p style={{ marginBottom: '12px', lineHeight: 1.4 }}>
                {help.detailed_help.explanation}
              </p>
            )}
            
            {help.detailed_help?.commands && (
              <div>
                <strong>Suggested Commands:</strong>
                <div style={{ marginTop: '8px' }}>
                  {help.detailed_help.commands.map((cmd, index) => (
                    <div key={index} style={{ margin: '4px 0' }}>
                      <HelpCommand>{cmd}</HelpCommand>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {help.general_tips && (
              <div style={{ marginTop: '12px', borderTop: '1px solid #374151', paddingTop: '8px' }}>
                <strong>General Tips:</strong>
                <ul style={{ marginTop: '4px', paddingLeft: '16px' }}>
                  {help.general_tips.map((tip, index) => (
                    <li key={index} style={{ margin: '2px 0', fontSize: '0.75rem' }}>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </HelpPanel>
        )}

        {showSolution && solution && (
          <HelpPanel
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <h4 style={{ color: '#f472b6', marginBottom: '8px' }}>🧩 Solution:</h4>
            <p style={{ marginBottom: '0', lineHeight: 1.4 }}>
              {solution}
            </p>
          </HelpPanel>
        )}
      </StageHeader>
    </Container>
  );
};

export default StageInfo;
