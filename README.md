# flask-container-backup

A lightweight, self-hosted Flask server that stops a Docker container, zips up its local volume data, and uploads the archive to a remote destination. Designed to run as a Docker container alongside your existing stack.

[![Docker Hub](https://img.shields.io/badge/docker-zackwag%2Fflask--container--backup-blue?style=flat-square&logo=docker)](https://hub.docker.com/r/zackwag/flask-container-backup)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Backend](https://img.shields.io/badge/backend-Python%20%2B%20Flask-3776AB?style=flat-square&logo=python)](https://flask.palletsprojects.com/)

---

## Overview

`flask-container-backup` exposes a simple REST API for triggering on-demand or scheduled backups of Docker containers. Each backup stops the target container, compresses the source folder into a timestamped zip archive, uploads it to the configured destination, and applies retention cleanup to remove old backups beyond a specified number of days.

---

## Features

- **Per-container endpoints** — Trigger a backup for any individual container via `POST /backup/<container_name>`
- **Backup all at once** — Trigger all configured container backups simultaneously via `POST /backup`
- **Non-blocking** — Backups run in background threads and return immediately with a `202 Accepted` response
- **Retention management** — Automatically removes backups older than the configured number of days
- **JSON-driven config** — Define all containers and their backup settings in a single `containers.json` file
- **Cloud upload support** — Works with OneDrive and other rclone-compatible destinations

---

## Quick Start

### 1. Pull the image

```bash
docker pull zackwag/flask-container-backup
```

### 2. Create your `containers.json`

```json
[
  {
    "container_name": "my-app",
    "source_folder": "/docker/my-app",
    "destination_folder": "onedrive:/backups/my-app",
    "retention_days": 7
  },
  {
    "container_name": "another-app",
    "source_folder": "/docker/another-app",
    "destination_folder": "onedrive:/backups/another-app",
    "retention_days": 14
  }
]
```

### 3. Run the container

```yaml
services:
  flask-container-backup:
    image: zackwag/flask-container-backup:latest
    container_name: flask-container-backup
    restart: unless-stopped
    ports:
      - 2128:2128
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /path/to/containers.json:/app/containers.json
      - /docker:/docker
```

> The Docker socket mount is required so the container can stop and start other containers. Adjust the `/docker` volume mount to match your local data path.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/backup` | Trigger a backup for all configured containers |
| `POST` | `/backup/<container_name>` | Trigger a backup for a specific container |

### Example

```bash
# Backup all containers
curl -X POST http://localhost:2128/backup

# Backup a specific container
curl -X POST http://localhost:2128/backup/my-app
```

### Response

```json
{
  "status": "Backup started",
  "container": "my-app"
}
```

All backup endpoints return `202 Accepted` immediately. The backup runs asynchronously in the background.

---

## Configuration

Container backup settings are defined in `containers.json`. Each entry supports the following fields:

| Field | Description |
|-------|-------------|
| `container_name` | The name of the Docker container to back up |
| `source_folder` | Local path to the container's data directory |
| `destination_folder` | Remote destination path (rclone-compatible) |
| `retention_days` | Number of days to retain backups before cleanup |

---

## Building from Source

```bash
git clone https://github.com/zackwag/flask-container-backup
cd flask-container-backup
docker build -t flask-container-backup .
```

---

## Docker Hub

[https://hub.docker.com/r/zackwag/flask-container-backup](https://hub.docker.com/r/zackwag/flask-container-backup)

---

## License

MIT
