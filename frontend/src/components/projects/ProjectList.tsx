import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  PlusIcon,
  FolderIcon,
  EllipsisVerticalIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ChartBarIcon,
  ClockIcon,
  TagIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { projectApi } from '../../services/api';

// Project data will come from the API

export default function ProjectList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive' | 'archived'>('all');

  // Fetch real projects from API
  const { data: projects = [], isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      return await projectApi.getProjects();
    }
  });

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
    switch (status) {
      case 'active':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'inactive':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      case 'archived':
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
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-white rounded-lg border p-6">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-red-800">Error loading projects</h3>
          <p className="mt-1 text-sm text-red-700">
            {error instanceof Error ? error.message : 'Failed to load projects'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your workflow projects and track their performance
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            to="/projects/new"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            New Project
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>
      </div>

      {/* Projects Grid */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <FolderIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
          <p className="text-gray-500 mb-4">
            {searchTerm || statusFilter !== 'all' 
              ? 'Try adjusting your search or filter criteria.'
              : 'Get started by creating your first project.'
            }
          </p>
          <Link
            to="/projects/new"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Create Project
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredProjects.map((project) => {
            // Real project data from API includes metrics directly
            
            return (
              <div key={project.id} className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                {/* Card Header */}
                <div className="p-6 pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Link 
                        to={`/projects/${project.id}`}
                        className="text-lg font-semibold text-gray-900 hover:text-blue-600 line-clamp-1"
                      >
                        {project.name}
                      </Link>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {project.description}
                      </p>
                    </div>
                    
                    <Menu as="div" className="relative">
                      <Menu.Button className="p-1 rounded-full hover:bg-gray-100">
                        <EllipsisVerticalIcon className="h-5 w-5 text-gray-400" />
                      </Menu.Button>
                      <Transition
                        as={Fragment}
                        enter="transition ease-out duration-100"
                        enterFrom="transform opacity-0 scale-95"
                        enterTo="transform opacity-100 scale-100"
                        leave="transition ease-in duration-75"
                        leaveFrom="transform opacity-100 scale-100"
                        leaveTo="transform opacity-0 scale-95"
                      >
                        <Menu.Items className="absolute right-0 z-10 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                          <div className="py-1">
                            <Menu.Item>
                              {({ active }) => (
                                <Link
                                  to={`/projects/${project.id}/edit`}
                                  className={`${active ? 'bg-gray-100' : ''} block px-4 py-2 text-sm text-gray-700`}
                                >
                                  Edit Project
                                </Link>
                              )}
                            </Menu.Item>
                            <Menu.Item>
                              {({ active }) => (
                                <Link
                                  to={`/projects/${project.id}/workflows`}
                                  className={`${active ? 'bg-gray-100' : ''} block px-4 py-2 text-sm text-gray-700`}
                                >
                                  Manage Workflows
                                </Link>
                              )}
                            </Menu.Item>
                            <Menu.Item>
                              {({ active }) => (
                                <button
                                  className={`${active ? 'bg-gray-100' : ''} block w-full text-left px-4 py-2 text-sm text-red-700`}
                                  onClick={() => {
                                    // Handle archive/delete
                                  }}
                                >
                                  Archive Project
                                </button>
                              )}
                            </Menu.Item>
                          </div>
                        </Menu.Items>
                      </Transition>
                    </Menu>
                  </div>

                  {/* Status and Tags */}
                  <div className="flex items-center justify-between mt-4">
                    <span className={getStatusBadge(project.status)}>
                      {project.status}
                    </span>
                    <div className="flex items-center space-x-1">
                      {project.tags?.slice(0, 2).map((tag) => (
                        <span key={tag} className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-100 text-gray-600">
                          <TagIcon className="h-3 w-3 mr-1" />
                          {tag}
                        </span>
                      ))}
                      {project.tags && project.tags.length > 2 && (
                        <span className="text-xs text-gray-500">+{project.tags.length - 2}</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Metrics */}
                <div className="border-t px-6 py-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <Cog6ToothIcon className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{(project as any).workflow_count || 0}</p>
                          <p className="text-xs text-gray-500">Workflows</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <FolderIcon className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{(project as any).file_count || 0}</p>
                          <p className="text-xs text-gray-500">Files</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <ChartBarIcon className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {(project as any).has_project_plan ? 'Yes' : 'No'}
                          </p>
                          <p className="text-xs text-gray-500">Project Plan</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <ClockIcon className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
                          </p>
                          <p className="text-xs text-gray-500">Last Update</p>
                        </div>
                      </div>
                    </div>
                  </div>

                {/* Quick Actions */}
                <div className="border-t px-6 py-3 bg-gray-50 rounded-b-lg">
                  <div className="flex justify-between">
                    <Link
                      to={`/projects/${project.id}/workflows`}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      View Workflows
                    </Link>
                    <Link
                      to={`/projects/${project.id}`}
                      className="text-sm text-gray-600 hover:text-gray-800 font-medium"
                    >
                      View Details →
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}