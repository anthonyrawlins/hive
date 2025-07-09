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
  EyeIcon
} from '@heroicons/react/24/outline';
import { executionApi } from '../services/api';
import { formatDistanceToNow, format } from 'date-fns';
import DataTable, { Column } from '../components/ui/DataTable';

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

export default function ExecutionsAdvanced() {
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const { data: executions = [], isLoading, refetch } = useQuery({
    queryKey: ['executions-analytics'],
    queryFn: async () => {
      try {
        return await executionApi.getExecutions();
      } catch (err) {
        // Return mock data if API fails
        return generateMockExecutions();
      }
    },
    refetchInterval: 5000 // Refresh every 5 seconds
  });

  const generateMockExecutions = (): WorkflowExecution[] => {
    const statuses: WorkflowExecution['status'][] = ['pending', 'running', 'completed', 'failed', 'cancelled'];
    const workflows = [
      'Customer Data Processing',
      'Machine Learning Pipeline',
      'Report Generation',
      'Data Validation',
      'System Backup',
      'Model Training',
      'API Integration Test',
      'Performance Analysis'
    ];

    return Array.from({ length: 50 }, (_, i) => {
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      const startTime = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
      const duration = status === 'completed' || status === 'failed' 
        ? Math.floor(Math.random() * 3600) 
        : undefined;
      
      return {
        id: `exec-${String(i + 1).padStart(3, '0')}`,
        workflow_id: `wf-${String(i + 1).padStart(3, '0')}`,
        workflow_name: workflows[Math.floor(Math.random() * workflows.length)],
        status,
        started_at: startTime.toISOString(),
        completed_at: duration ? new Date(startTime.getTime() + duration * 1000).toISOString() : undefined,
        duration,
        agent_id: `agent-${Math.floor(Math.random() * 5) + 1}`,
        error: status === 'failed' ? 'Connection timeout' : undefined,
        output: status === 'completed' ? { processed: Math.floor(Math.random() * 1000) } : undefined
      };
    });
  };

  const getStatusIcon = (status: WorkflowExecution['status']) => {
    const iconClass = "h-4 w-4";
    switch (status) {
      case 'pending':
        return <ClockIcon className={`${iconClass} text-yellow-500`} />;
      case 'running':
        return <PlayIcon className={`${iconClass} text-blue-500`} />;
      case 'completed':
        return <CheckCircleIcon className={`${iconClass} text-green-500`} />;
      case 'failed':
        return <XCircleIcon className={`${iconClass} text-red-500`} />;
      case 'cancelled':
        return <ExclamationTriangleIcon className={`${iconClass} text-gray-500`} />;
      default:
        return <ClockIcon className={`${iconClass} text-gray-400`} />;
    }
  };

  const getStatusBadge = (status: WorkflowExecution['status']) => {
    const baseClasses = "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'pending':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'running':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'cancelled':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '-';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const handleAction = (action: string, execution: WorkflowExecution) => {
    console.log(`${action} execution:`, execution.id);
    // Implement action logic here
    refetch();
  };

  const columns: Column<WorkflowExecution>[] = [
    {
      key: 'id',
      header: 'ID',
      sortable: true,
      filterable: true,
      width: 'w-32',
      render: (execution) => (
        <span className="font-mono text-sm">{execution.id}</span>
      )
    },
    {
      key: 'workflow_name',
      header: 'Workflow',
      sortable: true,
      filterable: true,
      render: (execution) => (
        <div>
          <div className="font-medium text-gray-900">{execution.workflow_name}</div>
          <div className="text-sm text-gray-500 font-mono">{execution.workflow_id}</div>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      filterable: true,
      filterType: 'select',
      filterOptions: [
        { label: 'Pending', value: 'pending' },
        { label: 'Running', value: 'running' },
        { label: 'Completed', value: 'completed' },
        { label: 'Failed', value: 'failed' },
        { label: 'Cancelled', value: 'cancelled' }
      ],
      render: (execution) => (
        <div className="flex items-center space-x-2">
          {getStatusIcon(execution.status)}
          <span className={getStatusBadge(execution.status)}>
            {execution.status.charAt(0).toUpperCase() + execution.status.slice(1)}
          </span>
        </div>
      )
    },
    {
      key: 'agent_id',
      header: 'Agent',
      sortable: true,
      filterable: true,
      render: (execution) => (
        <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
          {execution.agent_id}
        </span>
      )
    },
    {
      key: 'started_at',
      header: 'Started',
      sortable: true,
      render: (execution) => (
        <div>
          <div className="text-sm text-gray-900">
            {formatDistanceToNow(new Date(execution.started_at), { addSuffix: true })}
          </div>
          <div className="text-xs text-gray-500">
            {format(new Date(execution.started_at), 'MMM dd, HH:mm')}
          </div>
        </div>
      )
    },
    {
      key: 'duration',
      header: 'Duration',
      sortable: true,
      render: (execution) => (
        <span className="text-sm text-gray-900">
          {formatDuration(execution.duration)}
        </span>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (execution) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedExecution(execution);
              setShowDetails(true);
            }}
            className="text-blue-600 hover:text-blue-800"
            title="View Details"
          >
            <EyeIcon className="h-4 w-4" />
          </button>
          
          {execution.status === 'running' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleAction('stop', execution);
              }}
              className="text-red-600 hover:text-red-800"
              title="Stop Execution"
            >
              <StopIcon className="h-4 w-4" />
            </button>
          )}
          
          {(execution.status === 'failed' || execution.status === 'cancelled') && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleAction('retry', execution);
              }}
              className="text-green-600 hover:text-green-800"
              title="Retry Execution"
            >
              <ArrowPathIcon className="h-4 w-4" />
            </button>
          )}
        </div>
      )
    }
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Workflow Executions</h1>
        <p className="text-gray-600 mt-1">
          Monitor and manage workflow execution history with advanced filtering and sorting
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        {['all', 'pending', 'running', 'completed', 'failed'].map((status) => {
          const count = status === 'all' 
            ? executions.length 
            : executions.filter(e => e.status === status).length;
          
          return (
            <div key={status} className="bg-white rounded-lg shadow-sm border p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                    {status === 'all' ? 'Total' : status}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                </div>
                <div className="text-2xl">
                  {status === 'all' && '📊'}
                  {status === 'pending' && '⏳'}
                  {status === 'running' && '▶️'}
                  {status === 'completed' && '✅'}
                  {status === 'failed' && '❌'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Advanced Data Table */}
      <DataTable
        data={executions}
        columns={columns}
        loading={isLoading}
        searchPlaceholder="Search executions..."
        pageSize={15}
        emptyMessage="No executions found"
        onRowClick={(execution) => {
          setSelectedExecution(execution);
          setShowDetails(true);
        }}
      />

      {/* Details Modal */}
      {showDetails && selectedExecution && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
                 onClick={() => setShowDetails(false)} />
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Execution Details
                  </h3>
                  <button
                    onClick={() => setShowDetails(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircleIcon className="h-6 w-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">ID</label>
                      <p className="mt-1 text-sm text-gray-900 font-mono">{selectedExecution.id}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Status</label>
                      <div className="mt-1 flex items-center space-x-2">
                        {getStatusIcon(selectedExecution.status)}
                        <span className={getStatusBadge(selectedExecution.status)}>
                          {selectedExecution.status.charAt(0).toUpperCase() + selectedExecution.status.slice(1)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Workflow</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedExecution.workflow_name}</p>
                    <p className="text-xs text-gray-500 font-mono">{selectedExecution.workflow_id}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Started At</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {format(new Date(selectedExecution.started_at), 'PPpp')}
                      </p>
                    </div>
                    {selectedExecution.completed_at && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Completed At</label>
                        <p className="mt-1 text-sm text-gray-900">
                          {format(new Date(selectedExecution.completed_at), 'PPpp')}
                        </p>
                      </div>
                    )}
                  </div>
                  
                  {selectedExecution.duration && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Duration</label>
                      <p className="mt-1 text-sm text-gray-900">{formatDuration(selectedExecution.duration)}</p>
                    </div>
                  )}
                  
                  {selectedExecution.error && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Error</label>
                      <p className="mt-1 text-sm text-red-900 bg-red-50 p-2 rounded">{selectedExecution.error}</p>
                    </div>
                  )}
                  
                  {selectedExecution.output && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Output</label>
                      <pre className="mt-1 text-xs text-gray-900 bg-gray-50 p-3 rounded overflow-x-auto">
                        {JSON.stringify(selectedExecution.output, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  onClick={() => setShowDetails(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}