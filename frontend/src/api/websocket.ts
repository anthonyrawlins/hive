import { io, Socket } from 'socket.io-client';
import React from 'react';

// Types for real-time events
export interface TaskUpdate {
  task_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress?: number;
  result?: any;
  error?: string;
  timestamp: string;
}

export interface AgentUpdate {
  agent_id: string;
  status: 'online' | 'offline' | 'busy' | 'error';
  current_tasks: number;
  cpu_usage?: number;
  memory_usage?: number;
  gpu_usage?: number;
  timestamp: string;
}

export interface WorkflowUpdate {
  workflow_id: string;
  execution_id: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  current_step?: string;
  progress?: number;
  timestamp: string;
}

export interface SystemAlert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  severity: 'high' | 'medium' | 'low';
  title: string;
  message: string;
  component: string;
  timestamp: string;
}

export interface MetricsUpdate {
  timestamp: string;
  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    active_connections: number;
  };
  cluster: {
    total_agents: number;
    active_agents: number;
    total_tasks: number;
    active_tasks: number;
  };
}

// Event handlers type
export interface WebSocketEventHandlers {
  onTaskUpdate?: (update: TaskUpdate) => void;
  onAgentUpdate?: (update: AgentUpdate) => void;
  onWorkflowUpdate?: (update: WorkflowUpdate) => void;
  onSystemAlert?: (alert: SystemAlert) => void;
  onMetricsUpdate?: (metrics: MetricsUpdate) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
}

// WebSocket service class
export class WebSocketService {
  private socket: Socket | null = null;
  private handlers: WebSocketEventHandlers = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor() {
    // Don't auto-connect - let the app connect when authenticated
  }

  private _connect(): void {
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('No auth token found for WebSocket connection');
      return;
    }

    const baseURL = process.env.REACT_APP_SOCKETIO_URL || 'https://hive.home.deepblack.cloud';
    
    this.socket = io(baseURL, {
      auth: {
        token: `Bearer ${token}`,
      },
      transports: ['websocket', 'polling'],
    });

    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.handlers.onConnect?.();
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.handlers.onDisconnect?.();
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, try to reconnect
        this.handleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.handlers.onError?.(error);
      this.handleReconnect();
    });

    // Task events
    this.socket.on('task_update', (update: TaskUpdate) => {
      this.handlers.onTaskUpdate?.(update);
    });

    this.socket.on('task_started', (update: TaskUpdate) => {
      this.handlers.onTaskUpdate?.(update);
    });

    this.socket.on('task_completed', (update: TaskUpdate) => {
      this.handlers.onTaskUpdate?.(update);
    });

    this.socket.on('task_failed', (update: TaskUpdate) => {
      this.handlers.onTaskUpdate?.(update);
    });

    // Agent events
    this.socket.on('agent_update', (update: AgentUpdate) => {
      this.handlers.onAgentUpdate?.(update);
    });

    this.socket.on('agent_connected', (update: AgentUpdate) => {
      this.handlers.onAgentUpdate?.(update);
    });

    this.socket.on('agent_disconnected', (update: AgentUpdate) => {
      this.handlers.onAgentUpdate?.(update);
    });

    // Workflow events
    this.socket.on('workflow_update', (update: WorkflowUpdate) => {
      this.handlers.onWorkflowUpdate?.(update);
    });

    this.socket.on('workflow_started', (update: WorkflowUpdate) => {
      this.handlers.onWorkflowUpdate?.(update);
    });

    this.socket.on('workflow_completed', (update: WorkflowUpdate) => {
      this.handlers.onWorkflowUpdate?.(update);
    });

    this.socket.on('workflow_failed', (update: WorkflowUpdate) => {
      this.handlers.onWorkflowUpdate?.(update);
    });

    // System events
    this.socket.on('system_alert', (alert: SystemAlert) => {
      this.handlers.onSystemAlert?.(alert);
    });

    this.socket.on('metrics_update', (metrics: MetricsUpdate) => {
      this.handlers.onMetricsUpdate?.(metrics);
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);
    
    setTimeout(() => {
      this._connect();
    }, delay);
  }

  // Public methods
  public connect(): void {
    if (this.socket?.connected) {
      console.log('WebSocket already connected');
      return;
    }
    this._connect();
  }

  public disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.reconnectAttempts = 0;
    }
  }

  public setEventHandlers(handlers: WebSocketEventHandlers): void {
    this.handlers = { ...this.handlers, ...handlers };
  }

  public subscribe(event: string, handler: (data: any) => void): void {
    this.socket?.on(event, handler);
  }

  public unsubscribe(event: string, handler?: (data: any) => void): void {
    if (handler) {
      this.socket?.off(event, handler);
    } else {
      this.socket?.off(event);
    }
  }

  public emit(event: string, data?: any): void {
    this.socket?.emit(event, data);
  }


  public isConnected(): boolean {
    return this.socket?.connected ?? false;
  }

  // Room management for targeted updates
  public joinRoom(room: string): void {
    this.socket?.emit('join_room', room);
  }

  public leaveRoom(room: string): void {
    this.socket?.emit('leave_room', room);
  }

  // Subscribe to specific agent updates
  public subscribeToAgent(agentId: string): void {
    this.joinRoom(`agent_${agentId}`);
  }

  public unsubscribeFromAgent(agentId: string): void {
    this.leaveRoom(`agent_${agentId}`);
  }

  // Subscribe to specific workflow updates
  public subscribeToWorkflow(workflowId: string): void {
    this.joinRoom(`workflow_${workflowId}`);
  }

  public unsubscribeFromWorkflow(workflowId: string): void {
    this.leaveRoom(`workflow_${workflowId}`);
  }

  // Subscribe to specific task updates
  public subscribeToTask(taskId: string): void {
    this.joinRoom(`task_${taskId}`);
  }

  public unsubscribeFromTask(taskId: string): void {
    this.leaveRoom(`task_${taskId}`);
  }
}

// Create singleton instance
export const webSocketService = new WebSocketService();

// React hook for using WebSocket in components
export const useWebSocket = (handlers: WebSocketEventHandlers) => {
  React.useEffect(() => {
    webSocketService.setEventHandlers(handlers);
    
    return () => {
      // Clean up handlers when component unmounts
      Object.keys(handlers).forEach(key => {
        webSocketService.setEventHandlers({ [key]: undefined });
      });
    };
  }, [handlers]);

  return {
    isConnected: webSocketService.isConnected(),
    subscribe: webSocketService.subscribe.bind(webSocketService),
    unsubscribe: webSocketService.unsubscribe.bind(webSocketService),
    emit: webSocketService.emit.bind(webSocketService),
    subscribeToAgent: webSocketService.subscribeToAgent.bind(webSocketService),
    unsubscribeFromAgent: webSocketService.unsubscribeFromAgent.bind(webSocketService),
    subscribeToWorkflow: webSocketService.subscribeToWorkflow.bind(webSocketService),
    unsubscribeFromWorkflow: webSocketService.unsubscribeFromWorkflow.bind(webSocketService),
    subscribeToTask: webSocketService.subscribeToTask.bind(webSocketService),
    unsubscribeFromTask: webSocketService.unsubscribeFromTask.bind(webSocketService),
  };
};

export default webSocketService;