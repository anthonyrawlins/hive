import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  PlayIcon,
  PauseIcon,
  ChartBarIcon,
  ClockIcon,
  TagIcon,
  Cog6ToothIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon as ClockIconOutline
} from '@heroicons/react/24/outline';
import { Tab } from '@headlessui/react';
import { formatDistanceToNow, format } from 'date-fns';
import { projectApi } from '../../services/api';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedTabIndex, setSelectedTabIndex] = useState(0);

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', id],
    queryFn: async () => {
      if (!id) throw new Error('Project ID is required');
      return await projectApi.getProject(id);
    },
    enabled: !!id
  });

  const { data: workflows = [] } = useQuery({
    queryKey: ['project', id, 'workflows'],
    queryFn: async () => {
      if (!id) throw new Error('Project ID is required');
      return await projectApi.getProjectWorkflows(id);
    },
    enabled: !!id
  });

  const { data: executions = [] } = useQuery({
    queryKey: ['project', id, 'executions'],
    queryFn: async () => {
      if (!id) throw new Error('Project ID is required');
      return await projectApi.getProjectExecutions(id);
    },
    enabled: !!id
  });

  const { data: metrics } = useQuery({
    queryKey: ['project', id, 'metrics'],
    queryFn: async () => {
      if (!id) throw new Error('Project ID is required');
      return await projectApi.getProjectMetrics(id);
    },
    enabled: !!id
  });

  const getStatusBadge = (status: string) => {
    const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
    switch (status) {
      case 'active':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'inactive':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      case 'draft':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'running':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'pending':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getExecutionIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'running':
        return <ClockIconOutline className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <ClockIconOutline className="h-5 w-5 text-gray-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="h-32 bg-gray-200 rounded mb-6"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Project not found</h2>
          <p className="text-gray-600 mb-4">The project you're looking for doesn't exist or has been deleted.</p>
          <button
            onClick={() => navigate('/projects')}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { name: 'Overview', count: null },
    { name: 'Workflows', count: workflows.length },
    { name: 'Executions', count: executions.length },
    { name: 'Settings', count: null }
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center space-x-4 mb-4">
          <button
            onClick={() => navigate('/projects')}
            className="flex items-center text-gray-500 hover:text-gray-700"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-1" />
            Back to Projects
          </button>
        </div>

        <div className="flex justify-between items-start">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              <span className={getStatusBadge(project.status)}>
                {project.status}
              </span>
            </div>
            <p className="text-gray-600 max-w-3xl">{project.description}</p>
            
            {/* Tags */}
            {project.tags && project.tags.length > 0 && (
              <div className="flex items-center space-x-2 mt-3">
                <TagIcon className="h-4 w-4 text-gray-400" />
                <div className="flex flex-wrap gap-2">
                  {project.tags.map((tag) => (
                    <span key={tag} className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-600">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate(`/projects/${id}/edit`)}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <PencilIcon className="h-4 w-4 mr-2" />
              Edit
            </button>
            <button className="inline-flex items-center px-3 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 bg-white hover:bg-red-50">
              <TrashIcon className="h-4 w-4 mr-2" />
              Archive
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <Cog6ToothIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{metrics?.active_workflows || workflows.filter(w => w.status === 'active').length}/{metrics?.total_workflows || workflows.length}</p>
              <p className="text-sm text-gray-500">Active Workflows</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <PlayIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{metrics?.total_executions || executions.length}</p>
              <p className="text-sm text-gray-500">Total Executions</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-2xl font-semibold text-gray-900">{metrics?.success_rate ? (metrics.success_rate * 100).toFixed(0) : (executions.length > 0 ? Math.round((executions.filter(e => e.status === 'completed').length / executions.length) * 100) : 0)}%</p>
              <p className="text-sm text-gray-500">Success Rate</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-lg font-semibold text-gray-900">
                {formatDistanceToNow(new Date(metrics?.last_activity || project.updated_at), { addSuffix: true })}
              </p>
              <p className="text-sm text-gray-500">Last Activity</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tab.Group selectedIndex={selectedTabIndex} onChange={setSelectedTabIndex}>
        <Tab.List className="flex space-x-1 rounded-xl bg-gray-100 p-1">
          {tabs.map((tab) => (
            <Tab
              key={tab.name}
              className={({ selected }) =>
                `w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all
                ${selected
                  ? 'bg-white text-blue-700 shadow'
                  : 'text-gray-600 hover:bg-white/[0.12] hover:text-gray-900'
                }`
              }
            >
              <span className="flex items-center justify-center space-x-2">
                <span>{tab.name}</span>
                {tab.count !== null && (
                  <span className="bg-gray-200 text-gray-600 px-2 py-1 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </span>
            </Tab>
          ))}
        </Tab.List>

        <Tab.Panels className="mt-6">
          {/* Overview Tab */}
          <Tab.Panel>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Project Information */}
              <div className="bg-white rounded-lg border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Information</h3>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Created</dt>
                    <dd className="text-sm text-gray-900">{format(new Date(project.created_at), 'PPP')}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                    <dd className="text-sm text-gray-900">{format(new Date(project.updated_at), 'PPP')}</dd>
                  </div>
                  {(project as any).metadata?.owner && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Owner</dt>
                      <dd className="text-sm text-gray-900">{(project as any).metadata.owner}</dd>
                    </div>
                  )}
                  {(project as any).metadata?.department && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Department</dt>
                      <dd className="text-sm text-gray-900">{(project as any).metadata.department}</dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Recent Activity */}
              <div className="bg-white rounded-lg border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Executions</h3>
                <div className="space-y-3">
                  {executions.slice(0, 5).map((execution) => {
                    const workflow = workflows.find(w => w.id === execution.workflow_id);
                    return (
                      <div key={execution.id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getExecutionIcon(execution.status)}
                          <div>
                            <p className="text-sm font-medium text-gray-900">{workflow?.name}</p>
                            <p className="text-xs text-gray-500">
                              {formatDistanceToNow(new Date(execution.started_at), { addSuffix: true })}
                            </p>
                          </div>
                        </div>
                        <span className={getStatusBadge(execution.status)}>
                          {execution.status}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </Tab.Panel>

          {/* Workflows Tab */}
          <Tab.Panel>
            <div className="bg-white rounded-lg border">
              <div className="p-6 border-b">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">Workflows</h3>
                  <Link
                    to={`/projects/${id}/workflows/new`}
                    className="inline-flex items-center px-3 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <PlusIcon className="h-4 w-4 mr-2" />
                    Add Workflow
                  </Link>
                </div>
              </div>
              <div className="divide-y">
                {workflows.map((workflow) => (
                  <div key={workflow.id} className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <Link
                            to={`/workflows/${workflow.id}`}
                            className="text-lg font-medium text-gray-900 hover:text-blue-600"
                          >
                            {workflow.name}
                          </Link>
                          <span className={getStatusBadge(workflow.status)}>
                            {workflow.status}
                          </span>
                        </div>
                        <p className="text-gray-600 mt-1">{workflow.description}</p>
                        <p className="text-sm text-gray-500 mt-2">
                          Updated {formatDistanceToNow(new Date(workflow.updated_at), { addSuffix: true })}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-400 hover:text-gray-600">
                          {workflow.status === 'active' ? <PauseIcon className="h-5 w-5" /> : <PlayIcon className="h-5 w-5" />}
                        </button>
                        <Link
                          to={`/workflows/${workflow.id}/edit`}
                          className="p-2 text-gray-400 hover:text-gray-600"
                        >
                          <PencilIcon className="h-5 w-5" />
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Tab.Panel>

          {/* Executions Tab */}
          <Tab.Panel>
            <div className="bg-white rounded-lg border">
              <div className="p-6 border-b">
                <h3 className="text-lg font-semibold text-gray-900">Execution History</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Workflow
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Started
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Duration
                      </th>
                      <th className="relative px-6 py-3"><span className="sr-only">Actions</span></th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {executions.map((execution) => {
                      const workflow = workflows.find(w => w.id === execution.workflow_id);
                      const duration = execution.completed_at 
                        ? new Date(execution.completed_at).getTime() - new Date(execution.started_at).getTime()
                        : null;
                      
                      return (
                        <tr key={execution.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              {getExecutionIcon(execution.status)}
                              <div className="ml-3">
                                <div className="text-sm font-medium text-gray-900">{workflow?.name}</div>
                                <div className="text-sm text-gray-500">{execution.id}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={getStatusBadge(execution.status)}>
                              {execution.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {format(new Date(execution.started_at), 'PPp')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {duration ? `${Math.round(duration / 1000)}s` : '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <Link
                              to={`/executions/${execution.id}`}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              View Details
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </Tab.Panel>

          {/* Settings Tab */}
          <Tab.Panel>
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Settings</h3>
              <p className="text-gray-600">Project settings and configuration options will be available here.</p>
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}