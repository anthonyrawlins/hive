import React, { createContext, useContext, useEffect, useState } from 'react';
import { useSocketIO, SocketIOMessage } from '../hooks/useSocketIO';

interface SocketIOContextType {
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  sendMessage: (event: string, data: any) => void;
  joinRoom: (room: string) => void;
  leaveRoom: (room: string) => void;
  lastMessage: SocketIOMessage | null;
  subscribe: (messageType: string, handler: (data: any) => void) => () => void;
  reconnect: () => void;
}

const SocketIOContext = createContext<SocketIOContextType | null>(null);

interface SocketIOProviderProps {
  children: React.ReactNode;
  url?: string;
}

export const SocketIOProvider: React.FC<SocketIOProviderProps> = ({ 
  children, 
  url = import.meta.env.VITE_WS_BASE_URL || 'https://hive.home.deepblack.cloud'
}) => {
  // Allow disabling SocketIO completely via environment variable
  const socketIODisabled = import.meta.env.VITE_DISABLE_SOCKETIO === 'true';
  
  if (socketIODisabled) {
    console.log('Socket.IO disabled via environment variable');
    const contextValue: SocketIOContextType = {
      isConnected: false,
      connectionState: 'disconnected',
      sendMessage: () => console.warn('Socket.IO is disabled'),
      joinRoom: () => console.warn('Socket.IO is disabled'),
      leaveRoom: () => console.warn('Socket.IO is disabled'),
      lastMessage: null,
      subscribe: () => () => {},
      reconnect: () => console.warn('Socket.IO is disabled')
    };
    
    return (
      <SocketIOContext.Provider value={contextValue}>
        {children}
      </SocketIOContext.Provider>
    );
  }
  const [subscriptions, setSubscriptions] = useState<Map<string, Set<(data: any) => void>>>(new Map());

  const {
    socket,
    isConnected,
    connectionState,
    sendMessage,
    joinRoom,
    leaveRoom,
    lastMessage,
    reconnect
  } = useSocketIO({
    url,
    onMessage: (message) => {
      // Handle incoming messages and notify subscribers
      const handlers = subscriptions.get(message.type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message.data);
          } catch (error) {
            console.error('Error in Socket.IO message handler:', error);
          }
        });
      }
    },
    onConnect: () => {
      console.log('✅ Socket.IO connected to Hive backend');
      
      // Join general room and subscribe to common events
      if (socket) {
        socket.emit('join_room', { room: 'general' });
        socket.emit('subscribe', { 
          events: ['agent_status_changed', 'execution_started', 'execution_completed', 'metrics_updated'],
          room: 'general'
        });
      }
    },
    onDisconnect: () => {
      console.log('🔌 Socket.IO disconnected from Hive backend');
    },
    onError: (error) => {
      // Errors are already logged in the hook, don't duplicate
      // console.error('Socket.IO error:', error);
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

  const contextValue: SocketIOContextType = {
    isConnected,
    connectionState,
    sendMessage,
    joinRoom,
    leaveRoom,
    lastMessage,
    subscribe,
    reconnect
  };

  return (
    <SocketIOContext.Provider value={contextValue}>
      {children}
    </SocketIOContext.Provider>
  );
};

export const useSocketIOContext = (): SocketIOContextType => {
  const context = useContext(SocketIOContext);
  if (!context) {
    throw new Error('useSocketIOContext must be used within a SocketIOProvider');
  }
  return context;
};

// Convenience hooks for common real-time updates
export const useAgentUpdates = (onAgentUpdate: (agentData: any) => void) => {
  const { subscribe } = useSocketIOContext();
  
  useEffect(() => {
    const unsubscribe = subscribe('agent_status_changed', onAgentUpdate);
    return unsubscribe;
  }, [subscribe, onAgentUpdate]);
};

export const useExecutionUpdates = (onExecutionUpdate: (executionData: any) => void) => {
  const { subscribe } = useSocketIOContext();
  
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
  const { subscribe } = useSocketIOContext();
  
  useEffect(() => {
    const unsubscribe = subscribe('metrics_updated', onMetricsUpdate);
    return unsubscribe;
  }, [subscribe, onMetricsUpdate]);
};