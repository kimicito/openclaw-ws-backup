#!/bin/bash
# send_whatsapp_voice.sh — Send audio as WhatsApp voice message
# Usage: bash send_whatsapp_voice.sh <audio-file> [phone_number]
# Requires: WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, WHATSAPP_TO in config.env
# Uses Meta's WhatsApp Business Cloud API

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

AUDIO_FILE="$1"
TO_NUMBER="${2:-$WHATSAPP_TO}"

if [ -z "$AUDIO_FILE" ]; then
  echo "Usage: bash send_whatsapp_voice.sh <audio-file> [phone_number]"
  exit 1
fi

if [ -z "$WHATSAPP_TOKEN" ] || [ -z "$WHATSAPP_PHONE_ID" ]; then
  echo "❌ WHATSAPP_TOKEN and WHATSAPP_PHONE_ID required. Configure in config.env"
  exit 1
fi

if [ -z "$TO_NUMBER" ]; then
  echo "❌ WHATSAPP_TO not set. Configure in config.env or pass phone number as argument"
  exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
  echo "❌ ffmpeg not found"
  exit 1
fi

# WhatsApp requires ogg/opus
OGG_FILE="/tmp/soulsaying_wa_$(date +%s).ogg"
ffmpeg -y -i "${AUDIO_FILE}" -c:a libopus -b:a 48k "${OGG_FILE}" 2>/dev/null

# 1. Upload media
UPLOAD_RESP=$(curl -s -X POST "https://graph.facebook.com/v19.0/${WHATSAPP_PHONE_ID}/media" \
  -H "Authorization: Bearer ${WHATSAPP_TOKEN}" \
  -F "messaging_product=whatsapp" \
  -F "type=audio/ogg" \
  -F "file=@${OGG_FILE}")

MEDIA_ID=$(echo "$UPLOAD_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

rm -f "$OGG_FILE"

if [ -z "$MEDIA_ID" ]; then
  echo "❌ Failed to upload audio to WhatsApp:"
  echo "$UPLOAD_RESP"
  exit 1
fi

# 2. Send audio message
SEND_RESP=$(curl -s -X POST "https://graph.facebook.com/v19.0/${WHATSAPP_PHONE_ID}/messages" \
  -H "Authorization: Bearer ${WHATSAPP_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"messaging_product\": \"whatsapp\",
    \"to\": \"${TO_NUMBER}\",
    \"type\": \"audio\",
    \"audio\": {\"id\": \"${MEDIA_ID}\"}
  }")

MSG_STATUS=$(echo "$SEND_RESP" | python3 -c "
import json,sys
r = json.load(sys.stdin)
msgs = r.get('messages',[])
print(msgs[0].get('id','') if msgs else '')
" 2>/dev/null)

if [ -n "$MSG_STATUS" ]; then
  echo "✅ WhatsApp voice message sent"
else
  echo "❌ Failed to send WhatsApp voice:"
  echo "$SEND_RESP"
  exit 1
fi
