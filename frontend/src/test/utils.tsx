import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../contexts/AuthContext';

// Create a custom render function that includes providers
const AllProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };

// Mock data helpers
export const mockUser = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Test User',
  name: 'Test User',
  role: 'user',
  is_active: true,
  is_superuser: false,
  is_verified: true,
};

export const mockAgent = {
  id: 'test-agent-1',
  name: 'Test Agent',
  endpoint: 'http://localhost:11434',
  model: 'llama3.1:8b',
  specialty: 'general_ai',
  max_concurrent: 2,
  current_tasks: 0,
  agent_type: 'ollama',
  status: 'online',
  last_heartbeat: Date.now(),
};

export const mockTask = {
  id: 'task_1735589200_0',
  title: 'Test Task',
  description: 'A test task for unit testing',
  type: 'general_ai',
  priority: 3,
  status: 'pending',
  created_at: Date.now(),
  context: {
    objective: 'Test objective',
    requirements: ['Test requirement 1'],
  },
};

export const mockWorkflow = {
  id: 'workflow_1735589200',
  name: 'Test Workflow',
  description: 'A test workflow',
  steps: [
    {
      name: 'Step 1',
      type: 'general_ai',
      agent_type: 'general_ai',
      inputs: { prompt: 'Test prompt' },
      outputs: ['result'],
    },
  ],
  created_at: Date.now(),
  status: 'pending',
};

// Mock API responses
export const mockApiResponses = {
  auth: {
    login: {
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
      user: mockUser,
    },
    me: mockUser,
  },
  agents: {
    list: [mockAgent],
    detail: mockAgent,
  },
  tasks: {
    list: [mockTask],
    detail: mockTask,
  },
  workflows: {
    list: [mockWorkflow],
    detail: mockWorkflow,
  },
};

// Async utility for waiting for elements
export const waitFor = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));