import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { TeammateAction } from '../types/game';

interface TeammateActivityProps {
  sessionId: string;
  lastMessage: MessageEvent | null;
}

const Container = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const ActivityList = styled.div`
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column-reverse;
`;

const ActivityItem = styled(motion.div)`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 4px;
  padding: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.sm};
  font-size: 0.8rem;
`;

const TeammateAvatar = styled.div<{ teammate: string }>`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: ${props => {
    const colors = {
      alice: '#ff6b6b',
      bob: '#4ecdc4', 
      charlie: '#45b7d1',
      diana: '#f9ca24'
    };
    return colors[props.teammate as keyof typeof colors] || '#8b949e';
  }};
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
  color: white;
  margin-right: ${props => props.theme.spacing.sm};
`;

const ActivityText = styled.span`
  color: ${props => props.theme.colors.text};
`;

const Timestamp = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.6rem;
  margin-top: 4px;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.8rem;
  text-align: center;
`;

const TeammateActivity: React.FC<TeammateActivityProps> = ({ sessionId, lastMessage }) => {
  const [activities, setActivities] = useState<(TeammateAction & { id: string; timestamp: number })[]>([]);
  
  useEffect(() => {
    if (!lastMessage) return;
    
    try {
      const message = JSON.parse(lastMessage.data);
      
      if (message.type === 'teammate_activity' && message.data) {
        const newActivity = {
          ...message.data,
          id: `${Date.now()}-${Math.random()}`,
          timestamp: Date.now()
        };
        
        setActivities(prev => [newActivity, ...prev.slice(0, 19)]); // Keep last 20 activities
      }
    } catch (error) {
      console.error('Failed to parse teammate activity message:', error);
    }
  }, [lastMessage]);
  
  // Simulate some initial activity
  useEffect(() => {
    const initialActivities = [
      {
        id: '1',
        type: 'teammate_commit' as const,
        teammate: 'alice',
        action: 'Added user authentication',
        timestamp: Date.now() - 300000 // 5 minutes ago
      },
      {
        id: '2',
        type: 'teammate_merge' as const,
        teammate: 'bob',
        action: 'Merged feature branch',
        timestamp: Date.now() - 600000 // 10 minutes ago
      },
      {
        id: '3',
        type: 'teammate_push' as const,
        teammate: 'charlie',
        action: 'Pushed to development',
        timestamp: Date.now() - 900000 // 15 minutes ago
      }
    ];
    
    setActivities(initialActivities);
  }, []);
  
  const formatTimestamp = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    return 'yesterday';
  };
  
  const getActionIcon = (type: string) => {
    switch (type) {
      case 'teammate_commit': return '📝';
      case 'teammate_push': return '🚀';
      case 'teammate_merge': return '🌱';
      case 'teammate_rebase': return '🔄';
      default: return '👥';
    }
  };
  
  if (activities.length === 0) {
    return (
      <Container>
        <EmptyState>
          <div style={{ fontSize: '2rem', marginBottom: '8px' }}>👥</div>
          <div>No teammate activity yet</div>
          <div style={{ fontSize: '0.7rem', marginTop: '4px' }}>
            Your teammates will start working soon!
          </div>
        </EmptyState>
      </Container>
    );
  }
  
  return (
    <Container>
      <ActivityList>
        <AnimatePresence initial={false}>
          {activities.map((activity) => (
            <ActivityItem
              key={activity.id}
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <TeammateAvatar teammate={activity.teammate}>
                  {activity.teammate[0].toUpperCase()}
                </TeammateAvatar>
                <div style={{ flex: 1 }}>
                  <ActivityText>
                    <strong>{activity.teammate}</strong> {activity.action}
                  </ActivityText>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span>{getActionIcon(activity.type)}</span>
                    <Timestamp>{formatTimestamp(activity.timestamp)}</Timestamp>
                  </div>
                </div>
              </div>
            </ActivityItem>
          ))}
        </AnimatePresence>
      </ActivityList>
    </Container>
  );
};

export default TeammateActivity;
