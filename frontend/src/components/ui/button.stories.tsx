import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './button';

/**
 * Button component for Hive UI
 * 
 * A versatile button component with multiple variants, sizes, and states.
 * Supports all standard button functionality with consistent styling.
 */
const meta = {
  title: 'UI Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
The Button component is a fundamental UI element used throughout the Hive application.
It provides consistent styling and behavior across different contexts.

## Features
- Multiple visual variants (default, destructive, outline, secondary, ghost)
- Different sizes (small, default, large)
- Disabled state support
- Loading state (future enhancement)
- Icon support (via children)
- Full accessibility support

## Usage
\`\`\`tsx
import { Button } from '@/components/ui/button';

<Button variant="default" size="default" onClick={handleClick}>
  Click me
</Button>
\`\`\`
        `,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost'],
      description: 'Visual variant of the button',
    },
    size: {
      control: 'select', 
      options: ['sm', 'default', 'lg'],
      description: 'Size of the button',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the button is disabled',
    },
    type: {
      control: 'select',
      options: ['button', 'submit', 'reset'],
      description: 'HTML button type',
    },
    children: {
      control: 'text',
      description: 'Button content',
    },
    onClick: {
      action: 'clicked',
      description: 'Click event handler',
    },
  },
  args: {
    onClick: () => console.log('Button clicked'),
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default button style with primary blue color
 */
export const Default: Story = {
  args: {
    children: 'Default Button',
    variant: 'default',
    size: 'default',
  },
};

/**
 * Destructive variant for dangerous actions like deletion
 */
export const Destructive: Story = {
  args: {
    children: 'Delete Item',
    variant: 'destructive',
    size: 'default',
  },
};

/**
 * Outline variant for secondary actions
 */
export const Outline: Story = {
  args: {
    children: 'Outline Button',
    variant: 'outline', 
    size: 'default',
  },
};

/**
 * Secondary variant for less important actions
 */
export const Secondary: Story = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
    size: 'default',
  },
};

/**
 * Ghost variant for minimal styling
 */
export const Ghost: Story = {
  args: {
    children: 'Ghost Button',
    variant: 'ghost',
    size: 'default',
  },
};

/**
 * Small size variant
 */
export const Small: Story = {
  args: {
    children: 'Small Button',
    variant: 'default',
    size: 'sm',
  },
};

/**
 * Large size variant
 */
export const Large: Story = {
  args: {
    children: 'Large Button',
    variant: 'default',
    size: 'lg',
  },
};

/**
 * Disabled state
 */
export const Disabled: Story = {
  args: {
    children: 'Disabled Button',
    variant: 'default',
    size: 'default',
    disabled: true,
  },
};

/**
 * All variants showcase
 */
export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-4">
      <Button variant="default">Default</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Showcase of all button variants side by side',
      },
    },
  },
};

/**
 * All sizes showcase
 */
export const AllSizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Showcase of all button sizes side by side',
      },
    },
  },
};

/**
 * Common Hive use cases
 */
export const HiveUseCases: Story = {
  render: () => (
    <div className="flex flex-col gap-4 max-w-md">
      <div className="flex gap-2">
        <Button variant="default">Create Agent</Button>
        <Button variant="outline">View Details</Button>
      </div>
      <div className="flex gap-2">
        <Button variant="default">Execute Task</Button>
        <Button variant="secondary">Cancel</Button>
      </div>
      <div className="flex gap-2">
        <Button variant="default">Deploy Workflow</Button>
        <Button variant="destructive">Stop Execution</Button>
      </div>
      <div className="flex gap-2">
        <Button variant="outline">Export Logs</Button>
        <Button variant="ghost">Refresh</Button>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Common button combinations used throughout the Hive application',
      },
    },
  },
};