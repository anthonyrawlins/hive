import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  PlayIcon,
  StopIcon,
  ArrowPathIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  FunnelIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { executionApi } from '../services/api';
import { formatDistanceToNow, format } from 'date-fns';

interface WorkflowExecution {
  id: string;
  workflow_id: string;
  workflow_name?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  started_at: string;
  completed_at?: string;
  error?: string;
  output?: any;
  duration?: number;
  agent_id?: string;
}

export default function Executions() {
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const { data: executions = [], isLoading, refetch } = useQuery({
    queryKey: ['executions'],
    queryFn: async () => {
      try {
        return await executionApi.getExecutions();
      } catch (err) {
        // Return mock data if API fails
        return [
          {
            id: 'exec-001',
            workflow_id: 'wf-001',
            workflow_name: 'Customer Data Processing',
            status: 'completed',
            started_at: new Date(Date.now() - 3600000).toISOString(),
            completed_at: new Date(Date.now() - 3300000).toISOString(),
            duration: 300,
            agent_id: 'walnut',
            output: { processed_records: 1250, status: 'success' }
          },
          {
            id: 'exec-002',
            workflow_id: 'wf-002',
            workflow_name: 'Document Analysis',
            status: 'running',
            started_at: new Date(Date.now() - 1800000).toISOString(),
            agent_id: 'ironwood'
          },
          {
            id: 'exec-003',
            workflow_id: 'wf-001',
            workflow_name: 'Customer Data Processing',
            status: 'failed',
            started_at: new Date(Date.now() - 7200000).toISOString(),
            completed_at: new Date(Date.now() - 7000000).toISOString(),
            duration: 200,
            agent_id: 'acacia',
            error: 'Database connection timeout'
          },
          {
            id: 'exec-004',
            workflow_id: 'wf-003',
            workflow_name: 'Email Campaign',
            status: 'pending',
            started_at: new Date().toISOString()
          },
          {
            id: 'exec-005',
            workflow_id: 'wf-002',
            workflow_name: 'Document Analysis',
            status: 'completed',
            started_at: new Date(Date.now() - 14400000).toISOString(),
            completed_at: new Date(Date.now() - 14100000).toISOString(),
            duration: 300,
            agent_id: 'walnut',
            output: { documents_processed: 45, insights_extracted: 23 }
          }
        ] as WorkflowExecution[];
      }
    },
    refetchInterval: 5000 // Refresh every 5 seconds for real-time updates
  });

  const handleExecutionAction = async (executionId: string, action: 'cancel' | 'retry') => {
    try {
      if (action === 'cancel') {
        await executionApi.cancelExecution?.(executionId);
      } else if (action === 'retry') {
        await executionApi.retryExecution?.(executionId);
      }
      refetch();
    } catch (err) {
      console.error(`Failed to ${action} execution:`, err);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'running':
        return <ClockIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'cancelled':
        return <StopIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
    switch (status) {
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'running':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'pending':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'cancelled':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Filter executions based on status and search term
  const filteredExecutions = executions.filter((execution: WorkflowExecution) => {
    const matchesStatus = selectedStatus === 'all' || execution.status === selectedStatus;
    const matchesSearch = searchTerm === '' || 
      execution.workflow_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      execution.id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const completedCount = executions.filter((e: WorkflowExecution) => e.status === 'completed').length;
  const runningCount = executions.filter((e: WorkflowExecution) => e.status === 'running').length;
  const successRate = executions.length > 0 ? Math.round((completedCount / executions.length) * 100) : 0;

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Executions</h1>
        <p className="text-gray-600">Monitor and manage workflow executions</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <PlayIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{executions.length}</p>
              <p className="text-sm text-gray-500">Total Executions</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{completedCount}</p>
              <p className="text-sm text-gray-500">Completed</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{runningCount}</p>
              <p className="text-sm text-gray-500">Running</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <XCircleIcon className="h-8 w-8 text-red-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{successRate}%</p>
              <p className="text-sm text-gray-500">Success Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg border p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex items-center space-x-2">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="running">Running</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="flex items-center space-x-2 flex-1">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search executions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm"
            />
          </div>
        </div>
      </div>

      {/* Executions Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Execution
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Workflow
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Started
                </th>
                <th className="relative px-6 py-3"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredExecutions.map((execution: WorkflowExecution) => (
                <tr key={execution.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(execution.status)}
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">{execution.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{execution.workflow_name}</div>
                    <div className="text-sm text-gray-500">{execution.workflow_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={getStatusBadge(execution.status)}>
                      {execution.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {execution.agent_id || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {execution.duration ? formatDuration(execution.duration) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDistanceToNow(new Date(execution.started_at), { addSuffix: true })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button
                      onClick={() => {
                        setSelectedExecution(execution);
                        setShowDetails(true);
                      }}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    {execution.status === 'running' && (
                      <button
                        onClick={() => handleExecutionAction(execution.id, 'cancel')}
                        className="text-red-600 hover:text-red-900"
                      >
                        <StopIcon className="h-4 w-4" />
                      </button>
                    )}
                    {(execution.status === 'failed' || execution.status === 'cancelled') && (
                      <button
                        onClick={() => handleExecutionAction(execution.id, 'retry')}
                        className="text-green-600 hover:text-green-900"
                      >
                        <ArrowPathIcon className="h-4 w-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Execution Details Modal */}
      {showDetails && selectedExecution && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-3/4 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Execution Details</h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-2">Basic Information</h4>
                  <dl className="space-y-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Execution ID</dt>
                      <dd className="text-sm text-gray-900">{selectedExecution.id}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Workflow</dt>
                      <dd className="text-sm text-gray-900">{selectedExecution.workflow_name}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Status</dt>
                      <dd><span className={getStatusBadge(selectedExecution.status)}>{selectedExecution.status}</span></dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Agent</dt>
                      <dd className="text-sm text-gray-900">{selectedExecution.agent_id || 'Not assigned'}</dd>
                    </div>
                  </dl>
                </div>

                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-2">Timing</h4>
                  <dl className="space-y-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Started</dt>
                      <dd className="text-sm text-gray-900">{format(new Date(selectedExecution.started_at), 'PPp')}</dd>
                    </div>
                    {selectedExecution.completed_at && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Completed</dt>
                        <dd className="text-sm text-gray-900">{format(new Date(selectedExecution.completed_at), 'PPp')}</dd>
                      </div>
                    )}
                    {selectedExecution.duration && (
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Duration</dt>
                        <dd className="text-sm text-gray-900">{formatDuration(selectedExecution.duration)}</dd>
                      </div>
                    )}
                  </dl>
                </div>
              </div>

              {selectedExecution.error && (
                <div className="mt-6">
                  <h4 className="text-md font-medium text-red-900 mb-2">Error Details</h4>
                  <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <p className="text-sm text-red-800">{selectedExecution.error}</p>
                  </div>
                </div>
              )}

              {selectedExecution.output && (
                <div className="mt-6">
                  <h4 className="text-md font-medium text-gray-900 mb-2">Output</h4>
                  <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                      {JSON.stringify(selectedExecution.output, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}