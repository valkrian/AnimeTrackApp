# Docker Deployment Guide

This guide explains how to deploy the Seasonal Anime Tracker application using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

### 1. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Service Configuration

### Backend Service

**Port**: 8000  
**Health Check**: `/health` endpoint  
**Environment Variables**:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `ENVIRONMENT`: Environment mode (development/production)
- `DEBUG`: Enable debug mode (true/false)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `JIKAN_API_BASE_URL`: Jikan API base URL
- `CACHE_TTL_MINUTES`: Cache time-to-live in minutes
- `CACHE_CLEANUP_INTERVAL_MINUTES`: Cache cleanup interval

### Frontend Service

**Port**: 3000  
**Environment Variables**:

- `NODE_ENV`: Node environment (production/development)
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_TELEMETRY_DISABLED`: Disable Next.js telemetry

## Development vs Production

### Development Mode

The default `docker-compose.yml` is configured for development:

```bash
docker-compose up
```

### Production Mode

For production deployment, create a `docker-compose.prod.yml`:

```yaml
version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - CORS_ORIGINS=https://yourdomain.com
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    restart: always
```

Deploy with:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Networking

Services communicate through a custom bridge network `anime-tracker-network`:

- **Internal communication**: Services use container names (e.g., `http://backend:8000`)
- **External access**: Services are exposed on host ports (3000, 8000)

## Health Checks

Both services include health checks:

- **Backend**: Checks `/health` endpoint every 30s
- **Frontend**: Checks Node.js server every 30s
- **Startup grace period**: 5s
- **Retries**: 3 attempts before marking unhealthy

## Troubleshooting

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild Services

```bash
# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache backend
```

### Check Service Health

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend (should return HTML)
curl http://localhost:3000
```

### Common Issues

**Issue**: Frontend can't connect to backend  
**Solution**: Ensure `NEXT_PUBLIC_API_URL` points to the correct backend URL

**Issue**: CORS errors  
**Solution**: Add frontend URL to `CORS_ORIGINS` in backend environment

**Issue**: Services won't start  
**Solution**: Check logs with `docker-compose logs` and verify port availability

## Resource Management

### View Resource Usage

```bash
docker stats
```

### Limit Resources

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove all containers, networks, and images
docker-compose down --rmi all

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Security Best Practices

1. **Non-root users**: Both Dockerfiles use non-root users
2. **Multi-stage builds**: Reduces image size and attack surface
3. **Health checks**: Ensures services are running correctly
4. **Environment variables**: Never commit `.env` files with secrets
5. **Network isolation**: Services communicate through private network

## Performance Optimization

1. **Layer caching**: Dependencies are cached in separate layers
2. **Minimal base images**: Uses Alpine Linux for smaller images
3. **Production builds**: Frontend uses optimized Next.js standalone output
4. **Single worker**: Backend uses 1 uvicorn worker (adjust for production)

## Next Steps

- Configure reverse proxy (nginx/traefik) for production
- Set up SSL/TLS certificates
- Implement container orchestration (Kubernetes/Docker Swarm)
- Add monitoring and logging solutions
- Configure automated backups
