import React, { useEffect, useState } from 'react';
import { 
  ComputerDesktopIcon, 
  CpuChipIcon, 
  CircleStackIcon,
  CommandLineIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { clusterApi } from '../../services/api';

interface ClusterNode {
  id: string;
  hostname: string;
  ip: string;
  status: 'online' | 'offline';
  role: 'manager' | 'worker';
  hardware: {
    cpu: string;
    memory: string;
    gpu: string;
  };
  model_count: number;
  models: Array<{
    name: string;
    size: number;
  }>;
  metrics: {
    cpu_percent?: number;
    memory_percent?: number;
    disk_usage?: {
      total: number;
      used: number;
      free: number;
      percent: number;
    };
  };
  services: {
    ollama: string;
    cockpit: string;
  };
  last_check: string;
}

interface ClusterOverview {
  cluster_name: string;
  total_nodes: number;
  active_nodes: number;
  total_models: number;
  nodes: ClusterNode[];
  last_updated: string;
}

const ClusterNodes: React.FC = () => {
  const [overview, setOverview] = useState<ClusterOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchClusterOverview();
    const interval = setInterval(fetchClusterOverview, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchClusterOverview = async () => {
    try {
      const data = await clusterApi.getOverview();
      setOverview(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch cluster overview');
      console.error('Error fetching cluster overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'offline':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getHealthColor = (percent?: number) => {
    if (!percent) return 'bg-gray-200';
    if (percent < 70) return 'bg-green-500';
    if (percent < 90) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <XCircleIcon className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!overview) {
    return <div>No cluster data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Cluster Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Cluster Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <ComputerDesktopIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-600">Total Nodes</p>
                <p className="text-2xl font-bold text-blue-900">{overview.total_nodes}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-600">Active Nodes</p>
                <p className="text-2xl font-bold text-green-900">{overview.active_nodes}</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <CpuChipIcon className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-600">Total Models</p>
                <p className="text-2xl font-bold text-purple-900">{overview.total_models}</p>
              </div>
            </div>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center">
              <CircleStackIcon className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-600">Cluster Health</p>
                <p className="text-2xl font-bold text-orange-900">
                  {Math.round((overview.active_nodes / overview.total_nodes) * 100)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Node Details */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Cluster Nodes</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {overview.nodes.map((node) => (
              <div key={node.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <ComputerDesktopIcon className="h-6 w-6 text-gray-500 mr-2" />
                    <h4 className="text-lg font-medium text-gray-900">{node.hostname}</h4>
                    <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
                      node.role === 'manager' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {node.role}
                    </span>
                  </div>
                  <div className="flex items-center">
                    {getStatusIcon(node.status)}
                    <span className="ml-1 text-sm font-medium text-gray-700">
                      {node.status}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">IP Address</p>
                    <p className="text-sm font-medium text-gray-900">{node.ip}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Models</p>
                    <p className="text-sm font-medium text-gray-900">{node.model_count}</p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">CPU</p>
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{node.hardware.cpu}</p>
                      {node.metrics.cpu_percent && (
                        <span className="text-xs text-gray-500">
                          {node.metrics.cpu_percent.toFixed(1)}%
                        </span>
                      )}
                    </div>
                    {node.metrics.cpu_percent && (
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div 
                          className={`h-2 rounded-full ${getHealthColor(node.metrics.cpu_percent)}`}
                          style={{ width: `${node.metrics.cpu_percent}%` }}
                        />
                      </div>
                    )}
                  </div>

                  <div>
                    <p className="text-sm text-gray-600">Memory</p>
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{node.hardware.memory}</p>
                      {node.metrics.memory_percent && (
                        <span className="text-xs text-gray-500">
                          {node.metrics.memory_percent.toFixed(1)}%
                        </span>
                      )}
                    </div>
                    {node.metrics.memory_percent && (
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div 
                          className={`h-2 rounded-full ${getHealthColor(node.metrics.memory_percent)}`}
                          style={{ width: `${node.metrics.memory_percent}%` }}
                        />
                      </div>
                    )}
                  </div>

                  <div>
                    <p className="text-sm text-gray-600">GPU</p>
                    <p className="text-sm font-medium text-gray-900">{node.hardware.gpu}</p>
                  </div>
                </div>

                {node.metrics.disk_usage && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-600">Disk Usage</p>
                      <span className="text-xs text-gray-500">
                        {formatBytes(node.metrics.disk_usage.used)} / {formatBytes(node.metrics.disk_usage.total)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className={`h-2 rounded-full ${getHealthColor(node.metrics.disk_usage.percent)}`}
                        style={{ width: `${node.metrics.disk_usage.percent}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="flex space-x-2">
                  <a
                    href={node.services.ollama}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    <CommandLineIcon className="h-4 w-4 mr-1" />
                    Ollama
                  </a>
                  <a
                    href={node.services.cockpit}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    <ComputerDesktopIcon className="h-4 w-4 mr-1" />
                    Cockpit
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClusterNodes;