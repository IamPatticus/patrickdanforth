#!/bin/bash
# Sync Reginald daily comic to flipbook archive and regenerate index.json

set -e

ARCHIVE_DIR="$HOME/.cache/reginald-daily/archive"
FLIPBOOK_DIR="/home/patrick/.openclaw/workspace/services/reginald-flipbook/images"
FLIPBOOK_ROOT="/home/patrick/.openclaw/workspace/services/reginald-flipbook"

mkdir -p "$FLIPBOOK_DIR"

# Get today's date
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Copy today's image if it exists
if [ -f "$ARCHIVE_DIR/reginald-$TODAY.png" ]; then
    cp "$ARCHIVE_DIR/reginald-$TODAY.png" "$FLIPBOOK_DIR/reginald-$TODAY.png"
    echo "Synced reginald-$TODAY.png to flipbook"
fi

# Also copy yesterday's in case it was missed
if [ -f "$ARCHIVE_DIR/reginald-$YESTERDAY.png" ]; then
    cp "$ARCHIVE_DIR/reginald-$YESTERDAY.png" "$FLIPBOOK_DIR/reginald-$YESTERDAY.png"
    echo "Synced reginald-$YESTERDAY.png to flipbook"
fi

# Copy all archive images (ensure everything is present)
cp -n "$ARCHIVE_DIR"/reginald-*.png "$FLIPBOOK_DIR/" 2>/dev/null || true

# Get all dates in the flipbook, sort them (oldest first for JSON)
cd "$FLIPBOOK_DIR"
DATES=$(ls -1 reginald-*.png 2>/dev/null | sed 's/reginald-//;s/.png//' | sort)

if [ -z "$DATES" ]; then
    echo "No images found in flipbook directory"
    exit 1
fi

# Generate index.json
JSON_ENTRIES=""
COUNT=0
for date in $DATES; do
    COUNT=$((COUNT + 1))
    if [ -n "$JSON_ENTRIES" ]; then
        JSON_ENTRIES="${JSON_ENTRIES},"
    fi
    JSON_ENTRIES="${JSON_ENTRIES}
    {\n      \"date\": \"${date}\",\n      \"filename\": \"reginald-${date}.png\",\n      \"label\": \"Reginald — ${date}\"\n    }"
done

cat > "$FLIPBOOK_ROOT/index.json" << EOF
{
  "count": ${COUNT},
  "entries": [${JSON_ENTRIES}
  ]
}
EOF

TOTAL=$(echo "$DATES" | wc -l)
echo "Flipbook index.json updated. Total images: $TOTAL"
echo "Latest: $(echo "$DATES" | tail -1)"
