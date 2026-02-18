import { useState, useEffect, useCallback, useRef } from 'react';

// Types
import { ConnectionStatus, WebSocketMessage } from '../types/game';

const getDefaultWsBaseUrl = () => {
  if (process.env.REACT_APP_WS_URL) {
    return process.env.REACT_APP_WS_URL;
  }

  if (typeof window !== 'undefined' && window.location) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}`;
  }

  return 'ws://localhost:8000';
};

interface UseWebSocketReturn {
  lastMessage: MessageEvent | null;
  connectionStatus: ConnectionStatus;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: WebSocketMessage) => void;
}

export const useWebSocket = (sessionId: string): UseWebSocketReturn => {
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  
  const connect = useCallback(() => {
    if (!sessionId) {
      console.warn('Cannot connect WebSocket without session ID');
      return;
    }
    
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket is already connected');
      return;
    }
    
    setConnectionStatus('connecting');
    
    try {
      const wsBaseUrl = getDefaultWsBaseUrl();
      const wsUrl = `${wsBaseUrl}/ws/${sessionId}`;
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        console.log('🔗 WebSocket connected');
        setConnectionStatus('connected');
        reconnectAttempts.current = 0;
        
        // Send ping to confirm connection
        websocket.send(JSON.stringify({ type: 'ping' }));
      };
      
      websocket.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason);
        setConnectionStatus('disconnected');
        
        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          console.log(`♾️ Attempting to reconnect in ${timeout}ms...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, timeout);
        }
      };
      
      websocket.onerror = (error) => {
        console.error('🚨 WebSocket error:', error);
        setConnectionStatus('error');
      };
      
      websocket.onmessage = (event) => {
        setLastMessage(event);
        
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          
          if (message.type === 'pong') {
            // Handle ping/pong for keep-alive
            return;
          }
          
          console.log('💬 Received WebSocket message:', message.type);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };
      
      websocketRef.current = websocket;
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('error');
    }
  }, [sessionId]);
  
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (websocketRef.current) {
      websocketRef.current.close(1000, 'Manual disconnect');
      websocketRef.current = null;
    }
    
    setConnectionStatus('disconnected');
    setLastMessage(null);
  }, []);
  
  const sendMessage = useCallback((message: WebSocketMessage) => {
    const websocket = websocketRef.current;
    
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      console.warn('Cannot send message: WebSocket is not connected');
      return;
    }
    
    try {
      websocket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
    }
  }, []);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);
  
  // Auto-reconnect when sessionId changes
  useEffect(() => {
    if (sessionId && connectionStatus === 'disconnected') {
      connect();
    }
  }, [sessionId, connect]);
  
  // Ping interval to keep connection alive
  useEffect(() => {
    let pingInterval: NodeJS.Timeout;
    
    if (connectionStatus === 'connected') {
      pingInterval = setInterval(() => {
        sendMessage({ type: 'ping' });
      }, 30000); // Ping every 30 seconds
    }
    
    return () => {
      if (pingInterval) {
        clearInterval(pingInterval);
      }
    };
  }, [connectionStatus, sendMessage]);
  
  return {
    lastMessage,
    connectionStatus,
    connect,
    disconnect,
    sendMessage
  };
};
