import { renderHook, act } from '@testing-library/react';
import { useSocketIO } from '../useSocketIO';
import { io } from 'socket.io-client';

// Mock socket.io-client
jest.mock('socket.io-client');
const mockIo = io as jest.MockedFunction<typeof io>;

// Mock socket instance
const mockSocket = {
  connected: false,
  on: jest.fn(),
  emit: jest.fn(),
  disconnect: jest.fn(),
  onAny: jest.fn(),
};

describe('useSocketIO', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSocket.connected = false;
    mockIo.mockReturnValue(mockSocket as any);
  });

  it('initializes with disconnected state', () => {
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: false,
    }));

    expect(result.current.isConnected).toBe(false);
    expect(result.current.connectionState).toBe('disconnected');
    expect(result.current.socket).toBe(null);
    expect(result.current.lastMessage).toBe(null);
  });

  it('auto-connects when autoConnect is true', () => {
    renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
    }));

    expect(mockIo).toHaveBeenCalledWith('http://localhost:8087', expect.objectContaining({
      transports: ['websocket', 'polling'],
      upgrade: true,
      rememberUpgrade: true,
      autoConnect: true,
      reconnection: true,
      timeout: 20000,
      forceNew: false,
    }));
  });

  it('does not auto-connect when autoConnect is false', () => {
    renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: false,
    }));

    expect(mockIo).not.toHaveBeenCalled();
  });

  it('handles connection events', () => {
    const onConnect = jest.fn();
    const onDisconnect = jest.fn();
    const onError = jest.fn();

    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
      onConnect,
      onDisconnect,
      onError,
    }));

    // Simulate connection
    const connectHandler = mockSocket.on.mock.calls.find(call => call[0] === 'connect')[1];
    act(() => {
      connectHandler();
    });

    expect(result.current.isConnected).toBe(true);
    expect(result.current.connectionState).toBe('connected');
    expect(onConnect).toHaveBeenCalled();

    // Simulate disconnection
    const disconnectHandler = mockSocket.on.mock.calls.find(call => call[0] === 'disconnect')[1];
    act(() => {
      disconnectHandler('transport close');
    });

    expect(result.current.isConnected).toBe(false);
    expect(result.current.connectionState).toBe('disconnected');
    expect(onDisconnect).toHaveBeenCalled();

    // Simulate error
    const errorHandler = mockSocket.on.mock.calls.find(call => call[0] === 'connect_error')[1];
    act(() => {
      errorHandler(new Error('Connection failed'));
    });

    expect(result.current.connectionState).toBe('error');
    expect(onError).toHaveBeenCalledWith(new Error('Connection failed'));
  });

  it('handles message events', () => {
    const onMessage = jest.fn();
    
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
      onMessage,
    }));

    // Simulate generic message
    const anyHandler = mockSocket.onAny.mock.calls[0][0];
    act(() => {
      anyHandler('task_update', { id: 'task1', status: 'completed' });
    });

    expect(result.current.lastMessage).toMatchObject({
      type: 'task_update',
      data: { id: 'task1', status: 'completed' },
    });
    expect(onMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'task_update',
        data: { id: 'task1', status: 'completed' },
      })
    );
  });

  it('sends messages when connected', () => {
    mockSocket.connected = true;
    
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
    }));

    act(() => {
      result.current.sendMessage('test_event', { data: 'test' });
    });

    expect(mockSocket.emit).toHaveBeenCalledWith('test_event', { data: 'test' });
  });

  it('does not send messages when not connected', () => {
    mockSocket.connected = false;
    
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
    
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
    }));

    act(() => {
      result.current.sendMessage('test_event', { data: 'test' });
    });

    expect(mockSocket.emit).not.toHaveBeenCalled();
    expect(consoleSpy).toHaveBeenCalledWith(
      'Socket.IO is not connected. Cannot send message:',
      { event: 'test_event', data: { data: 'test' } }
    );
    
    consoleSpy.mockRestore();
  });

  it('joins and leaves rooms', () => {
    mockSocket.connected = true;
    
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
    }));

    act(() => {
      result.current.joinRoom('task_updates');
    });

    expect(mockSocket.emit).toHaveBeenCalledWith('join_room', { room: 'task_updates' });

    act(() => {
      result.current.leaveRoom('task_updates');
    });

    expect(mockSocket.emit).toHaveBeenCalledWith('leave_room', { room: 'task_updates' });
  });

  it('subscribes to events', () => {
    mockSocket.connected = true;
    
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
    }));

    act(() => {
      result.current.subscribe(['task_update', 'agent_status'], 'monitoring');
    });

    expect(mockSocket.emit).toHaveBeenCalledWith('subscribe', {
      events: ['task_update', 'agent_status'],
      room: 'monitoring',
    });
  });

  it('handles manual connect and disconnect', () => {
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: false,
    }));

    // Manual connect
    act(() => {
      result.current.connect();
    });

    expect(mockIo).toHaveBeenCalled();
    expect(result.current.connectionState).toBe('connecting');

    // Manual disconnect
    act(() => {
      result.current.disconnect();
    });

    expect(mockSocket.disconnect).toHaveBeenCalled();
    expect(result.current.isConnected).toBe(false);
    expect(result.current.connectionState).toBe('disconnected');
  });

  it('handles reconnection', () => {
    const { result } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
    }));

    // Simulate initial connection
    const connectHandler = mockSocket.on.mock.calls.find(call => call[0] === 'connect')[1];
    act(() => {
      connectHandler();
    });

    // Trigger reconnect
    act(() => {
      result.current.reconnect();
    });

    expect(mockSocket.disconnect).toHaveBeenCalled();
    // Should attempt to reconnect after a short delay
  });

  it('cleans up on unmount', () => {
    const { unmount } = renderHook(() => useSocketIO({
      url: 'http://localhost:8087',
      autoConnect: true,
    }));

    unmount();

    expect(mockSocket.disconnect).toHaveBeenCalled();
  });
});