import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  PlusIcon,
  DocumentTextIcon,
  ClockIcon,
  TagIcon,
  UserIcon,
  PlayIcon,
  PencilIcon,
  DocumentDuplicateIcon,
  EyeIcon,
  StarIcon,
  FolderIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import DataTable, { Column } from '../components/ui/DataTable';
import { formatDistanceToNow } from 'date-fns';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_duration: number; // in minutes
  created_by: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
  rating: number;
  is_favorite: boolean;
  tags: string[];
  steps: WorkflowStep[];
  variables: WorkflowVariable[];
  version: string;
  is_public: boolean;
}

interface WorkflowStep {
  id: string;
  name: string;
  type: 'task' | 'condition' | 'loop' | 'parallel';
  agent_type?: string;
  description: string;
  config: Record<string, any>;
  dependencies: string[];
}

interface WorkflowVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'file';
  required: boolean;
  default_value?: any;
  description: string;
}

export default function WorkflowTemplates() {
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const { data: templates = [], isLoading, refetch } = useQuery({
    queryKey: ['workflow-templates'],
    queryFn: async () => {
      // Simulate API call - replace with actual API
      return generateMockTemplates();
    }
  });

  const generateMockTemplates = (): WorkflowTemplate[] => {
    const categories = ['Development', 'Testing', 'Data Processing', 'Documentation', 'DevOps', 'AI/ML'];
    const difficulties: WorkflowTemplate['difficulty'][] = ['beginner', 'intermediate', 'advanced'];
    const agentTypes = ['kernel_dev', 'pytorch_dev', 'profiler', 'docs_writer', 'tester'];
    
    const templateNames = [
      'Python Code Review Pipeline',
      'React Component Generator',
      'API Documentation Builder',
      'Database Migration Runner',
      'Model Training Pipeline',
      'Test Suite Generator',
      'Security Audit Workflow',
      'Performance Profiling',
      'Docker Container Builder',
      'CI/CD Pipeline Setup',
      'Data Validation Framework',
      'Microservice Scaffold',
      'Machine Learning Experiment',
      'Code Quality Analysis',
      'Deployment Automation'
    ];

    return templateNames.map((name, i) => {
      const category = categories[Math.floor(Math.random() * categories.length)];
      const difficulty = difficulties[Math.floor(Math.random() * difficulties.length)];
      const stepCount = Math.floor(Math.random() * 8) + 3;
      
      const steps: WorkflowStep[] = Array.from({ length: stepCount }, (_, stepIndex) => ({
        id: `step-${stepIndex + 1}`,
        name: `Step ${stepIndex + 1}`,
        type: ['task', 'condition', 'loop', 'parallel'][Math.floor(Math.random() * 4)] as any,
        agent_type: agentTypes[Math.floor(Math.random() * agentTypes.length)],
        description: `Description for step ${stepIndex + 1}`,
        config: { timeout: 300, retry_count: 3 },
        dependencies: stepIndex > 0 ? [`step-${stepIndex}`] : []
      }));

      const variables: WorkflowVariable[] = [
        {
          name: 'project_path',
          type: 'string',
          required: true,
          description: 'Path to the project directory'
        },
        {
          name: 'environment',
          type: 'string',
          required: false,
          default_value: 'development',
          description: 'Target environment'
        }
      ];

      return {
        id: `template-${String(i + 1).padStart(3, '0')}`,
        name,
        description: `${name} workflow template for automated ${category.toLowerCase()} tasks`,
        category,
        difficulty,
        estimated_duration: Math.floor(Math.random() * 120) + 15,
        created_by: `user-${Math.floor(Math.random() * 5) + 1}`,
        created_at: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
        usage_count: Math.floor(Math.random() * 500),
        rating: Math.round((Math.random() * 2 + 3) * 10) / 10, // 3.0 to 5.0
        is_favorite: Math.random() > 0.8,
        tags: [category.toLowerCase(), difficulty, 'automation'].concat(
          Math.random() > 0.5 ? ['popular'] : [],
          Math.random() > 0.7 ? ['community'] : []
        ),
        steps,
        variables,
        version: `1.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
        is_public: Math.random() > 0.3
      };
    });
  };

  const getDifficultyBadge = (difficulty: WorkflowTemplate['difficulty']) => {
    const colors = {
      beginner: 'bg-green-100 text-green-800',
      intermediate: 'bg-yellow-100 text-yellow-800',
      advanced: 'bg-red-100 text-red-800'
    };
    
    return `inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[difficulty]}`;
  };

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, React.ComponentType<any>> = {
      'Development': PencilIcon,
      'Testing': PlayIcon,
      'Data Processing': DocumentTextIcon,
      'Documentation': DocumentTextIcon,
      'DevOps': FolderIcon,
      'AI/ML': StarIcon
    };
    
    const IconComponent = icons[category] || DocumentTextIcon;
    return <IconComponent className="h-4 w-4" />;
  };

  const toggleFavorite = (template: WorkflowTemplate) => {
    // Simulate API call to toggle favorite
    console.log('Toggle favorite for template:', template.id);
    refetch();
  };

  const handleAction = (action: string, template: WorkflowTemplate) => {
    console.log(`${action} template:`, template.id);
    switch (action) {
      case 'use':
        // Navigate to workflow creation with template
        break;
      case 'edit':
        // Open template editor
        break;
      case 'duplicate':
        // Create copy of template
        break;
      case 'delete':
        // Delete template with confirmation
        break;
    }
    refetch();
  };

  const categories = ['all', ...Array.from(new Set(templates.map(t => t.category)))];

  const filteredTemplates = selectedCategory === 'all' 
    ? templates 
    : templates.filter(t => t.category === selectedCategory);

  const columns: Column<WorkflowTemplate>[] = [
    {
      key: 'name',
      header: 'Template',
      sortable: true,
      filterable: true,
      render: (template) => (
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0 mt-1">
            {getCategoryIcon(template.category)}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">{template.name}</span>
              {template.is_favorite && (
                <StarIconSolid className="h-4 w-4 text-yellow-500" />
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1 line-clamp-2">{template.description}</p>
            <div className="flex items-center space-x-2 mt-2">
              <span className={getDifficultyBadge(template.difficulty)}>
                {template.difficulty}
              </span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {template.category}
              </span>
            </div>
          </div>
        </div>
      )
    },
    {
      key: 'estimated_duration',
      header: 'Duration',
      sortable: true,
      render: (template) => (
        <div className="flex items-center space-x-1 text-sm text-gray-900">
          <ClockIcon className="h-4 w-4 text-gray-400" />
          <span>{template.estimated_duration}m</span>
        </div>
      )
    },
    {
      key: 'usage_count',
      header: 'Usage',
      sortable: true,
      render: (template) => (
        <div className="text-center">
          <div className="text-sm font-medium text-gray-900">{template.usage_count}</div>
          <div className="text-xs text-gray-500">times used</div>
        </div>
      )
    },
    {
      key: 'rating',
      header: 'Rating',
      sortable: true,
      render: (template) => (
        <div className="flex items-center space-x-1">
          <StarIconSolid className="h-4 w-4 text-yellow-500" />
          <span className="text-sm font-medium text-gray-900">{template.rating}</span>
        </div>
      )
    },
    {
      key: 'created_by',
      header: 'Author',
      sortable: true,
      filterable: true,
      render: (template) => (
        <div className="flex items-center space-x-2">
          <UserIcon className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-900">{template.created_by}</span>
        </div>
      )
    },
    {
      key: 'updated_at',
      header: 'Updated',
      sortable: true,
      render: (template) => (
        <div>
          <div className="text-sm text-gray-900">
            {formatDistanceToNow(new Date(template.updated_at), { addSuffix: true })}
          </div>
          <div className="text-xs text-gray-500">
            v{template.version}
          </div>
        </div>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (template) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedTemplate(template);
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
              toggleFavorite(template);
            }}
            className={`${template.is_favorite ? 'text-yellow-500' : 'text-gray-400'} hover:text-yellow-600`}
            title="Toggle Favorite"
          >
            {template.is_favorite ? (
              <StarIconSolid className="h-4 w-4" />
            ) : (
              <StarIcon className="h-4 w-4" />
            )}
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('use', template);
            }}
            className="text-green-600 hover:text-green-800"
            title="Use Template"
          >
            <PlayIcon className="h-4 w-4" />
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('duplicate', template);
            }}
            className="text-purple-600 hover:text-purple-800"
            title="Duplicate Template"
          >
            <DocumentDuplicateIcon className="h-4 w-4" />
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
          <h1 className="text-2xl font-bold text-gray-900">Workflow Templates</h1>
          <p className="text-gray-600 mt-1">
            Discover and manage reusable workflow templates for common development tasks
          </p>
        </div>
        <button
          onClick={() => console.log('Create template form coming soon')}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Create Template</span>
        </button>
      </div>

      {/* Category Filter */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 overflow-x-auto">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {category === 'all' ? 'All Categories' : category}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Templates</p>
              <p className="text-2xl font-bold text-gray-900">{templates.length}</p>
            </div>
            <DocumentTextIcon className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Favorites</p>
              <p className="text-2xl font-bold text-gray-900">
                {templates.filter(t => t.is_favorite).length}
              </p>
            </div>
            <StarIconSolid className="h-8 w-8 text-yellow-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Usage</p>
              <p className="text-2xl font-bold text-gray-900">
                {templates.reduce((sum, t) => sum + t.usage_count, 0).toLocaleString()}
              </p>
            </div>
            <PlayIcon className="h-8 w-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Rating</p>
              <p className="text-2xl font-bold text-gray-900">
                {(templates.reduce((sum, t) => sum + t.rating, 0) / templates.length).toFixed(1)}
              </p>
            </div>
            <StarIcon className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Templates Table */}
      <DataTable
        data={filteredTemplates}
        columns={columns}
        loading={isLoading}
        searchPlaceholder="Search templates..."
        pageSize={10}
        emptyMessage="No templates found"
        onRowClick={(template) => {
          setSelectedTemplate(template);
          setShowDetails(true);
        }}
      />

      {/* Template Details Modal */}
      {showDetails && selectedTemplate && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
                 onClick={() => setShowDetails(false)} />
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 max-h-96 overflow-y-auto">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    {getCategoryIcon(selectedTemplate.category)}
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{selectedTemplate.name}</h3>
                      <p className="text-sm text-gray-500">v{selectedTemplate.version}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowDetails(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                      <p className="text-sm text-gray-700">{selectedTemplate.description}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Details</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Category:</span>
                          <span className="font-medium">{selectedTemplate.category}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Difficulty:</span>
                          <span className={getDifficultyBadge(selectedTemplate.difficulty)}>
                            {selectedTemplate.difficulty}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Duration:</span>
                          <span className="font-medium">{selectedTemplate.estimated_duration} minutes</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Rating:</span>
                          <div className="flex items-center space-x-1">
                            <StarIconSolid className="h-4 w-4 text-yellow-500" />
                            <span className="font-medium">{selectedTemplate.rating}</span>
                          </div>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Usage Count:</span>
                          <span className="font-medium">{selectedTemplate.usage_count}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Tags</h4>
                      <div className="flex flex-wrap gap-1">
                        {selectedTemplate.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            <TagIcon className="h-3 w-3 mr-1" />
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Workflow Steps ({selectedTemplate.steps.length})</h4>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {selectedTemplate.steps.map((step) => (
                          <div key={step.id} className="border border-gray-200 rounded p-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-900">{step.name}</span>
                              <span className="text-xs text-gray-500">{step.type}</span>
                            </div>
                            <p className="text-xs text-gray-600 mt-1">{step.description}</p>
                            {step.agent_type && (
                              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 mt-1">
                                {step.agent_type}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Variables ({selectedTemplate.variables.length})</h4>
                      <div className="space-y-2 max-h-32 overflow-y-auto">
                        {selectedTemplate.variables.map((variable, index) => (
                          <div key={index} className="border border-gray-200 rounded p-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-900">{variable.name}</span>
                              <div className="flex items-center space-x-1">
                                <span className="text-xs text-gray-500">{variable.type}</span>
                                {variable.required && (
                                  <span className="text-xs text-red-600">*</span>
                                )}
                              </div>
                            </div>
                            <p className="text-xs text-gray-600 mt-1">{variable.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  onClick={() => handleAction('use', selectedTemplate)}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Use Template
                </button>
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