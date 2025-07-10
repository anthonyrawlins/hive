# Hive Database Schema Management

This directory contains database schema files and migration scripts for the Hive platform.

## Files Overview

### Schema Files
- `000_complete_schema.sql` - **Complete database schema from scratch**
- `001_initial_schema.sql` - Original initial schema (legacy)
- `002_add_auth_fields.sql` - Migration to add authentication fields (legacy)

### Scripts
- `../scripts/rebuild_database.sh` - Shell script to rebuild database using Docker
- `../scripts/rebuild_database.py` - Python script to rebuild database

## Complete Database Rebuild

The `000_complete_schema.sql` file contains the **complete, unified database schema** that includes:

✅ **Unified User Management**
- UUID-based user IDs
- Complete authentication fields (username, email, passwords)
- User roles and permissions (is_active, is_superuser, is_verified)
- Backward compatibility fields (role, full_name)

✅ **Authentication System**
- API keys with scoped permissions
- JWT refresh tokens with device tracking
- Token blacklisting for security
- Comprehensive usage tracking

✅ **Agent Management**
- AI agent registration and configuration
- Performance metrics and monitoring
- Support for both Ollama and CLI agents

✅ **Workflow & Task Management**
- Workflow definitions with n8n integration
- Execution tracking and monitoring
- Task assignment and status management

✅ **Monitoring & Alerting**
- System alerts and notifications
- Performance metrics collection
- Agent health monitoring

## Usage

### Option 1: Docker-based Rebuild (Recommended)

```bash
# From the backend directory
cd /path/to/hive/backend
./scripts/rebuild_database.sh
```

This script:
- Connects to the PostgreSQL service in Docker swarm
- Executes the complete schema rebuild
- Verifies the installation
- Shows initial user credentials

### Option 2: Python Script

```bash
# Set environment variables if needed
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=hive
export DB_USER=postgres
export DB_PASSWORD=hive123

# Run the Python script
python scripts/rebuild_database.py
```

### Option 3: Manual SQL Execution

```bash
# Connect to PostgreSQL and execute directly
psql -h localhost -U postgres -d hive -f migrations/000_complete_schema.sql
```

## Default Users

After rebuild, the database will contain:

| Email | Username | Password | Role | Permissions |
|-------|----------|----------|------|-------------|
| admin@hive.local | admin | admin123 | admin | Superuser, Active, Verified |
| developer@hive.local | developer | dev123 | developer | Active, Verified |

**⚠️ SECURITY: Change these default passwords immediately in production!**

## Schema Features

### UUID-based Design
- All primary entities use UUIDs for better scalability
- Consistent identification across distributed systems
- No integer ID conflicts in multi-node deployments

### Complete Authentication
- Password hashing with bcrypt
- API key generation with prefixes (hive_xxx)
- JWT token management with refresh and blacklisting
- Scoped permissions for fine-grained access control

### Performance Optimized
- Comprehensive indexing strategy
- Efficient queries for common operations
- Time-series optimization for metrics
- Proper foreign key relationships

### Monitoring Ready
- Built-in metrics collection
- Alert management system
- Agent performance tracking
- Execution monitoring

## Migration from Legacy Schema

If you have an existing database with the old schema, the complete rebuild will:

1. **Drop existing tables** (⚠️ DATA LOSS)
2. **Create unified schema** with all new features
3. **Insert default users** for immediate access

For production systems with existing data, consider:
- Creating a backup before rebuild
- Developing custom migration scripts
- Using the incremental migration files instead

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL service is running
- Check network connectivity to database
- Verify credentials and database name

### Permission Errors
- Ensure user has CREATE/DROP privileges
- Check database ownership
- Verify network policies allow connections

### Schema Conflicts
- Use complete rebuild for clean installation
- Check for existing databases/schemas
- Ensure proper cleanup of old installations

## Next Steps

After successful database rebuild:

1. **Change default passwords**
2. **Configure authentication settings**
3. **Register AI agents**
4. **Create initial workflows**
5. **Set up monitoring dashboards**

The unified schema provides a solid foundation for the complete Hive platform with authentication, agent management, and workflow orchestration.