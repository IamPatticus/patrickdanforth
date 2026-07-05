---
name: "portainer"
description: "Manage Docker via Portainer API - containers, stacks, images, volumes, networks, and exec"
---

# Portainer Skill

Manage Docker containers, stacks, images, volumes, networks, and execute commands via the Portainer API.

## Prerequisites

- Portainer instance running (CE or BE)
- API access token or username/password authentication
- Environment ID (usually 1 for local)

## Configuration

Store credentials in `~/.config/portainer.env`:

```bash
PORTAINER_URL=https://portainer.your-domain.com
PORTAINER_TOKEN=your-api-token
# OR for username/password:
# PORTAINER_USERNAME=admin
# PORTAINER_PASSWORD=your-password
```

Or pass inline:
```bash
export PORTAINER_URL=https://portainer.local:9443
export PORTAINER_TOKEN=ptr_xxx
```

## Quick Start

```bash
# List all containers
openclaw portainer containers list

# Start/stop/restart a container
openclaw portainer container start my-app
openclaw portainer container stop my-app
openclaw portainer container restart my-app

# View container logs
openclaw portainer container logs my-app --tail 100

# Execute command in container
openclaw portainer container exec my-app "ls -la /app"

# List all stacks
openclaw portainer stacks list

# Deploy a stack from compose file
openclaw portainer stack deploy my-stack --file docker-compose.yml

# Update a stack (pull latest images)
openclaw portainer stack update my-stack

# List images
openclaw portainer images list

# Prune unused images
openclaw portainer images prune

# List volumes
openclaw portainer volumes list

# List networks
openclaw portainer networks list
```

## Commands

### Containers

| Command | Description |
|---------|-------------|
| `containers list` | List all containers with status |
| `container start <name>` | Start a container |
| `container stop <name>` | Stop a container |
| `container restart <name>` | Restart a container |
| `container logs <name>` | View container logs |
| `container exec <name> <cmd>` | Execute command inside container |
| `container inspect <name>` | Show container details |
| `container remove <name>` | Remove a stopped container |

### Stacks

| Command | Description |
|---------|-------------|
| `stacks list` | List all stacks |
| `stack deploy <name> --file <path>` | Deploy/update from compose file |
| `stack update <name>` | Pull latest images and recreate |
| `stack stop <name>` | Stop all containers in stack |
| `stack start <name>` | Start all containers in stack |
| `stack remove <name>` | Remove stack and containers |
| `stack inspect <name>` | Show stack configuration |

### Images

| Command | Description |
|---------|-------------|
| `images list` | List all images |
| `images pull <image>` | Pull an image |
| `images remove <image>` | Remove an image |
| `images prune` | Remove unused images |
| `images build --file <dockerfile> --tag <tag>` | Build an image |

### Volumes

| Command | Description |
|---------|-------------|
| `volumes list` | List all volumes |
| `volume create <name>` | Create a volume |
| `volume remove <name>` | Remove a volume |
| `volume prune` | Remove unused volumes |
| `volume inspect <name>` | Show volume details |

### Networks

| Command | Description |
|---------|-------------|
| `networks list` | List all networks |
| `network create <name>` | Create a network |
| `network remove <name>` | Remove a network |
| `network inspect <name>` | Show network details |

### System

| Command | Description |
|---------|-------------|
| `system info` | Show Portainer/Docker info |
| `system prune` | Clean up unused resources |

## API Usage Examples

### Authentication (token-based)

```bash
# Get environment ID
curl -s -H "X-API-Key: $PORTAINER_TOKEN" \
  "$PORTAINER_URL/api/endpoints" | jq '.[] | {Id, Name}'

# List containers
curl -s -H "X-API-Key: $PORTAINER_TOKEN" \
  "$PORTAINER_URL/api/endpoints/1/docker/containers/json?all=1" | jq '.[] | {Names, State, Status}'

# Start container
curl -s -X POST -H "X-API-Key: $PORTAINER_TOKEN" \
  "$PORTAINER_URL/api/endpoints/1/docker/containers/<id>/start"

# Get container logs
curl -s -H "X-API-Key: $PORTAINER_TOKEN" \
  "$PORTAINER_URL/api/endpoints/1/docker/containers/<id>/logs?stdout=1&stderr=1&tail=100"

# Execute command in container
curl -s -X POST -H "X-API-Key: $PORTAINER_TOKEN" -H "Content-Type: application/json" \
  -d '{"Cmd": ["ls", "-la", "/"], "AttachStdout": true, "AttachStderr": true}' \
  "$PORTAINER_URL/api/endpoints/1/docker/containers/<id>/exec" | jq -r '.Id'

# Then start the exec instance
```

### Stack Operations

```bash
# List stacks
curl -s -H "X-API-Key: $PORTAINER_TOKEN" \
  "$PORTAINER_URL/api/stacks" | jq '.[] | {Id, Name, Status}'

# Create/update stack (must be on Portainer host filesystem or via file upload)
# Use Portainer UI or API file upload endpoint for remote deployment
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PORTAINER_URL` | Portainer instance URL | Yes |
| `PORTAINER_TOKEN` | API access token | If no user/pass |
| `PORTAINER_USERNAME` | Username for auth | If no token |
| `PORTAINER_PASSWORD` | Password for auth | If no token |
| `PORTAINER_ENV_ID` | Environment ID (default: 1) | No |

## Finding Your Token

1. Log into Portainer UI
2. Go to **My account** → **API access**
3. Click **New access token**
4. Copy the token (starts with `ptr_`)

## Notes

- Environment ID is usually `1` for the local Docker environment
- For multi-node setups, check environment ID via `GET /api/endpoints`
- Some operations require admin permissions
- Stack file paths must be accessible by the Portainer agent if using agent-based endpoints
