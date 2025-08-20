import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import styled, { createGlobalStyle, ThemeProvider } from 'styled-components';
import { motion } from 'framer-motion';

// Components
import GameLayout from './components/GameLayout';
import HomePage from './components/HomePage';
import Leaderboard from './components/Leaderboard';
import StageSelector from './components/StageSelector';

// Store
import { useGameStore } from './store/gameStore';

// Types
import { Theme } from './types/theme';

const queryClient = new QueryClient();

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    background: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    overflow: hidden;
  }

  #root {
    height: 100vh;
    width: 100vw;
  }

  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.backgroundSecondary};
  }

  ::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.primary};
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${props => props.theme.colors.primaryHover};
  }
`;

const theme: Theme = {
  colors: {
    primary: '#00d2ff',
    primaryHover: '#00b8e6',
    secondary: '#ff6b6b',
    background: '#0d1117',
    backgroundSecondary: '#161b22',
    surface: '#21262d',
    text: '#f0f6fc',
    textSecondary: '#8b949e',
    success: '#238636',
    warning: '#d1a500',
    error: '#da3633',
    border: '#30363d',
  },
  fonts: {
    mono: 'Monaco, Menlo, Ubuntu Mono, monospace',
    sans: 'system-ui, -apple-system, sans-serif',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
  }
};

const AppContainer = styled.div`
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
`;

const AppHeader = styled(motion.header)`
  background: ${props => props.theme.colors.surface};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: ${props => props.theme.spacing.md};
  display: flex;
  justify-content: between;
  align-items: center;
  z-index: 100;
`;

const Logo = styled.h1`
  color: ${props => props.theme.colors.primary};
  font-size: 1.5rem;
  font-weight: bold;
`;

const Navigation = styled.nav`
  display: flex;
  gap: ${props => props.theme.spacing.lg};
  margin-left: auto;
`;

const NavButton = styled(motion.button)`
  background: transparent;
  border: 1px solid ${props => props.theme.colors.border};
  color: ${props => props.theme.colors.text};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: 6px;
  cursor: pointer;
  font-family: ${props => props.theme.fonts.mono};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.primary};
    color: ${props => props.theme.colors.background};
    border-color: ${props => props.theme.colors.primary};
  }
`;

function App() {
  const { isConnected, gameState } = useGameStore();
  const [currentRoute, setCurrentRoute] = useState('/');

  useEffect(() => {
    // Initialize any global app state
    console.log('🎮 Git Learning Game initialized');
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <GlobalStyle />
        <AppContainer>
          <Router>
            <AppHeader
              initial={{ y: -50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Logo>🌳 Git Learning Game</Logo>
              <Navigation>
                <NavButton
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setCurrentRoute('/')}
                >
                  🏠 Home
                </NavButton>
                <NavButton
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setCurrentRoute('/leaderboard')}
                >
                  🏆 Leaderboard
                </NavButton>
                <NavButton
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setCurrentRoute('/stages')}
                >
                  📚 Stages
                </NavButton>
                {gameState && (
                  <NavButton
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    style={{ 
                      background: theme.colors.success,
                      borderColor: theme.colors.success 
                    }}
                  >
                    🎯 Stage {gameState.stage}/{gameState.total_stages}
                  </NavButton>
                )}
              </Navigation>
            </AppHeader>
            
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/game" element={<GameLayout />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="/stages" element={<StageSelector />} />
            </Routes>
          </Router>
          
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: theme.colors.surface,
                color: theme.colors.text,
                border: `1px solid ${theme.colors.border}`,
                fontFamily: theme.fonts.mono,
                fontSize: '14px',
              },
              success: {
                iconTheme: {
                  primary: theme.colors.success,
                  secondary: theme.colors.text,
                },
              },
              error: {
                iconTheme: {
                  primary: theme.colors.error,
                  secondary: theme.colors.text,
                },
              },
            }}
          />
        </AppContainer>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
