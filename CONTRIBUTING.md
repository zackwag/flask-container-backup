# Contributing to flask-container-backup

Thanks for considering a contribution to this self-hosted Flask backup server for Docker containers.

## Getting started

```bash
git clone https://github.com/zackwag/flask-container-backup.git
cd flask-container-backup
pip install -r requirements.txt
```

## Development

```bash
python server.py   # run the Flask API locally (listens on port 2128)
```

There is currently no automated test suite in this repo — please test changes manually (trigger a backup via the API and confirm the archive/upload/retention behavior) and describe how you tested in your PR.

## Commit messages and pull requests

This repo uses [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`, etc.). Pull requests are squash-merged, and the **PR title** becomes the commit on `main` — so PR titles must follow this format. This is enforced automatically by the "Conventional Commits" check.

Direct pushes to `main` are allowed but must also use a Conventional Commits-formatted commit message (validated by the same check).

## Opening a pull request

1. Fork the repo and create a branch off `main`.
2. Make your changes.
3. Open a pull request with a Conventional Commits-formatted title.
4. Wait for CI to pass — required checks must be green before merge.

## Reporting issues

Use [GitHub Issues](../../issues) for bugs and feature requests.
