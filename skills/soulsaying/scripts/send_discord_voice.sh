#!/bin/bash
# send_discord_voice.sh — Send audio as Discord voice message attachment
# Usage: bash send_discord_voice.sh <audio-file> [channel_id]
# Requires: DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID in config.env
# Note: Discord doesn't have native voice messages via bot API,
#       so this sends the audio as a file attachment that plays inline.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

AUDIO_FILE="$1"
CHANNEL_ID="${2:-$DISCORD_CHANNEL_ID}"

if [ -z "$AUDIO_FILE" ]; then
  echo "Usage: bash send_discord_voice.sh <audio-file> [channel_id]"
  exit 1
fi

if [ -z "$DISCORD_BOT_TOKEN" ]; then
  echo "❌ DISCORD_BOT_TOKEN not set. Configure in config.env"
  exit 1
fi

if [ -z "$CHANNEL_ID" ]; then
  echo "❌ DISCORD_CHANNEL_ID not set. Configure in config.env or pass as argument"
  exit 1
fi

# Discord plays mp3 inline, no conversion needed
RESPONSE=$(curl -s -X POST "https://discord.com/api/v10/channels/${CHANNEL_ID}/messages" \
  -H "Authorization: Bot ${DISCORD_BOT_TOKEN}" \
  -F "files[0]=@${AUDIO_FILE};filename=voice.mp3" \
  -F "payload_json={\"content\":\"\",\"flags\":8192}")

MSG_ID=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

if [ -n "$MSG_ID" ]; then
  echo "✅ Discord audio sent (message: ${MSG_ID})"
else
  echo "❌ Failed to send Discord audio:"
  echo "$RESPONSE"
  exit 1
fi
