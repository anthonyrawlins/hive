import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  ArrowLeftIcon,
  XMarkIcon,
  PlusIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';

const projectSchema = z.object({
  name: z.string().min(1, 'Project name is required').max(100, 'Name must be less than 100 characters'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  tags: z.array(z.string()).optional(),
  metadata: z.object({
    owner: z.string().optional(),
    department: z.string().optional(),
    priority: z.enum(['low', 'medium', 'high']).optional()
  }).optional(),
  bzzz_config: z.object({
    git_url: z.string().url('Must be a valid Git URL').optional().or(z.literal('')),
    git_owner: z.string().optional(),
    git_repository: z.string().optional(),
    git_branch: z.string().optional(),
    bzzz_enabled: z.boolean().optional(),
    ready_to_claim: z.boolean().optional(),
    private_repo: z.boolean().optional(),
    github_token_required: z.boolean().optional()
  }).optional()
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface ProjectFormProps {
  mode: 'create' | 'edit';
  initialData?: Partial<ProjectFormData>;
  projectId?: string;
}

export default function ProjectForm({ mode, initialData, projectId }: ProjectFormProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentTag, setCurrentTag] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      tags: initialData?.tags || [],
      metadata: {
        owner: initialData?.metadata?.owner || '',
        department: initialData?.metadata?.department || '',
        priority: initialData?.metadata?.priority || 'medium'
      },
      bzzz_config: {
        git_url: initialData?.bzzz_config?.git_url || '',
        git_owner: initialData?.bzzz_config?.git_owner || '',
        git_repository: initialData?.bzzz_config?.git_repository || '',
        git_branch: initialData?.bzzz_config?.git_branch || 'main',
        bzzz_enabled: initialData?.bzzz_config?.bzzz_enabled || false,
        ready_to_claim: initialData?.bzzz_config?.ready_to_claim || false,
        private_repo: initialData?.bzzz_config?.private_repo || false,
        github_token_required: initialData?.bzzz_config?.github_token_required || false
      }
    }
  });

  const currentTags = watch('tags') || [];
  const gitUrl = watch('bzzz_config.git_url') || '';
  const bzzzEnabled = watch('bzzz_config.bzzz_enabled') || false;

  // Auto-parse Git URL to extract owner and repository
  const parseGitUrl = (url: string) => {
    if (!url) return;
    
    try {
      // Handle GitHub URLs like https://github.com/owner/repo or git@github.com:owner/repo.git
      const githubMatch = url.match(/github\.com[/:]([\w-]+)\/([\w-]+)(?:\.git)?$/);
      if (githubMatch) {
        const [, owner, repo] = githubMatch;
        setValue('bzzz_config.git_owner', owner);
        setValue('bzzz_config.git_repository', repo);
      }
    } catch (error) {
      console.log('Could not parse Git URL:', error);
    }
  };

  // Watch for Git URL changes and auto-parse
  const handleGitUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    parseGitUrl(url);
  };

  const createProjectMutation = useMutation({
    mutationFn: async (data: ProjectFormData) => {
      // In a real app, this would be an API call
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to create project');
      return response.json();
    },
    onSuccess: (newProject) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project created successfully!');
      navigate(`/projects/${newProject.id}`);
    },
    onError: (error) => {
      toast.error('Failed to create project');
      console.error('Create project error:', error);
    }
  });

  const updateProjectMutation = useMutation({
    mutationFn: async (data: ProjectFormData) => {
      const response = await fetch(`/api/projects/${projectId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to update project');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project updated successfully!');
      navigate(`/projects/${projectId}`);
    },
    onError: (error) => {
      toast.error('Failed to update project');
      console.error('Update project error:', error);
    }
  });

  const onSubmit = (data: ProjectFormData) => {
    if (mode === 'create') {
      createProjectMutation.mutate(data);
    } else {
      updateProjectMutation.mutate(data);
    }
  };

  const addTag = () => {
    if (currentTag.trim() && !currentTags.includes(currentTag.trim())) {
      const newTags = [...currentTags, currentTag.trim()];
      setValue('tags', newTags);
      setCurrentTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    const newTags = currentTags.filter(tag => tag !== tagToRemove);
    setValue('tags', newTags);
  };

  const handleTagKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => navigate('/projects')}
              className="flex items-center text-gray-500 hover:text-gray-700"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-1" />
              Back to Projects
            </button>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {mode === 'create' ? 'Create New Project' : 'Edit Project'}
            </h1>
            <p className="text-gray-600 mt-2">
              {mode === 'create' 
                ? 'Set up a new project to organize your workflows and track their progress.'
                : 'Update your project details and configuration.'
              }
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          <div className="bg-white shadow-sm rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Basic Information</h2>
              <p className="text-sm text-gray-500 mt-1">
                Provide the essential details for your project.
              </p>
            </div>
            
            <div className="px-6 py-4 space-y-6">
              {/* Project Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  id="name"
                  {...register('name')}
                  className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter project name"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                )}
              </div>

              {/* Description */}
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  id="description"
                  rows={4}
                  {...register('description')}
                  className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe the purpose and goals of this project"
                />
                <p className="mt-1 text-sm text-gray-500">
                  {watch('description')?.length || 0}/500 characters
                </p>
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                )}
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tags
                </label>
                <div className="space-y-3">
                  {/* Add Tag Input */}
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={currentTag}
                      onChange={(e) => setCurrentTag(e.target.value)}
                      onKeyPress={handleTagKeyPress}
                      className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Add a tag"
                    />
                    <button
                      type="button"
                      onClick={addTag}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <PlusIcon className="h-4 w-4" />
                    </button>
                  </div>
                  
                  {/* Current Tags */}
                  {currentTags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {currentTags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                        >
                          {tag}
                          <button
                            type="button"
                            onClick={() => removeTag(tag)}
                            className="ml-2 text-blue-600 hover:text-blue-800"
                          >
                            <XMarkIcon className="h-4 w-4" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <p className="mt-1 text-sm text-gray-500">
                  Tags help categorize and filter your projects.
                </p>
              </div>
            </div>
          </div>

          {/* Project Metadata */}
          <div className="bg-white shadow-sm rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Project Metadata</h2>
              <p className="text-sm text-gray-500 mt-1">
                Additional information to help organize and manage your project.
              </p>
            </div>
            
            <div className="px-6 py-4 space-y-6">
              {/* Owner */}
              <div>
                <label htmlFor="owner" className="block text-sm font-medium text-gray-700 mb-2">
                  Project Owner
                </label>
                <input
                  type="text"
                  id="owner"
                  {...register('metadata.owner')}
                  className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter owner name"
                />
              </div>

              {/* Department */}
              <div>
                <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-2">
                  Department
                </label>
                <input
                  type="text"
                  id="department"
                  {...register('metadata.department')}
                  className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter department name"
                />
              </div>

              {/* Priority */}
              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <select
                  id="priority"
                  {...register('metadata.priority')}
                  className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>
          </div>

          {/* Bzzz Integration Configuration */}
          <div className="bg-white shadow-sm rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-medium text-gray-900">🐝 Bzzz P2P Integration</h2>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Beta
                </span>
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Configure this project for distributed AI task coordination via the Bzzz P2P network.
              </p>
            </div>
            
            <div className="px-6 py-4 space-y-6">
              {/* Enable Bzzz Integration */}
              <div>
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="bzzz_enabled"
                    {...register('bzzz_config.bzzz_enabled')}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="bzzz_enabled" className="text-sm font-medium text-gray-700">
                    Enable Bzzz P2P coordination for this project
                  </label>
                </div>
                <p className="text-sm text-gray-500 mt-1 ml-7">
                  Allow Bzzz agents to discover and work on tasks from this project's GitHub repository.
                </p>
              </div>

              {/* Git Repository Configuration - Only show if Bzzz is enabled */}
              {bzzzEnabled && (
                <>
                  {/* Git Repository URL */}
                  <div>
                    <label htmlFor="git_url" className="block text-sm font-medium text-gray-700 mb-2">
                      Git Repository URL *
                    </label>
                    <input
                      type="url"
                      id="git_url"
                      {...register('bzzz_config.git_url')}
                      onChange={handleGitUrlChange}
                      className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="https://github.com/owner/repository"
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      GitHub repository URL where Bzzz will look for issues labeled with 'bzzz-task'.
                    </p>
                    {errors.bzzz_config?.git_url && (
                      <p className="mt-1 text-sm text-red-600">{errors.bzzz_config.git_url.message}</p>
                    )}
                  </div>

                  {/* Auto-parsed Git Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="git_owner" className="block text-sm font-medium text-gray-700 mb-2">
                        Repository Owner
                      </label>
                      <input
                        type="text"
                        id="git_owner"
                        {...register('bzzz_config.git_owner')}
                        className="block w-full border border-gray-300 rounded-md px-3 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Auto-detected from URL"
                        readOnly
                      />
                    </div>
                    <div>
                      <label htmlFor="git_repository" className="block text-sm font-medium text-gray-700 mb-2">
                        Repository Name
                      </label>
                      <input
                        type="text"
                        id="git_repository"
                        {...register('bzzz_config.git_repository')}
                        className="block w-full border border-gray-300 rounded-md px-3 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Auto-detected from URL"
                        readOnly
                      />
                    </div>
                  </div>

                  {/* Git Branch */}
                  <div>
                    <label htmlFor="git_branch" className="block text-sm font-medium text-gray-700 mb-2">
                      Default Branch
                    </label>
                    <input
                      type="text"
                      id="git_branch"
                      {...register('bzzz_config.git_branch')}
                      className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="main"
                    />
                  </div>

                  {/* Repository Configuration */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-gray-700">Repository Configuration</h3>
                    
                    <div className="space-y-2">
                      {/* Ready to Claim */}
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          id="ready_to_claim"
                          {...register('bzzz_config.ready_to_claim')}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="ready_to_claim" className="text-sm text-gray-700">
                          Ready for task claims (agents can start working immediately)
                        </label>
                      </div>

                      {/* Private Repository */}
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          id="private_repo"
                          {...register('bzzz_config.private_repo')}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="private_repo" className="text-sm text-gray-700">
                          Private repository (requires authentication)
                        </label>
                      </div>

                      {/* GitHub Token Required */}
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          id="github_token_required"
                          {...register('bzzz_config.github_token_required')}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="github_token_required" className="text-sm text-gray-700">
                          Requires GitHub token for API access
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Bzzz Integration Info */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex">
                      <InformationCircleIcon className="h-5 w-5 text-yellow-400" />
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-yellow-800">
                          How Bzzz Integration Works
                        </h3>
                        <div className="mt-2 text-sm text-yellow-700">
                          <p>When enabled, Bzzz agents will:</p>
                          <ul className="list-disc list-inside mt-1 space-y-1">
                            <li>Monitor GitHub issues labeled with 'bzzz-task'</li>
                            <li>Coordinate P2P to assign tasks based on agent capabilities</li>
                            <li>Execute tasks using distributed AI reasoning</li>
                            <li>Report progress and escalate when needed</li>
                          </ul>
                          <p className="mt-2 font-medium">
                            Make sure your repository has issues labeled with 'bzzz-task' for agents to discover.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Help Text */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex">
              <InformationCircleIcon className="h-5 w-5 text-blue-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">
                  What happens next?
                </h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>
                    After creating your project, you can:
                  </p>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    <li>Add workflows to automate your processes</li>
                    <li>Configure project settings and permissions</li>
                    <li>Monitor execution history and performance</li>
                    <li>Collaborate with team members</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4 pt-6">
            <button
              type="button"
              onClick={() => navigate('/projects')}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting 
                ? (mode === 'create' ? 'Creating...' : 'Updating...') 
                : (mode === 'create' ? 'Create Project' : 'Update Project')
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}