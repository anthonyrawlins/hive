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
      }
    }
  });

  const currentTags = watch('tags') || [];

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