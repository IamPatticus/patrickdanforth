#!/bin/bash
# Solar Scoreboard → GitHub Pages refresh script
# Triggered by cron to push latest solar-snapshot.json to GitHub Pages

set -e

REPO_DIR="/home/patrick/.openclaw/workspace"
SCRIPT_NAME="$(basename "$0")"
LOGFILE="/tmp/solar_github_refresh.log"

exec >>"$LOGFILE" 2>&1

echo "=========================================="
echo "[$SCRIPT_NAME] Started: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
echo "Local time: $(date +'%Y-%m-%d %H:%M:%S %Z')"

# Check if solar-snapshot.json exists and is recent
if [ ! -f "$REPO_DIR/solar-snapshot.json" ]; then
    echo "ERROR: solar-snapshot.json not found"
    exit 1
fi

AGE_MINUTES=$(( ($(date +%s) - $(stat -c %Y "$REPO_DIR/solar-snapshot.json")) / 60 ))
echo "Snapshot age: ${AGE_MINUTES} minutes"

cd "$REPO_DIR"

# Check git status
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Not a git repository"
    exit 1
fi

# Stage and commit if changed
if git diff --quiet solar-snapshot.json solar-scoreboard.html; then
    echo "No changes to commit"
    exit 0
fi

git add solar-snapshot.json solar-scoreboard.html
git commit -m "Update solar scoreboard: $(date -u +'%Y-%m-%d %H:%M UTC')" || true

# Push to origin
echo "Pushing to origin..."
git push origin main || {
    echo "ERROR: Push failed"
    exit 1
}

echo "[$SCRIPT_NAME] Completed successfully: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
echo "=========================================="
