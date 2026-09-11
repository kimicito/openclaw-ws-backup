#!/bin/bash
# speak.sh — Generate TTS and send as voice message (multi-platform)
# Usage: bash speak.sh "text" [platform] [target_id]
#
# Platforms: feishu (default), telegram, discord, whatsapp
# If platform is omitted, uses PLATFORM from config.env (default: feishu)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

TEXT="$1"
PLAT="${2:-${PLATFORM:-feishu}}"
TARGET="$3"

if [ -z "$TEXT" ]; then
  echo "Usage: bash speak.sh \"text\" [platform] [target_id]"
  echo ""
  echo "Platforms: feishu, telegram, discord, whatsapp"
  echo "Default platform: \${PLATFORM:-feishu}"
  exit 1
fi

TMP_MP3="/tmp/soulsaying_speak_$(date +%s).mp3"

# 1. Generate TTS
bash "${SCRIPT_DIR}/tts.sh" "$TEXT" "$TMP_MP3"

# 2. Send to platform
case "$PLAT" in
  feishu|lark)
    bash "${SCRIPT_DIR}/send_feishu_voice.sh" "$TMP_MP3" "$TARGET"
    ;;
  telegram|tg)
    bash "${SCRIPT_DIR}/send_telegram_voice.sh" "$TMP_MP3" "$TARGET"
    ;;
  discord)
    bash "${SCRIPT_DIR}/send_discord_voice.sh" "$TMP_MP3" "$TARGET"
    ;;
  whatsapp|wa)
    bash "${SCRIPT_DIR}/send_whatsapp_voice.sh" "$TMP_MP3" "$TARGET"
    ;;
  local)
    # Just play locally, don't send anywhere
    if command -v afplay &>/dev/null; then
      afplay "$TMP_MP3"
    elif command -v aplay &>/dev/null; then
      aplay "$TMP_MP3"
    else
      echo "Audio saved to: $TMP_MP3"
      exit 0
    fi
    ;;
  *)
    echo "❌ Unknown platform: $PLAT"
    echo "   Supported: feishu, telegram, discord, whatsapp, local"
    rm -f "$TMP_MP3"
    exit 1
    ;;
esac

# 3. Cleanup
rm -f "$TMP_MP3"
