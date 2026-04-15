#!/bin/bash
set -euo pipefail

LATEST_TAG=$gh release list --limit 1 --json tagName --jq '.[0].tagName' 2>/dev/null || echo "")

if [ -z "$LATEST_TAG" ]; then
    echo "has_changes=true" >> $GITHUB_OUTPUT
    exit 0
fi

LAST_RELEASE_SHA=$(git rev-parse "$LATEST_TAG^{commit}" 2>/dev/null || echo "")
CURRENT_SHA=$(git rev-parse HEAD)

if [ "$LAST_RELEASE_SHA" = "$CURRENT_SHA" ]; then
    echo "has_changes=false" >> $GITHUB_OUTPUT
else
    echo "has_changes=true" >> $GITHUB_OUTPUT
fi
