#!/usr/bin/env python3
"""
Migration script to consolidate existing distributed AI projects into Hive
"""

import os
import sys
import json
import yaml
import shutil
import asyncio
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add paths for importing from existing projects
sys.path.append('/home/tony/AI/projects/distributed-ai-dev')
sys.path.append('/home/tony/AI/projects/McPlan/mcplan-web/backend')

class HiveMigrator:
    """
    Migrates and consolidates data from existing distributed AI projects
    """
    
    def __init__(self):
        self.hive_root = Path("/home/tony/AI/projects/hive")
        self.projects = {
            'distributed-ai-dev': Path("/home/tony/AI/projects/distributed-ai-dev"),
            'mcplan': Path("/home/tony/AI/projects/McPlan"),
            'cluster': Path("/home/tony/AI/projects/cluster"),
            'n8n-integration': Path("/home/tony/AI/projects/n8n-integration")
        }
        
        # Migration results
        self.migration_log = []
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log migration step"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.migration_log.append(log_entry)
        
    def error(self, message: str):
        """Log error"""
        self.log(message, "ERROR")
        self.errors.append(message)
        
    async def migrate_all(self):
        """Execute complete migration process"""
        self.log("🚀 Starting Hive migration from existing projects")
        
        try:
            # Phase 1: Setup and validation
            await self.setup_hive_structure()
            await self.validate_source_projects()
            
            # Phase 2: Configuration migration
            await self.migrate_agent_configurations()
            await self.migrate_monitoring_configs()
            
            # Phase 3: Code integration
            await self.extract_core_components()
            await self.migrate_database_schemas()
            
            # Phase 4: Data migration
            await self.migrate_workflows()
            await self.migrate_execution_history()
            
            # Phase 5: Documentation and cleanup
            await self.generate_migration_report()
            
            self.log("✅ Migration completed successfully!")
            
        except Exception as e:
            self.error(f"Migration failed: {str(e)}")
            raise
    
    async def setup_hive_structure(self):
        """Create Hive project directory structure"""
        self.log("📁 Setting up Hive project structure")
        
        directories = [
            "backend/app/core",
            "backend/app/api",
            "backend/app/models",
            "backend/app/services",
            "backend/app/utils",
            "backend/migrations",
            "backend/tests",
            "frontend/src/components/dashboard",
            "frontend/src/components/workflows", 
            "frontend/src/components/agents",
            "frontend/src/components/projects",
            "frontend/src/stores",
            "frontend/src/services",
            "frontend/src/types",
            "frontend/src/hooks",
            "frontend/src/utils",
            "config/agents",
            "config/workflows",
            "config/monitoring",
            "scripts",
            "docker",
            "docs/api",
            "docs/user-guide",
            "docs/admin-guide",
            "docs/developer-guide",
            "tests/e2e",
            "tests/integration",
            "tests/performance"
        ]
        
        for directory in directories:
            (self.hive_root / directory).mkdir(parents=True, exist_ok=True)
            
        self.log(f"Created {len(directories)} directories")
    
    async def validate_source_projects(self):
        """Validate that source projects exist and are accessible"""
        self.log("🔍 Validating source projects")
        
        for name, path in self.projects.items():
            if path.exists():
                self.log(f"✅ Found {name} at {path}")
            else:
                self.error(f"❌ Missing {name} at {path}")
    
    async def migrate_agent_configurations(self):
        """Migrate agent configurations from distributed-ai-dev"""
        self.log("🤖 Migrating agent configurations")
        
        source_config = self.projects['distributed-ai-dev'] / 'config' / 'agents.yaml'
        if not source_config.exists():
            self.log("⚠️  No agent configuration found in distributed-ai-dev")
            return
            
        # Load existing configuration
        with open(source_config, 'r') as f:
            agents_config = yaml.safe_load(f)
            
        # Create enhanced Hive configuration
        hive_config = {
            'hive': {
                'cluster': {
                    'name': 'Development Cluster',
                    'region': 'home.deepblack.cloud'
                },
                'agents': {},
                'monitoring': {
                    'metrics_retention_days': 30,
                    'alert_thresholds': {
                        'cpu_usage': 85,
                        'memory_usage': 90,
                        'gpu_usage': 95,
                        'response_time': 60
                    },
                    'health_check_interval': 30
                },
                'workflows': {
                    'templates': {
                        'web_development': {
                            'agents': ['walnut', 'ironwood'],
                            'stages': ['planning', 'frontend', 'backend', 'integration', 'testing']
                        },
                        'infrastructure': {
                            'agents': ['acacia', 'ironwood'],
                            'stages': ['design', 'provisioning', 'deployment', 'monitoring']
                        }
                    }
                },
                'mcp_servers': {
                    'registry': {
                        'comfyui': 'ws://localhost:8188/api/mcp',
                        'code_review': 'http://localhost:8000/mcp'
                    }
                },
                'security': {
                    'require_approval': True,
                    'api_rate_limit': 100,
                    'session_timeout': 3600
                }
            }
        }
        
        # Migrate agent configurations with enhancements
        if 'agents' in agents_config:
            for agent_id, agent_config in agents_config['agents'].items():
                enhanced_config = {
                    'name': agent_config.get('name', f'{agent_id.upper()} Agent'),
                    'endpoint': agent_config.get('endpoint', f'http://localhost:11434'),
                    'model': agent_config.get('model', 'llama2'),
                    'specialization': agent_config.get('specialization', 'general'),
                    'capabilities': agent_config.get('capabilities', []),
                    'hardware': agent_config.get('hardware', {}),
                    'performance_targets': agent_config.get('performance_targets', {
                        'min_tps': 10,
                        'max_response_time': 30
                    })
                }
                hive_config['hive']['agents'][agent_id] = enhanced_config
        
        # Add default agents if none exist
        if not hive_config['hive']['agents']:
            hive_config['hive']['agents'] = {
                'acacia': {
                    'name': 'ACACIA Infrastructure Specialist',
                    'endpoint': 'http://192.168.1.72:11434',
                    'model': 'deepseek-r1:7b',
                    'specialization': 'infrastructure',
                    'capabilities': ['devops', 'architecture', 'deployment'],
                    'hardware': {
                        'gpu_type': 'AMD Radeon RX 7900 XTX',
                        'vram_gb': 24,
                        'cpu_cores': 16
                    },
                    'performance_targets': {
                        'min_tps': 15,
                        'max_response_time': 30
                    }
                },
                'walnut': {
                    'name': 'WALNUT Full-Stack Developer',
                    'endpoint': 'http://192.168.1.27:11434',
                    'model': 'starcoder2:15b',
                    'specialization': 'full-stack',
                    'capabilities': ['frontend', 'backend', 'ui-design'],
                    'hardware': {
                        'gpu_type': 'NVIDIA RTX 4090',
                        'vram_gb': 24,
                        'cpu_cores': 12
                    },
                    'performance_targets': {
                        'min_tps': 20,
                        'max_response_time': 25
                    }
                },
                'ironwood': {
                    'name': 'IRONWOOD Backend Specialist',
                    'endpoint': 'http://192.168.1.113:11434',
                    'model': 'deepseek-coder-v2',
                    'specialization': 'backend',
                    'capabilities': ['optimization', 'databases', 'apis'],
                    'hardware': {
                        'gpu_type': 'NVIDIA RTX 4080',
                        'vram_gb': 16,
                        'cpu_cores': 8
                    },
                    'performance_targets': {
                        'min_tps': 18,
                        'max_response_time': 35
                    }
                }
            }
        
        # Save unified configuration
        config_path = self.hive_root / 'config' / 'hive.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(hive_config, f, default_flow_style=False, sort_keys=False)
            
        self.log(f"✅ Migrated {len(hive_config['hive']['agents'])} agent configurations")
    
    async def migrate_monitoring_configs(self):
        """Migrate monitoring configurations from cluster project"""
        self.log("📊 Migrating monitoring configurations")
        
        # Create Prometheus configuration
        prometheus_config = {
            'global': {
                'scrape_interval': '30s',
                'evaluation_interval': '30s'
            },
            'rule_files': ['hive_alerts.yml'],
            'scrape_configs': [
                {
                    'job_name': 'hive-backend',
                    'static_configs': [{'targets': ['hive-coordinator:8000']}],
                    'metrics_path': '/api/metrics'
                },
                {
                    'job_name': 'hive-agents',
                    'static_configs': [
                        {'targets': ['192.168.1.72:11434']},
                        {'targets': ['192.168.1.27:11434']},
                        {'targets': ['192.168.1.113:11434']}
                    ]
                }
            ]
        }
        
        prometheus_path = self.hive_root / 'config' / 'monitoring' / 'prometheus.yml'
        with open(prometheus_path, 'w') as f:
            yaml.dump(prometheus_config, f)
            
        # Create Grafana dashboard configurations
        grafana_config = {
            'dashboards': {
                'hive_overview': {
                    'title': 'Hive Cluster Overview',
                    'panels': [
                        'Agent Status',
                        'Task Queue Length',
                        'Execution Success Rate',
                        'Response Times',
                        'Resource Utilization'
                    ]
                },
                'agent_performance': {
                    'title': 'Agent Performance Details',
                    'panels': [
                        'Tokens per Second',
                        'GPU Utilization',
                        'Memory Usage',
                        'Active Tasks'
                    ]
                }
            }
        }
        
        grafana_path = self.hive_root / 'config' / 'monitoring' / 'grafana.yml'
        with open(grafana_path, 'w') as f:
            yaml.dump(grafana_config, f)
            
        self.log("✅ Created monitoring configurations")
    
    async def extract_core_components(self):
        """Extract and adapt core components from existing projects"""
        self.log("🔧 Extracting core components")
        
        # Map of source files to destination files
        component_mapping = {
            # From distributed-ai-dev
            'distributed-ai-dev/src/core/ai_dev_coordinator.py': 'backend/app/core/hive_coordinator.py',
            'distributed-ai-dev/src/monitoring/performance_monitor.py': 'backend/app/core/performance_monitor.py',
            'distributed-ai-dev/src/config/agent_manager.py': 'backend/app/core/agent_manager.py',
            
            # From McPlan
            'McPlan/mcplan-web/backend/app/core/mcplan_engine.py': 'backend/app/core/workflow_engine.py',
            'McPlan/mcplan-web/backend/app/api/workflows.py': 'backend/app/api/workflows.py',
            'McPlan/mcplan-web/backend/app/api/execution.py': 'backend/app/api/executions.py',
            'McPlan/mcplan-web/backend/app/models/workflow.py': 'backend/app/models/workflow.py',
            
            # Frontend components
            'McPlan/mcplan-web/frontend/src/components/WorkflowEditor/': 'frontend/src/components/workflows/',
            'McPlan/mcplan-web/frontend/src/components/ExecutionPanel/': 'frontend/src/components/executions/',
            'McPlan/mcplan-web/frontend/src/stores/': 'frontend/src/stores/'
        }
        
        for source_rel, dest_rel in component_mapping.items():
            source_path = None
            for project_name, project_path in self.projects.items():
                potential_source = project_path / source_rel.split('/', 1)[1]
                if potential_source.exists():
                    source_path = potential_source
                    break
                    
            if source_path:
                dest_path = self.hive_root / dest_rel
                
                if source_path.is_file():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    self.log(f"📄 Copied {source_path.name}")
                elif source_path.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    self.log(f"📁 Copied directory {source_path.name}")
            else:
                self.log(f"⚠️  Could not find source: {source_rel}")
        
        self.log("✅ Core components extracted")
    
    async def migrate_database_schemas(self):
        """Create unified database schema"""
        self.log("🗄️  Creating unified database schema")
        
        schema_sql = """
-- Hive Unified Database Schema

-- User Management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    role VARCHAR(50) DEFAULT 'developer',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Agent Management
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    endpoint VARCHAR(512) NOT NULL,
    model VARCHAR(255),
    specialization VARCHAR(100),
    capabilities JSONB,
    hardware_config JSONB,
    status VARCHAR(50) DEFAULT 'offline',
    performance_targets JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

-- Workflow Management
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    n8n_data JSONB NOT NULL,
    mcp_tools JSONB,
    created_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Execution Tracking
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Task Management
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_agent_id UUID REFERENCES agents(id),
    workflow_id UUID REFERENCES workflows(id),
    execution_id UUID REFERENCES executions(id),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Performance Metrics (Time Series)
CREATE TABLE agent_metrics (
    agent_id UUID REFERENCES agents(id),
    timestamp TIMESTAMP NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    gpu_usage FLOAT,
    tokens_per_second FLOAT,
    response_time FLOAT,
    active_tasks INTEGER,
    status VARCHAR(50),
    PRIMARY KEY (agent_id, timestamp)
);

-- System Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    agent_id UUID REFERENCES agents(id),
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_workflows_active ON workflows(active, created_at);
CREATE INDEX idx_executions_status ON executions(status, created_at);
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC, created_at);
CREATE INDEX idx_agent_metrics_timestamp ON agent_metrics(timestamp);
CREATE INDEX idx_agent_metrics_agent_time ON agent_metrics(agent_id, timestamp);
CREATE INDEX idx_alerts_unresolved ON alerts(resolved, created_at) WHERE resolved = false;

-- Sample data
INSERT INTO users (email, hashed_password, role) VALUES 
('admin@hive.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewohT6ZErjH.2T.2', 'admin'),
('developer@hive.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewohT6ZErjH.2T.2', 'developer');
"""
        
        schema_path = self.hive_root / 'backend' / 'migrations' / '001_initial_schema.sql'
        with open(schema_path, 'w') as f:
            f.write(schema_sql)
            
        self.log("✅ Database schema created")
    
    async def migrate_workflows(self):
        """Migrate existing workflows from McPlan"""
        self.log("🔄 Migrating workflows")
        
        workflows_migrated = 0
        
        # Look for workflow files in McPlan
        mcplan_workflows = self.projects['mcplan'] / 'mcplan-web'
        workflow_files = []
        
        # Find JSON workflow files
        for json_file in mcplan_workflows.rglob('*.json'):
            if 'workflow' in json_file.name.lower() or 'n8n' in json_file.name.lower():
                workflow_files.append(json_file)
                
        # Migrate each workflow file
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = json.load(f)
                    
                # Create workflow migration record
                migration_record = {
                    'source_file': str(workflow_file),
                    'name': workflow_data.get('name', workflow_file.stem),
                    'description': f'Migrated from {workflow_file.name}',
                    'n8n_data': workflow_data,
                    'migrated_at': datetime.now().isoformat()
                }
                
                # Save to Hive workflows directory
                dest_file = self.hive_root / 'config' / 'workflows' / f'{workflow_file.stem}.json'
                with open(dest_file, 'w') as f:
                    json.dump(migration_record, f, indent=2)
                    
                workflows_migrated += 1
                self.log(f"📄 Migrated workflow: {workflow_file.name}")
                
            except Exception as e:
                self.error(f"Failed to migrate {workflow_file.name}: {str(e)}")
        
        self.log(f"✅ Migrated {workflows_migrated} workflows")
    
    async def migrate_execution_history(self):
        """Migrate execution history from McPlan database"""
        self.log("📊 Migrating execution history")
        
        # Look for McPlan database
        mcplan_db = self.projects['mcplan'] / 'mcplan-web' / 'mcplan.db'
        if not mcplan_db.exists():
            self.log("⚠️  No McPlan database found, skipping execution history")
            return
            
        executions_migrated = 0
        
        try:
            # Connect to McPlan SQLite database
            conn = sqlite3.connect(mcplan_db)
            cursor = conn.cursor()
            
            # Export execution data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            migration_data = {}
            
            for (table_name,) in tables:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Convert to dictionaries
                table_data = []
                for row in rows:
                    table_data.append(dict(zip(columns, row)))
                    
                migration_data[table_name] = table_data
                
            conn.close()
            
            # Save migration data
            migration_file = self.hive_root / 'scripts' / 'mcplan_data_export.json'
            with open(migration_file, 'w') as f:
                json.dump(migration_data, f, indent=2, default=str)
                
            executions_migrated = len(migration_data.get('executions', []))
            self.log(f"✅ Exported {executions_migrated} execution records")
            
        except Exception as e:
            self.error(f"Failed to migrate execution history: {str(e)}")
    
    async def generate_migration_report(self):
        """Generate comprehensive migration report"""
        self.log("📋 Generating migration report")
        
        report = {
            'migration_summary': {
                'timestamp': datetime.now().isoformat(),
                'source_projects': list(self.projects.keys()),
                'hive_version': '1.0.0',
                'migration_status': 'completed' if not self.errors else 'completed_with_errors'
            },
            'components_migrated': {
                'agent_configurations': 'config/hive.yaml',
                'monitoring_configs': 'config/monitoring/',
                'database_schema': 'backend/migrations/001_initial_schema.sql',
                'core_components': 'backend/app/core/',
                'api_endpoints': 'backend/app/api/',
                'frontend_components': 'frontend/src/components/',
                'workflows': 'config/workflows/'
            },
            'next_steps': [
                'Review and update imported configurations',
                'Set up development environment with docker-compose up',
                'Run database migrations',
                'Test agent connectivity',
                'Verify workflow execution',
                'Configure monitoring and alerting',
                'Update documentation'
            ],
            'migration_log': self.migration_log,
            'errors': self.errors
        }
        
        report_path = self.hive_root / 'MIGRATION_REPORT.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Also create a markdown summary
        md_report = f"""# Hive Migration Report

## Summary
- **Migration Date**: {report['migration_summary']['timestamp']}
- **Status**: {report['migration_summary']['migration_status']}
- **Source Projects**: {', '.join(report['migration_summary']['source_projects'])}
- **Errors**: {len(self.errors)}

## Components Migrated
"""
        
        for component, location in report['components_migrated'].items():
            md_report += f"- **{component.replace('_', ' ').title()}**: `{location}`\n"
            
        md_report += f"""
## Next Steps
"""
        for i, step in enumerate(report['next_steps'], 1):
            md_report += f"{i}. {step}\n"
            
        if self.errors:
            md_report += f"""
## Errors Encountered
"""
            for error in self.errors:
                md_report += f"- {error}\n"
                
        md_report_path = self.hive_root / 'MIGRATION_REPORT.md'
        with open(md_report_path, 'w') as f:
            f.write(md_report)
            
        self.log("✅ Migration report generated")
        self.log(f"📄 Report saved to: {report_path}")
        self.log(f"📄 Summary saved to: {md_report_path}")

async def main():
    """Main migration function"""
    migrator = HiveMigrator()
    
    try:
        await migrator.migrate_all()
        
        print("\n" + "="*60)
        print("🎉 HIVE MIGRATION COMPLETED!")
        print("="*60)
        print(f"✅ Migration successful with {len(migrator.errors)} errors")
        print(f"📁 Hive project created at: {migrator.hive_root}")
        print(f"📋 Check MIGRATION_REPORT.md for detailed results")
        print("\nNext steps:")
        print("1. cd /home/tony/AI/projects/hive")
        print("2. Review config/hive.yaml")
        print("3. docker-compose up -d")
        print("4. Visit http://localhost:3000")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print(f"📋 Check logs for details")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())