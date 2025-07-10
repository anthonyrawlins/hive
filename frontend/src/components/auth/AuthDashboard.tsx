/**
 * Authentication Dashboard Component
 * Main dashboard for authentication and authorization management
 */

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  User, 
  Key, 
  Shield, 
  Clock, 
  Settings, 
  LogOut,
  Calendar,
  Activity
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { APIKeyManager } from './APIKeyManager';

export const AuthDashboard: React.FC = () => {
  const { user, tokens, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  const handleLogout = async () => {
    await logout();
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTokenExpirationTime = () => {
    if (!tokens?.access_token) return null;
    
    try {
      const payload = JSON.parse(atob(tokens.access_token.split('.')[1]));
      return new Date(payload.exp * 1000);
    } catch {
      return null;
    }
  };

  const tokenExpiration = getTokenExpirationTime();
  const isTokenExpiringSoon = tokenExpiration && (tokenExpiration.getTime() - Date.now()) < 5 * 60 * 1000; // 5 minutes

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Authentication Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Manage your account, tokens, and API keys
            </p>
          </div>
          
          <Button onClick={handleLogout} variant="outline">
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </Button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Account Status</p>
                  <p className="font-medium">
                    {user?.is_active ? 'Active' : 'Inactive'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Shield className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Role</p>
                  <p className="font-medium">
                    {user?.is_superuser ? 'Administrator' : 'User'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${isTokenExpiringSoon ? 'bg-red-100' : 'bg-yellow-100'}`}>
                  <Clock className={`w-5 h-5 ${isTokenExpiringSoon ? 'text-red-600' : 'text-yellow-600'}`} />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Token Expires</p>
                  <p className="font-medium text-xs">
                    {tokenExpiration ? formatDate(tokenExpiration.toISOString()) : 'Unknown'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Activity className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Last Login</p>
                  <p className="font-medium text-xs">
                    {formatDate(user?.last_login)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="api-keys">API Keys</TabsTrigger>
            <TabsTrigger value="tokens">Tokens</TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="w-5 h-5" />
                  <span>User Profile</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Username</label>
                    <p className="mt-1 text-gray-900">{user?.username}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Email</label>
                    <p className="mt-1 text-gray-900">{user?.email}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Full Name</label>
                    <p className="mt-1 text-gray-900">{user?.full_name || 'Not set'}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Account Created</label>
                    <p className="mt-1 text-gray-900">{formatDate(user?.created_at)}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 pt-4">
                  <Badge variant={user?.is_active ? "default" : "secondary"}>
                    {user?.is_active ? "Active" : "Inactive"}
                  </Badge>
                  
                  <Badge variant={user?.is_verified ? "default" : "secondary"}>
                    {user?.is_verified ? "Verified" : "Unverified"}
                  </Badge>
                  
                  {user?.is_superuser && (
                    <Badge variant="destructive">
                      Administrator
                    </Badge>
                  )}
                </div>

                <div className="pt-4 border-t">
                  <Button variant="outline">
                    <Settings className="w-4 h-4 mr-2" />
                    Edit Profile
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api-keys">
            <APIKeyManager />
          </TabsContent>

          <TabsContent value="tokens" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Key className="w-5 h-5" />
                  <span>Authentication Tokens</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">Access Token</h4>
                      <Badge variant={isTokenExpiringSoon ? "destructive" : "default"}>
                        {isTokenExpiringSoon ? "Expiring Soon" : "Active"}
                      </Badge>
                    </div>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4" />
                        <span>
                          Expires: {tokenExpiration ? formatDate(tokenExpiration.toISOString()) : 'Unknown'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Key className="w-4 h-4" />
                        <span>Type: Bearer Token</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">Refresh Token</h4>
                      <Badge variant="secondary">
                        Available
                      </Badge>
                    </div>
                    <div className="space-y-2 text-sm text-gray-600">
                      <p>Used to automatically refresh access tokens when they expire.</p>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <div className="flex space-x-2">
                    <Button variant="outline">
                      Refresh Token
                    </Button>
                    <Button variant="outline" onClick={handleLogout}>
                      Revoke All Tokens
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Token Usage Guidelines</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div>
                    <h5 className="font-medium">Bearer Token Authentication</h5>
                    <p className="text-gray-600">
                      Include your access token in API requests using the Authorization header:
                    </p>
                    <code className="block mt-1 p-2 bg-gray-100 rounded text-xs">
                      Authorization: Bearer YOUR_ACCESS_TOKEN
                    </code>
                  </div>
                  
                  <div>
                    <h5 className="font-medium">Token Security</h5>
                    <ul className="list-disc list-inside text-gray-600 space-y-1">
                      <li>Never share your tokens with others</li>
                      <li>Use HTTPS for all API requests</li>
                      <li>Store tokens securely in your applications</li>
                      <li>Revoke tokens if they may be compromised</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AuthDashboard;