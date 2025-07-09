import { useEffect, useState, useRef, useCallback } from 'react';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface WebSocketHookOptions {
  url: string;
  reconnectAttempts?: number;
  reconnectDelay?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export interface WebSocketHookReturn {
  socket: WebSocket | null;
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  sendMessage: (type: string, data: any) => void;
  lastMessage: WebSocketMessage | null;
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
}

export const useWebSocket = (options: WebSocketHookOptions): WebSocketHookReturn => {
  const {
    url,
    reconnectAttempts = 5,
    reconnectDelay = 3000,
    onMessage,
    onConnect,
    onDisconnect,
    onError
  } = options;

  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    if (socket?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      setConnectionState('connecting');
      // Ensure we use the correct URL in production
      const wsUrl = url.includes('localhost') ? 'wss://hive.home.deepblack.cloud/socket.io/general' : url;
      console.log('WebSocket connecting to:', wsUrl);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setSocket(null);
        
        if (event.code !== 1000 && shouldReconnectRef.current) {
          setConnectionState('disconnected');
          // Attempt to reconnect
          if (reconnectAttemptsRef.current < reconnectAttempts) {
            reconnectAttemptsRef.current++;
            console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${reconnectAttempts})`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, reconnectDelay);
          } else {
            setConnectionState('error');
            console.error('Max reconnection attempts reached');
          }
        } else {
          setConnectionState('disconnected');
        }
        
        onDisconnect?.();
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionState('error');
        onError?.(error);
      };

      setSocket(ws);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionState('error');
    }
  }, [url, reconnectAttempts, reconnectDelay, onMessage, onConnect, onDisconnect, onError, socket]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (socket) {
      socket.close(1000, 'User disconnected');
    }
    
    setSocket(null);
    setIsConnected(false);
    setConnectionState('disconnected');
  }, [socket]);

  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    reconnectAttemptsRef.current = 0;
    setTimeout(() => connect(), 100);
  }, [disconnect, connect]);

  const sendMessage = useCallback((type: string, data: any) => {
    if (socket?.readyState === WebSocket.OPEN) {
      const message = {
        type,
        data,
        timestamp: new Date().toISOString()
      };
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', { type, data });
    }
  }, [socket]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socket) {
        socket.close(1000, 'Component unmounted');
      }
    };
  }, [socket]);

  // Auto-connect on mount
  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    return () => {
      shouldReconnectRef.current = false;
    };
  }, [connect]);

  return {
    socket,
    isConnected,
    connectionState,
    sendMessage,
    lastMessage,
    connect,
    disconnect,
    reconnect
  };
};

// Utility hook for subscribing to specific message types
export const useWebSocketSubscription = (
  socket: WebSocket | null,
  messageType: string,
  handler: (data: any) => void
) => {
  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        if (message.type === messageType) {
          handler(message.data);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    socket.addEventListener('message', handleMessage);

    return () => {
      socket.removeEventListener('message', handleMessage);
    };
  }, [socket, messageType, handler]);
};