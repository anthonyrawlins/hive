#!/bin/bash
# Hive Database Rebuild Script
# Completely rebuilds the Hive database schema using Docker and the complete schema file

set -e

echo "🔄 Starting Hive database rebuild..."

# Configuration
POSTGRES_HOST=${DB_HOST:-"hive_postgres"}
POSTGRES_DB=${DB_NAME:-"hive"}
POSTGRES_USER=${DB_USER:-"postgres"}
POSTGRES_PASSWORD=${DB_PASSWORD:-"hive123"}
POSTGRES_PORT=${DB_PORT:-"5432"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() { echo -e "${BLUE}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo_error "❌ Docker is not available"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "./migrations/000_complete_schema.sql" ]]; then
    echo_error "❌ Complete schema file not found. Please run from backend directory."
    exit 1
fi

echo_info "📄 Using complete schema: ./migrations/000_complete_schema.sql"

# Check if PostgreSQL container is running
if ! docker service ls | grep -q hive_postgres; then
    echo_warning "⚠️  PostgreSQL service not found in Docker swarm"
    echo_info "🚀 Starting PostgreSQL service..."
    
    # Try to find a PostgreSQL container to use
    if docker ps | grep -q postgres; then
        echo_info "📦 Found running PostgreSQL container"
    else
        echo_error "❌ No PostgreSQL container available. Please start the Hive stack first."
        echo_info "Run: docker stack deploy -c docker-compose.swarm.yml hive"
        exit 1
    fi
fi

# Function to execute SQL using Docker
execute_sql() {
    local sql_file="$1"
    echo_info "🏗️  Executing SQL file: $sql_file"
    
    # Copy SQL file to a temporary location and execute it via Docker
    docker run --rm \
        --network hive_default \
        -v "$(pwd):/workspace" \
        -e PGPASSWORD="$POSTGRES_PASSWORD" \
        postgres:15-alpine \
        psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "/workspace/$sql_file"
}

# Function to test database connection
test_connection() {
    echo_info "🔌 Testing database connection..."
    
    docker run --rm \
        --network hive_default \
        -e PGPASSWORD="$POSTGRES_PASSWORD" \
        postgres:15-alpine \
        psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();" > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        echo_success "✅ Database connection successful"
        return 0
    else
        echo_error "❌ Database connection failed"
        return 1
    fi
}

# Function to verify rebuild
verify_rebuild() {
    echo_info "📊 Verifying database rebuild..."
    
    local result=$(docker run --rm \
        --network hive_default \
        -e PGPASSWORD="$POSTGRES_PASSWORD" \
        postgres:15-alpine \
        psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "
        SELECT 
            (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public') as tables,
            (SELECT COUNT(*) FROM users) as users;
        ")
    
    local tables=$(echo "$result" | awk '{print $1}')
    local users=$(echo "$result" | awk '{print $3}')
    
    echo_info "   - Tables created: $tables"
    echo_info "   - Initial users: $users"
    
    if [[ $tables -gt 10 ]] && [[ $users -ge 2 ]]; then
        echo_success "✅ Database rebuild verification passed"
        echo_warning "⚠️  SECURITY: Change default passwords in production!"
        return 0
    else
        echo_error "❌ Database rebuild verification failed"
        return 1
    fi
}

# Main execution
main() {
    # Test connection first
    if ! test_connection; then
        echo_error "❌ Cannot proceed without database connection"
        exit 1
    fi
    
    # Execute the complete schema rebuild
    echo_info "🏗️  Rebuilding database schema..."
    
    if execute_sql "migrations/000_complete_schema.sql"; then
        echo_success "✅ Database schema rebuilt successfully!"
        
        # Verify the rebuild
        if verify_rebuild; then
            echo_success "🎉 Hive database rebuild completed successfully!"
            echo_info "🚀 Ready for authentication and full platform functionality"
            echo_info ""
            echo_info "Default credentials:"
            echo_info "  Admin: admin@hive.local / admin123"
            echo_info "  Developer: developer@hive.local / dev123"
            echo_warning "⚠️  CHANGE THESE PASSWORDS IN PRODUCTION!"
        else
            exit 1
        fi
    else
        echo_error "❌ Failed to rebuild database schema"
        exit 1
    fi
}

# Run main function
main "$@"