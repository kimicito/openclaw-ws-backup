#!/bin/bash
# delete_voice.sh — Delete a cloned voice from SiliconFlow
# Usage: bash delete_voice.sh <voice-uri>

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

VOICE_TO_DELETE="$1"

if [ -z "$VOICE_TO_DELETE" ]; then
  echo "Usage: bash delete_voice.sh <voice-uri>"
  echo ""
  echo "Run list_voices.sh to see available voice URIs."
  exit 1
fi

if [ -z "$SILICONFLOW_API_KEY" ]; then
  echo "❌ SILICONFLOW_API_KEY not set"
  exit 1
fi

echo "🗑️  Deleting voice: $VOICE_TO_DELETE"

RESPONSE=$(curl -s -X POST "https://api.siliconflow.cn/v1/uploads/audio/voice/deletions" \
  -H "Authorization: Bearer ${SILICONFLOW_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"${VOICE_TO_DELETE}\"}")

if echo "$RESPONSE" | python3 -c "import json,sys; sys.exit(0 if json.load(sys.stdin).get('message','')=='success' else 1)" 2>/dev/null; then
  echo "✅ Voice deleted successfully"
else
  echo "Result: $RESPONSE"
fi
