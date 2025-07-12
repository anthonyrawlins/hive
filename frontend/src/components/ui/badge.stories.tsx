import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from './badge';

/**
 * Badge component for Hive UI
 * 
 * A small status indicator component used to display labels, statuses, and categories.
 * Perfect for showing agent statuses, task priorities, and workflow states.
 */
const meta = {
  title: 'UI Components/Badge',
  component: Badge,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
The Badge component is used to display small labels and status indicators throughout the Hive application.
It's commonly used for showing agent statuses, task priorities, and other categorical information.

## Features
- Multiple color variants for different semantic meanings
- Consistent sizing and typography
- Rounded pill design for modern appearance
- Customizable through className prop

## Usage
\`\`\`tsx
import { Badge } from '@/components/ui/badge';

<Badge variant="success">Online</Badge>
<Badge variant="warning">Busy</Badge>
<Badge variant="destructive">Offline</Badge>
\`\`\`

## Semantic Meanings
- **default**: Primary information or neutral status
- **secondary**: Less important or secondary information
- **success**: Positive status (available, completed, healthy)
- **warning**: Attention needed (busy, pending, degraded)
- **destructive**: Negative status (error, failed, offline)
- **outline**: Minimal emphasis or placeholder
        `,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'destructive', 'outline', 'success', 'warning'],
      description: 'Visual variant of the badge',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
    children: {
      control: 'text',
      description: 'Badge content',
    },
  },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default blue badge
 */
export const Default: Story = {
  args: {
    children: 'Default',
    variant: 'default',
  },
};

/**
 * Secondary gray badge
 */
export const Secondary: Story = {
  args: {
    children: 'Secondary',
    variant: 'secondary',
  },
};

/**
 * Success green badge
 */
export const Success: Story = {
  args: {
    children: 'Available',
    variant: 'success',
  },
};

/**
 * Warning yellow badge
 */
export const Warning: Story = {
  args: {
    children: 'Busy',
    variant: 'warning',
  },
};

/**
 * Destructive red badge
 */
export const Destructive: Story = {
  args: {
    children: 'Offline',
    variant: 'destructive',
  },
};

/**
 * Outline variant
 */
export const Outline: Story = {
  args: {
    children: 'Outline',
    variant: 'outline',
  },
};

/**
 * All variants showcase
 */
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="default">Default</Badge>
      <Badge variant="secondary">Secondary</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="destructive">Destructive</Badge>
      <Badge variant="outline">Outline</Badge>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All available badge variants displayed together',
      },
    },
  },
};

/**
 * Agent status badges as used in Hive
 */
export const AgentStatuses: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="success">Available</Badge>
      <Badge variant="warning">Busy</Badge>
      <Badge variant="destructive">Offline</Badge>
      <Badge variant="secondary">Maintenance</Badge>
      <Badge variant="default">Connected</Badge>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Common agent status badges used throughout the Hive application',
      },
    },
  },
};

/**
 * Task priority badges
 */
export const TaskPriorities: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="destructive">Critical</Badge>
      <Badge variant="warning">High</Badge>
      <Badge variant="default">Medium</Badge>
      <Badge variant="secondary">Low</Badge>
      <Badge variant="outline">Background</Badge>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Task priority badges with semantic color coding',
      },
    },
  },
};

/**
 * Task status badges
 */
export const TaskStatuses: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="secondary">Pending</Badge>
      <Badge variant="warning">In Progress</Badge>
      <Badge variant="success">Completed</Badge>
      <Badge variant="destructive">Failed</Badge>
      <Badge variant="outline">Cancelled</Badge>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Task execution status badges used in task management',
      },
    },
  },
};

/**
 * Workflow status badges
 */
export const WorkflowStatuses: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="success">Active</Badge>
      <Badge variant="warning">Running</Badge>
      <Badge variant="secondary">Paused</Badge>
      <Badge variant="destructive">Failed</Badge>
      <Badge variant="outline">Draft</Badge>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Workflow status badges used in workflow management',
      },
    },
  },
};

/**
 * Custom styled badges
 */
export const CustomStyling: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="default" className="text-lg px-4 py-1">Large Badge</Badge>
      <Badge variant="success" className="uppercase tracking-wider">Success</Badge>
      <Badge variant="warning" className="animate-pulse">Flashing</Badge>
      <Badge variant="outline" className="border-dashed border-2">Dashed Border</Badge>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Examples of custom styling applied to badges using the className prop',
      },
    },
  },
};