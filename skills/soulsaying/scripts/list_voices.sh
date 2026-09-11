#!/bin/bash
# list_voices.sh — List your cloned voices on SiliconFlow
# Usage: bash list_voices.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

if [ -z "$SILICONFLOW_API_KEY" ]; then
  echo "❌ SILICONFLOW_API_KEY not set"
  exit 1
fi

RESPONSE=$(curl -s -X GET "https://api.siliconflow.cn/v1/audio/voice/list" \
  -H "Authorization: Bearer ${SILICONFLOW_API_KEY}")

echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
voices = data.get('result', [])
if not voices:
    print('No cloned voices found.')
    print('Run clone_voice.sh to create one.')
else:
    print(f'Found {len(voices)} cloned voice(s):')
    print()
    for v in voices:
        print(f'  Name: {v.get(\"customName\", \"unnamed\")}')
        print(f'  URI:  {v.get(\"uri\", \"\")}')
        print(f'  Model: {v.get(\"model\", \"\")}')
        print()
"
