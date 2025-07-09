import { useState } from 'react';
import {
  Cog6ToothIcon,
  ServerIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  BellIcon,
  ChartBarIcon,
  WrenchScrewdriverIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

type SettingsSection = 
  | 'general' 
  | 'cluster' 
  | 'users' 
  | 'security' 
  | 'notifications' 
  | 'monitoring' 
  | 'advanced' 
  | 'logs';

interface SettingsMenuItem {
  id: SettingsSection;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const settingsMenu: SettingsMenuItem[] = [
  {
    id: 'general',
    name: 'General',
    description: 'Basic system configuration and preferences',
    icon: Cog6ToothIcon
  },
  {
    id: 'cluster',
    name: 'Cluster Management',
    description: 'Configure cluster nodes, models, and resources',
    icon: ServerIcon
  },
  {
    id: 'users',
    name: 'User Management',
    description: 'Manage users, roles, and permissions',
    icon: UserGroupIcon
  },
  {
    id: 'security',
    name: 'Security',
    description: 'Authentication, authorization, and security policies',
    icon: ShieldCheckIcon
  },
  {
    id: 'notifications',
    name: 'Notifications',
    description: 'Configure alerts, webhooks, and notification channels',
    icon: BellIcon
  },
  {
    id: 'monitoring',
    name: 'Monitoring',
    description: 'Metrics collection, retention, and dashboard settings',
    icon: ChartBarIcon
  },
  {
    id: 'advanced',
    name: 'Advanced',
    description: 'System tuning, performance optimization, and debugging',
    icon: WrenchScrewdriverIcon
  },
  {
    id: 'logs',
    name: 'Logs & Audit',
    description: 'Log management, audit trails, and compliance',
    icon: DocumentTextIcon
  }
];

export default function Settings() {
  const [activeSection, setActiveSection] = useState<SettingsSection>('general');

  const renderSettingsContent = () => {
    switch (activeSection) {
      case 'general':
        return <GeneralSettings />;
      case 'cluster':
        return <ClusterSettings />;
      case 'users':
        return <UserManagementSettings />;
      case 'security':
        return <SecuritySettings />;
      case 'notifications':
        return <NotificationSettings />;
      case 'monitoring':
        return <MonitoringSettings />;
      case 'advanced':
        return <AdvancedSettings />;
      case 'logs':
        return <LogsSettings />;
      default:
        return <GeneralSettings />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-2">
            Configure and manage your Hive distributed AI platform
          </p>
        </div>

        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Configuration</h2>
              </div>
              <nav className="p-2">
                {settingsMenu.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full text-left p-3 rounded-lg mb-1 transition-colors ${
                      activeSection === item.id
                        ? 'bg-blue-50 text-blue-900 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <item.icon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${
                        activeSection === item.id ? 'text-blue-600' : 'text-gray-400'
                      }`} />
                      <div>
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-gray-500 mt-1">{item.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-white rounded-lg shadow-sm border">
              {renderSettingsContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// General Settings Component
function GeneralSettings() {
  const [settings, setSettings] = useState({
    systemName: 'Hive Development Cluster',
    description: 'Distributed AI development platform for collaborative coding',
    timezone: 'Australia/Melbourne',
    language: 'en-US',
    autoRefresh: true,
    refreshInterval: 30
  });

  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">General Settings</h2>
        <p className="text-gray-600 mt-1">Basic system configuration and preferences</p>
      </div>

      <div className="space-y-6">
        {/* System Information */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                System Name
              </label>
              <input
                type="text"
                value={settings.systemName}
                onChange={(e) => setSettings({...settings, systemName: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timezone
              </label>
              <select
                value={settings.timezone}
                onChange={(e) => setSettings({...settings, timezone: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="Australia/Melbourne">Australia/Melbourne</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">America/New_York</option>
                <option value="Europe/London">Europe/London</option>
              </select>
            </div>
          </div>
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={settings.description}
              onChange={(e) => setSettings({...settings, description: e.target.value})}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Interface Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Interface Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-900">Auto Refresh</label>
                <p className="text-sm text-gray-500">Automatically refresh data in real-time</p>
              </div>
              <button
                onClick={() => setSettings({...settings, autoRefresh: !settings.autoRefresh})}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  settings.autoRefresh ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    settings.autoRefresh ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            
            {settings.autoRefresh && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Refresh Interval (seconds)
                </label>
                <input
                  type="number"
                  min="5"
                  max="300"
                  value={settings.refreshInterval}
                  onChange={(e) => setSettings({...settings, refreshInterval: parseInt(e.target.value)})}
                  className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="pt-6 border-t">
          <div className="flex space-x-3">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm font-medium">
              Save Changes
            </button>
            <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 text-sm font-medium">
              Reset to Defaults
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Cluster Settings Component
function ClusterSettings() {
  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Cluster Management</h2>
        <p className="text-gray-600 mt-1">Configure cluster nodes, models, and resources</p>
      </div>

      <div className="space-y-6">
        {/* Cluster Nodes */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Cluster Nodes</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900">WALNUT</h4>
                <p className="text-sm text-gray-500 mt-1">Primary Node</p>
                <div className="mt-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Online
                  </span>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900">IRONWOOD</h4>
                <p className="text-sm text-gray-500 mt-1">GPU Node - 2x GTX 1070 + 2x Tesla P4</p>
                <div className="mt-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Online
                  </span>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900">ACACIA</h4>
                <p className="text-sm text-gray-500 mt-1">Secondary Node</p>
                <div className="mt-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    Offline
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Model Configuration */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Model Configuration</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">Default Model</h4>
                <p className="text-sm text-gray-500">Primary model for new tasks</p>
              </div>
              <select className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="codellama:34b">CodeLlama 34B</option>
                <option value="codellama:13b">CodeLlama 13B</option>
                <option value="deepseek-coder:33b">DeepSeek Coder 33B</option>
              </select>
            </div>
          </div>
        </div>

        {/* Resource Limits */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Resource Limits</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Concurrent Tasks per Node
              </label>
              <input
                type="number"
                min="1"
                max="10"
                defaultValue="2"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Task Timeout (minutes)
              </label>
              <input
                type="number"
                min="5"
                max="120"
                defaultValue="30"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// User Management Settings Component
function UserManagementSettings() {
  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">User Management</h2>
        <p className="text-gray-600 mt-1">Manage users, roles, and permissions</p>
      </div>

      <div className="space-y-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-blue-900 mb-2">Development Mode</h3>
          <p className="text-blue-800">
            User management is currently in development mode. Only the demo admin account is available.
            Full user management features will be implemented in a future release.
          </p>
        </div>

        {/* Current Users */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Current Users</h3>
          <div className="bg-white border rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-medium text-sm">A</span>
                      </div>
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">Administrator</div>
                        <div className="text-sm text-gray-500">admin@hive.local</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      Administrator
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Active
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    Just now
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Security Settings Component
function SecuritySettings() {
  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Security Settings</h2>
        <p className="text-gray-600 mt-1">Authentication, authorization, and security policies</p>
      </div>

      <div className="space-y-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-yellow-900 mb-2">Demo Mode</h3>
          <p className="text-yellow-800">
            Security features are currently in demo mode. Authentication uses mock tokens and 
            passwords are not encrypted. Do not use in production environments.
          </p>
        </div>

        {/* Authentication Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Authentication</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">Session Timeout</h4>
                <p className="text-sm text-gray-500">Automatic logout after inactivity</p>
              </div>
              <select className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="30">30 minutes</option>
                <option value="60">1 hour</option>
                <option value="240">4 hours</option>
                <option value="480">8 hours</option>
              </select>
            </div>
            
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">Remember Login</h4>
                <p className="text-sm text-gray-500">Allow users to stay logged in across sessions</p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
              </button>
            </div>
          </div>
        </div>

        {/* API Security */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">API Security</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Rate Limit (requests per minute)
              </label>
              <input
                type="number"
                min="10"
                max="1000"
                defaultValue="60"
                className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">CORS Enabled</h4>
                <p className="text-sm text-gray-500">Allow cross-origin requests</p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Notification Settings Component
function NotificationSettings() {
  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Notification Settings</h2>
        <p className="text-gray-600 mt-1">Configure alerts, webhooks, and notification channels</p>
      </div>

      <div className="space-y-6">
        {/* Email Notifications */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Email Notifications</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">Task Completion</h4>
                <p className="text-sm text-gray-500">Notify when tasks complete or fail</p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
              </button>
            </div>
            
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">System Alerts</h4>
                <p className="text-sm text-gray-500">Notify about system issues and maintenance</p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Webhook Configuration */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Webhook Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Webhook URL
              </label>
              <input
                type="url"
                placeholder="https://your-webhook-endpoint.com/hive"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Events to Send
              </label>
              <div className="space-y-2">
                {['task.completed', 'task.failed', 'agent.registered', 'system.alert'].map((event) => (
                  <label key={event} className="flex items-center">
                    <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                    <span className="ml-2 text-sm text-gray-700">{event}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Monitoring Settings Component
function MonitoringSettings() {
  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Monitoring Settings</h2>
        <p className="text-gray-600 mt-1">Metrics collection, retention, and dashboard settings</p>
      </div>

      <div className="space-y-6">
        {/* Metrics Collection */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Metrics Collection</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Collection Interval (seconds)
              </label>
              <input
                type="number"
                min="10"
                max="300"
                defaultValue="30"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Retention Period (days)
              </label>
              <input
                type="number"
                min="1"
                max="365"
                defaultValue="30"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Performance Monitoring */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Monitoring</h3>
          <div className="space-y-4">
            {['CPU Usage', 'Memory Usage', 'GPU Utilization', 'Network I/O', 'Disk I/O'].map((metric) => (
              <div key={metric} className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{metric}</h4>
                  <p className="text-sm text-gray-500">Monitor {metric.toLowerCase()} across cluster nodes</p>
                </div>
                <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Advanced Settings Component
function AdvancedSettings() {
  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Advanced Settings</h2>
        <p className="text-gray-600 mt-1">System tuning, performance optimization, and debugging</p>
      </div>

      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-red-900 mb-2">Warning</h3>
          <p className="text-red-800">
            These settings are for advanced users only. Incorrect configuration may impact system performance or stability.
          </p>
        </div>

        {/* Debug Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Debug & Logging</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Log Level
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="ERROR">ERROR</option>
                <option value="WARN">WARN</option>
                <option value="INFO" selected>INFO</option>
                <option value="DEBUG">DEBUG</option>
              </select>
            </div>
            
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">Enable Debug Mode</h4>
                <p className="text-sm text-gray-500">Show detailed error messages and stack traces</p>
              </div>
              <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200">
                <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-1" />
              </button>
            </div>
          </div>
        </div>

        {/* Performance Tuning */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Tuning</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Connection Pool Size
              </label>
              <input
                type="number"
                min="5"
                max="100"
                defaultValue="20"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Worker Threads
              </label>
              <input
                type="number"
                min="1"
                max="16"
                defaultValue="4"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Logs Settings Component
function LogsSettings() {
  return (
    <div className="p-6">
      <div className="border-b pb-4 mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Logs & Audit</h2>
        <p className="text-gray-600 mt-1">Log management, audit trails, and compliance</p>
      </div>

      <div className="space-y-6">
        {/* Log Management */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Log Management</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Log Retention (days)
              </label>
              <input
                type="number"
                min="1"
                max="365"
                defaultValue="90"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Log File Size (MB)
              </label>
              <input
                type="number"
                min="10"
                max="1000"
                defaultValue="100"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Audit Trail */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Audit Trail</h3>
          <div className="space-y-4">
            {['User Authentication', 'Task Execution', 'Configuration Changes', 'API Access'].map((event) => (
              <div key={event} className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{event}</h4>
                  <p className="text-sm text-gray-500">Log {event.toLowerCase()} events</p>
                </div>
                <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                  <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Export Options */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Export Options</h3>
          <div className="flex space-x-3">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm font-medium">
              Export System Logs
            </button>
            <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-50 text-sm font-medium">
              Export Audit Trail
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}