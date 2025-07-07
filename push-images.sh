#!/bin/bash

# Push Hive images to local registry for swarm deployment

set -e

REGISTRY="anthonyrawlins"
BACKEND_IMAGE="hive-backend"
FRONTEND_IMAGE="hive-frontend"
LOCAL_BACKEND="hive-hive-backend"
LOCAL_FRONTEND="hive-hive-frontend"

echo "🏗️ Building and pushing Hive images to Docker Hub..."

# Tag and push backend
echo "📦 Pushing backend image..."
docker tag ${LOCAL_BACKEND}:latest ${REGISTRY}/${BACKEND_IMAGE}:latest
docker push ${REGISTRY}/${BACKEND_IMAGE}:latest

# Tag and push frontend  
echo "📦 Pushing frontend image..."
docker tag ${LOCAL_FRONTEND}:latest ${REGISTRY}/${FRONTEND_IMAGE}:latest
docker push ${REGISTRY}/${FRONTEND_IMAGE}:latest

echo "✅ Images pushed to Docker Hub successfully!"
echo "Backend: ${REGISTRY}/${BACKEND_IMAGE}:latest"
echo "Frontend: ${REGISTRY}/${FRONTEND_IMAGE}:latest"