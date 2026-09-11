#!/bin/bash
# clone_voice.sh — Upload a voice sample to SiliconFlow for voice cloning
# Usage: bash clone_voice.sh <audio-file> <voice-name>
# Output: prints the voice URI to use in TTS calls

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load config
if [ -f "$SKILL_DIR/config.env" ]; then
  source "$SKILL_DIR/config.env"
fi

AUDIO_FILE="$1"
VOICE_NAME="${2:-my_cloned_voice}"

if [ -z "$AUDIO_FILE" ]; then
  echo "Usage: bash clone_voice.sh <audio-file> <voice-name>"
  echo ""
  echo "  audio-file  Path to mp3/wav file (10-30s clear speech recommended)"
  echo "  voice-name  Name for the cloned voice (default: my_cloned_voice)"
  echo ""
  echo "Tips for best results:"
  echo "  - Extract audio from video: https://www.abcdtools.com/video-to-audio"
  echo "  - 10-30 seconds of clear speech, single speaker"
  echo "  - No background music or sound effects"
  exit 1
fi

if [ -z "$SILICONFLOW_API_KEY" ]; then
  echo "❌ SILICONFLOW_API_KEY not set. Configure it in config.env"
  exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
  echo "❌ File not found: $AUDIO_FILE"
  exit 1
fi

# Check file size (warn if > 2MB)
FILE_SIZE=$(wc -c < "$AUDIO_FILE" | tr -d ' ')
if [ "$FILE_SIZE" -gt 2097152 ]; then
  echo "⚠️  File is $(($FILE_SIZE / 1024))KB — large files may cause errors."
  echo "   Recommend trimming to 10-30s (< 1MB)."
fi

echo "📤 Uploading voice sample: $AUDIO_FILE"
echo "   Voice name: $VOICE_NAME"

RESPONSE=$(curl -s -X POST "https://api.siliconflow.cn/v1/uploads/audio/voice" \
  -H "Authorization: Bearer ${SILICONFLOW_API_KEY}" \
  -F "file=@${AUDIO_FILE}" \
  -F "model=FunAudioLLM/CosyVoice2-0.5B" \
  -F "customName=${VOICE_NAME}")

# Extract URI
VOICE_URI=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('uri',''))" 2>/dev/null)

if [ -z "$VOICE_URI" ]; then
  echo "❌ Voice cloning failed:"
  echo "$RESPONSE"
  exit 1
fi

echo ""
echo "✅ Voice cloned successfully!"
echo ""
echo "Voice URI: $VOICE_URI"
echo ""
echo "Add this to your config.env:"
echo "  VOICE_URI=\"$VOICE_URI\""
