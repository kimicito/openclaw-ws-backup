#!/bin/bash
# send_feishu_voice.sh — Upload audio to Feishu and send as voice message
# Usage: bash send_feishu_voice.sh <audio-file> [open_id] [chat_id]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load config
if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

AUDIO_FILE="$1"
OPEN_ID="${2:-$FEISHU_OPEN_ID}"
CHAT_ID="$3"

if [ -z "$AUDIO_FILE" ]; then
  echo "Usage: bash send_feishu_voice.sh <audio-file> [open_id] [chat_id]"
  exit 1
fi

if [ -z "$FEISHU_APP_ID" ] || [ -z "$FEISHU_APP_SECRET" ]; then
  echo "❌ FEISHU_APP_ID and FEISHU_APP_SECRET required. Configure in config.env"
  exit 1
fi

if [ -z "$OPEN_ID" ] && [ -z "$CHAT_ID" ]; then
  echo "❌ Need either FEISHU_OPEN_ID in config.env or pass open_id/chat_id as argument"
  exit 1
fi

# Check ffmpeg
if ! command -v ffmpeg &>/dev/null; then
  echo "❌ ffmpeg not found. Install: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
  exit 1
fi

# 1. Get tenant_access_token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"${FEISHU_APP_ID}\",\"app_secret\":\"${FEISHU_APP_SECRET}\"}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tenant_access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get Feishu access token. Check app credentials."
  exit 1
fi

# 2. Convert to opus
OPUS_FILE="/tmp/soulsaying_$(date +%s).opus"
ffmpeg -y -i "${AUDIO_FILE}" -c:a libopus -b:a 32k "${OPUS_FILE}" 2>/dev/null

# 3. Get duration in milliseconds
DURATION_MS=$(python3 -c "
import subprocess, json
r = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration',
    '-of','json','$AUDIO_FILE'], capture_output=True, text=True)
d = json.loads(r.stdout)
print(int(float(d['format']['duration']) * 1000))
" 2>/dev/null)

# 4. Upload to Feishu
UPLOAD_RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file_type=opus" \
  -F "file_name=voice.opus" \
  -F "file=@${OPUS_FILE}" \
  -F "duration=${DURATION_MS}")

FILE_KEY=$(echo "$UPLOAD_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('file_key',''))" 2>/dev/null)

if [ -z "$FILE_KEY" ]; then
  echo "❌ Failed to upload audio to Feishu:"
  echo "$UPLOAD_RESP"
  rm -f "$OPUS_FILE"
  exit 1
fi

# 5. Send audio message
if [ -n "$CHAT_ID" ]; then
  SEND_RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"receive_id\":\"${CHAT_ID}\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"${FILE_KEY}\\\"}\"}")
else
  SEND_RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"receive_id\":\"${OPEN_ID}\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"${FILE_KEY}\\\"}\"}")
fi

CODE=$(echo "$SEND_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('code',-1))" 2>/dev/null)

rm -f "$OPUS_FILE"

if [ "$CODE" = "0" ]; then
  echo "✅ Voice message sent (${DURATION_MS}ms)"
else
  echo "❌ Failed to send voice message:"
  echo "$SEND_RESP"
  exit 1
fi
