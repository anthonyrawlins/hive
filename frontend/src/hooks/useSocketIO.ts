import { useEffect, useState, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

export interface SocketIOMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface SocketIOHookOptions {
  url: string;
  autoConnect?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
  onMessage?: (message: SocketIOMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
}

export interface SocketIOHookReturn {
  socket: Socket | null;
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  sendMessage: (event: string, data: any) => void;
  joinRoom: (room: string) => void;
  leaveRoom: (room: string) => void;
  subscribe: (events: string[], room?: string) => void;
  lastMessage: SocketIOMessage | null;
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
}

export const useSocketIO = (options: SocketIOHookOptions): SocketIOHookReturn => {
  const {
    url,
    autoConnect = true,
    reconnectionAttempts = 5,
    reconnectionDelay = 1000,
    onMessage,
    onConnect,
    onDisconnect,
    onError
  } = options;

  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<SocketIOMessage | null>(null);
  
  const reconnectAttemptsRef = useRef(0);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    if (socket?.connected) {
      return;
    }

    try {
      setConnectionState('connecting');
      console.log('Socket.IO connecting to:', url);
      
      const socketInstance = io(url, {
        transports: ['websocket', 'polling'],
        upgrade: true,
        rememberUpgrade: true,
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts,
        reconnectionDelay,
        timeout: 20000,
        forceNew: false
      });

      socketInstance.on('connect', () => {
        console.log('Socket.IO connected');
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      });

      socketInstance.on('disconnect', (reason) => {
        console.log('Socket.IO disconnected:', reason);
        setIsConnected(false);
        setConnectionState('disconnected');
        onDisconnect?.();
      });

      socketInstance.on('connect_error', (error) => {
        console.error('Socket.IO connection error:', error);
        setConnectionState('error');
        onError?.(error);
      });

      socketInstance.on('reconnect_error', (error) => {
        console.error('Socket.IO reconnection error:', error);
        setConnectionState('error');
        onError?.(error);
      });

      socketInstance.on('reconnect', (attemptNumber) => {
        console.log(`Socket.IO reconnected after ${attemptNumber} attempts`);
        setIsConnected(true);
        setConnectionState('connected');
        reconnectAttemptsRef.current = 0;
        onConnect?.();
      });

      socketInstance.on('reconnect_failed', () => {
        console.error('Socket.IO reconnection failed');
        setConnectionState('error');
        onError?.(new Error('Reconnection failed'));
      });

      // Listen for connection confirmation
      socketInstance.on('connection_confirmed', (data) => {
        console.log('Socket.IO connection confirmed:', data);
        setLastMessage({
          type: 'connection_confirmed',
          data,
          timestamp: new Date().toISOString()
        });
      });

      // Listen for room events
      socketInstance.on('room_joined', (data) => {
        console.log('Socket.IO room joined:', data);
        setLastMessage({
          type: 'room_joined',
          data,
          timestamp: new Date().toISOString()
        });
      });

      socketInstance.on('room_left', (data) => {
        console.log('Socket.IO room left:', data);
        setLastMessage({
          type: 'room_left',
          data,
          timestamp: new Date().toISOString()
        });
      });

      socketInstance.on('subscription_confirmed', (data) => {
        console.log('Socket.IO subscription confirmed:', data);
        setLastMessage({
          type: 'subscription_confirmed',
          data,
          timestamp: new Date().toISOString()
        });
      });

      // Handle generic messages
      socketInstance.onAny((event, data) => {
        const message: SocketIOMessage = {
          type: event,
          data,
          timestamp: new Date().toISOString()
        };
        setLastMessage(message);
        onMessage?.(message);
      });

      setSocket(socketInstance);
    } catch (error) {
      console.error('Failed to create Socket.IO connection:', error);
      setConnectionState('error');
      onError?.(error);
    }
  }, [url, reconnectionAttempts, reconnectionDelay, onMessage, onConnect, onDisconnect, onError]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (socket) {
      socket.disconnect();
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

  const sendMessage = useCallback((event: string, data: any) => {
    if (socket?.connected) {
      socket.emit(event, data);
    } else {
      console.warn('Socket.IO is not connected. Cannot send message:', { event, data });
    }
  }, [socket]);

  const joinRoom = useCallback((room: string) => {
    if (socket?.connected) {
      socket.emit('join_room', { room });
    } else {
      console.warn('Socket.IO is not connected. Cannot join room:', room);
    }
  }, [socket]);

  const leaveRoom = useCallback((room: string) => {
    if (socket?.connected) {
      socket.emit('leave_room', { room });
    } else {
      console.warn('Socket.IO is not connected. Cannot leave room:', room);
    }
  }, [socket]);

  const subscribe = useCallback((events: string[], room: string = 'general') => {
    if (socket?.connected) {
      socket.emit('subscribe', { events, room });
    } else {
      console.warn('Socket.IO is not connected. Cannot subscribe to events:', { events, room });
    }
  }, [socket]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      shouldReconnectRef.current = false;
      if (socket) {
        socket.disconnect();
      }
    };
  }, [socket]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      shouldReconnectRef.current = true;
      connect();
    }

    return () => {
      shouldReconnectRef.current = false;
    };
  }, [connect, autoConnect]);

  return {
    socket,
    isConnected,
    connectionState,
    sendMessage,
    joinRoom,
    leaveRoom,
    subscribe,
    lastMessage,
    connect,
    disconnect,
    reconnect
  };
};