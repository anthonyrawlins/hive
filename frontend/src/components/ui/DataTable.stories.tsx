import type { Meta, StoryObj } from '@storybook/react';
import DataTable, { Column } from './DataTable';
import { Badge } from './badge';
import { Button } from './button';

/**
 * DataTable component for Hive UI
 * 
 * A powerful and flexible data table component with sorting, filtering, searching, and pagination.
 * Perfect for displaying agent lists, task queues, and workflow executions.
 */
const meta = {
  title: 'UI Components/DataTable',
  component: DataTable,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: `
The DataTable component is a comprehensive solution for displaying tabular data in the Hive application.
It provides powerful features for data manipulation and user interaction.

## Features
- **Sorting**: Click column headers to sort data ascending/descending
- **Filtering**: Column-specific filters with text, select, and numeric options
- **Searching**: Global search across all visible columns
- **Pagination**: Built-in pagination with configurable page sizes
- **Custom Rendering**: Custom cell renderers for complex content
- **Row Actions**: Clickable rows with custom action handlers
- **Loading States**: Built-in loading indicator
- **Responsive**: Horizontal scrolling on smaller screens

## Column Configuration
\`\`\`tsx
const columns: Column<Agent>[] = [
  {
    key: 'id',
    header: 'ID',
    sortable: true,
    filterable: true,
    width: 'w-32'
  },
  {
    key: 'status',
    header: 'Status',
    sortable: true,
    filterable: true,
    filterType: 'select',
    filterOptions: [
      { label: 'Available', value: 'available' },
      { label: 'Busy', value: 'busy' },
      { label: 'Offline', value: 'offline' }
    ],
    render: (agent, value) => (
      <Badge variant={getStatusVariant(value)}>{value}</Badge>
    )
  }
];
\`\`\`

## Usage
\`\`\`tsx
import DataTable from '@/components/ui/DataTable';

<DataTable
  data={agents}
  columns={columns}
  searchable={true}
  pageSize={10}
  onRowClick={(agent) => navigate(\`/agents/\${agent.id}\`)}
/>
\`\`\`
        `,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    data: {
      control: false,
      description: 'Array of data objects to display',
    },
    columns: {
      control: false,
      description: 'Column configuration array',
    },
    searchable: {
      control: 'boolean',
      description: 'Enable global search functionality',
    },
    searchPlaceholder: {
      control: 'text',
      description: 'Placeholder text for search input',
    },
    pageSize: {
      control: 'number',
      description: 'Number of rows per page',
    },
    loading: {
      control: 'boolean',
      description: 'Show loading state',
    },
    emptyMessage: {
      control: 'text',
      description: 'Message displayed when no data is available',
    },
    onRowClick: {
      action: 'row-clicked',
      description: 'Handler for row click events',
    },
  },
} satisfies Meta<typeof DataTable>;

export default meta;
type Story = StoryObj<typeof meta>;

// Sample data for stories
interface Agent {
  id: string;
  name: string;
  model: string;
  status: 'available' | 'busy' | 'offline';
  current_tasks: number;
  max_concurrent: number;
  specialization: string;
  last_heartbeat: string;
  utilization: number;
}

const sampleAgents: Agent[] = [
  {
    id: 'walnut-codellama',
    name: 'Walnut CodeLlama',
    model: 'codellama:34b',
    status: 'available',
    current_tasks: 2,
    max_concurrent: 4,
    specialization: 'kernel_dev',
    last_heartbeat: '2024-01-15T10:30:00Z',
    utilization: 0.5,
  },
  {
    id: 'oak-gemma',
    name: 'Oak Gemma',
    model: 'gemma:7b',
    status: 'busy',
    current_tasks: 3,
    max_concurrent: 3,
    specialization: 'tester',
    last_heartbeat: '2024-01-15T10:29:45Z',
    utilization: 1.0,
  },
  {
    id: 'ironwood-llama',
    name: 'Ironwood Llama',
    model: 'llama2:13b',
    status: 'offline',
    current_tasks: 0,
    max_concurrent: 2,
    specialization: 'docs_writer',
    last_heartbeat: '2024-01-15T09:15:22Z',
    utilization: 0.0,
  },
  {
    id: 'pine-mistral',
    name: 'Pine Mistral',
    model: 'mistral:7b',
    status: 'available',
    current_tasks: 1,
    max_concurrent: 4,
    specialization: 'general_ai',
    last_heartbeat: '2024-01-15T10:29:58Z',
    utilization: 0.25,
  },
  {
    id: 'birch-phi',
    name: 'Birch Phi',
    model: 'phi:3b',
    status: 'busy',
    current_tasks: 2,
    max_concurrent: 2,
    specialization: 'profiler',
    last_heartbeat: '2024-01-15T10:30:12Z',
    utilization: 1.0,
  },
];

const getStatusVariant = (status: string) => {
  switch (status) {
    case 'available': return 'success';
    case 'busy': return 'warning';
    case 'offline': return 'destructive';
    default: return 'secondary';
  }
};

const agentColumns: Column<Agent>[] = [
  {
    key: 'id',
    header: 'Agent ID',
    sortable: true,
    filterable: true,
    width: 'w-40',
  },
  {
    key: 'name',
    header: 'Name',
    sortable: true,
    filterable: true,
  },
  {
    key: 'model',
    header: 'Model',
    sortable: true,
    filterable: true,
    filterType: 'select',
    filterOptions: [
      { label: 'CodeLlama 34B', value: 'codellama:34b' },
      { label: 'Gemma 7B', value: 'gemma:7b' },
      { label: 'Llama2 13B', value: 'llama2:13b' },
      { label: 'Mistral 7B', value: 'mistral:7b' },
      { label: 'Phi 3B', value: 'phi:3b' },
    ],
  },
  {
    key: 'status',
    header: 'Status',
    sortable: true,
    filterable: true,
    filterType: 'select',
    filterOptions: [
      { label: 'Available', value: 'available' },
      { label: 'Busy', value: 'busy' },
      { label: 'Offline', value: 'offline' },
    ],
    render: (agent, value) => (
      <Badge variant={getStatusVariant(value) as any}>
        {value.charAt(0).toUpperCase() + value.slice(1)}
      </Badge>
    ),
  },
  {
    key: 'current_tasks',
    header: 'Tasks',
    sortable: true,
    filterable: true,
    filterType: 'number',
    render: (agent) => `${agent.current_tasks} / ${agent.max_concurrent}`,
  },
  {
    key: 'specialization',
    header: 'Specialization',
    sortable: true,
    filterable: true,
    filterType: 'select',
    filterOptions: [
      { label: 'Kernel Development', value: 'kernel_dev' },
      { label: 'Testing', value: 'tester' },
      { label: 'Documentation', value: 'docs_writer' },
      { label: 'General AI', value: 'general_ai' },
      { label: 'Profiler', value: 'profiler' },
    ],
  },
  {
    key: 'utilization',
    header: 'Utilization',
    sortable: true,
    render: (agent) => {
      const percentage = Math.round(agent.utilization * 100);
      return (
        <div className="flex items-center space-x-2">
          <div className="w-16 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                percentage >= 80 ? 'bg-red-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${percentage}%` }}
            />
          </div>
          <span className="text-sm">{percentage}%</span>
        </div>
      );
    },
  },
];

/**
 * Basic agent data table
 */
export const Default: Story = {
  args: {
    data: sampleAgents,
    columns: agentColumns,
    searchable: true,
    pageSize: 10,
    loading: false,
  },
};

/**
 * Loading state
 */
export const Loading: Story = {
  args: {
    data: [],
    columns: agentColumns,
    loading: true,
  },
};

/**
 * Empty state
 */
export const Empty: Story = {
  args: {
    data: [],
    columns: agentColumns,
    loading: false,
    emptyMessage: 'No agents found. Register some agents to get started.',
  },
};

/**
 * Small page size for pagination demo
 */
export const WithPagination: Story = {
  args: {
    data: [...sampleAgents, ...sampleAgents, ...sampleAgents], // 15 items
    columns: agentColumns,
    pageSize: 3,
    searchable: true,
  },
};

/**
 * Simple task data table
 */
export const TaskTable: Story = {
  render: () => {
    interface Task {
      id: string;
      type: string;
      priority: number;
      status: string;
      assigned_agent: string;
      created_at: string;
      progress: number;
    }

    const tasks: Task[] = [
      {
        id: 'task-001',
        type: 'code_analysis',
        priority: 1,
        status: 'in_progress',
        assigned_agent: 'walnut-codellama',
        created_at: '2024-01-15T10:00:00Z',
        progress: 75,
      },
      {
        id: 'task-002',
        type: 'testing',
        priority: 2,
        status: 'completed',
        assigned_agent: 'oak-gemma',
        created_at: '2024-01-15T09:30:00Z',
        progress: 100,
      },
      {
        id: 'task-003',
        type: 'documentation',
        priority: 3,
        status: 'pending',
        assigned_agent: null,
        created_at: '2024-01-15T10:15:00Z',
        progress: 0,
      },
    ];

    const taskColumns: Column<Task>[] = [
      {
        key: 'id',
        header: 'Task ID',
        sortable: true,
        filterable: true,
      },
      {
        key: 'type',
        header: 'Type',
        sortable: true,
        filterable: true,
        filterType: 'select',
        filterOptions: [
          { label: 'Code Analysis', value: 'code_analysis' },
          { label: 'Testing', value: 'testing' },
          { label: 'Documentation', value: 'documentation' },
        ],
      },
      {
        key: 'priority',
        header: 'Priority',
        sortable: true,
        filterable: true,
        filterType: 'select',
        filterOptions: [
          { label: 'Critical (1)', value: 1 },
          { label: 'High (2)', value: 2 },
          { label: 'Medium (3)', value: 3 },
        ],
        render: (task) => {
          const priority = task.priority;
          const variant = priority === 1 ? 'destructive' : priority === 2 ? 'warning' : 'default';
          const label = priority === 1 ? 'Critical' : priority === 2 ? 'High' : 'Medium';
          return <Badge variant={variant as any}>{label}</Badge>;
        },
      },
      {
        key: 'status',
        header: 'Status',
        sortable: true,
        filterable: true,
        filterType: 'select',
        filterOptions: [
          { label: 'Pending', value: 'pending' },
          { label: 'In Progress', value: 'in_progress' },
          { label: 'Completed', value: 'completed' },
        ],
        render: (task, value) => {
          const variant = value === 'completed' ? 'success' : value === 'in_progress' ? 'warning' : 'secondary';
          return <Badge variant={variant as any}>{value.replace('_', ' ')}</Badge>;
        },
      },
      {
        key: 'assigned_agent',
        header: 'Agent',
        sortable: true,
        filterable: true,
        render: (task, value) => value || <span className="text-gray-400">Unassigned</span>,
      },
      {
        key: 'progress',
        header: 'Progress',
        sortable: true,
        render: (task) => (
          <div className="flex items-center space-x-2">
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${task.progress}%` }}
              />
            </div>
            <span className="text-sm">{task.progress}%</span>
          </div>
        ),
      },
    ];

    return (
      <DataTable
        data={tasks}
        columns={taskColumns}
        searchable={true}
        pageSize={10}
        emptyMessage="No tasks available"
      />
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Example task management table with custom rendering and status badges',
      },
    },
  },
};

/**
 * Interactive table with row actions
 */
export const WithRowActions: Story = {
  render: () => {
    const handleRowClick = (agent: Agent) => {
      alert(`Clicked on agent: ${agent.name}`);
    };

    const columnsWithActions: Column<Agent>[] = [
      ...agentColumns,
      {
        key: 'actions',
        header: 'Actions',
        render: (agent) => (
          <div className="flex space-x-2" onClick={(e) => e.stopPropagation()}>
            <Button size="sm" variant="outline">
              View
            </Button>
            <Button size="sm" variant="default">
              Assign
            </Button>
          </div>
        ),
      },
    ];

    return (
      <DataTable
        data={sampleAgents}
        columns={columnsWithActions}
        searchable={true}
        onRowClick={handleRowClick}
        pageSize={5}
      />
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Table with clickable rows and action buttons in cells',
      },
    },
  },
};

/**
 * Minimal table without search and filters
 */
export const Minimal: Story = {
  render: () => {
    const minimalColumns: Column<Agent>[] = [
      {
        key: 'name',
        header: 'Agent Name',
      },
      {
        key: 'status',
        header: 'Status',
        render: (agent, value) => (
          <Badge variant={getStatusVariant(value) as any}>
            {value.charAt(0).toUpperCase() + value.slice(1)}
          </Badge>
        ),
      },
      {
        key: 'current_tasks',
        header: 'Active Tasks',
        render: (agent) => `${agent.current_tasks} / ${agent.max_concurrent}`,
      },
    ];

    return (
      <DataTable
        data={sampleAgents}
        columns={minimalColumns}
        searchable={false}
        pageSize={10}
        className="border-0 shadow-none"
      />
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Simplified table without search, filters, or advanced features',
      },
    },
  },
};