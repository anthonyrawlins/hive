import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  InformationCircleIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  EyeIcon,
  LinkIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { BzzzTask, BzzzRepository, Project } from '../../types/project';

interface BzzzIntegrationProps {
  project: Project;
}

export default function BzzzIntegration({ project }: BzzzIntegrationProps) {
  const queryClient = useQueryClient();
  const [showAllTasks, setShowAllTasks] = useState(false);

  // Fetch Bzzz tasks for this project
  const { data: bzzzTasks = [], isLoading: tasksLoading } = useQuery({
    queryKey: ['bzzz-tasks', project.id],
    queryFn: async (): Promise<BzzzTask[]> => {
      const response = await fetch(`/api/bzzz/projects/${project.id}/tasks`);
      if (!response.ok) throw new Error('Failed to fetch Bzzz tasks');
      return response.json();
    },
    enabled: !!project.bzzz_config?.bzzz_enabled
  });

  // Fetch active repositories to check if this project is discoverable
  const { data: activeRepos = [] } = useQuery({
    queryKey: ['bzzz-active-repos'],
    queryFn: async (): Promise<{ repositories: BzzzRepository[] }> => {
      const response = await fetch('/api/bzzz/active-repos');
      if (!response.ok) throw new Error('Failed to fetch active repositories');
      return response.json();
    }
  });

  // Toggle project activation for Bzzz
  const toggleActivationMutation = useMutation({
    mutationFn: async (ready: boolean) => {
      const response = await fetch(`/api/projects/${project.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bzzz_config: {
            ...project.bzzz_config,
            ready_to_claim: ready
          }
        })
      });
      if (!response.ok) throw new Error('Failed to update project');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', project.id] });
      queryClient.invalidateQueries({ queryKey: ['bzzz-active-repos'] });
      toast.success('Project Bzzz status updated!');
    },
    onError: () => {
      toast.error('Failed to update project status');
    }
  });

  if (!project.bzzz_config?.bzzz_enabled) {
    return (
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="text-center">
          <InformationCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Bzzz Integration Disabled</h3>
          <p className="text-gray-500 mb-4">
            This project is not configured for Bzzz P2P task coordination.
          </p>
          <p className="text-sm text-gray-400">
            Enable Bzzz integration in project settings to allow distributed AI agents to discover and work on tasks.
          </p>
        </div>
      </div>
    );
  }

  const isDiscoverable = activeRepos.repositories.some(repo => repo.name === project.name);
  const readyToClaim = project.bzzz_config?.ready_to_claim || false;
  const hasGitConfig = project.bzzz_config?.git_url;

  const displayTasks = showAllTasks ? bzzzTasks : bzzzTasks.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">🐝 Bzzz Integration Status</h2>
          {isDiscoverable ? (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              <CheckCircleIcon className="h-4 w-4 mr-1" />
              Discoverable
            </span>
          ) : (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
              <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
              Not Discoverable
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Git Repository */}
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <LinkIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">Git Repository</p>
            <p className="text-xs text-gray-500 mt-1">
              {hasGitConfig ? (
                <a 
                  href={project.bzzz_config.git_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800"
                >
                  {project.bzzz_config.git_owner}/{project.bzzz_config.git_repository}
                </a>
              ) : (
                'Not configured'
              )}
            </p>
          </div>

          {/* Available Tasks */}
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{bzzzTasks.length}</div>
            <p className="text-sm font-medium text-gray-900">Available Tasks</p>
            <p className="text-xs text-gray-500">With bzzz-task label</p>
          </div>

          {/* Claim Status */}
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-center mb-2">
              {readyToClaim ? (
                <CheckCircleIcon className="h-8 w-8 text-green-500" />
              ) : (
                <XMarkIcon className="h-8 w-8 text-red-500" />
              )}
            </div>
            <p className="text-sm font-medium text-gray-900">Ready to Claim</p>
            <button
              onClick={() => toggleActivationMutation.mutate(!readyToClaim)}
              disabled={toggleActivationMutation.isPending}
              className={`text-xs px-2 py-1 rounded mt-1 ${
                readyToClaim 
                  ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                  : 'bg-green-100 text-green-700 hover:bg-green-200'
              }`}
            >
              {toggleActivationMutation.isPending 
                ? 'Updating...' 
                : (readyToClaim ? 'Deactivate' : 'Activate')
              }
            </button>
          </div>
        </div>
      </div>

      {/* GitHub Tasks */}
      {hasGitConfig && (
        <div className="bg-white rounded-lg border">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">GitHub Issues (bzzz-task)</h3>
              {bzzzTasks.length > 5 && (
                <button
                  onClick={() => setShowAllTasks(!showAllTasks)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  <EyeIcon className="h-4 w-4 inline mr-1" />
                  {showAllTasks ? 'Show Less' : `Show All (${bzzzTasks.length})`}
                </button>
              )}
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {tasksLoading ? (
              <div className="p-6 text-center text-gray-500">Loading tasks...</div>
            ) : displayTasks.length === 0 ? (
              <div className="p-6 text-center">
                <p className="text-gray-500">No issues found with 'bzzz-task' label.</p>
                <p className="text-sm text-gray-400 mt-1">
                  Create GitHub issues and add the 'bzzz-task' label for agents to discover them.
                </p>
              </div>
            ) : (
              displayTasks.map((task) => (
                <div key={task.number} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="text-sm font-medium text-gray-900">
                          #{task.number}: {task.title}
                        </h4>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          task.is_claimed 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {task.is_claimed ? 'Claimed' : 'Available'}
                        </span>
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-600">
                          {task.task_type}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                        {task.description || 'No description provided.'}
                      </p>
                      
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>State: {task.state}</span>
                        {task.assignees.length > 0 && (
                          <span>Assigned to: {task.assignees.join(', ')}</span>
                        )}
                        <span>Labels: {task.labels.join(', ')}</span>
                      </div>
                    </div>
                    
                    <a
                      href={task.html_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 ml-4"
                    >
                      View on GitHub →
                    </a>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Integration Help */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <InformationCircleIcon className="h-5 w-5 text-yellow-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">How to Use Bzzz Integration</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <ol className="list-decimal list-inside space-y-1">
                <li>Ensure your GitHub repository has issues labeled with 'bzzz-task'</li>
                <li>Activate the project using the "Ready to Claim" toggle above</li>
                <li>Bzzz agents will discover and coordinate to work on available tasks</li>
                <li>Monitor progress through GitHub issue updates and agent coordination</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}