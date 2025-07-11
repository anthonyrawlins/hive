import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '../AuthContext';
import * as authApi from '../../api/auth';
import { mockApiResponses, mockUser } from '../../test/utils';

// Mock the auth API
jest.mock('../../api/auth');
const mockAuthApi = authApi as jest.Mocked<typeof authApi>;

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  it('initializes with no user when no token in localStorage', () => {
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
  });

  it('attempts to load user when token exists in localStorage', async () => {
    mockLocalStorage.getItem.mockReturnValue('mock-token');
    mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);
    
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    // Initially loading
    expect(result.current.isLoading).toBe(true);
    
    // Wait for the async operation to complete
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isLoading).toBe(false);
  });

  it('clears user data when token is invalid', async () => {
    mockLocalStorage.getItem.mockReturnValue('invalid-token');
    mockAuthApi.getCurrentUser.mockRejectedValue(new Error('Unauthorized'));
    
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
  });

  it('logs in user successfully', async () => {
    mockAuthApi.login.mockResolvedValue(mockApiResponses.auth.login);
    
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    await act(async () => {
      await result.current.login('test@example.com', 'password123');
    });
    
    expect(mockAuthApi.login).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    });
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', 'mock-jwt-token');
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('throws error on login failure', async () => {
    const loginError = new Error('Invalid credentials');
    mockAuthApi.login.mockRejectedValue(loginError);
    
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    await expect(act(async () => {
      await result.current.login('test@example.com', 'wrongpassword');
    })).rejects.toThrow('Invalid credentials');
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('logs out user successfully', async () => {
    // First set up an authenticated user
    mockLocalStorage.getItem.mockReturnValue('mock-token');
    mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);
    
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Now logout
    await act(async () => {
      result.current.logout();
    });
    
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('updates user data', async () => {
    // First set up an authenticated user
    mockLocalStorage.getItem.mockReturnValue('mock-token');
    mockAuthApi.getCurrentUser.mockResolvedValue(mockUser);
    
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    const updatedUser = { ...mockUser, full_name: 'Updated Name' };
    
    act(() => {
      result.current.updateUser(updatedUser);
    });
    
    expect(result.current.user).toEqual(updatedUser);
  });

  it('handles register functionality', async () => {
    const registerData = {
      email: 'newuser@example.com',
      password: 'password123',
      full_name: 'New User',
      username: 'newuser',
    };
    
    mockAuthApi.register.mockResolvedValue(mockApiResponses.auth.login);
    
    const { result } = renderHook(() => useAuth(), { wrapper: createWrapper() });
    
    await act(async () => {
      await result.current.register(registerData);
    });
    
    expect(mockAuthApi.register).toHaveBeenCalledWith(registerData);
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });
});