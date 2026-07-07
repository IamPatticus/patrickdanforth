#!/usr/bin/env bash
# OpenClaw Heartbeat Runner
# Performs batched checks and updates heartbeat.md

HB_FILE="/home/patrick/.openclaw/workspace/heartbeat.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RUN_ID=$(date -u +"%Y%m%d%H%M%S")

# Environment check
ENV_STATUS="ok"
ENV_DETAILS="OPENCLAW_SERVICE_KIND=${OPENCLAW_SERVICE_KIND}, version=${OPENCLAW_SERVICE_VERSION}"

# Storage check
STORAGE_INFO=$(df -h / | awk 'NR==2 {print $3" used, "$4" avail, "$5" usage"}')
STORAGE_STATUS="ok"
if echo "$STORAGE_INFO" | grep -q '7[0-9]%'; then STORAGE_STATUS="warn"; fi

# Entropy check (simple)
ENTROPY_STATUS="ok"
if [[ -f /proc/sys/kernel/random/entropy_avail ]]; then
    ENTROPY=$(cat /proc/sys/kernel/random/entropy_avail)
    if [[ $ENTROPY -lt 100 ]]; then ENTROPY_STATUS="warn"; fi
else
    ENTROPY_STATUS="warn"
    ENTROPY_INFO="unavailable"
fi

# Skills check (browser-automation, notion)
check_skill() {
    local SKILL=$1
    if find /home/patrick/.openclaw/plugin-skills /home/patrick/.npm-global/lib/node_modules/openclaw/skills -iname "${SKILL}" -type d | grep -q .; then
        echo "ok"
    else
        echo "warn"
    fi
}
SKILL_BROWSER=$(check_skill "browser-automation")
SKILL_NOTION=$(check_skill "notion")

# Build JSON summary
SUMMARY="All checks passed."
if [[ "$STORAGE_STATUS" == "warn" ]]; then SUMMARY="Storage usage elevated."; fi
if [[ "$ENTROPY_STATUS" == "warn" ]]; then SUMMARY="Low entropy."; fi
if [[ "$SKILL_BROWSER" != "ok" || "$SKILL_NOTION" != "ok" ]]; then SUMMARY="Some skills unavailable."; fi

# Update heartbeat.md (simple append or replace)
python3 -c "
import json, sys, datetime
hb_file = '$HB_FILE'
try:
    with open(hb_file) as f:
        lines = f.read()
    # Replace last Checks block (naive: find last ```json and replace until next ```)
    import re
    pattern = r'(\`\`\`json\n)(.*?)(\n\`\`\`)'
    last = re.search(pattern, lines, re.DOTALL)
    new_block = '''\1$(cat <<'EOS'
{
  \"runId\": \"$RUN_ID\",
  \"timestamp\": \"$TIMESTAMP\",
  \"hostname\": \"$(hostname)\",
  \"checks\": {
    \"env\": { \"status\": \"$ENV_STATUS\", \"details\": \"$ENV_DETAILS\" },
    \"storage\": { \"status\": \"$STORAGE_STATUS\", \"details\": \"$STORAGE_INFO\" },
    \"entropy\": { \"status\": \"$ENTROPY_STATUS\", \"details\": \"$(if [[ -z \\\"\$ENTROPY_INFO\\\"]]; then echo \\\"available: $ENTROPY\\\"; else echo \\\"\\\"; fi)\" },
    \"skills\": {
      \"browser-automation\": { \"status\": \"$SKILL_BROWSER\", \"details\": \"skill directory present\" },
      \"notion\": { \"status\": \"$SKILL_NOTION\", \"details\": \"skill directory present\" }
    }
  }
}
EOS
)\3'''
    # fallback if python regex fails
except Exception as e:
    sys.stderr.write(str(e))
" 2>/dev/null || true

# Fallback: append a new run block if not present
grep -q "$RUN_ID" "$HB_FILE" 2>/dev/null || cat >> "$HB_FILE" <<HEREDOC

## Run $RUN_ID
- timestamp: $TIMESTAMP
- env: $ENV_STATUS
- storage: $STORAGE_STATUS
- entropy: $ENTROPY_STATUS
- skills: browser=$SKILL_BROWSER, notion=$SKILL_NOTION
HEREDOC

echo "Heartbeat updated at $HB_FILE"