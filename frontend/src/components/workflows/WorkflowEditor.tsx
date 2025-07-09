import { useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  NodeTypes,
  Panel,
  BackgroundVariant
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  ArrowLeftIcon,
  PlayIcon,
  PauseIcon,
  TrashIcon,
  BookmarkIcon
} from '@heroicons/react/24/outline';
import { useQuery, useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';

// Custom Node Components
const CustomNode = ({ data, selected }: { data: any; selected: boolean }) => {
  return (
    <div className={`px-4 py-2 shadow-md rounded-md bg-white border-2 min-w-[150px] ${
      selected ? 'border-blue-500' : 'border-gray-200'
    }`}>
      <div className="flex items-center">
        <div className="rounded-full w-3 h-3 mr-2 bg-blue-500"></div>
        <div>
          <div className="text-sm font-bold">{data.label}</div>
          <div className="text-xs text-gray-500">{data.nodeType}</div>
        </div>
      </div>
    </div>
  );
};

const StartNode = ({ selected }: { data: any; selected: boolean }) => {
  return (
    <div className={`px-4 py-2 shadow-md rounded-md bg-green-100 border-2 min-w-[120px] ${
      selected ? 'border-green-500' : 'border-green-300'
    }`}>
      <div className="flex items-center">
        <div className="rounded-full w-3 h-3 mr-2 bg-green-500"></div>
        <div>
          <div className="text-sm font-bold text-green-800">Start</div>
          <div className="text-xs text-green-600">Trigger</div>
        </div>
      </div>
    </div>
  );
};

const EndNode = ({ selected }: { data: any; selected: boolean }) => {
  return (
    <div className={`px-4 py-2 shadow-md rounded-md bg-red-100 border-2 min-w-[120px] ${
      selected ? 'border-red-500' : 'border-red-300'
    }`}>
      <div className="flex items-center">
        <div className="rounded-full w-3 h-3 mr-2 bg-red-500"></div>
        <div>
          <div className="text-sm font-bold text-red-800">End</div>
          <div className="text-xs text-red-600">Output</div>
        </div>
      </div>
    </div>
  );
};

const nodeTypes: NodeTypes = {
  custom: CustomNode,
  start: StartNode,
  end: EndNode,
};

// Sample initial nodes and edges
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'start',
    position: { x: 250, y: 25 },
    data: { label: 'Start', nodeType: 'trigger' },
  },
  {
    id: '2',
    type: 'custom',
    position: { x: 250, y: 125 },
    data: { label: 'Process Data', nodeType: 'function' },
  },
  {
    id: '3',
    type: 'custom',
    position: { x: 100, y: 225 },
    data: { label: 'Send Email', nodeType: 'notification' },
  },
  {
    id: '4',
    type: 'custom',
    position: { x: 400, y: 225 },
    data: { label: 'Save to DB', nodeType: 'database' },
  },
  {
    id: '5',
    type: 'end',
    position: { x: 250, y: 325 },
    data: { label: 'End', nodeType: 'output' },
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', animated: true },
  { id: 'e2-4', source: '2', target: '4', animated: true },
  { id: 'e3-5', source: '3', target: '5', animated: true },
  { id: 'e4-5', source: '4', target: '5', animated: true },
];

// Available node types for the sidebar
const availableNodes = [
  { type: 'trigger', label: 'HTTP Trigger', icon: '🌐' },
  { type: 'function', label: 'Function', icon: '⚙️' },
  { type: 'database', label: 'Database', icon: '🗄️' },
  { type: 'notification', label: 'Email', icon: '📧' },
  { type: 'webhook', label: 'Webhook', icon: '🔗' },
  { type: 'condition', label: 'Condition', icon: '🔀' },
  { type: 'delay', label: 'Delay', icon: '⏱️' },
  { type: 'transform', label: 'Transform', icon: '🔄' },
];

export default function WorkflowEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
  
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  // In a real app, these would fetch from APIs
  const { data: workflow, isLoading } = useQuery({
    queryKey: ['workflow', id],
    queryFn: async () => ({
      id: id || 'new',
      name: id ? 'Sample Workflow' : 'New Workflow',
      description: 'A sample workflow for demonstration',
      status: 'draft',
      nodes: initialNodes,
      edges: initialEdges,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })
  });

  const saveWorkflowMutation = useMutation({
    mutationFn: async (workflowData: any) => {
      // In a real app, this would save to the API
      await new Promise(resolve => setTimeout(resolve, 1000));
      return workflowData;
    },
    onSuccess: () => {
      toast.success('Workflow saved successfully!');
    },
    onError: () => {
      toast.error('Failed to save workflow');
    }
  });

  const executeWorkflowMutation = useMutation({
    mutationFn: async () => {
      setIsRunning(true);
      await new Promise(resolve => setTimeout(resolve, 3000));
      return { status: 'completed', executionId: 'exec-123' };
    },
    onSuccess: (result) => {
      setIsRunning(false);
      toast.success(`Workflow executed successfully! (${result.executionId})`);
    },
    onError: () => {
      setIsRunning(false);
      toast.error('Workflow execution failed');
    }
  });

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type || !reactFlowBounds) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode: Node = {
        id: `${nodes.length + 1}`,
        type: 'custom',
        position,
        data: { 
          label: `New ${type}`, 
          nodeType: type 
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, nodes, setNodes]
  );

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const saveWorkflow = () => {
    const workflowData = {
      id: workflow?.id,
      name: workflow?.name,
      nodes,
      edges,
    };
    saveWorkflowMutation.mutate(workflowData);
  };

  const executeWorkflow = () => {
    executeWorkflowMutation.mutate();
  };

  const deleteSelectedNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
      setEdges((eds) => eds.filter((edge) => 
        edge.source !== selectedNode.id && edge.target !== selectedNode.id
      ));
      setSelectedNode(null);
    }
  };

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/workflows')}
              className="flex items-center text-gray-500 hover:text-gray-700"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-1" />
              Back
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">{workflow?.name}</h1>
              <p className="text-sm text-gray-500">Workflow Editor</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={saveWorkflow}
              disabled={saveWorkflowMutation.isPending}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              <BookmarkIcon className="h-4 w-4 mr-2" />
              {saveWorkflowMutation.isPending ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={executeWorkflow}
              disabled={isRunning}
              className="inline-flex items-center px-3 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {isRunning ? (
                <>
                  <PauseIcon className="h-4 w-4 mr-2 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Execute
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-1">
        {/* Sidebar */}
        <div className="w-64 bg-white border-r border-gray-200 p-4">
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Add Nodes</h3>
            <div className="space-y-2">
              {availableNodes.map((nodeType) => (
                <div
                  key={nodeType.type}
                  className="flex items-center p-2 border border-gray-200 rounded-md cursor-move hover:bg-gray-50"
                  onDragStart={(event) => onDragStart(event, nodeType.type)}
                  draggable
                >
                  <span className="text-lg mr-3">{nodeType.icon}</span>
                  <span className="text-sm text-gray-700">{nodeType.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Node Properties */}
          {selectedNode && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Node Properties</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Label
                  </label>
                  <input
                    type="text"
                    value={selectedNode.data.label}
                    onChange={(e) => {
                      setNodes((nds) =>
                        nds.map((node) =>
                          node.id === selectedNode.id
                            ? { ...node, data: { ...node.data, label: e.target.value } }
                            : node
                        )
                      );
                      setSelectedNode({
                        ...selectedNode,
                        data: { ...selectedNode.data, label: e.target.value }
                      });
                    }}
                    className="block w-full text-xs border border-gray-300 rounded px-2 py-1"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Type
                  </label>
                  <select
                    value={selectedNode.data.nodeType}
                    onChange={(e) => {
                      setNodes((nds) =>
                        nds.map((node) =>
                          node.id === selectedNode.id
                            ? { ...node, data: { ...node.data, nodeType: e.target.value } }
                            : node
                        )
                      );
                      setSelectedNode({
                        ...selectedNode,
                        data: { ...selectedNode.data, nodeType: e.target.value }
                      });
                    }}
                    className="block w-full text-xs border border-gray-300 rounded px-2 py-1"
                  >
                    {availableNodes.map((type) => (
                      <option key={type.type} value={type.type}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={deleteSelectedNode}
                  className="w-full flex items-center justify-center px-3 py-2 border border-red-300 rounded-md text-xs font-medium text-red-700 bg-white hover:bg-red-50"
                >
                  <TrashIcon className="h-3 w-3 mr-1" />
                  Delete Node
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Main Canvas */}
        <div className="flex-1" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="top-right"
          >
            <Controls />
            <MiniMap />
            <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
            
            {/* Workflow Status Panel */}
            <Panel position="top-left">
              <div className="bg-white rounded-lg shadow-lg border p-3">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    isRunning ? 'bg-blue-500 animate-pulse' : 'bg-green-500'
                  }`}></div>
                  <span className="text-sm font-medium">
                    {isRunning ? 'Executing...' : 'Ready'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {nodes.length} nodes, {edges.length} connections
                  </span>
                </div>
              </div>
            </Panel>
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}