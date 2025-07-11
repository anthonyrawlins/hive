import axios from 'axios';

// Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  username: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  name?: string; // For backward compatibility
  role?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}

export interface APIKey {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  created_at: string;
  last_used?: string;
  expires_at?: string;
  is_active: boolean;
}

export interface CreateAPIKeyRequest {
  name: string;
  scopes: string[];
  expires_in_days?: number;
}

export interface CreateAPIKeyResponse {
  api_key: APIKey;
  key: string; // Full key (only returned once)
}

// API client
const apiClient = axios.create({
  baseURL: process.env.VITE_API_BASE_URL || 'http://localhost:8087',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API functions
export const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
  const response = await apiClient.post('/api/auth/login', credentials);
  return response.data;
};

export const register = async (userData: RegisterRequest): Promise<AuthResponse> => {
  const response = await apiClient.post('/api/auth/register', userData);
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get('/api/auth/me');
  return response.data;
};

export const logout = async (): Promise<void> => {
  try {
    await apiClient.post('/api/auth/logout');
  } finally {
    // Always clear local storage even if API call fails
    localStorage.removeItem('token');
  }
};

export const refreshToken = async (): Promise<AuthResponse> => {
  const response = await apiClient.post('/api/auth/refresh');
  return response.data;
};

// API Key management
export const getAPIKeys = async (): Promise<APIKey[]> => {
  const response = await apiClient.get('/api/auth/api-keys');
  return response.data;
};

export const createAPIKey = async (data: CreateAPIKeyRequest): Promise<CreateAPIKeyResponse> => {
  const response = await apiClient.post('/api/auth/api-keys', data);
  return response.data;
};

export const revokeAPIKey = async (keyId: string): Promise<void> => {
  await apiClient.delete(`/api/auth/api-keys/${keyId}`);
};

export const updateAPIKey = async (keyId: string, data: Partial<CreateAPIKeyRequest>): Promise<APIKey> => {
  const response = await apiClient.put(`/api/auth/api-keys/${keyId}`, data);
  return response.data;
};

// Password management
export const changePassword = async (oldPassword: string, newPassword: string): Promise<void> => {
  await apiClient.post('/api/auth/change-password', {
    old_password: oldPassword,
    new_password: newPassword,
  });
};

export const requestPasswordReset = async (email: string): Promise<void> => {
  await apiClient.post('/api/auth/forgot-password', { email });
};

export const resetPassword = async (token: string, newPassword: string): Promise<void> => {
  await apiClient.post('/api/auth/reset-password', {
    token,
    new_password: newPassword,
  });
};

// Profile management
export const updateProfile = async (data: Partial<User>): Promise<User> => {
  const response = await apiClient.put('/api/auth/profile', data);
  return response.data;
};

export const verifyEmail = async (token: string): Promise<void> => {
  await apiClient.post('/api/auth/verify-email', { token });
};

export const resendVerificationEmail = async (): Promise<void> => {
  await apiClient.post('/api/auth/resend-verification');
};

export default {
  login,
  register,
  getCurrentUser,
  logout,
  refreshToken,
  getAPIKeys,
  createAPIKey,
  revokeAPIKey,
  updateAPIKey,
  changePassword,
  requestPasswordReset,
  resetPassword,
  updateProfile,
  verifyEmail,
  resendVerificationEmail,
};