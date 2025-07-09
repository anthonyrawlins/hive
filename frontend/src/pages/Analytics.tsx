import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ChartBarIcon,
  CpuChipIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { executionApi } from '../services/api';

interface MetricsData {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  active_executions: number;
  completed_executions: number;
  failed_executions: number;
  response_time: number;
}

interface SystemAlert {
  id: string;
  type: 'warning' | 'error' | 'info';
  message: string;
  timestamp: string;
  resolved?: boolean;
}

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('24h');

  // Future: Real-time metrics will be fetched here
  // const { data: clusterMetrics } = useQuery({
  //   queryKey: ['cluster-metrics'],
  //   queryFn: () => clusterApi.getMetrics(),
  //   refetchInterval: 30000
  // });
  //
  // const { data: systemStatus } = useQuery({
  //   queryKey: ['system-status'],
  //   queryFn: () => systemApi.getStatus(),
  //   refetchInterval: 10000
  // });

  // Fetch recent executions for analytics
  const { data: executions = [] } = useQuery({
    queryKey: ['executions-analytics'],
    queryFn: () => executionApi.getExecutions(),
    refetchInterval: 30000
  });

  // Generate mock time series data for demonstration
  const generateTimeSeriesData = (): MetricsData[] => {
    const data: MetricsData[] = [];
    const now = new Date();
    const hours = timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : 720;
    const interval = timeRange === '24h' ? 1 : timeRange === '7d' ? 6 : 24;

    for (let i = hours; i >= 0; i -= interval) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        timestamp: timestamp.toISOString(),
        cpu_usage: Math.random() * 80 + 10,
        memory_usage: Math.random() * 70 + 20,
        active_executions: Math.floor(Math.random() * 10) + 1,
        completed_executions: Math.floor(Math.random() * 50) + 10,
        failed_executions: Math.floor(Math.random() * 5),
        response_time: Math.random() * 3 + 0.5
      });
    }
    return data;
  };

  const [timeSeriesData] = useState(() => generateTimeSeriesData());

  // Calculate execution analytics
  const executionStats = {
    total: executions.length,
    completed: executions.filter(e => e.status === 'completed').length,
    failed: executions.filter(e => e.status === 'failed').length,
    running: executions.filter(e => e.status === 'running').length,
    success_rate: executions.length > 0 ? 
      Math.round((executions.filter(e => e.status === 'completed').length / executions.length) * 100) : 0
  };

  // Execution status distribution for pie chart
  const executionDistribution = [
    { name: 'Completed', value: executionStats.completed, color: '#10B981' },
    { name: 'Failed', value: executionStats.failed, color: '#EF4444' },
    { name: 'Running', value: executionStats.running, color: '#3B82F6' },
    { name: 'Pending', value: executions.filter(e => e.status === 'pending').length, color: '#F59E0B' }
  ].filter(item => item.value > 0);

  // Performance trends data
  const performanceData = timeSeriesData.slice(-7).map((item, index) => ({
    day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index],
    executions: item.completed_executions,
    response_time: item.response_time,
    success_rate: Math.random() * 20 + 80
  }));

  // System alerts (mock data)
  const systemAlerts: SystemAlert[] = [
    {
      id: 'alert-1',
      type: 'warning',
      message: 'High memory usage on WALNUT node (85%)',
      timestamp: new Date(Date.now() - 1800000).toISOString()
    },
    {
      id: 'alert-2',
      type: 'info',
      message: 'ACACIA node reconnected successfully',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      resolved: true
    },
    {
      id: 'alert-3',
      type: 'error',
      message: 'Workflow execution failed: timeout after 5 minutes',
      timestamp: new Date(Date.now() - 7200000).toISOString()
    }
  ];

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return timeRange === '24h' ? 
      date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) :
      date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'info':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600">System performance and execution analytics</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-semibold text-gray-900">{executionStats.total}</p>
              <p className="text-sm text-gray-500">Total Executions</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-blue-500" />
          </div>
          <div className="mt-2 flex items-center">
            <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-sm text-green-600">+12% from yesterday</span>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-semibold text-gray-900">{executionStats.success_rate}%</p>
              <p className="text-sm text-gray-500">Success Rate</p>
            </div>
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
          </div>
          <div className="mt-2 flex items-center">
            <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-sm text-green-600">+2.1% improvement</span>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-semibold text-gray-900">2.3s</p>
              <p className="text-sm text-gray-500">Avg Response Time</p>
            </div>
            <ClockIcon className="h-8 w-8 text-yellow-500" />
          </div>
          <div className="mt-2 flex items-center">
            <ArrowTrendingDownIcon className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-sm text-green-600">-0.2s faster</span>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-semibold text-gray-900">{executionStats.running}</p>
              <p className="text-sm text-gray-500">Active Executions</p>
            </div>
            <CpuChipIcon className="h-8 w-8 text-purple-500" />
          </div>
          <div className="mt-2 flex items-center">
            <span className="text-sm text-gray-600">Currently processing</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Execution Trends */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Execution Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatTimestamp}
                interval="preserveStartEnd"
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(value) => formatTimestamp(value as string)}
                formatter={(value: any, name: string) => [value, name === 'completed_executions' ? 'Completed' : 'Failed']}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="completed_executions" 
                stroke="#10B981" 
                strokeWidth={2}
                name="Completed"
              />
              <Line 
                type="monotone" 
                dataKey="failed_executions" 
                stroke="#EF4444" 
                strokeWidth={2}
                name="Failed"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* System Resource Usage */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Resource Usage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp" 
                tickFormatter={formatTimestamp}
                interval="preserveStartEnd"
              />
              <YAxis domain={[0, 100]} />
              <Tooltip 
                labelFormatter={(value) => formatTimestamp(value as string)}
                formatter={(value: any, name: string) => [`${Math.round(value)}%`, name === 'cpu_usage' ? 'CPU' : 'Memory']}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="cpu_usage" 
                stackId="1"
                stroke="#3B82F6" 
                fill="#3B82F6"
                fillOpacity={0.3}
                name="CPU Usage"
              />
              <Area 
                type="monotone" 
                dataKey="memory_usage" 
                stackId="2"
                stroke="#8B5CF6" 
                fill="#8B5CF6"
                fillOpacity={0.3}
                name="Memory Usage"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Execution Status Distribution */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Execution Status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={executionDistribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {executionDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Trends */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="executions" fill="#3B82F6" name="Executions" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* System Alerts */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Alerts</h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {systemAlerts.map((alert) => (
              <div 
                key={alert.id} 
                className={`flex items-start space-x-3 p-3 rounded-md ${
                  alert.resolved ? 'bg-gray-50' : 
                  alert.type === 'error' ? 'bg-red-50' : 
                  alert.type === 'warning' ? 'bg-yellow-50' : 'bg-blue-50'
                }`}
              >
                {getAlertIcon(alert.type)}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm ${alert.resolved ? 'text-gray-600' : 'text-gray-900'}`}>
                    {alert.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
                {alert.resolved && (
                  <CheckCircleIcon className="h-4 w-4 text-gray-400" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Response Time Trends */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Response Time Trends</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={formatTimestamp}
              interval="preserveStartEnd"
            />
            <YAxis domain={[0, 'dataMax']} />
            <Tooltip 
              labelFormatter={(value) => formatTimestamp(value as string)}
              formatter={(value: any) => [`${value.toFixed(2)}s`, 'Response Time']}
            />
            <Line 
              type="monotone" 
              dataKey="response_time" 
              stroke="#F59E0B" 
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}