#!/bin/bash
# send_telegram_voice.sh — Send audio as Telegram voice message
# Usage: bash send_telegram_voice.sh <audio-file> [chat_id]
# Requires: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.env

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

AUDIO_FILE="$1"
CHAT_ID="${2:-$TELEGRAM_CHAT_ID}"

if [ -z "$AUDIO_FILE" ]; then
  echo "Usage: bash send_telegram_voice.sh <audio-file> [chat_id]"
  exit 1
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "❌ TELEGRAM_BOT_TOKEN not set. Configure in config.env"
  exit 1
fi

if [ -z "$CHAT_ID" ]; then
  echo "❌ TELEGRAM_CHAT_ID not set. Configure in config.env or pass as argument"
  exit 1
fi

# Check ffmpeg
if ! command -v ffmpeg &>/dev/null; then
  echo "❌ ffmpeg not found. Install: brew install ffmpeg / apt install ffmpeg"
  exit 1
fi

# Telegram voice messages require ogg/opus
OGG_FILE="/tmp/soulsaying_tg_$(date +%s).ogg"
ffmpeg -y -i "${AUDIO_FILE}" -c:a libopus -b:a 48k "${OGG_FILE}" 2>/dev/null

# Send via Telegram Bot API
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendVoice" \
  -F "chat_id=${CHAT_ID}" \
  -F "voice=@${OGG_FILE}")

OK=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ok',False))" 2>/dev/null)

rm -f "$OGG_FILE"

if [ "$OK" = "True" ]; then
  echo "✅ Telegram voice message sent"
else
  echo "❌ Failed to send Telegram voice:"
  echo "$RESPONSE"
  exit 1
fi
