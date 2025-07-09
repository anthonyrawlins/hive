
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ReactFlowProvider } from 'reactflow'
import Layout from './components/Layout'
import { SocketIOProvider } from './contexts/SocketIOContext'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import Login from './pages/Login'
import UserProfile from './components/auth/UserProfile'
import Settings from './pages/Settings'
import WorkflowTemplates from './pages/WorkflowTemplates'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Executions from './pages/Executions'
import Analytics from './pages/Analytics'
import ProjectList from './components/projects/ProjectList'
import ProjectDetail from './components/projects/ProjectDetail'
import ProjectForm from './components/projects/ProjectForm'
import WorkflowEditor from './components/workflows/WorkflowEditor'
import WorkflowDashboard from './components/workflows/WorkflowDashboard'
import ClusterNodes from './components/cluster/ClusterNodes'

function App() {
  return (
    <Router>
      <AuthProvider>
        <ReactFlowProvider>
          <SocketIOProvider>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Projects */}
              <Route path="/projects" element={
                <ProtectedRoute>
                  <Layout>
                    <ProjectList />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/projects/new" element={
                <ProtectedRoute>
                  <Layout>
                    <ProjectForm mode="create" />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/projects/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <ProjectDetail />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/projects/:id/edit" element={
                <ProtectedRoute>
                  <Layout>
                    <ProjectForm mode="edit" />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Workflows */}
              <Route path="/workflows" element={
                <ProtectedRoute>
                  <Layout>
                    <WorkflowDashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/workflows/new" element={
                <ProtectedRoute>
                  <Layout>
                    <WorkflowEditor />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/workflows/:id" element={
                <ProtectedRoute>
                  <Layout>
                    <WorkflowEditor />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/workflows/:id/edit" element={
                <ProtectedRoute>
                  <Layout>
                    <WorkflowEditor />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/workflows/templates" element={
                <ProtectedRoute>
                  <Layout>
                    <WorkflowTemplates />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Cluster */}
              <Route path="/cluster" element={
                <ProtectedRoute>
                  <Layout>
                    <ClusterNodes />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/cluster/nodes" element={
                <ProtectedRoute>
                  <Layout>
                    <ClusterNodes />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Agents */}
              <Route path="/agents" element={
                <ProtectedRoute>
                  <Layout>
                    <Agents />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Executions */}
              <Route path="/executions" element={
                <ProtectedRoute>
                  <Layout>
                    <Executions />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Analytics */}
              <Route path="/analytics" element={
                <ProtectedRoute>
                  <Layout>
                    <Analytics />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* User Profile */}
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Layout>
                    <UserProfile />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Settings */}
              <Route path="/settings" element={
                <ProtectedRoute>
                  <Layout>
                    <Settings />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* Redirect unknown routes to dashboard */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </SocketIOProvider>
        </ReactFlowProvider>
      </AuthProvider>
    </Router>
  )
}

// Placeholder component for routes that aren't implemented yet
// function PlaceholderPage({ title }: { title: string }) {
//   return (
//     <div className="p-6">
//       <div className="text-center py-12">
//         <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
//         <p className="text-gray-600">This page is coming soon!</p>
//       </div>
//     </div>
//   )
// }


export default App