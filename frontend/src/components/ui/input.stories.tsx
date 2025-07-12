import type { Meta, StoryObj } from '@storybook/react';
import { Input } from './input';
import { Label } from './label';
import { Button } from './button';

/**
 * Input component for Hive UI
 * 
 * A versatile input component for forms and user input throughout the Hive application.
 * Supports various input types with consistent styling and behavior.
 */
const meta = {
  title: 'UI Components/Input',
  component: Input,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
The Input component provides consistent styling and behavior for form inputs across the Hive application.
It supports all standard HTML input types with enhanced styling and focus states.

## Features
- Consistent styling across all input types
- Built-in focus and disabled states
- File upload support with custom styling
- Form validation integration
- Responsive design
- Accessibility support

## Usage
\`\`\`tsx
import { Input } from '@/components/ui/input';

<Input
  type="text"
  placeholder="Enter agent name"
  value={agentName}
  onChange={(e) => setAgentName(e.target.value)}
  required
/>
\`\`\`

## Input Types
- **text**: General text input
- **email**: Email address input with validation
- **password**: Password input with hidden text
- **number**: Numeric input with step controls
- **search**: Search input with enhanced styling
- **url**: URL input with validation
- **tel**: Telephone number input
- **file**: File upload input
        `,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'number', 'search', 'url', 'tel', 'file'],
      description: 'HTML input type',
    },
    placeholder: {
      control: 'text',
      description: 'Placeholder text',
    },
    value: {
      control: 'text',
      description: 'Input value',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the input is disabled',
    },
    required: {
      control: 'boolean',
      description: 'Whether the input is required',
    },
    className: {
      control: 'text',
      description: 'Additional CSS classes',
    },
    onChange: {
      action: 'changed',
      description: 'Change event handler',
    },
  },
  args: {
    onChange: (e: any) => console.log('Input changed:', e.target.value),
  },
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default text input
 */
export const Default: Story = {
  args: {
    type: 'text',
    placeholder: 'Enter text...',
  },
};

/**
 * Email input with validation
 */
export const Email: Story = {
  args: {
    type: 'email',
    placeholder: 'Enter email address',
  },
};

/**
 * Password input
 */
export const Password: Story = {
  args: {
    type: 'password',
    placeholder: 'Enter password',
  },
};

/**
 * Number input
 */
export const Number: Story = {
  args: {
    type: 'number',
    placeholder: 'Enter number',
  },
};

/**
 * Search input
 */
export const Search: Story = {
  args: {
    type: 'search',
    placeholder: 'Search agents...',
  },
};

/**
 * File input
 */
export const File: Story = {
  args: {
    type: 'file',
  },
};

/**
 * Disabled state
 */
export const Disabled: Story = {
  args: {
    type: 'text',
    placeholder: 'Disabled input',
    disabled: true,
    value: 'Cannot edit this value',
  },
};

/**
 * Required input
 */
export const Required: Story = {
  args: {
    type: 'text',
    placeholder: 'Required field',
    required: true,
  },
};

/**
 * Input with label (form example)
 */
export const WithLabel: Story = {
  render: () => (
    <div className="space-y-2">
      <Label htmlFor="agent-name">Agent Name</Label>
      <Input
        id="agent-name"
        name="agentName"
        type="text"
        placeholder="e.g., walnut-codellama"
        required
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Input component used with a label in a form context',
      },
    },
  },
};

/**
 * Form example with multiple inputs
 */
export const FormExample: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div className="space-y-2">
        <Label htmlFor="agent-id">Agent ID</Label>
        <Input
          id="agent-id"
          name="agentId"
          type="text"
          placeholder="unique-agent-id"
          required
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="endpoint">Endpoint URL</Label>
        <Input
          id="endpoint"
          name="endpoint"
          type="url"
          placeholder="http://hostname:port"
          required
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="model">Model Name</Label>
        <Input
          id="model"
          name="model"
          type="text"
          placeholder="codellama:34b"
          required
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="max-concurrent">Max Concurrent Tasks</Label>
        <Input
          id="max-concurrent"
          name="maxConcurrent"
          type="number"
          placeholder="4"
          min="1"
          max="10"
          required
        />
      </div>
      
      <div className="flex gap-2">
        <Button variant="default" className="flex-1">Register Agent</Button>
        <Button variant="outline" className="flex-1">Cancel</Button>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Complete form example showing agent registration with multiple input types',
      },
    },
  },
};

/**
 * Search and filter inputs
 */
export const SearchAndFilter: Story = {
  render: () => (
    <div className="space-y-4 w-96">
      <div className="space-y-2">
        <Label htmlFor="search-agents">Search Agents</Label>
        <Input
          id="search-agents"
          type="search"
          placeholder="Search by name, model, or status..."
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="min-tasks">Min Tasks</Label>
          <Input
            id="min-tasks"
            type="number"
            placeholder="0"
            min="0"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="max-tasks">Max Tasks</Label>
          <Input
            id="max-tasks"
            type="number"
            placeholder="10"
            min="0"
          />
        </div>
      </div>
      
      <Button variant="default" className="w-full">Apply Filters</Button>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Input components used for search and filtering functionality',
      },
    },
  },
};

/**
 * All input types showcase
 */
export const AllTypes: Story = {
  render: () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl">
      <div className="space-y-2">
        <Label>Text Input</Label>
        <Input type="text" placeholder="Text input" />
      </div>
      
      <div className="space-y-2">
        <Label>Email Input</Label>
        <Input type="email" placeholder="email@example.com" />
      </div>
      
      <div className="space-y-2">
        <Label>Password Input</Label>
        <Input type="password" placeholder="Password" />
      </div>
      
      <div className="space-y-2">
        <Label>Number Input</Label>
        <Input type="number" placeholder="123" />
      </div>
      
      <div className="space-y-2">
        <Label>Search Input</Label>
        <Input type="search" placeholder="Search..." />
      </div>
      
      <div className="space-y-2">
        <Label>URL Input</Label>
        <Input type="url" placeholder="https://example.com" />
      </div>
      
      <div className="space-y-2">
        <Label>Tel Input</Label>
        <Input type="tel" placeholder="+1 (555) 123-4567" />
      </div>
      
      <div className="space-y-2">
        <Label>File Input</Label>
        <Input type="file" />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Showcase of all supported input types',
      },
    },
  },
};

/**
 * Validation states example
 */
export const ValidationStates: Story = {
  render: () => (
    <div className="space-y-4 w-80">
      <div className="space-y-2">
        <Label htmlFor="valid-input">Valid Input</Label>
        <Input
          id="valid-input"
          type="text"
          value="valid-agent-name"
          className="border-green-500 focus-visible:ring-green-500"
        />
        <p className="text-sm text-green-600">✓ Agent name is available</p>
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="error-input">Error Input</Label>
        <Input
          id="error-input"
          type="text"
          value="invalid name!"
          className="border-red-500 focus-visible:ring-red-500"
        />
        <p className="text-sm text-red-600">✗ Agent name contains invalid characters</p>
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="warning-input">Warning Input</Label>
        <Input
          id="warning-input"
          type="text"
          value="existing-agent"
          className="border-yellow-500 focus-visible:ring-yellow-500"
        />
        <p className="text-sm text-yellow-600">⚠ Similar agent name already exists</p>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Examples of input validation states with custom styling',
      },
    },
  },
};