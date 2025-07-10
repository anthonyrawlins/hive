/**
 * Authentication Context
 * Manages user authentication state, JWT tokens, and API key authentication
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string; // UUID as string
  username: string;
  email: string;
  full_name?: string;
  name?: string; // For backward compatibility
  role?: string; // For backward compatibility
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!tokens;

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedTokens = localStorage.getItem('hive_tokens');
        const storedUser = localStorage.getItem('hive_user');

        if (storedTokens && storedUser) {
          const parsedTokens: AuthTokens = JSON.parse(storedTokens);
          const parsedUser: User = JSON.parse(storedUser);

          // Check if tokens are still valid
          if (await validateTokens(parsedTokens)) {
            setTokens(parsedTokens);
            setUser(parsedUser);
          } else {
            // Try to refresh tokens
            const refreshed = await refreshTokenWithStoredData(parsedTokens);
            if (!refreshed) {
              clearAuthData();
            }
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuthData();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const validateTokens = async (tokens: AuthTokens): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  };

  const refreshTokenWithStoredData = async (oldTokens: AuthTokens): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: oldTokens.refresh_token,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const newTokens: AuthTokens = {
          access_token: data.access_token,
          refresh_token: data.refresh_token,
          token_type: data.token_type,
          expires_in: data.expires_in,
        };

        setTokens(newTokens);
        setUser(data.user);
        
        localStorage.setItem('hive_tokens', JSON.stringify(newTokens));
        localStorage.setItem('hive_user', JSON.stringify(data.user));
        
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  const login = async (username: string, password: string): Promise<void> => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      const newTokens: AuthTokens = {
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        token_type: data.token_type,
        expires_in: data.expires_in,
      };

      setTokens(newTokens);
      setUser(data.user);

      // Store in localStorage
      localStorage.setItem('hive_tokens', JSON.stringify(newTokens));
      localStorage.setItem('hive_user', JSON.stringify(data.user));

    } catch (error: any) {
      throw new Error(error.message || 'Login failed');
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Call logout endpoint if we have a token
      if (tokens) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${tokens.access_token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      clearAuthData();
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    if (!tokens?.refresh_token) {
      return false;
    }

    return await refreshTokenWithStoredData(tokens);
  };

  const updateUser = (userData: Partial<User>): void => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem('hive_user', JSON.stringify(updatedUser));
    }
  };

  const clearAuthData = (): void => {
    setUser(null);
    setTokens(null);
    localStorage.removeItem('hive_tokens');
    localStorage.removeItem('hive_user');
  };

  const contextValue: AuthContextType = {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshToken,
    updateUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Hook for making authenticated API requests
export const useAuthenticatedFetch = () => {
  const { tokens, refreshToken, logout } = useAuth();

  const authenticatedFetch = async (url: string, options: RequestInit = {}): Promise<Response> => {
    if (!tokens) {
      throw new Error('No authentication tokens available');
    }

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
      'Authorization': `Bearer ${tokens.access_token}`,
    };

    let response = await fetch(url, {
      ...options,
      headers,
    });

    // If token expired, try to refresh and retry
    if (response.status === 401) {
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry with new token
        response = await fetch(url, {
          ...options,
          headers: {
            ...headers,
            'Authorization': `Bearer ${tokens.access_token}`,
          },
        });
      } else {
        // Refresh failed, logout user
        logout();
        throw new Error('Authentication expired');
      }
    }

    return response;
  };

  return authenticatedFetch;
};

export default AuthContext;