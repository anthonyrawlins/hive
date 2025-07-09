import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ComputerDesktopIcon,
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  CpuChipIcon,
  ServerIcon,
  BoltIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { agentApi } from '../services/api';

interface Agent {
  id: string;
  name: string;
  endpoint: string;
  model: string;
  specialty: string;
  status: 'online' | 'offline' | 'busy' | 'idle';
  max_concurrent: number;
  current_tasks: number;
  last_seen: string;
  capabilities?: string[];
  metrics?: {
    tasks_completed: number;
    uptime: string;
    response_time: number;
  };
}

export default function Agents() {
  const [showRegistrationForm, setShowRegistrationForm] = useState(false);
  const [newAgent, setNewAgent] = useState({
    name: '',
    endpoint: '',
    model: '',
    specialty: 'general',
    max_concurrent: 1
  });

  const { data: agents = [], isLoading, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      try {
        return await agentApi.getAgents();
      } catch (err) {
        // Return mock data if API fails
        return [
          {
            id: 'walnut',
            name: 'WALNUT',
            endpoint: 'http://192.168.1.27:11434',
            model: 'deepseek-coder-v2:latest',
            specialty: 'frontend',
            status: 'online',
            max_concurrent: 2,
            current_tasks: 1,
            last_seen: new Date().toISOString(),
            capabilities: ['React', 'TypeScript', 'TailwindCSS'],
            metrics: {
              tasks_completed: 45,
              uptime: '23h 45m',
              response_time: 2.3
            }
          },
          {
            id: 'ironwood',
            name: 'IRONWOOD', 
            endpoint: 'http://192.168.1.113:11434',
            model: 'qwen2.5-coder:latest',
            specialty: 'backend',
            status: 'online',
            max_concurrent: 2,
            current_tasks: 0,
            last_seen: new Date().toISOString(),
            capabilities: ['Python', 'FastAPI', 'PostgreSQL'],
            metrics: {
              tasks_completed: 32,
              uptime: '18h 12m',
              response_time: 1.8
            }
          },
          {
            id: 'acacia',
            name: 'ACACIA',
            endpoint: 'http://192.168.1.72:11434',
            model: 'qwen2.5:latest',
            specialty: 'documentation',
            status: 'offline',
            max_concurrent: 1,
            current_tasks: 0,
            last_seen: new Date(Date.now() - 3600000).toISOString(),
            capabilities: ['Documentation', 'Testing', 'QA'],
            metrics: {
              tasks_completed: 18,
              uptime: '0h 0m',
              response_time: 0
            }
          }
        ] as Agent[];
      }
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  const handleRegisterAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await agentApi.registerAgent?.(newAgent);
      setNewAgent({ name: '', endpoint: '', model: '', specialty: 'general', max_concurrent: 1 });
      setShowRegistrationForm(false);
      refetch();
    } catch (err) {
      console.error('Failed to register agent:', err);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'busy':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-pulse" />;
      case 'idle':
        return <ClockIcon className="h-5 w-5 text-blue-500" />;
      case 'offline':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
    switch (status) {
      case 'online':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'busy':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'idle':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'offline':
        return `${baseClasses} bg-red-100 text-red-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const onlineAgents = agents.filter((agent: Agent) => agent.status === 'online').length;
  const busyAgents = agents.filter((agent: Agent) => agent.status === 'busy').length;
  const totalTasks = agents.reduce((sum: number, agent: Agent) => sum + (agent.metrics?.tasks_completed || 0), 0);

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Agents</h1>
            <p className="text-gray-600">Manage AI agents in your distributed cluster</p>
          </div>
          <button
            onClick={() => setShowRegistrationForm(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Register Agent
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <ComputerDesktopIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{agents.length}</p>
              <p className="text-sm text-gray-500">Total Agents</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{onlineAgents}</p>
              <p className="text-sm text-gray-500">Online</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <BoltIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{busyAgents}</p>
              <p className="text-sm text-gray-500">Busy</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{totalTasks}</p>
              <p className="text-sm text-gray-500">Tasks Completed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {agents.map((agent: Agent) => (
          <div key={agent.id} className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow">
            {/* Agent Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <ServerIcon className="h-8 w-8 text-gray-600" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                  <p className="text-sm text-gray-500">{agent.specialty}</p>
                </div>
              </div>
              <span className={getStatusBadge(agent.status)}>
                {agent.status}
              </span>
            </div>

            {/* Agent Details */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Model</span>
                <span className="text-sm font-medium text-gray-900">{agent.model}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Tasks</span>
                <span className="text-sm font-medium text-gray-900">
                  {agent.current_tasks}/{agent.max_concurrent}
                </span>
              </div>

              {agent.metrics && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Completed</span>
                    <span className="text-sm font-medium text-gray-900">{agent.metrics.tasks_completed}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Uptime</span>
                    <span className="text-sm font-medium text-gray-900">{agent.metrics.uptime}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Response Time</span>
                    <span className="text-sm font-medium text-gray-900">{agent.metrics.response_time}s</span>
                  </div>
                </>
              )}
            </div>

            {/* Capabilities */}
            {agent.capabilities && agent.capabilities.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-gray-500 mb-2">Capabilities</p>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities.map((capability: string) => (
                    <span
                      key={capability}
                      className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-600"
                    >
                      {capability}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Status Indicator */}
            <div className="mt-4 flex items-center space-x-2">
              {getStatusIcon(agent.status)}
              <span className="text-sm text-gray-500">
                Last seen: {new Date(agent.last_seen).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Registration Form Modal */}
      {showRegistrationForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Register New Agent</h3>
              <form onSubmit={handleRegisterAgent} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={newAgent.name}
                    onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Endpoint</label>
                  <input
                    type="url"
                    value={newAgent.endpoint}
                    onChange={(e) => setNewAgent({ ...newAgent, endpoint: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="http://192.168.1.100:11434"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Model</label>
                  <input
                    type="text"
                    value={newAgent.model}
                    onChange={(e) => setNewAgent({ ...newAgent, model: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="deepseek-coder-v2:latest"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Specialty</label>
                  <select
                    value={newAgent.specialty}
                    onChange={(e) => setNewAgent({ ...newAgent, specialty: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="general">General</option>
                    <option value="frontend">Frontend</option>
                    <option value="backend">Backend</option>
                    <option value="documentation">Documentation</option>
                    <option value="testing">Testing</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Max Concurrent Tasks</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={newAgent.max_concurrent}
                    onChange={(e) => setNewAgent({ ...newAgent, max_concurrent: parseInt(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowRegistrationForm(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                  >
                    Register Agent
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}