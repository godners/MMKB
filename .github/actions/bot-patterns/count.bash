#!/bin/bash

echo "[BASH] Bot Patterns (Count)"
echo ".github/actions/bot-patterns/Count.bash"

COUNT_PATTERNS=$(echo "${PATTERNS}" | sed '/^$/d' | wc -l)
echo "COUNT_PATTERNS=${COUNT_PATTERNS}" >> $GITHUB_OUTPUT
if [ -z "$PATHS" ]
then
    echo "COUNT_FILES=0" >> $GITHUB_OUTPUT
else
    COUNT_FILES=$(echo "PATHS" | awk -F \'${SEPARATOR}\' '{print NF}')
    echo "COUNT_FILES=${COUNT_FILES}" >> $GITHUB_OUTPUT
fi
