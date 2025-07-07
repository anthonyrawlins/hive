#!/bin/bash

# Deploy Hive to Docker Swarm
# This script deploys the Hive distributed AI orchestration platform to the Docker Swarm

set -e

# Configuration
STACK_NAME="hive"
COMPOSE_FILE="docker-compose.swarm.yml"
DOMAIN="hive.home.deepblack.cloud"

echo "🐝 Deploying Hive to Docker Swarm"
echo "=================================="

# Check if we're on a swarm manager
if ! docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
    echo "❌ This node is not part of a Docker Swarm or not a manager"
    exit 1
fi

# Check if tengig network exists
if ! docker network ls | grep -q "tengig"; then
    echo "❌ The 'tengig' network does not exist. Please create it first."
    echo "Run: docker network create --driver overlay --attachable tengig"
    exit 1
fi

# Build images first (if needed)
echo "🔨 Building Docker images..."
docker compose -f $COMPOSE_FILE build

# Deploy to swarm
echo "🚀 Deploying stack to swarm..."
docker stack deploy -c $COMPOSE_FILE $STACK_NAME

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check deployment status
echo "📊 Checking deployment status..."
docker stack services $STACK_NAME

# Show service logs
echo "📋 Recent service logs:"
docker service logs ${STACK_NAME}_hive-backend --tail 20
docker service logs ${STACK_NAME}_hive-frontend --tail 20

echo ""
echo "✅ Hive deployment completed!"
echo "🌐 Access your Hive cluster at: https://$DOMAIN"
echo "📊 Grafana dashboard: https://$DOMAIN/grafana"
echo "📈 Prometheus metrics: https://$DOMAIN/prometheus"
echo ""
echo "🔧 Useful commands:"
echo "  docker stack services $STACK_NAME"
echo "  docker stack ps $STACK_NAME"
echo "  docker service logs ${STACK_NAME}_hive-backend"
echo "  docker stack rm $STACK_NAME"
echo ""

# DNS Configuration note
echo "📝 DNS Configuration:"
echo "Make sure $DOMAIN points to your swarm manager IP"
echo "Add this to your local DNS or hosts file if needed"
echo ""

# Test connectivity
echo "🔍 Testing connectivity..."
if curl -s --connect-timeout 5 https://$DOMAIN > /dev/null; then
    echo "✅ HTTPS connection successful"
else
    echo "⚠️  HTTPS connection failed - check DNS and SSL certificates"
    echo "💡 It may take a few minutes for SSL certificates to be provisioned"
fi

echo "🎉 Deployment complete! The Hive cluster is now running on Docker Swarm."