import React, { createContext, useContext, useEffect, useState } from 'react';
import { useWebSocket, WebSocketMessage } from '../hooks/useWebSocket';

interface WebSocketContextType {
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  sendMessage: (type: string, data: any) => void;
  lastMessage: WebSocketMessage | null;
  subscribe: (messageType: string, handler: (data: any) => void) => () => void;
  reconnect: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

interface WebSocketProviderProps {
  children: React.ReactNode;
  url?: string;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ 
  children, 
  url = import.meta.env.VITE_WS_BASE_URL || 'wss://hive.home.deepblack.cloud'
}) => {
  const [subscriptions, setSubscriptions] = useState<Map<string, Set<(data: any) => void>>>(new Map());

  const {
    isConnected,
    connectionState,
    sendMessage,
    lastMessage,
    reconnect
  } = useWebSocket({
    url,
    reconnectAttempts: 5,
    reconnectDelay: 3000,
    onMessage: (message) => {
      // Handle incoming messages and notify subscribers
      const handlers = subscriptions.get(message.type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message.data);
          } catch (error) {
            console.error('Error in WebSocket message handler:', error);
          }
        });
      }
    },
    onConnect: () => {
      console.log('WebSocket connected to Hive backend');
      // Subscribe to general system events
      sendMessage('subscribe', { 
        events: ['agent_status_changed', 'execution_started', 'execution_completed', 'metrics_updated'] 
      });
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected from Hive backend');
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    }
  });

  const subscribe = (messageType: string, handler: (data: any) => void) => {
    setSubscriptions(prev => {
      const newSubscriptions = new Map(prev);
      if (!newSubscriptions.has(messageType)) {
        newSubscriptions.set(messageType, new Set());
      }
      newSubscriptions.get(messageType)!.add(handler);
      return newSubscriptions;
    });

    // Return unsubscribe function
    return () => {
      setSubscriptions(prev => {
        const newSubscriptions = new Map(prev);
        const handlers = newSubscriptions.get(messageType);
        if (handlers) {
          handlers.delete(handler);
          if (handlers.size === 0) {
            newSubscriptions.delete(messageType);
          }
        }
        return newSubscriptions;
      });
    };
  };

  const contextValue: WebSocketContextType = {
    isConnected,
    connectionState,
    sendMessage,
    lastMessage,
    subscribe,
    reconnect
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};

// Convenience hooks for common real-time updates
export const useAgentUpdates = (onAgentUpdate: (agentData: any) => void) => {
  const { subscribe } = useWebSocketContext();
  
  useEffect(() => {
    const unsubscribe = subscribe('agent_status_changed', onAgentUpdate);
    return unsubscribe;
  }, [subscribe, onAgentUpdate]);
};

export const useExecutionUpdates = (onExecutionUpdate: (executionData: any) => void) => {
  const { subscribe } = useWebSocketContext();
  
  useEffect(() => {
    const unsubscribeStart = subscribe('execution_started', onExecutionUpdate);
    const unsubscribeComplete = subscribe('execution_completed', onExecutionUpdate);
    const unsubscribeFailed = subscribe('execution_failed', onExecutionUpdate);
    
    return () => {
      unsubscribeStart();
      unsubscribeComplete();
      unsubscribeFailed();
    };
  }, [subscribe, onExecutionUpdate]);
};

export const useMetricsUpdates = (onMetricsUpdate: (metricsData: any) => void) => {
  const { subscribe } = useWebSocketContext();
  
  useEffect(() => {
    const unsubscribe = subscribe('metrics_updated', onMetricsUpdate);
    return unsubscribe;
  }, [subscribe, onMetricsUpdate]);
};