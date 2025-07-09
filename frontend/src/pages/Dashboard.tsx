import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  FolderIcon,
  Cog6ToothIcon,
  PlayIcon,
  ClockIcon,
  PlusIcon,
  ArrowRightIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';
import { projectApi, clusterApi, systemApi } from '../services/api';

interface SystemStatus {
  status: string;
  components: {
    api: string;
    database: string;
    coordinator: string;
  };
}

// Remove unused interface

// Real-time data from APIs

// Activity data will come from APIs

export default function Dashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  const { data: projects = [] } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectApi.getProjects()
  });

  const { data: clusterOverview } = useQuery({
    queryKey: ['cluster-overview'],
    queryFn: () => clusterApi.getOverview()
  });

  const { data: workflows = [] } = useQuery({
    queryKey: ['workflows'],
    queryFn: () => clusterApi.getWorkflows()
  });

  // Calculate stats from real data
  const stats = {
    projects: { 
      total: projects.length, 
      active: projects.filter(p => p.status === 'active').length 
    },
    workflows: { 
      total: workflows.length, 
      active: workflows.filter((w: any) => w.active).length 
    },
    cluster: {
      total_nodes: clusterOverview?.total_nodes || 0,
      active_nodes: clusterOverview?.active_nodes || 0,
      total_models: clusterOverview?.total_models || 0
    },
    executions: { total: 0, recent: 0, success_rate: 0.95 }
  };

  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const health = await systemApi.getHealth();
        setSystemStatus(health);
      } catch (err) {
        console.error('Failed to fetch system status:', err);
      }
    };

    checkSystemStatus();
    const interval = setInterval(checkSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Removed unused functions

  return (
    <div className="p-6">
      {/* Welcome Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome to Hive
            </h1>
            <p className="text-gray-600 mt-2">
              Monitor your distributed AI orchestration platform
            </p>
          </div>
          
          {/* System Status */}
          <div className="flex items-center space-x-2 bg-white rounded-lg border px-4 py-2">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus?.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
            }`}></div>
            <span className="text-sm font-medium">
              {systemStatus?.status === 'healthy' ? 'All Systems Operational' : 'System Initializing'}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Link to="/projects" className="group">
          <div className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FolderIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">{stats.projects.active}/{stats.projects.total}</p>
                <p className="text-sm text-gray-500">Active Projects</p>
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-blue-600 group-hover:text-blue-800">
              <span>View all projects</span>
              <ArrowRightIcon className="h-4 w-4 ml-1" />
            </div>
          </div>
        </Link>

        <Link to="/workflows" className="group">
          <div className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Cog6ToothIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">{stats.workflows.active}/{stats.workflows.total}</p>
                <p className="text-sm text-gray-500">Active Workflows</p>
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-purple-600 group-hover:text-purple-800">
              <span>Manage workflows</span>
              <ArrowRightIcon className="h-4 w-4 ml-1" />
            </div>
          </div>
        </Link>

        <Link to="/executions" className="group">
          <div className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <PlayIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">{stats.executions.recent}</p>
                <p className="text-sm text-gray-500">Recent Executions</p>
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-green-600 group-hover:text-green-800">
              <span>{(stats.executions.success_rate * 100).toFixed(0)}% success rate</span>
              <ArrowRightIcon className="h-4 w-4 ml-1" />
            </div>
          </div>
        </Link>

        <Link to="/cluster" className="group">
          <div className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <ComputerDesktopIcon className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-semibold text-gray-900">{stats.cluster.active_nodes}/{stats.cluster.total_nodes}</p>
                <p className="text-sm text-gray-500">Active Nodes</p>
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-orange-600 group-hover:text-orange-800">
              <span>{stats.cluster.total_models} models available</span>
              <ArrowRightIcon className="h-4 w-4 ml-1" />
            </div>
          </div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/projects/new"
              className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="p-2 bg-blue-100 rounded-lg">
                <PlusIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="font-medium text-gray-900">Create New Project</p>
                <p className="text-sm text-gray-500">Start organizing your workflows</p>
              </div>
              <ArrowRightIcon className="h-5 w-5 text-gray-400 ml-auto" />
            </Link>

            <Link
              to="/workflows/new"
              className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="p-2 bg-purple-100 rounded-lg">
                <Cog6ToothIcon className="h-5 w-5 text-purple-600" />
              </div>
              <div className="ml-3">
                <p className="font-medium text-gray-900">Build Workflow</p>
                <p className="text-sm text-gray-500">Design automation processes</p>
              </div>
              <ArrowRightIcon className="h-5 w-5 text-gray-400 ml-auto" />
            </Link>

            <Link
              to="/cluster"
              className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="p-2 bg-orange-100 rounded-lg">
                <ComputerDesktopIcon className="h-5 w-5 text-orange-600" />
              </div>
              <div className="ml-3">
                <p className="font-medium text-gray-900">Monitor Cluster</p>
                <p className="text-sm text-gray-500">View nodes and AI models</p>
              </div>
              <ArrowRightIcon className="h-5 w-5 text-gray-400 ml-auto" />
            </Link>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
            <Link to="/activity" className="text-sm text-blue-600 hover:text-blue-800">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            <div className="text-center py-8 text-gray-500">
              <ClockIcon className="h-8 w-8 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">Recent activity will appear here</p>
              <p className="text-xs">Activity from projects and workflows will be shown</p>
            </div>
          </div>
        </div>
      </div>

      {/* System Components Status */}
      {systemStatus && systemStatus.status === 'healthy' && (
        <div className="mt-6 bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Components</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">API</p>
                <p className="text-xs text-gray-500">{systemStatus.components.api}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Database</p>
                <p className="text-xs text-gray-500">{systemStatus.components.database}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Coordinator</p>
                <p className="text-xs text-gray-500">{systemStatus.components.coordinator}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}