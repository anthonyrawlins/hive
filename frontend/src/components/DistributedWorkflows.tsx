/**
 * Distributed Workflows Management Component
 * Provides UI for managing cluster-wide development workflows
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
// import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  // Play,
  // Pause,
  Square,
  RefreshCw,
  Cpu,
  Zap,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  Server,
  Activity,
  Code,
  TestTube,
  Wrench,
  FileText,
  Upload,
  Eye
} from 'lucide-react';
import { toast } from 'sonner';
import { useSocketIOContext, useAgentUpdates, useExecutionUpdates, useMetricsUpdates } from '../contexts/SocketIOContext';

// Types
interface Agent {
  id: string;
  endpoint: string;
  model: string;
  gpu_type: string;
  specializations: string[];
  max_concurrent: number;
  current_load: number;
  utilization: number;
  performance_score: number;
  health_status: string;
}

interface Task {
  id: string;
  type: string;
  status: string;
  assigned_agent?: string;
  execution_time: number;
  result?: any;
}

interface Workflow {
  workflow_id: string;
  name: string;
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  progress: number;
  status: string;
  created_at: string;
  tasks: Task[];
}

interface ClusterStatus {
  total_agents: number;
  healthy_agents: number;
  total_capacity: number;
  current_load: number;
  utilization: number;
  agents: Agent[];
}

interface PerformanceMetrics {
  total_workflows: number;
  completed_workflows: number;
  failed_workflows: number;
  average_completion_time: number;
  throughput_per_hour: number;
  agent_performance: Record<string, any>;
}

interface WorkflowFormData {
  name: string;
  requirements: string;
  context: string;
  language: string;
  priority: string;
}

// API functions
const api = {
  async submitWorkflow(workflow: WorkflowFormData) {
    const response = await fetch('/api/distributed/workflows', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workflow),
    });
    if (!response.ok) throw new Error('Failed to submit workflow');
    return response.json();
  },

  async getWorkflows(): Promise<Workflow[]> {
    const response = await fetch('/api/distributed/workflows');
    if (!response.ok) throw new Error('Failed to fetch workflows');
    return response.json();
  },

  async getWorkflowStatus(workflowId: string): Promise<Workflow> {
    const response = await fetch(`/api/distributed/workflows/${workflowId}`);
    if (!response.ok) throw new Error('Failed to fetch workflow status');
    return response.json();
  },

  async getClusterStatus(): Promise<ClusterStatus> {
    const response = await fetch('/api/distributed/cluster/status');
    if (!response.ok) throw new Error('Failed to fetch cluster status');
    return response.json();
  },

  async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    const response = await fetch('/api/distributed/performance/metrics');
    if (!response.ok) throw new Error('Failed to fetch performance metrics');
    return response.json();
  },

  async cancelWorkflow(workflowId: string) {
    const response = await fetch(`/api/distributed/workflows/${workflowId}/cancel`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to cancel workflow');
    return response.json();
  },

  async optimizeCluster() {
    const response = await fetch('/api/distributed/cluster/optimize', {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to optimize cluster');
    return response.json();
  },
};

// Status icons and colors
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'failed':
      return <XCircle className="h-4 w-4 text-red-500" />;
    case 'executing':
    case 'in_progress':
      return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />;
    case 'pending':
      return <Clock className="h-4 w-4 text-yellow-500" />;
    default:
      return <AlertCircle className="h-4 w-4 text-gray-500" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    case 'executing':
    case 'in_progress':
      return 'bg-blue-100 text-blue-800';
    case 'pending':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getTaskTypeIcon = (type: string) => {
  switch (type) {
    case 'code_generation':
      return <Code className="h-4 w-4" />;
    case 'code_review':
      return <Eye className="h-4 w-4" />;
    case 'testing':
      return <TestTube className="h-4 w-4" />;
    case 'compilation':
      return <Wrench className="h-4 w-4" />;
    case 'optimization':
      return <TrendingUp className="h-4 w-4" />;
    case 'documentation':
      return <FileText className="h-4 w-4" />;
    default:
      return <Activity className="h-4 w-4" />;
  }
};

// Main component
export default function DistributedWorkflows() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [clusterStatus, setClusterStatus] = useState<ClusterStatus | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Socket.IO connection
  const { isConnected, connectionState, reconnect } = useSocketIOContext();

  // Form state
  const [formData, setFormData] = useState<WorkflowFormData>({
    name: '',
    requirements: '',
    context: '',
    language: 'python',
    priority: 'normal',
  });

  // Data fetching
  const fetchData = useCallback(async () => {
    try {
      setIsRefreshing(true);
      const [workflowsData, clusterData, metricsData] = await Promise.all([
        api.getWorkflows(),
        api.getClusterStatus(),
        api.getPerformanceMetrics(),
      ]);
      setWorkflows(workflowsData);
      setClusterStatus(clusterData);
      setPerformanceMetrics(metricsData);
    } catch (error) {
      toast.error('Failed to fetch data');
      console.error('Error fetching data:', error);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [fetchData]);

  // Socket.IO real-time updates
  useAgentUpdates((agentData) => {
    console.log('Agent status updated:', agentData);
    // Refresh cluster status when agent changes
    fetchData();
  });

  useExecutionUpdates((executionData) => {
    console.log('Execution status updated:', executionData);
    // Refresh workflows when execution changes
    fetchData();
  });

  useMetricsUpdates((metricsData) => {
    console.log('Metrics updated:', metricsData);
    // Update performance metrics
    setPerformanceMetrics(metricsData);
  });

  // Form handlers
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.requirements) {
      toast.error('Please fill in required fields');
      return;
    }

    try {
      setIsSubmitting(true);
      const result = await api.submitWorkflow(formData);
      toast.success(`Workflow submitted: ${result.workflow_id}`);
      setFormData({
        name: '',
        requirements: '',
        context: '',
        language: 'python',
        priority: 'normal',
      });
      fetchData();
    } catch (error) {
      toast.error('Failed to submit workflow');
      console.error('Error submitting workflow:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelWorkflow = async (workflowId: string) => {
    try {
      await api.cancelWorkflow(workflowId);
      toast.success('Workflow cancelled');
      fetchData();
    } catch (error) {
      toast.error('Failed to cancel workflow');
      console.error('Error cancelling workflow:', error);
    }
  };

  const handleOptimizeCluster = async () => {
    try {
      await api.optimizeCluster();
      toast.success('Cluster optimization triggered');
      fetchData();
    } catch (error) {
      toast.error('Failed to optimize cluster');
      console.error('Error optimizing cluster:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Distributed Workflows</h1>
          <p className="text-muted-foreground">
            Manage development workflows across the cluster
          </p>
        </div>
        <div className="flex space-x-2 items-center">
          <div className="flex items-center space-x-2">
            <div className={`h-2 w-2 rounded-full ${
              connectionState === 'connected' ? 'bg-green-500' : 
              connectionState === 'connecting' ? 'bg-yellow-500' : 
              'bg-red-500'
            }`} />
            <span className="text-sm text-muted-foreground">
              Socket.IO {connectionState}
            </span>
            {!isConnected && (
              <Button
                variant="outline"
                size="sm"
                onClick={reconnect}
              >
                Reconnect
              </Button>
            )}
          </div>
          <Button
            variant="outline"
            onClick={fetchData}
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button onClick={handleOptimizeCluster}>
            <Zap className="h-4 w-4 mr-2" />
            Optimize Cluster
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="cluster">Cluster</TabsTrigger>
          <TabsTrigger value="submit">Submit Workflow</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Active Workflows
                </CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {Array.isArray(workflows) ? workflows.filter(w => w.status === 'in_progress').length : 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Currently executing
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Cluster Utilization
                </CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clusterStatus?.utilization.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  {clusterStatus?.current_load}/{clusterStatus?.total_capacity} tasks
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Healthy Agents
                </CardTitle>
                <Server className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {clusterStatus?.healthy_agents}/{clusterStatus?.total_agents}
                </div>
                <p className="text-xs text-muted-foreground">
                  Agents online
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Completion Rate
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {performanceMetrics?.total_workflows && performanceMetrics.total_workflows > 0
                    ? ((performanceMetrics.completed_workflows / performanceMetrics.total_workflows) * 100).toFixed(1)
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  Success rate
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Workflows */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Workflows</CardTitle>
              <CardDescription>
                Latest workflow executions across the cluster
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {Array.isArray(workflows) ? workflows.slice(0, 10).map((workflow) => (
                    <div
                      key={workflow.workflow_id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(workflow.status)}
                        <div>
                          <p className="font-medium">{workflow.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {workflow.completed_tasks}/{workflow.total_tasks} tasks completed
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(workflow.status)}>
                          {workflow.status}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedWorkflow(workflow)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )) : []}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>All Workflows</CardTitle>
              <CardDescription>
                Manage and monitor all development workflows
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {Array.isArray(workflows) ? workflows.map((workflow) => (
                    <Card key={workflow.workflow_id}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            {getStatusIcon(workflow.status)}
                            <div>
                              <h3 className="font-medium">{workflow.name}</h3>
                              <p className="text-sm text-muted-foreground">
                                ID: {workflow.workflow_id}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={getStatusColor(workflow.status)}>
                              {workflow.status}
                            </Badge>
                            {workflow.status === 'in_progress' && (
                              <AlertDialog>
                                <AlertDialogTrigger>
                                  <Button variant="outline" size="sm">
                                    <Square className="h-4 w-4" />
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Cancel Workflow</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      Are you sure you want to cancel this workflow?
                                      This will stop all running tasks.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction
                                      onClick={() => handleCancelWorkflow(workflow.workflow_id)}
                                    >
                                      Confirm
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            )}
                          </div>
                        </div>
                        <div className="mt-4">
                          <div className="flex justify-between text-sm mb-1">
                            <span>Progress</span>
                            <span>{workflow.progress.toFixed(1)}%</span>
                          </div>
                          <Progress value={workflow.progress} className="h-2" />
                        </div>
                        <div className="mt-3 flex flex-wrap gap-2">
                          {workflow.tasks.map((task) => (
                            <div
                              key={task.id}
                              className="flex items-center space-x-1 text-xs"
                            >
                              {getTaskTypeIcon(task.type)}
                              <Badge
                                variant="outline"
                                className={getStatusColor(task.status)}
                              >
                                {task.type}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )) : []}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cluster Tab */}
        <TabsContent value="cluster" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cluster Status</CardTitle>
              <CardDescription>
                Real-time cluster health and agent information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {clusterStatus?.agents.map((agent) => (
                  <Card key={agent.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium">{agent.id}</h3>
                        <Badge
                          className={
                            agent.health_status === 'healthy'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }
                        >
                          {agent.health_status}
                        </Badge>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">Model:</span>{' '}
                          {agent.model}
                        </div>
                        <div>
                          <span className="text-muted-foreground">GPU:</span>{' '}
                          {agent.gpu_type}
                        </div>
                        <div>
                          <span className="text-muted-foreground">Load:</span>{' '}
                          {agent.current_load}/{agent.max_concurrent}
                        </div>
                        <div>
                          <span className="text-muted-foreground">Utilization:</span>
                          <div className="mt-1">
                            <Progress value={agent.utilization} className="h-1" />
                            <span className="text-xs">{agent.utilization.toFixed(1)}%</span>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {agent.specializations.map((spec) => (
                            <Badge key={spec} variant="secondary" className="text-xs">
                              {spec}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Submit Workflow Tab */}
        <TabsContent value="submit" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Submit New Workflow</CardTitle>
              <CardDescription>
                Create a new distributed development workflow
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="name">Workflow Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      placeholder="e.g., REST API Development"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="language">Programming Language</Label>
                    <Select
                      value={formData.language}
                      onValueChange={(value: string) =>
                        setFormData({ ...formData, language: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="python">Python</SelectItem>
                        <SelectItem value="javascript">JavaScript</SelectItem>
                        <SelectItem value="typescript">TypeScript</SelectItem>
                        <SelectItem value="rust">Rust</SelectItem>
                        <SelectItem value="go">Go</SelectItem>
                        <SelectItem value="java">Java</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="requirements">Requirements *</Label>
                  <Textarea
                    id="requirements"
                    value={formData.requirements}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      setFormData({ ...formData, requirements: e.target.value })
                    }
                    placeholder="Describe what you want to build..."
                    className="h-32"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="context">Additional Context</Label>
                  <Textarea
                    id="context"
                    value={formData.context}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      setFormData({ ...formData, context: e.target.value })
                    }
                    placeholder="Any additional context, constraints, or preferences..."
                    className="h-24"
                  />
                </div>
                <div>
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={formData.priority}
                    onValueChange={(value: string) =>
                      setFormData({ ...formData, priority: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" disabled={isSubmitting} className="w-full">
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Submit Workflow
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}