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
  ExclamationTriangleIcon,
  CommandLineIcon,
  CloudIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';
import { agentApi } from '../services/api';

interface Agent {
  id: string;
  name: string;
  endpoint: string;
  model: string;
  specialty: string;
  status: 'online' | 'offline' | 'busy' | 'idle' | 'available';
  max_concurrent: number;
  current_tasks: number;
  last_seen: string;
  agent_type?: 'ollama' | 'cli';
  cli_config?: {
    host?: string;
    node_version?: string;
    model?: string;
    specialization?: string;
    max_concurrent?: number;
    command_timeout?: number;
    ssh_timeout?: number;
    agent_type?: string;
  };
  capabilities?: string[];
  metrics?: {
    tasks_completed: number;
    uptime: string;
    response_time: number;
  };
}

export default function Agents() {
  const [showRegistrationForm, setShowRegistrationForm] = useState(false);
  const [showCliRegistrationForm, setShowCliRegistrationForm] = useState(false);
  const [registrationMode, setRegistrationMode] = useState<'ollama' | 'cli'>('ollama');
  const [newAgent, setNewAgent] = useState({
    name: '',
    endpoint: '',
    model: '',
    specialty: 'general',
    max_concurrent: 1
  });
  const [newCliAgent, setNewCliAgent] = useState({
    id: '',
    host: '',
    node_version: '',
    model: 'gemini-2.5-pro',
    specialization: 'general_ai',
    max_concurrent: 2,
    command_timeout: 60,
    ssh_timeout: 5,
    agent_type: 'gemini'
  });

  const { data: agents = [], isLoading, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      try {
        return await agentApi.getAgents();
      } catch (err) {
        // Return mock data if API fails - mixed agent types
        return [
          {
            id: 'walnut-ollama',
            name: 'WALNUT',
            endpoint: 'http://192.168.1.27:11434',
            model: 'deepseek-coder-v2:latest',
            specialty: 'frontend',
            status: 'online',
            agent_type: 'ollama',
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
            id: 'ironwood-ollama',
            name: 'IRONWOOD', 
            endpoint: 'http://192.168.1.113:11434',
            model: 'qwen2.5-coder:latest',
            specialty: 'backend',
            status: 'online',
            agent_type: 'ollama',
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
            agent_type: 'ollama',
            max_concurrent: 1,
            current_tasks: 0,
            last_seen: new Date(Date.now() - 3600000).toISOString(),
            capabilities: ['Documentation', 'Testing', 'QA'],
            metrics: {
              tasks_completed: 18,
              uptime: '0h 0m',
              response_time: 0
            }
          },
          // CLI Agents
          {
            id: 'walnut-gemini',
            name: 'WALNUT-GEMINI',
            endpoint: 'cli://walnut',
            model: 'gemini-2.5-pro',
            specialty: 'general_ai',
            status: 'available',
            agent_type: 'cli',
            max_concurrent: 2,
            current_tasks: 0,
            last_seen: new Date().toISOString(),
            cli_config: {
              host: 'walnut',
              node_version: 'v22.14.0',
              model: 'gemini-2.5-pro',
              specialization: 'general_ai',
              command_timeout: 60,
              ssh_timeout: 5
            },
            capabilities: ['Advanced Reasoning', 'General AI', 'Multi-modal'],
            metrics: {
              tasks_completed: 12,
              uptime: '4h 23m',
              response_time: 3.1
            }
          },
          {
            id: 'ironwood-gemini',
            name: 'IRONWOOD-GEMINI',
            endpoint: 'cli://ironwood',
            model: 'gemini-2.5-pro',
            specialty: 'reasoning',
            status: 'available',
            agent_type: 'cli',
            max_concurrent: 2,
            current_tasks: 1,
            last_seen: new Date().toISOString(),
            cli_config: {
              host: 'ironwood',
              node_version: 'v22.17.0',
              model: 'gemini-2.5-pro',
              specialization: 'reasoning',
              command_timeout: 60,
              ssh_timeout: 5
            },
            capabilities: ['Complex Reasoning', 'Problem Solving', 'Analysis'],
            metrics: {
              tasks_completed: 8,
              uptime: '2h 15m',
              response_time: 2.7
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

  const handleRegisterCliAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await agentApi.registerCliAgent(newCliAgent);
      setNewCliAgent({
        id: '',
        host: '',
        node_version: '',
        model: 'gemini-2.5-pro',
        specialization: 'general_ai',
        max_concurrent: 2,
        command_timeout: 60,
        ssh_timeout: 5,
        agent_type: 'gemini'
      });
      setShowCliRegistrationForm(false);
      refetch();
    } catch (err) {
      console.error('Failed to register CLI agent:', err);
    }
  };

  const handleRegisterPredefinedAgents = async () => {
    try {
      await agentApi.registerPredefinedCliAgents();
      refetch();
    } catch (err) {
      console.error('Failed to register predefined CLI agents:', err);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'available':
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

  const getAgentTypeIcon = (agentType?: string) => {
    switch (agentType) {
      case 'cli':
        return <CommandLineIcon className="h-5 w-5 text-purple-500" />;
      case 'ollama':
      default:
        return <ServerIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getAgentTypeBadge = (agentType?: string) => {
    const baseClasses = 'inline-flex items-center px-2 py-1 rounded text-xs font-medium';
    switch (agentType) {
      case 'cli':
        return `${baseClasses} bg-purple-100 text-purple-800`;
      case 'ollama':
      default:
        return `${baseClasses} bg-blue-100 text-blue-800`;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
    switch (status) {
      case 'online':
      case 'available':
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

  // Ensure agents is an array before using filter/reduce
  const agentsArray = Array.isArray(agents) ? agents : [];
  const onlineAgents = agentsArray.filter((agent: Agent) => agent.status === 'online' || agent.status === 'available').length;
  const busyAgents = agentsArray.filter((agent: Agent) => agent.status === 'busy').length;
  const ollamaAgents = agentsArray.filter((agent: Agent) => !agent.agent_type || agent.agent_type === 'ollama').length;
  const cliAgents = agentsArray.filter((agent: Agent) => agent.agent_type === 'cli').length;
  const totalTasks = agentsArray.reduce((sum: number, agent: Agent) => sum + (agent.metrics?.tasks_completed || 0), 0);

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Agents</h1>
            <p className="text-gray-600">Manage AI agents in your distributed cluster</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleRegisterPredefinedAgents}
              className="inline-flex items-center px-4 py-2 border border-purple-600 rounded-md text-sm font-medium text-purple-600 bg-white hover:bg-purple-50"
            >
              <CommandLineIcon className="h-4 w-4 mr-2" />
              Quick Setup CLI
            </button>
            <div className="relative">
              <button
                onClick={() => setShowRegistrationForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Register Agent
                <ChevronDownIcon className="h-4 w-4 ml-1" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
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
            <ServerIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{ollamaAgents}</p>
              <p className="text-sm text-gray-500">Ollama Agents</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <CommandLineIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{cliAgents}</p>
              <p className="text-sm text-gray-500">CLI Agents</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{onlineAgents}</p>
              <p className="text-sm text-gray-500">Available</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-indigo-500" />
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
                {getAgentTypeIcon(agent.agent_type)}
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                    <span className={getAgentTypeBadge(agent.agent_type)}>
                      {agent.agent_type === 'cli' ? '⚡ CLI' : '🤖 API'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">{agent.specialty}</p>
                  {agent.cli_config?.host && (
                    <p className="text-xs text-purple-600">SSH: {agent.cli_config.host} (Node {agent.cli_config.node_version})</p>
                  )}
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
          <div className="relative top-10 mx-auto p-5 border w-[500px] shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Register New Agent</h3>
                <button
                  onClick={() => setShowRegistrationForm(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>
              
              {/* Agent Type Tabs */}
              <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
                <button
                  onClick={() => setRegistrationMode('ollama')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    registrationMode === 'ollama'
                      ? 'bg-white text-blue-600 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <ServerIcon className="h-4 w-4 inline mr-2" />
                  Ollama Agent
                </button>
                <button
                  onClick={() => setRegistrationMode('cli')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    registrationMode === 'cli'
                      ? 'bg-white text-purple-600 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <CommandLineIcon className="h-4 w-4 inline mr-2" />
                  CLI Agent
                </button>
              </div>
              
              {/* Ollama Agent Form */}
              {registrationMode === 'ollama' && (
                <form onSubmit={handleRegisterAgent} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Agent Name</label>
                    <input
                      type="text"
                      value={newAgent.name}
                      onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="e.g., WALNUT"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Endpoint URL</label>
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
                      <option value="kernel_dev">Kernel Development</option>
                      <option value="pytorch_dev">PyTorch Development</option>
                      <option value="profiler">Profiler</option>
                      <option value="docs_writer">Documentation</option>
                      <option value="tester">Testing</option>
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
                      <ServerIcon className="h-4 w-4 inline mr-2" />
                      Register Ollama Agent
                    </button>
                  </div>
                </form>
              )}
              
              {/* CLI Agent Form */}
              {registrationMode === 'cli' && (
                <form onSubmit={handleRegisterCliAgent} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Agent ID</label>
                    <input
                      type="text"
                      value={newCliAgent.id}
                      onChange={(e) => setNewCliAgent({ ...newCliAgent, id: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="e.g., walnut-gemini"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">SSH Host</label>
                    <select
                      value={newCliAgent.host}
                      onChange={(e) => setNewCliAgent({ ...newCliAgent, host: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="">Select host...</option>
                      <option value="walnut">WALNUT (192.168.1.27)</option>
                      <option value="ironwood">IRONWOOD (192.168.1.113)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Node.js Version</label>
                    <select
                      value={newCliAgent.node_version}
                      onChange={(e) => setNewCliAgent({ ...newCliAgent, node_version: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="">Select version...</option>
                      <option value="v22.14.0">v22.14.0 (WALNUT)</option>
                      <option value="v22.17.0">v22.17.0 (IRONWOOD)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Model</label>
                    <select
                      value={newCliAgent.model}
                      onChange={(e) => setNewCliAgent({ ...newCliAgent, model: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                      <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Specialization</label>
                    <select
                      value={newCliAgent.specialization}
                      onChange={(e) => setNewCliAgent({ ...newCliAgent, specialization: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="general_ai">General AI</option>
                      <option value="reasoning">Advanced Reasoning</option>
                      <option value="code_analysis">Code Analysis</option>
                      <option value="documentation">Documentation</option>
                      <option value="testing">Testing</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Max Concurrent</label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={newCliAgent.max_concurrent}
                        onChange={(e) => setNewCliAgent({ ...newCliAgent, max_concurrent: parseInt(e.target.value) })}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Timeout (sec)</label>
                      <input
                        type="number"
                        min="30"
                        max="300"
                        value={newCliAgent.command_timeout}
                        onChange={(e) => setNewCliAgent({ ...newCliAgent, command_timeout: parseInt(e.target.value) })}
                        className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                  </div>

                  <div className="bg-purple-50 p-3 rounded-md">
                    <p className="text-sm text-purple-700">
                      <CommandLineIcon className="h-4 w-4 inline mr-1" />
                      CLI agents require SSH access to the target machine and Gemini CLI installation.
                    </p>
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
                      className="px-4 py-2 text-sm font-medium text-white bg-purple-600 border border-transparent rounded-md hover:bg-purple-700"
                    >
                      <CommandLineIcon className="h-4 w-4 inline mr-2" />
                      Register CLI Agent
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}