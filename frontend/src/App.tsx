
function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <div className="text-8xl mb-8">🐝</div>
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            Welcome to Hive
          </h1>
          <p className="text-2xl text-gray-700 mb-8">
            Unified Distributed AI Orchestration Platform
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-16">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-2">Multi-Agent Coordination</h3>
              <p className="text-gray-600">
                Coordinate specialized AI agents across your cluster for optimal task distribution
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-4xl mb-4">🔄</div>
              <h3 className="text-xl font-semibold mb-2">Workflow Orchestration</h3>
              <p className="text-gray-600">
                Visual n8n-compatible workflow editor with real-time execution monitoring
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-2">Performance Monitoring</h3>
              <p className="text-gray-600">
                Real-time metrics, alerts, and dashboards for comprehensive system monitoring
              </p>
            </div>
          </div>
          
          <div className="mt-16 text-center">
            <div className="text-lg text-gray-700 mb-4">
              🚀 Hive is starting up... Please wait for all services to be ready.
            </div>
            <div className="text-sm text-gray-500">
              This unified platform consolidates McPlan, distributed-ai-dev, and cluster monitoring
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App