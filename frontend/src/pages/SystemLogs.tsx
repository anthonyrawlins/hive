import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  CalendarDaysIcon
} from '@heroicons/react/24/outline';
import { formatDistanceToNow, format } from 'date-fns';
import DataTable, { Column } from '../components/ui/DataTable';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';
  component: string;
  message: string;
  metadata?: Record<string, any>;
  user_id?: string;
  session_id?: string;
  request_id?: string;
  stack_trace?: string;
}

interface LogStats {
  total: number;
  last_24h: number;
  by_level: Record<string, number>;
  by_component: Record<string, number>;
}

export default function SystemLogs() {
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [selectedComponent, setSelectedComponent] = useState<string>('all');
  const [dateRange, setDateRange] = useState<string>('today');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const { data: logs = [], isLoading, refetch } = useQuery({
    queryKey: ['system-logs', selectedLevel, selectedComponent, dateRange],
    queryFn: async () => {
      // Simulate API call - replace with actual API
      return generateMockLogs();
    },
    refetchInterval: autoRefresh ? 10000 : false // Refresh every 10 seconds if auto-refresh is enabled
  });

  const { data: stats } = useQuery({
    queryKey: ['log-stats'],
    queryFn: async () => {
      return generateMockStats();
    },
    refetchInterval: autoRefresh ? 30000 : false
  });

  const generateMockLogs = (): LogEntry[] => {
    const levels: LogEntry['level'][] = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'];
    const components = [
      'hive-coordinator', 'agent-manager', 'workflow-engine', 'api-gateway',
      'auth-service', 'task-executor', 'metrics-collector', 'websocket-server'
    ];
    
    const messages = {
      DEBUG: [
        'Processing task queue',
        'Agent heartbeat received',
        'Cache hit for request',
        'Database query executed',
        'Session validated'
      ],
      INFO: [
        'Agent successfully registered',
        'Workflow execution started',
        'User authentication successful',
        'Task completed successfully',
        'System backup completed'
      ],
      WARN: [
        'High memory usage detected',
        'Agent response time elevated',
        'Connection pool near capacity',
        'Rate limit threshold reached',
        'Deprecated API endpoint accessed'
      ],
      ERROR: [
        'Agent connection failed',
        'Task execution timeout',
        'Database connection lost',
        'Authentication failed',
        'Failed to parse request'
      ],
      CRITICAL: [
        'System disk space critical',
        'Database connection pool exhausted',
        'Security breach detected',
        'Service unavailable',
        'Memory allocation failed'
      ]
    };

    return Array.from({ length: 200 }, (_, i) => {
      const level = levels[Math.floor(Math.random() * levels.length)];
      const component = components[Math.floor(Math.random() * components.length)];
      const messageOptions = messages[level];
      const message = messageOptions[Math.floor(Math.random() * messageOptions.length)];
      
      const timestamp = new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
      
      const entry: LogEntry = {
        id: `log-${String(i + 1).padStart(6, '0')}`,
        timestamp: timestamp.toISOString(),
        level,
        component,
        message,
        user_id: Math.random() > 0.7 ? `user-${Math.floor(Math.random() * 100)}` : undefined,
        session_id: `session-${Math.random().toString(36).substr(2, 9)}`,
        request_id: `req-${Math.random().toString(36).substr(2, 9)}`
      };

      // Add metadata for some entries
      if (Math.random() > 0.6) {
        entry.metadata = {
          duration_ms: Math.floor(Math.random() * 5000),
          endpoint: `/api/v1/${component}`,
          status_code: Math.random() > 0.8 ? 500 : 200,
          ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`
        };
      }

      // Add stack trace for errors
      if (level === 'ERROR' || level === 'CRITICAL') {
        if (Math.random() > 0.5) {
          entry.stack_trace = `
Traceback (most recent call last):
  File "/app/src/${component.replace('-', '_')}.py", line ${Math.floor(Math.random() * 200) + 1}, in process_request
    result = process_data(input_data)
  File "/app/src/utils.py", line ${Math.floor(Math.random() * 100) + 1}, in process_data
    return transform(data)
${level}Exception: ${message}
          `.trim();
        }
      }

      return entry;
    }).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  };

  const generateMockStats = (): LogStats => {
    const levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'];
    const components = [
      'hive-coordinator', 'agent-manager', 'workflow-engine', 'api-gateway',
      'auth-service', 'task-executor', 'metrics-collector', 'websocket-server'
    ];

    return {
      total: 15847,
      last_24h: 1203,
      by_level: levels.reduce((acc, level) => {
        acc[level] = Math.floor(Math.random() * 1000) + 50;
        return acc;
      }, {} as Record<string, number>),
      by_component: components.reduce((acc, component) => {
        acc[component] = Math.floor(Math.random() * 500) + 20;
        return acc;
      }, {} as Record<string, number>)
    };
  };

  const getLevelIcon = (level: LogEntry['level']) => {
    const iconClass = "h-4 w-4";
    switch (level) {
      case 'DEBUG':
        return <InformationCircleIcon className={`${iconClass} text-gray-500`} />;
      case 'INFO':
        return <CheckCircleIcon className={`${iconClass} text-blue-500`} />;
      case 'WARN':
        return <ExclamationTriangleIcon className={`${iconClass} text-yellow-500`} />;
      case 'ERROR':
        return <XCircleIcon className={`${iconClass} text-red-500`} />;
      case 'CRITICAL':
        return <XCircleIcon className={`${iconClass} text-red-700`} />;
      default:
        return <InformationCircleIcon className={`${iconClass} text-gray-400`} />;
    }
  };

  const getLevelBadge = (level: LogEntry['level']) => {
    const baseClasses = "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium";
    switch (level) {
      case 'DEBUG':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      case 'INFO':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'WARN':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'ERROR':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'CRITICAL':
        return `${baseClasses} bg-red-200 text-red-900`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getComponentBadge = () => {
    return "inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700";
  };

  const exportLogs = () => {
    // Simulate log export
    const csv = logs.map(log => 
      `"${log.timestamp}","${log.level}","${log.component}","${log.message.replace(/"/g, '""')}"`
    ).join('\n');
    
    const blob = new Blob([`"Timestamp","Level","Component","Message"\n${csv}`], 
      { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `system-logs-${format(new Date(), 'yyyy-MM-dd-HH-mm')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearLogs = () => {
    if (confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
      console.log('Clearing logs...');
      refetch();
    }
  };

  const levels = ['all', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'];
  const components = ['all', ...Array.from(new Set(logs.map(log => log.component)))];
  console.log('Available components:', components.length); // Use components variable
  const dateRanges = [
    { value: 'today', label: 'Today' },
    { value: 'yesterday', label: 'Yesterday' },
    { value: 'week', label: 'Last 7 days' },
    { value: 'month', label: 'Last 30 days' }
  ];

  const filteredLogs = logs.filter(log => {
    if (selectedLevel !== 'all' && log.level !== selectedLevel) return false;
    if (selectedComponent !== 'all' && log.component !== selectedComponent) return false;
    
    const logDate = new Date(log.timestamp);
    const now = new Date();
    
    switch (dateRange) {
      case 'today':
        return logDate.toDateString() === now.toDateString();
      case 'yesterday':
        const yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        return logDate.toDateString() === yesterday.toDateString();
      case 'week':
        return logDate >= new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      case 'month':
        return logDate >= new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      default:
        return true;
    }
  });

  const columns: Column<LogEntry>[] = [
    {
      key: 'timestamp',
      header: 'Time',
      sortable: true,
      width: 'w-40',
      render: (log) => (
        <div>
          <div className="text-sm text-gray-900">
            {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
          </div>
          <div className="text-xs text-gray-500 font-mono">
            {format(new Date(log.timestamp), 'HH:mm:ss.SSS')}
          </div>
        </div>
      )
    },
    {
      key: 'level',
      header: 'Level',
      sortable: true,
      filterable: true,
      filterType: 'select',
      filterOptions: levels.slice(1).map(level => ({ label: level, value: level })),
      render: (log) => (
        <div className="flex items-center space-x-2">
          {getLevelIcon(log.level)}
          <span className={getLevelBadge(log.level)}>
            {log.level}
          </span>
        </div>
      )
    },
    {
      key: 'component',
      header: 'Component',
      sortable: true,
      filterable: true,
      render: (log) => (
        <span className={getComponentBadge()}>
          {log.component}
        </span>
      )
    },
    {
      key: 'message',
      header: 'Message',
      filterable: true,
      render: (log) => (
        <div className="max-w-md">
          <p className="text-sm text-gray-900 truncate" title={log.message}>
            {log.message}
          </p>
          {log.user_id && (
            <p className="text-xs text-gray-500 mt-1">User: {log.user_id}</p>
          )}
        </div>
      )
    },
    {
      key: 'metadata',
      header: 'Details',
      render: (log) => (
        <div className="text-xs text-gray-500">
          {log.metadata && (
            <div>
              {log.metadata.status_code && (
                <span className={`inline-block px-1 rounded ${
                  log.metadata.status_code >= 400 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                }`}>
                  {log.metadata.status_code}
                </span>
              )}
              {log.metadata.duration_ms && (
                <span className="ml-1">{log.metadata.duration_ms}ms</span>
              )}
            </div>
          )}
          {log.stack_trace && (
            <span className="text-red-600">Stack trace available</span>
          )}
        </div>
      )
    }
  ];

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Logs</h1>
          <p className="text-gray-600 mt-1">
            Monitor system activity and troubleshoot issues with comprehensive logging
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              autoRefresh 
                ? 'bg-green-100 text-green-700' 
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <ArrowPathIcon className="h-4 w-4" />
            <span>Auto Refresh</span>
          </button>
          <button
            onClick={exportLogs}
            className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button
            onClick={clearLogs}
            className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 rounded-md"
          >
            <TrashIcon className="h-4 w-4" />
            <span>Clear Logs</span>
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Logs</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total.toLocaleString()}</p>
              </div>
              <DocumentTextIcon className="h-8 w-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Last 24h</p>
                <p className="text-2xl font-bold text-gray-900">{stats.last_24h.toLocaleString()}</p>
              </div>
              <CalendarDaysIcon className="h-8 w-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Errors</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(stats.by_level.ERROR || 0) + (stats.by_level.CRITICAL || 0)}
                </p>
              </div>
              <XCircleIcon className="h-8 w-8 text-red-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Warnings</p>
                <p className="text-2xl font-bold text-gray-900">{stats.by_level.WARN || 0}</p>
              </div>
              <ExclamationTriangleIcon className="h-8 w-8 text-yellow-500" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Log Level</label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {levels.map(level => (
                <option key={level} value={level}>
                  {level === 'all' ? 'All Levels' : level}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Component</label>
            <select
              value={selectedComponent}
              onChange={(e) => setSelectedComponent(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {components.map(component => (
                <option key={component} value={component}>
                  {component === 'all' ? 'All Components' : component}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {dateRanges.map(range => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => {
                setSelectedLevel('all');
                setSelectedComponent('all');
                setDateRange('today');
              }}
              className="w-full px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md border border-gray-300"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <DataTable
        data={filteredLogs}
        columns={columns}
        loading={isLoading}
        searchPlaceholder="Search log messages..."
        pageSize={15}
        emptyMessage="No logs found"
        onRowClick={(log) => {
          setSelectedLog(log);
          setShowDetails(true);
        }}
      />

      {/* Log Details Modal */}
      {showDetails && selectedLog && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
                 onClick={() => setShowDetails(false)} />
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Log Entry Details</h3>
                  <button
                    onClick={() => setShowDetails(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Timestamp</label>
                      <p className="mt-1 text-sm text-gray-900 font-mono">
                        {format(new Date(selectedLog.timestamp), 'PPpp')}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Level</label>
                      <div className="mt-1 flex items-center space-x-2">
                        {getLevelIcon(selectedLog.level)}
                        <span className={getLevelBadge(selectedLog.level)}>
                          {selectedLog.level}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Component</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedLog.component}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Log ID</label>
                      <p className="mt-1 text-sm text-gray-900 font-mono">{selectedLog.id}</p>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Message</label>
                    <p className="mt-1 text-sm text-gray-900 bg-gray-50 p-3 rounded">{selectedLog.message}</p>
                  </div>
                  
                  {selectedLog.metadata && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Metadata</label>
                      <pre className="mt-1 text-xs text-gray-900 bg-gray-50 p-3 rounded overflow-x-auto">
                        {JSON.stringify(selectedLog.metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                  
                  {selectedLog.stack_trace && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Stack Trace</label>
                      <pre className="mt-1 text-xs text-red-900 bg-red-50 p-3 rounded overflow-x-auto">
                        {selectedLog.stack_trace}
                      </pre>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {selectedLog.user_id && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">User ID</label>
                        <p className="mt-1 text-sm text-gray-900 font-mono">{selectedLog.user_id}</p>
                      </div>
                    )}
                    {selectedLog.session_id && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Session ID</label>
                        <p className="mt-1 text-sm text-gray-900 font-mono">{selectedLog.session_id}</p>
                      </div>
                    )}
                    {selectedLog.request_id && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Request ID</label>
                        <p className="mt-1 text-sm text-gray-900 font-mono">{selectedLog.request_id}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
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