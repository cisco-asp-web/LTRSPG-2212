#!/bin/bash

cd /home/cisco/LTRSPG-2212

# Ensure correct branch
git checkout main

# Discard local changes and untracked files
git reset --hard HEAD
git clean -fd

# Pull latest commits from GitHub
git pull origin main