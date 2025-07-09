import React, { useEffect, useState } from 'react';
import { 
  PlayIcon, 
  PauseIcon, 
  ClockIcon, 
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  LinkIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';
import { clusterApi } from '../../services/api';

interface Workflow {
  id: string;
  name: string;
  active: boolean;
  created_at: string;
  updated_at: string;
  tags: string[];
  node_count: number;
  webhook_url?: string;
  description: string;
}

interface WorkflowExecution {
  id: string;
  workflow_id: string;
  mode: string;
  status: string;
  started_at: string;
  finished_at?: string;
  duration?: number;
}

const WorkflowDashboard: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkflowData();
    const interval = setInterval(fetchWorkflowData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchWorkflowData = async () => {
    try {
      const [workflows, executions] = await Promise.all([
        clusterApi.getWorkflows(),
        clusterApi.getExecutions()
      ]);
      
      setWorkflows(workflows);
      setExecutions(executions);
      setError(null);
    } catch (err) {
      setError('Failed to fetch workflow data');
      console.error('Error fetching workflow data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'running':
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
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

  const activeWorkflows = workflows.filter(w => w.active);
  const inactiveWorkflows = workflows.filter(w => !w.active);

  return (
    <div className="space-y-6">
      {/* Workflow Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">n8n Workflow Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <CpuChipIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-600">Total Workflows</p>
                <p className="text-2xl font-bold text-blue-900">{workflows.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <PlayIcon className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-600">Active</p>
                <p className="text-2xl font-bold text-green-900">{activeWorkflows.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center">
              <PauseIcon className="h-8 w-8 text-gray-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Inactive</p>
                <p className="text-2xl font-bold text-gray-900">{inactiveWorkflows.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <ClockIcon className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-600">Recent Executions</p>
                <p className="text-2xl font-bold text-purple-900">{executions.length}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Active Workflows */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Active Workflows</h3>
        </div>
        <div className="p-6">
          {activeWorkflows.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No active workflows</p>
          ) : (
            <div className="space-y-4">
              {activeWorkflows.map((workflow) => (
                <div key={workflow.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <PlayIcon className="h-5 w-5 text-green-500 mr-2" />
                      <h4 className="text-lg font-medium text-gray-900">{workflow.name}</h4>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                        Active
                      </span>
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                        {workflow.node_count} nodes
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{workflow.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">
                        Updated: {formatDate(workflow.updated_at)}
                      </span>
                      {workflow.tags.length > 0 && (
                        <div className="flex space-x-1">
                          {workflow.tags.map((tag, index) => (
                            <span key={index} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    {workflow.webhook_url && (
                      <a
                        href={workflow.webhook_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 hover:bg-gray-50"
                      >
                        <LinkIcon className="h-4 w-4 mr-1" />
                        Webhook
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Executions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Executions</h3>
        </div>
        <div className="p-6">
          {executions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No recent executions</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Mode
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Started
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Workflow ID
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {executions.map((execution) => (
                    <tr key={execution.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getStatusIcon(execution.status)}
                          <span className="ml-2 text-sm font-medium text-gray-900">
                            {execution.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {execution.mode}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(execution.started_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDuration(execution.duration)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {execution.workflow_id}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Inactive Workflows */}
      {inactiveWorkflows.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Inactive Workflows</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {inactiveWorkflows.map((workflow) => (
                <div key={workflow.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <PauseIcon className="h-5 w-5 text-gray-500 mr-2" />
                      <h4 className="text-lg font-medium text-gray-700">{workflow.name}</h4>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                        Inactive
                      </span>
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                        {workflow.node_count} nodes
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{workflow.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      Updated: {formatDate(workflow.updated_at)}
                    </span>
                    {workflow.webhook_url && (
                      <a
                        href={workflow.webhook_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 hover:bg-gray-50"
                      >
                        <LinkIcon className="h-4 w-4 mr-1" />
                        Webhook
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowDashboard;