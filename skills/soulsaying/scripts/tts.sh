#!/bin/bash
# tts.sh — Generate speech audio using SiliconFlow TTS with cloned or preset voice
# Usage: bash tts.sh "text to speak" [output.mp3]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load config
if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

TEXT="$1"
OUTPUT="${2:-/tmp/soulsaying_tts_$(date +%s).mp3}"

if [ -z "$TEXT" ]; then
  echo "Usage: bash tts.sh \"text to speak\" [output.mp3]"
  exit 1
fi

if [ -z "$SILICONFLOW_API_KEY" ]; then
  echo "❌ SILICONFLOW_API_KEY not set. Configure it in config.env"
  exit 1
fi

if [ -z "$VOICE_URI" ]; then
  echo "❌ VOICE_URI not set. Run clone_voice.sh first or set a preset voice in config.env"
  exit 1
fi

MODEL="${TTS_MODEL:-IndexTeam/IndexTTS-2}"

# Build JSON body safely via Python
JSON_BODY=$(python3 -c "
import json, sys
print(json.dumps({
    'model': sys.argv[1],
    'input': sys.argv[2],
    'voice': sys.argv[3],
    'response_format': 'mp3'
}))
" "$MODEL" "$TEXT" "$VOICE_URI")

curl -s -X POST "https://api.siliconflow.cn/v1/audio/speech" \
  -H "Authorization: Bearer ${SILICONFLOW_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "${JSON_BODY}" \
  -o "${OUTPUT}"

# Validate output is audio
if file "${OUTPUT}" | grep -q "Audio\|MPEG\|ID3"; then
  SIZE=$(du -h "${OUTPUT}" | cut -f1)
  echo "✅ TTS generated: ${OUTPUT} (${SIZE})"
else
  echo "❌ TTS failed:"
  cat "${OUTPUT}"
  rm -f "${OUTPUT}"
  exit 1
fi
