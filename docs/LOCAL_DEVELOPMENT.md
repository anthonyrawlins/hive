# Local Development Setup

## Overview

This guide explains how to set up Hive for local development when you don't have access to the production domain `hive.home.deepblack.cloud`.

## Custom DNS Setup

### Option 1: Edit /etc/hosts (Recommended)

Add the following entries to your `/etc/hosts` file:

```
127.0.0.1 hive.home.deepblack.cloud
127.0.0.1 hive-api.home.deepblack.cloud
127.0.0.1 hive-grafana.home.deepblack.cloud
127.0.0.1 hive-prometheus.home.deepblack.cloud
```

### Option 2: Use Local Domain

Alternatively, you can modify `docker-compose.swarm.yml` to use a local domain:

1. Replace all instances of `hive.home.deepblack.cloud` with `hive.localhost`
2. Update the CORS_ORIGINS environment variable:
   ```bash
   export CORS_ORIGINS=https://hive.localhost
   ```

## Port Access

When running locally, you can also access services directly via ports:

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8087
- **Grafana**: http://localhost:3002
- **Prometheus**: http://localhost:9091
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6380

## CORS Configuration

For local development, you may need to adjust CORS settings:

```bash
# For development with localhost
export CORS_ORIGINS="http://localhost:3000,http://localhost:3001,https://hive.localhost"

# Then deploy
docker stack deploy -c docker-compose.swarm.yml hive
```

## SSL Certificates

### Development Mode (HTTP)

For local development, you can disable HTTPS by:

1. Removing the TLS configuration from Traefik labels
2. Using `web` instead of `web-secured` entrypoints
3. Setting up a local Traefik instance without Let's Encrypt

### Self-Signed Certificates

For testing HTTPS locally:

1. Generate self-signed certificates for your local domain
2. Configure Traefik to use the local certificates
3. Add the certificates to your browser's trusted store

## Environment Variables

Create a `.env` file with local settings:

```bash
# .env for local development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://hive.localhost
DATABASE_URL=postgresql://hive:hivepass@postgres:5432/hive
REDIS_URL=redis://redis:6379
ENVIRONMENT=development
LOG_LEVEL=debug
```

## Troubleshooting

### DNS Not Resolving

If custom domains don't resolve:
1. Check your `/etc/hosts` file syntax
2. Clear your DNS cache: `sudo systemctl flush-dns` (Linux) or `sudo dscacheutil -flushcache` (macOS)
3. Try using IP addresses directly

### CORS Errors

If you see CORS errors:
1. Check the `CORS_ORIGINS` environment variable
2. Ensure the frontend is accessing the correct backend URL
3. Verify the backend is receiving requests from the expected origin

### SSL Certificate Errors

If you see SSL certificate errors:
1. Use HTTP instead of HTTPS for local development
2. Add certificate exceptions in your browser
3. Use a local certificate authority

## Alternative: Development Docker Compose

You can create a `docker-compose.dev.yml` file specifically for local development:

```yaml
# Simplified version without Traefik, using direct port mapping
services:
  hive-backend:
    # ... same config but without Traefik labels
    ports:
      - "8000:8000"  # Direct port mapping
    environment:
      - CORS_ORIGINS=http://localhost:3000
  
  hive-frontend:
    # ... same config but without Traefik labels  
    ports:
      - "3000:3000"  # Direct port mapping
```

Then run with:
```bash
docker-compose -f docker-compose.dev.yml up -d
```