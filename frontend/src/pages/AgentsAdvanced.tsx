import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CpuChipIcon,
  EyeIcon,
  TrashIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { agentApi } from '../services/api';
import { formatDistanceToNow, format } from 'date-fns';
import DataTable, { Column } from '../components/ui/DataTable';

interface Agent {
  id: string;
  name: string;
  model: string;
  specialty: string;
  endpoint: string;
  status: 'online' | 'offline' | 'busy' | 'error';
  last_seen: string;
  max_concurrent: number;
  current_tasks: number;
  total_tasks: number;
  success_rate: number;
  avg_response_time: number;
  version?: string;
  capabilities?: string[];
}

export default function AgentsAdvanced() {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const { data: agents = [], isLoading, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      try {
        return await agentApi.getAgents();
      } catch (err) {
        return generateMockAgents();
      }
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  const generateMockAgents = (): Agent[] => {
    const models = ['codellama:34b', 'codellama:13b', 'deepseek-coder:33b', 'llama2:70b', 'mistral:7b'];
    const specialties = ['kernel_dev', 'pytorch_dev', 'profiler', 'docs_writer', 'tester'];
    const statuses: Agent['status'][] = ['online', 'offline', 'busy', 'error'];
    const capabilities = [
      ['Python', 'JavaScript', 'TypeScript'],
      ['Rust', 'C++', 'Go'],
      ['React', 'Vue', 'Angular'],
      ['Docker', 'Kubernetes', 'DevOps'],
      ['Machine Learning', 'PyTorch', 'TensorFlow']
    ];

    return Array.from({ length: 15 }, (_, i) => {
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      const maxConcurrent = Math.floor(Math.random() * 5) + 1;
      const currentTasks = status === 'busy' ? maxConcurrent : Math.floor(Math.random() * maxConcurrent);
      const totalTasks = Math.floor(Math.random() * 1000) + 50;
      
      return {
        id: `agent-${String(i + 1).padStart(3, '0')}`,
        name: `Agent ${i + 1}`,
        model: models[Math.floor(Math.random() * models.length)],
        specialty: specialties[Math.floor(Math.random() * specialties.length)],
        endpoint: `http://192.168.1.${100 + i}:11434`,
        status,
        last_seen: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
        max_concurrent: maxConcurrent,
        current_tasks: currentTasks,
        total_tasks: totalTasks,
        success_rate: Math.floor(Math.random() * 30) + 70,
        avg_response_time: Math.floor(Math.random() * 5000) + 500,
        version: `1.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
        capabilities: capabilities[Math.floor(Math.random() * capabilities.length)]
      };
    });
  };

  const getStatusIcon = (status: Agent['status']) => {
    const iconClass = "h-4 w-4";
    switch (status) {
      case 'online':
        return <CheckCircleIcon className={`${iconClass} text-green-500`} />;
      case 'offline':
        return <XCircleIcon className={`${iconClass} text-gray-500`} />;
      case 'busy':
        return <ClockIcon className={`${iconClass} text-yellow-500`} />;
      case 'error':
        return <ExclamationTriangleIcon className={`${iconClass} text-red-500`} />;
      default:
        return <XCircleIcon className={`${iconClass} text-gray-400`} />;
    }
  };

  const getStatusBadge = (status: Agent['status']) => {
    const baseClasses = "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium";
    switch (status) {
      case 'online':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'offline':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      case 'busy':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'error':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getSpecialtyBadge = (specialty: string) => {
    const colors: Record<string, string> = {
      kernel_dev: 'bg-purple-100 text-purple-800',
      pytorch_dev: 'bg-orange-100 text-orange-800',
      profiler: 'bg-blue-100 text-blue-800',
      docs_writer: 'bg-green-100 text-green-800',
      tester: 'bg-indigo-100 text-indigo-800'
    };
    
    return `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[specialty] || 'bg-gray-100 text-gray-800'}`;
  };

  const handleAction = (action: string, agent: Agent) => {
    console.log(`${action} agent:`, agent.id);
    // Implement action logic here
    refetch();
  };

  const columns: Column<Agent>[] = [
    {
      key: 'name',
      header: 'Agent',
      sortable: true,
      filterable: true,
      render: (agent) => (
        <div>
          <div className="flex items-center space-x-2">
            <CpuChipIcon className="h-5 w-5 text-gray-400" />
            <div>
              <div className="font-medium text-gray-900">{agent.name}</div>
              <div className="text-sm text-gray-500 font-mono">{agent.id}</div>
            </div>
          </div>
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
        { label: 'Online', value: 'online' },
        { label: 'Offline', value: 'offline' },
        { label: 'Busy', value: 'busy' },
        { label: 'Error', value: 'error' }
      ],
      render: (agent) => (
        <div className="flex items-center space-x-2">
          {getStatusIcon(agent.status)}
          <span className={getStatusBadge(agent.status)}>
            {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
          </span>
        </div>
      )
    },
    {
      key: 'model',
      header: 'Model',
      sortable: true,
      filterable: true,
      render: (agent) => (
        <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
          {agent.model}
        </span>
      )
    },
    {
      key: 'specialty',
      header: 'Specialty',
      sortable: true,
      filterable: true,
      filterType: 'select',
      filterOptions: [
        { label: 'Kernel Dev', value: 'kernel_dev' },
        { label: 'PyTorch Dev', value: 'pytorch_dev' },
        { label: 'Profiler', value: 'profiler' },
        { label: 'Docs Writer', value: 'docs_writer' },
        { label: 'Tester', value: 'tester' }
      ],
      render: (agent) => (
        <span className={getSpecialtyBadge(agent.specialty)}>
          {agent.specialty.replace('_', ' ')}
        </span>
      )
    },
    {
      key: 'current_tasks',
      header: 'Load',
      sortable: true,
      render: (agent) => (
        <div className="text-center">
          <div className="text-sm font-medium text-gray-900">
            {agent.current_tasks}/{agent.max_concurrent}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
            <div 
              className={`h-1.5 rounded-full ${
                agent.current_tasks / agent.max_concurrent > 0.8 
                  ? 'bg-red-500' 
                  : agent.current_tasks / agent.max_concurrent > 0.6 
                  ? 'bg-yellow-500' 
                  : 'bg-green-500'
              }`}
              style={{ width: `${(agent.current_tasks / agent.max_concurrent) * 100}%` }}
            />
          </div>
        </div>
      )
    },
    {
      key: 'success_rate',
      header: 'Success Rate',
      sortable: true,
      render: (agent) => (
        <div className="text-center">
          <div className="text-sm font-medium text-gray-900">{agent.success_rate}%</div>
          <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
            <div 
              className={`h-1.5 rounded-full ${
                agent.success_rate >= 90 
                  ? 'bg-green-500' 
                  : agent.success_rate >= 80 
                  ? 'bg-yellow-500' 
                  : 'bg-red-500'
              }`}
              style={{ width: `${agent.success_rate}%` }}
            />
          </div>
        </div>
      )
    },
    {
      key: 'avg_response_time',
      header: 'Avg Response',
      sortable: true,
      render: (agent) => (
        <span className="text-sm text-gray-900">
          {agent.avg_response_time}ms
        </span>
      )
    },
    {
      key: 'last_seen',
      header: 'Last Seen',
      sortable: true,
      render: (agent) => (
        <div>
          <div className="text-sm text-gray-900">
            {formatDistanceToNow(new Date(agent.last_seen), { addSuffix: true })}
          </div>
          <div className="text-xs text-gray-500">
            {format(new Date(agent.last_seen), 'MMM dd, HH:mm')}
          </div>
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (agent) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedAgent(agent);
              setShowDetails(true);
            }}
            className="text-blue-600 hover:text-blue-800"
            title="View Details"
          >
            <EyeIcon className="h-4 w-4" />
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('refresh', agent);
            }}
            className="text-green-600 hover:text-green-800"
            title="Refresh Agent"
          >
            <ArrowPathIcon className="h-4 w-4" />
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('remove', agent);
            }}
            className="text-red-600 hover:text-red-800"
            title="Remove Agent"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Agents</h1>
          <p className="text-gray-600 mt-1">
            Manage and monitor your distributed AI agent network
          </p>
        </div>
        <button
          onClick={() => console.log('Registration form coming soon')}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Register Agent</span>
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {['online', 'busy', 'offline', 'error'].map((status) => {
          const count = agents.filter((a: Agent) => a.status === status).length;
          const totalTasks = agents.filter((a: Agent) => a.status === status).reduce((sum: number, a: Agent) => sum + a.current_tasks, 0);
          
          return (
            <div key={status} className="bg-white rounded-lg shadow-sm border p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                    {status}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                  <p className="text-xs text-gray-500">{totalTasks} active tasks</p>
                </div>
                <div className="text-2xl">
                  {status === 'online' && '🟢'}
                  {status === 'busy' && '🟡'}
                  {status === 'offline' && '⚫'}
                  {status === 'error' && '🔴'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Advanced Data Table */}
      <DataTable
        data={agents}
        columns={columns}
        loading={isLoading}
        searchPlaceholder="Search agents..."
        pageSize={12}
        emptyMessage="No agents registered"
        onRowClick={(agent) => {
          setSelectedAgent(agent);
          setShowDetails(true);
        }}
      />

      {/* Agent Details Modal */}
      {showDetails && selectedAgent && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
                 onClick={() => setShowDetails(false)} />
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Agent Details: {selectedAgent.name}
                  </h3>
                  <button
                    onClick={() => setShowDetails(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircleIcon className="h-6 w-6" />
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Basic Info */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">Basic Information</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">ID</label>
                        <p className="mt-1 text-sm text-gray-900 font-mono">{selectedAgent.id}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Status</label>
                        <div className="mt-1 flex items-center space-x-2">
                          {getStatusIcon(selectedAgent.status)}
                          <span className={getStatusBadge(selectedAgent.status)}>
                            {selectedAgent.status.charAt(0).toUpperCase() + selectedAgent.status.slice(1)}
                          </span>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Model</label>
                        <p className="mt-1 text-sm text-gray-900 font-mono">{selectedAgent.model}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Specialty</label>
                        <span className={getSpecialtyBadge(selectedAgent.specialty)}>
                          {selectedAgent.specialty.replace('_', ' ')}
                        </span>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Endpoint</label>
                        <p className="mt-1 text-sm text-gray-900 font-mono">{selectedAgent.endpoint}</p>
                      </div>
                      {selectedAgent.version && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Version</label>
                          <p className="mt-1 text-sm text-gray-900">{selectedAgent.version}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Performance Stats */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">Performance Statistics</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Current Load</label>
                        <div className="mt-1">
                          <div className="flex justify-between text-sm">
                            <span>{selectedAgent.current_tasks}/{selectedAgent.max_concurrent}</span>
                            <span>{Math.round((selectedAgent.current_tasks / selectedAgent.max_concurrent) * 100)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                            <div 
                              className={`h-2 rounded-full ${
                                selectedAgent.current_tasks / selectedAgent.max_concurrent > 0.8 
                                  ? 'bg-red-500' 
                                  : selectedAgent.current_tasks / selectedAgent.max_concurrent > 0.6 
                                  ? 'bg-yellow-500' 
                                  : 'bg-green-500'
                              }`}
                              style={{ width: `${(selectedAgent.current_tasks / selectedAgent.max_concurrent) * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Success Rate</label>
                        <div className="mt-1">
                          <div className="flex justify-between text-sm">
                            <span>{selectedAgent.success_rate}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                            <div 
                              className={`h-2 rounded-full ${
                                selectedAgent.success_rate >= 90 
                                  ? 'bg-green-500' 
                                  : selectedAgent.success_rate >= 80 
                                  ? 'bg-yellow-500' 
                                  : 'bg-red-500'
                              }`}
                              style={{ width: `${selectedAgent.success_rate}%` }}
                            />
                          </div>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Total Tasks Completed</label>
                        <p className="mt-1 text-sm text-gray-900">{selectedAgent.total_tasks.toLocaleString()}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Average Response Time</label>
                        <p className="mt-1 text-sm text-gray-900">{selectedAgent.avg_response_time}ms</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Last Seen</label>
                        <p className="mt-1 text-sm text-gray-900">
                          {formatDistanceToNow(new Date(selectedAgent.last_seen), { addSuffix: true })}
                        </p>
                        <p className="text-xs text-gray-500">
                          {format(new Date(selectedAgent.last_seen), 'PPpp')}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Capabilities */}
                {selectedAgent.capabilities && selectedAgent.capabilities.length > 0 && (
                  <div className="mt-6">
                    <h4 className="font-medium text-gray-900 mb-2">Capabilities</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedAgent.capabilities.map((capability, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {capability}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
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