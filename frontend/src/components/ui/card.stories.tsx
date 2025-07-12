import type { Meta, StoryObj } from '@storybook/react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './card';
import { Button } from './button';
import { Badge } from './badge';

/**
 * Card component system for Hive UI
 * 
 * A flexible card component system that provides a container for content.
 * Includes header, title, description, and content sections.
 */
const meta = {
  title: 'UI Components/Card',
  component: Card,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
The Card component system provides a structured way to display content in containers.
It's composed of several sub-components that work together to create consistent layouts.

## Components
- **Card**: Main container component
- **CardHeader**: Header section for titles and descriptions
- **CardTitle**: Primary title text
- **CardDescription**: Subtitle or description text
- **CardContent**: Main content area

## Features
- Consistent styling across the application
- Flexible composition with sub-components
- Responsive design support
- Shadow and border styling
- Customizable through className props

## Usage
\`\`\`tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
</Card>
\`\`\`
        `,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
    children: {
      control: false,
      description: 'Card content',
    },
  },
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Basic card with title and content
 */
export const Default: Story = {
  render: () => (
    <Card className="w-80">
      <CardHeader>
        <CardTitle>Default Card</CardTitle>
        <CardDescription>
          This is a basic card component with a title and description.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p>This is the main content area of the card where you can put any content.</p>
      </CardContent>
    </Card>
  ),
};

/**
 * Card with only content, no header
 */
export const ContentOnly: Story = {
  render: () => (
    <Card className="w-80">
      <CardContent>
        <p>This card contains only content without a header section.</p>
      </CardContent>
    </Card>
  ),
};

/**
 * Agent status card as used in Hive
 */
export const AgentStatusCard: Story = {
  render: () => (
    <Card className="w-96">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>walnut-codellama</CardTitle>
            <CardDescription>Code analysis specialist agent</CardDescription>
          </div>
          <Badge variant="success">Available</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Model:</span>
            <span>codellama:34b</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Active Tasks:</span>
            <span>2 / 4</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Utilization:</span>
            <span>50%</span>
          </div>
          <div className="flex gap-2 mt-4">
            <Button size="sm" variant="outline">View Details</Button>
            <Button size="sm" variant="default">Assign Task</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Example of how cards are used to display agent information in the Hive dashboard',
      },
    },
  },
};

/**
 * Task execution card as used in Hive
 */
export const TaskCard: Story = {
  render: () => (
    <Card className="w-96">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Code Analysis Task</CardTitle>
            <CardDescription>task-abc123 • 5 minutes ago</CardDescription>
          </div>
          <Badge variant="warning">In Progress</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Assigned Agent:</span>
            <span>walnut-codellama</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Priority:</span>
            <span>High</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Progress:</span>
            <span>75%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div className="bg-blue-600 h-2 rounded-full" style={{ width: '75%' }}></div>
          </div>
          <div className="flex gap-2 mt-4">
            <Button size="sm" variant="outline">View Logs</Button>
            <Button size="sm" variant="destructive">Cancel</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Example of how cards are used to display task information in the Hive dashboard',
      },
    },
  },
};

/**
 * Workflow card as used in Hive
 */
export const WorkflowCard: Story = {
  render: () => (
    <Card className="w-96">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Code Review Pipeline</CardTitle>
            <CardDescription>Automated code review and testing workflow</CardDescription>
          </div>
          <Badge variant="success">Active</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Steps:</span>
            <span>4</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Success Rate:</span>
            <span>92.5%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Last Run:</span>
            <span>2 hours ago</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Executions:</span>
            <span>25</span>
          </div>
          <div className="flex gap-2 mt-4">
            <Button size="sm" variant="default">Execute</Button>
            <Button size="sm" variant="outline">Edit</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Example of how cards are used to display workflow information in the Hive dashboard',
      },
    },
  },
};

/**
 * System metrics card
 */
export const MetricsCard: Story = {
  render: () => (
    <Card className="w-80">
      <CardHeader>
        <CardTitle>System Metrics</CardTitle>
        <CardDescription>Real-time cluster performance</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">12</div>
            <div className="text-sm text-gray-600">Active Agents</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">8</div>
            <div className="text-sm text-gray-600">Running Tasks</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">3</div>
            <div className="text-sm text-gray-600">Workflows</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">98.5%</div>
            <div className="text-sm text-gray-600">Uptime</div>
          </div>
        </div>
      </CardContent>
    </Card>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Example of a metrics card showing system statistics',
      },
    },
  },
};

/**
 * Card grid layout example
 */
export const CardGrid: Story = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-6xl">
      <Card>
        <CardHeader>
          <CardTitle>Agent 1</CardTitle>
          <CardDescription>Available</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Active tasks: 2/4</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Agent 2</CardTitle>
          <CardDescription>Busy</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Active tasks: 4/4</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Agent 3</CardTitle>
          <CardDescription>Available</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Active tasks: 1/4</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Agent 4</CardTitle>
          <CardDescription>Offline</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Active tasks: 0/4</p>
        </CardContent>
      </Card>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Example of cards arranged in a responsive grid layout',
      },
    },
  },
};