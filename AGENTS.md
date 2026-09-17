# AGENTS.md

## Project overview

flask-container-backup is a self-hosted Flask server (Python 3) that stops a Docker container, zips its volume data, uploads the archive to a configured remote destination, and applies retention cleanup. v2 supports a hub/spoke architecture fanning out backups across multiple Docker hosts. Runs as a Docker container alongside the stack it backs up.

## Setup

```bash
pip install -r requirements.txt
```

## Build / Run

```bash
docker build -t flask-container-backup .
python server.py   # listens on port 2128
```

Configuration is driven by a `containers.json` file (see README for schema).

## Test

No automated test suite currently exists in this repo. Verify changes manually against the `/backup/<container_name>` and `/backup` endpoints.

## Repository structure

- `server.py` — Flask app / API routes
- `backup_container.py` — core backup logic (stop container, zip, upload, retention cleanup)
- `Dockerfile` — container build definition

## Commit and PR conventions

- Commit messages and PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`, `build:`, `perf:`, `style:`, `revert:`), optionally with a scope, e.g. `fix(api): handle null response`.
- This repo squash-merges pull requests only; the PR title becomes the final commit message on `main`.
- A "Conventional Commits" CI check enforces this on both PR titles and direct-push commit messages.
- Branch protection on `main`: no force-pushes, no branch deletion, required status checks must pass.
