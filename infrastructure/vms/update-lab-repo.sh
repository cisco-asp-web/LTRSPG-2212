#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/cisco/LTRSPG-2212"
BRANCH="main"

cd "$REPO_DIR"

# Ensure correct branch
git checkout "$BRANCH"

# Discard local changes and untracked files (LAB MODE - destructive)
git reset --hard HEAD
git clean -fd

# Pull latest commits
git pull origin "$BRANCH"