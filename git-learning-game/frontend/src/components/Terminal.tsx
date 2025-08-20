import React, { useEffect, useRef, useState } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from '@xterm/addon-fit';
import styled from 'styled-components';

// CSS for xterm
import 'xterm/css/xterm.css';

// Types
import { GitState } from '../types/game';

interface TerminalProps {
  onCommandExecute: (command: string) => Promise<void>;
  gameState: GitState | null;
}

const TerminalContainer = styled.div`
  height: 100%;
  width: 100%;
  background: #0d1117;
  padding: ${props => props.theme.spacing.md};
  position: relative;
  
  .xterm {
    height: 100% !important;
  }
  
  .xterm-viewport {
    background: transparent !important;
  }
  
  .xterm-screen {
    background: transparent !important;
  }
`;

const HelpPanel = styled.div<{ show: boolean }>`
  position: absolute;
  top: 10px;
  right: 10px;
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 6px;
  padding: ${props => props.theme.spacing.md};
  font-family: ${props => props.theme.fonts.mono};
  font-size: 12px;
  max-width: 350px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 20;
  opacity: ${props => props.show ? 1 : 0};
  pointer-events: ${props => props.show ? 'auto' : 'none'};
  transition: opacity 0.2s ease;
`;

const HelpCommand = styled.div`
  color: ${props => props.theme.colors.primary};
  margin: 4px 0;
  
  &:before {
    content: '$ ';
    color: ${props => props.theme.colors.success};
  }
`;

const HelpDescription = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  margin-left: 16px;
  margin-bottom: 8px;
`;

const Terminal: React.FC<TerminalProps> = ({ onCommandExecute, gameState }) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const [currentInput, setCurrentInput] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [showHelp, setShowHelp] = useState(false);
  
  const commonCommands = [
    { cmd: 'git status', desc: '현재 리포지토리 상태 확인' },
    { cmd: 'git log --oneline --graph --all', desc: '커밋 히스토리 그래프로 보기' },
    { cmd: 'git add .', desc: '모든 변경사항 스테이징' },
    { cmd: 'git commit -m "message"', desc: '커밋 생성' },
    { cmd: 'git branch', desc: '브랜치 목록 보기' },
    { cmd: 'git checkout -b new-branch', desc: '새 브랜치 생성 및 전환' },
    { cmd: 'git merge branch-name', desc: '브랜치 병합' },
    { cmd: 'git rebase -i HEAD~3', desc: '대화형 리베이스' },
    { cmd: 'git cherry-pick <commit>', desc: '특정 커밋 고르기' },
    { cmd: 'git stash', desc: '작업 내용 임시 저장' },
    { cmd: 'help', desc: '도움말 보기/숨기기' },
    { cmd: 'clear', desc: '터미널 화면 지우기' },
    { cmd: 'ls', desc: '파일 목록 보기' },
    { cmd: 'cat filename', desc: '파일 내용 보기' }
  ];
  
  useEffect(() => {
    if (!terminalRef.current) return;
    
    // Initialize xterm
    const terminal = new XTerm({
      theme: {
        background: '#0d1117',
        foreground: '#f0f6fc',
        cursor: '#00d2ff',
        cursorAccent: '#f0f6fc',
        selection: '#264f78',
        black: '#0d1117',
        red: '#da3633',
        green: '#238636',
        yellow: '#d1a500',
        blue: '#0969da',
        magenta: '#8b949e',
        cyan: '#00d2ff',
        white: '#f0f6fc',
        brightBlack: '#30363d',
        brightRed: '#ff6b6b',
        brightGreen: '#4ade80',
        brightYellow: '#facc15',
        brightBlue: '#60a5fa',
        brightMagenta: '#c084fc',
        brightCyan: '#22d3ee',
        brightWhite: '#ffffff'
      },
      fontFamily: 'Monaco, Menlo, Ubuntu Mono, monospace',
      fontSize: 14,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 1000,
      tabStopWidth: 4
    });
    
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    
    terminal.open(terminalRef.current);
    fitAddon.fit();
    
    // Welcome message
    terminal.writeln('\x1b[36m┌───────────────────────────────────────┐');
    terminal.writeln('│  🎮 Git Learning Game Terminal  │');
    terminal.writeln('├───────────────────────────────────────┤');
    terminal.writeln('│  Type "help" for available commands  │');
    terminal.writeln('│  Use arrow keys for command history   │');
    terminal.writeln('└───────────────────────────────────────┘\x1b[0m');
    terminal.writeln('');
    
    // Show current branch and stage info
    if (gameState) {
      terminal.writeln(`\x1b[32mℹ️  Current Stage: ${gameState.stage}/${gameState.total_stages}\x1b[0m`);
      if (gameState.current_branch) {
        terminal.writeln(`\x1b[34m🌳  Current Branch: ${gameState.current_branch}\x1b[0m`);
      }
      terminal.writeln('');
    }
    
    // Show prompt
    const showPrompt = () => {
      const branch = gameState?.current_branch || 'main';
      terminal.write(`\x1b[32mgame\x1b[0m:\x1b[34m~\x1b[0m (\x1b[33m${branch}\x1b[0m) $ `);
    };
    
    showPrompt();
    
    // Handle input
    let currentLine = '';
    
    terminal.onKey(({ key, domEvent }) => {
      const char = key;
      
      if (domEvent.key === 'Enter') {
        terminal.writeln('');
        
        if (currentLine.trim()) {
          executeCommand(currentLine.trim());
          
          // Add to history
          setCommandHistory(prev => {
            const newHistory = [...prev, currentLine.trim()];
            return newHistory.slice(-50); // Keep last 50 commands
          });
          setHistoryIndex(-1);
        }
        
        currentLine = '';
        setCurrentInput('');
        
      } else if (domEvent.key === 'Backspace') {
        if (currentLine.length > 0) {
          currentLine = currentLine.slice(0, -1);
          terminal.write('\b \b');
          setCurrentInput(currentLine);
        }
        
      } else if (domEvent.key === 'ArrowUp') {
        domEvent.preventDefault();
        if (commandHistory.length > 0) {
          const newIndex = historyIndex + 1;
          if (newIndex < commandHistory.length) {
            setHistoryIndex(newIndex);
            const historicalCommand = commandHistory[commandHistory.length - 1 - newIndex];
            
            // Clear current line
            for (let i = 0; i < currentLine.length; i++) {
              terminal.write('\b \b');
            }
            
            // Write historical command
            currentLine = historicalCommand;
            terminal.write(currentLine);
            setCurrentInput(currentLine);
          }
        }
        
      } else if (domEvent.key === 'ArrowDown') {
        domEvent.preventDefault();
        if (historyIndex > 0) {
          const newIndex = historyIndex - 1;
          setHistoryIndex(newIndex);
          const historicalCommand = commandHistory[commandHistory.length - 1 - newIndex];
          
          // Clear current line
          for (let i = 0; i < currentLine.length; i++) {
            terminal.write('\b \b');
          }
          
          // Write historical command
          currentLine = historicalCommand;
          terminal.write(currentLine);
          setCurrentInput(currentLine);
        } else if (historyIndex === 0) {
          setHistoryIndex(-1);
          
          // Clear current line
          for (let i = 0; i < currentLine.length; i++) {
            terminal.write('\b \b');
          }
          currentLine = '';
          setCurrentInput('');
        }
        
      } else if (domEvent.key === 'Tab') {
        domEvent.preventDefault();
        // Simple command completion
        const matches = commonCommands.filter(c => c.cmd.startsWith(currentLine));
        if (matches.length === 1) {
          const completion = matches[0].cmd.substring(currentLine.length);
          currentLine += completion;
          terminal.write(completion);
          setCurrentInput(currentLine);
        }
        
      } else if (char.length === 1) {
        currentLine += char;
        terminal.write(char);
        setCurrentInput(currentLine);
      }
    });
    
    const executeCommand = async (command: string) => {
      // Handle built-in commands
      if (command === 'clear') {
        terminal.clear();
        showPrompt();
        return;
      }
      
      if (command === 'help') {
        setShowHelp(!showHelp);
        terminal.writeln('\x1b[33mℹ️  Help panel toggled\x1b[0m');
        showPrompt();
        return;
      }
      
      if (command === 'exit' || command === 'quit') {
        terminal.writeln('\x1b[31m😜  Use the game interface to exit\x1b[0m');
        showPrompt();
        return;
      }
      
      // Show loading indicator
      terminal.writeln('\x1b[33m⏳ Executing command...\x1b[0m');
      
      try {
        // Execute through parent component
        await onCommandExecute(command);
        
        // Command executed successfully - let the parent handle the response
        showPrompt();
        
      } catch (error) {
        terminal.writeln(`\x1b[31m❌ Error: ${error}\x1b[0m`);
        showPrompt();
      }
    };
    
    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;
    
    // Handle resize
    const handleResize = () => {
      if (fitAddonRef.current) {
        fitAddonRef.current.fit();
      }
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      terminal.dispose();
    };
  }, []);
  
  // Update terminal when game state changes
  useEffect(() => {
    if (xtermRef.current && gameState) {
      // Could show status updates here
    }
  }, [gameState]);
  
  return (
    <TerminalContainer>
      <div ref={terminalRef} style={{ height: '100%', width: '100%' }} />
      
      <HelpPanel show={showHelp}>
        <div style={{ fontWeight: 'bold', marginBottom: '12px', color: '#00d2ff' }}>
          📚 사용 가능한 명령어
        </div>
        {commonCommands.map((cmd, index) => (
          <div key={index}>
            <HelpCommand>{cmd.cmd}</HelpCommand>
            <HelpDescription>{cmd.desc}</HelpDescription>
          </div>
        ))}
        
        <div style={{ 
          borderTop: '1px solid #30363d',
          marginTop: '12px', 
          paddingTop: '12px',
          fontSize: '11px',
          color: '#8b949e'
        }}>
          ⌨️  사용법: ↑↓ 화살표로 명령 히스토리 탐색<br/>
          🎨  Tab 키로 명령 자동완성<br/>
          🧙  "help" 입력으로 도움말 토글
        </div>
      </HelpPanel>
    </TerminalContainer>
  );
};

export default Terminal;
