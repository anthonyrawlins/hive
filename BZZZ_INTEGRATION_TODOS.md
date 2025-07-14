# 🐝 Hive-Bzzz Integration TODOs

**Updated**: January 13, 2025  
**Context**: Dynamic Project-Based Task Discovery for Bzzz P2P Coordination

---

## 🎯 **HIGH PRIORITY: Project Registration & Activation System**

### **1. Database-Driven Project Management**
- [ ] **Migrate from filesystem-only to hybrid approach**
  - [ ] Update `ProjectService` to use PostgreSQL instead of filesystem scanning
  - [ ] Implement proper CRUD operations for projects table
  - [ ] Add database migration for enhanced project schema
  - [ ] Create repository management fields in projects table

### **2. Enhanced Project Schema**
- [ ] **Extend projects table with Git repository fields**
  ```sql
  ALTER TABLE projects ADD COLUMN git_url VARCHAR(500);
  ALTER TABLE projects ADD COLUMN git_owner VARCHAR(255);
  ALTER TABLE projects ADD COLUMN git_repository VARCHAR(255);
  ALTER TABLE projects ADD COLUMN git_branch VARCHAR(255) DEFAULT 'main';
  ALTER TABLE projects ADD COLUMN bzzz_enabled BOOLEAN DEFAULT false;
  ALTER TABLE projects ADD COLUMN ready_to_claim BOOLEAN DEFAULT false;
  ALTER TABLE projects ADD COLUMN private_repo BOOLEAN DEFAULT false;
  ALTER TABLE projects ADD COLUMN github_token_required BOOLEAN DEFAULT false;
  ```

### **3. Project Registration API**
- [ ] **Create comprehensive project registration endpoints**
  ```python
  POST /api/projects/register - Register new Git repository as project
  PUT /api/projects/{id}/activate - Mark project as ready for Bzzz consumption  
  PUT /api/projects/{id}/deactivate - Remove project from Bzzz scanning
  GET /api/projects/active - Get all projects marked for Bzzz consumption
  PUT /api/projects/{id}/git-config - Update Git repository configuration
  ```

### **4. Bzzz Integration Endpoints**
- [ ] **Create dedicated endpoints for Bzzz agents**
  ```python
  GET /api/bzzz/active-repos - Get list of active repository configurations
  GET /api/bzzz/projects/{id}/tasks - Get bzzz-task labeled issues for project
  POST /api/bzzz/projects/{id}/claim - Register task claim with Hive system
  PUT /api/bzzz/projects/{id}/status - Update task status in Hive
  ```

### **5. Frontend Project Management**
- [ ] **Enhance ProjectForm component**
  - [ ] Add Git repository URL field
  - [ ] Add "Enable for Bzzz" toggle
  - [ ] Add "Ready to Claim" activation control
  - [ ] Add private repository authentication settings

- [ ] **Update ProjectList component**
  - [ ] Add Bzzz status indicators (active/inactive/ready-to-claim)
  - [ ] Add bulk activation/deactivation controls
  - [ ] Add filter for Bzzz-enabled projects

- [ ] **Enhance ProjectDetail component**
  - [ ] Add "Bzzz Integration" tab
  - [ ] Display active bzzz-task issues from GitHub
  - [ ] Show task claim history and agent assignments
  - [ ] Add manual project activation controls

---

## 🔧 **MEDIUM PRIORITY: Enhanced GitHub Integration**

### **6. GitHub API Service Enhancement**
- [ ] **Extend GitHubService class**
  - [ ] Add method to fetch issues with bzzz-task label
  - [ ] Implement issue status synchronization
  - [ ] Add webhook support for real-time issue updates
  - [ ] Create GitHub token management for private repos

### **7. Task Synchronization System**
- [ ] **Bidirectional GitHub-Hive sync**
  - [ ] Sync bzzz-task issues to Hive tasks table
  - [ ] Update Hive when GitHub issues change
  - [ ] Propagate task claims back to GitHub assignees
  - [ ] Handle issue closure and completion status

### **8. Authentication & Security**
- [ ] **GitHub token management**
  - [ ] Store encrypted GitHub tokens per project
  - [ ] Support organization-level access tokens
  - [ ] Implement token rotation and validation
  - [ ] Add API key authentication for Bzzz agents

---

## 🚀 **LOW PRIORITY: Advanced Features**

### **9. Project Analytics & Monitoring**
- [ ] **Bzzz coordination metrics**
  - [ ] Track task claim rates per project
  - [ ] Monitor agent coordination efficiency
  - [ ] Measure task completion times
  - [ ] Generate project activity reports

### **10. Workflow Integration**
- [ ] **N8N workflow triggers**
  - [ ] Trigger workflows when projects are activated
  - [ ] Notify administrators of project registration
  - [ ] Automate project setup and validation
  - [ ] Create project health monitoring workflows

### **11. Advanced UI Features**
- [ ] **Real-time project monitoring**
  - [ ] Live task claim notifications
  - [ ] Real-time agent coordination display
  - [ ] Project activity timeline view
  - [ ] Collaborative task assignment interface

---

## 📋 **API ENDPOINT SPECIFICATIONS**

### **GET /api/bzzz/active-repos**
```json
{
  "repositories": [
    {
      "project_id": 1,
      "name": "hive",
      "git_url": "https://github.com/anthonyrawlins/hive",
      "owner": "anthonyrawlins",
      "repository": "hive",
      "branch": "main",
      "bzzz_enabled": true,
      "ready_to_claim": true,
      "private_repo": false,
      "github_token_required": false
    }
  ]
}
```

### **POST /api/projects/register**
```json
{
  "name": "project-name",
  "description": "Project description",
  "git_url": "https://github.com/owner/repo",
  "private_repo": false,
  "bzzz_enabled": true,
  "auto_activate": false
}
```

---

## ✅ **SUCCESS CRITERIA**

### **Phase 1 Complete When:**
- [ ] Projects can be registered via UI with Git repository info
- [ ] Projects can be activated/deactivated for Bzzz consumption
- [ ] Bzzz agents can query active repositories via API
- [ ] Database properly stores all project configuration

### **Phase 2 Complete When:**
- [ ] GitHub issues sync with Hive task system
- [ ] Task claims propagate between systems
- [ ] Real-time updates work bidirectionally
- [ ] Private repository authentication functional

### **Full Integration Complete When:**
- [ ] Multiple projects can be managed simultaneously
- [ ] Bzzz agents coordinate across multiple repositories
- [ ] UI provides comprehensive project monitoring
- [ ] Analytics track cross-project coordination efficiency

---

**Next Immediate Action**: Implement database CRUD operations in ProjectService and create /api/bzzz/active-repos endpoint.