import React from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const HomeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 80px);
  padding: ${props => props.theme.spacing.xxl};
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
`;

const Title = styled(motion.h1)`
  font-size: 3rem;
  margin-bottom: ${props => props.theme.spacing.lg};
  text-align: center;
  background: linear-gradient(45deg, #00d2ff, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const Subtitle = styled(motion.p)`
  font-size: 1.2rem;
  margin-bottom: ${props => props.theme.spacing.xxl};
  text-align: center;
  color: ${props => props.theme.colors.textSecondary};
  max-width: 600px;
`;

const StartButton = styled(motion.button)`
  background: linear-gradient(45deg, #00d2ff, #0069da);
  border: none;
  color: white;
  font-size: 1.2rem;
  font-weight: bold;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xxl};
  border-radius: 8px;
  cursor: pointer;
  font-family: ${props => props.theme.fonts.mono};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 210, 255, 0.3);
  }
`;

const FeatureGrid = styled(motion.div)`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${props => props.theme.spacing.xl};
  margin-top: ${props => props.theme.spacing.xxl};
  max-width: 1000px;
`;

const FeatureCard = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
`;

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  
  const handleStartGame = () => {
    navigate('/game');
  };
  
  return (
    <HomeContainer>
      <Title
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        🎮 Git Learning Game
      </Title>
      
      <Subtitle
        initial={{ y: -30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        Interactive Git command mastery through progressive challenges.
        Learn from basic to expert level with real-time visualization!
      </Subtitle>
      
      <StartButton
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleStartGame}
      >
        🚀 Start Learning Git!
      </StartButton>
      
      <FeatureGrid
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <FeatureCard whileHover={{ scale: 1.02 }}>
          <h3>🎯 50 Progressive Stages</h3>
          <p>From basic commits to advanced rebasing and conflict resolution</p>
        </FeatureCard>
        
        <FeatureCard whileHover={{ scale: 1.02 }}>
          <h3>🌳 Visual Git Graph</h3>
          <p>Real-time branch visualization to understand your actions</p>
        </FeatureCard>
        
        <FeatureCard whileHover={{ scale: 1.02 }}>
          <h3>👥 Team Simulation</h3>
          <p>Experience realistic collaboration scenarios</p>
        </FeatureCard>
        
        <FeatureCard whileHover={{ scale: 1.02 }}>
          <h3>🏆 Leaderboards</h3>
          <p>Compete with others and track your progress</p>
        </FeatureCard>
      </FeatureGrid>
    </HomeContainer>
  );
};

export default HomePage;
