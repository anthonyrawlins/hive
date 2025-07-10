/**
 * API Key Management Component
 * Provides interface for creating, viewing, and managing API keys
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Key, 
  Plus, 
  Copy, 
  Eye, 
  EyeOff, 
  Trash2, 
  CheckCircle, 
  AlertCircle,
  Calendar,
  Shield
} from 'lucide-react';
import { useAuthenticatedFetch } from '../../contexts/AuthContext';

interface APIKey {
  id: number;
  name: string;
  key_prefix: string;
  scopes: string[];
  is_active: boolean;
  last_used?: string;
  created_at: string;
  expires_at?: string;
}

interface CreateAPIKeyRequest {
  name: string;
  scopes: string[];
  expires_days?: number;
}

interface CreateAPIKeyResponse {
  api_key: APIKey;
  plain_key: string;
}

const API_SCOPES = [
  { id: 'read', label: 'Read Access', description: 'View data and resources' },
  { id: 'write', label: 'Write Access', description: 'Create and modify resources' },
  { id: 'admin', label: 'Admin Access', description: 'Full administrative access' },
  { id: 'agents', label: 'Agent Management', description: 'Manage AI agents' },
  { id: 'workflows', label: 'Workflow Management', description: 'Create and run workflows' },
  { id: 'monitoring', label: 'Monitoring', description: 'Access monitoring and metrics' }
];

export const APIKeyManager: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [showNewKey, setShowNewKey] = useState(false);
  const [copiedKeyId, setCopiedKeyId] = useState<number | null>(null);

  // Create form state
  const [createForm, setCreateForm] = useState({
    name: '',
    scopes: [] as string[],
    expires_days: undefined as number | undefined
  });

  const authenticatedFetch = useAuthenticatedFetch();

  useEffect(() => {
    loadAPIKeys();
  }, []);

  const loadAPIKeys = async () => {
    try {
      setIsLoading(true);
      const response = await authenticatedFetch('/api/auth/api-keys');
      
      if (response.ok) {
        const keys = await response.json();
        setApiKeys(keys);
      } else {
        setError('Failed to load API keys');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load API keys');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAPIKey = async () => {
    try {
      const requestData: CreateAPIKeyRequest = {
        name: createForm.name,
        scopes: createForm.scopes,
        ...(createForm.expires_days && { expires_days: createForm.expires_days })
      };

      const response = await authenticatedFetch('/api/auth/api-keys', {
        method: 'POST',
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const data: CreateAPIKeyResponse = await response.json();
        setNewKey(data.plain_key);
        setApiKeys(prev => [...prev, data.api_key]);
        
        // Reset form
        setCreateForm({
          name: '',
          scopes: [],
          expires_days: undefined
        });
        
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create API key');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create API key');
    }
  };

  const handleDeleteAPIKey = async (keyId: number, keyName: string) => {
    if (!confirm(`Are you sure you want to delete the API key "${keyName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await authenticatedFetch(`/api/auth/api-keys/${keyId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setApiKeys(prev => prev.filter(key => key.id !== keyId));
      } else {
        setError('Failed to delete API key');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete API key');
    }
  };

  const handleToggleAPIKey = async (keyId: number, isActive: boolean) => {
    try {
      const response = await authenticatedFetch(`/api/auth/api-keys/${keyId}/toggle`, {
        method: 'PATCH'
      });

      if (response.ok) {
        const updatedKey = await response.json();
        setApiKeys(prev => prev.map(key => key.id === keyId ? updatedKey : key));
      } else {
        setError('Failed to update API key status');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update API key status');
    }
  };

  const copyToClipboard = (text: string, keyId?: number) => {
    navigator.clipboard.writeText(text);
    if (keyId) {
      setCopiedKeyId(keyId);
      setTimeout(() => setCopiedKeyId(null), 2000);
    }
  };

  const handleScopeChange = (scope: string, checked: boolean) => {
    setCreateForm(prev => ({
      ...prev,
      scopes: checked 
        ? [...prev.scopes, scope]
        : prev.scopes.filter(s => s !== scope)
    }));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
          <p className="text-gray-600 mt-1">
            Manage API keys for programmatic access to Hive
          </p>
        </div>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create API Key
            </Button>
          </DialogTrigger>
          
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create New API Key</DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="key-name">Key Name</Label>
                <Input
                  id="key-name"
                  value={createForm.name}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Production API Key"
                  className="mt-1"
                />
              </div>

              <div>
                <Label>Scopes</Label>
                <div className="mt-2 space-y-2 max-h-48 overflow-y-auto">
                  {API_SCOPES.map(scope => (
                    <div key={scope.id} className="flex items-start space-x-3">
                      <Checkbox
                        id={scope.id}
                        checked={createForm.scopes.includes(scope.id)}
                        onCheckedChange={(checked) => handleScopeChange(scope.id, !!checked)}
                      />
                      <div>
                        <Label htmlFor={scope.id} className="text-sm font-medium">
                          {scope.label}
                        </Label>
                        <p className="text-xs text-gray-500">{scope.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <Label htmlFor="expires-days">Expiration (days)</Label>
                <Select 
                  value={createForm.expires_days?.toString() || ''} 
                  onValueChange={(value) => setCreateForm(prev => ({ 
                    ...prev, 
                    expires_days: value ? parseInt(value) : undefined 
                  }))}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Never expires" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Never expires</SelectItem>
                    <SelectItem value="7">7 days</SelectItem>
                    <SelectItem value="30">30 days</SelectItem>
                    <SelectItem value="90">90 days</SelectItem>
                    <SelectItem value="365">1 year</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button 
                onClick={handleCreateAPIKey}
                disabled={!createForm.name || createForm.scopes.length === 0}
                className="w-full"
              >
                Create API Key
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {newKey && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <p className="font-medium">API Key Created Successfully!</p>
              <p className="text-sm">
                Please copy your API key now. You won't be able to see it again.
              </p>
              <div className="flex items-center space-x-2 bg-gray-50 p-2 rounded">
                <code className="flex-1 text-sm">
                  {showNewKey ? newKey : '•'.repeat(40)}
                </code>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowNewKey(!showNewKey)}
                >
                  {showNewKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(newKey)}
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setNewKey(null)}
              >
                I've saved the key
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        {apiKeys.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Key className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No API Keys</h3>
              <p className="text-gray-600 mb-4">
                Create your first API key to start using the Hive API programmatically.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create API Key
              </Button>
            </CardContent>
          </Card>
        ) : (
          apiKeys.map(apiKey => (
            <Card key={apiKey.id}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">
                        {apiKey.name}
                      </h3>
                      <Badge variant={apiKey.is_active ? "default" : "secondary"}>
                        {apiKey.is_active ? "Active" : "Disabled"}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <Key className="w-4 h-4" />
                          <span>Key: {apiKey.key_prefix}...</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(`${apiKey.key_prefix}...`)}
                            className="h-auto p-1"
                          >
                            {copiedKeyId === apiKey.id ? (
                              <CheckCircle className="w-3 h-3 text-green-600" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </Button>
                        </div>
                        
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>Created: {formatDate(apiKey.created_at)}</span>
                        </div>
                        
                        {apiKey.last_used && (
                          <div className="flex items-center space-x-1">
                            <span>Last used: {formatDate(apiKey.last_used)}</span>
                          </div>
                        )}
                      </div>
                      
                      {apiKey.expires_at && (
                        <div className="flex items-center space-x-1 text-amber-600">
                          <Calendar className="w-4 h-4" />
                          <span>Expires: {formatDate(apiKey.expires_at)}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-1">
                        <Shield className="w-4 h-4" />
                        <span>Scopes:</span>
                        <div className="flex space-x-1">
                          {apiKey.scopes.map(scope => (
                            <Badge key={scope} variant="outline" className="text-xs">
                              {scope}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleAPIKey(apiKey.id, !apiKey.is_active)}
                    >
                      {apiKey.is_active ? 'Disable' : 'Enable'}
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteAPIKey(apiKey.id, apiKey.name)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default APIKeyManager;