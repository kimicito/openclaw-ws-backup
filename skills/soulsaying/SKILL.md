---
name: skill-soulsaying
description: "Give your OpenClaw bot a cloned voice — text-to-speech via SiliconFlow (IndexTTS-2 / CosyVoice2) with voice cloning from a short audio sample. Multi-platform: Feishu, Telegram, Discord, WhatsApp. Supports switchable voice/text modes. Use when: user wants voice replies, TTS, voice cloning, audio messages, or asks to give the bot a voice, enable voice mode, clone a voice, 语音模式, 声音克隆, 让机器人说话."
---

# SoulSaying — Voice for Your OpenClaw Bot

Clone any voice from a short audio sample and let your bot speak with it.

## Supported Platforms

| Platform | Script | Audio Format |
|----------|--------|-------------|
| Feishu / Lark | send_feishu_voice.sh | opus |
| Telegram | send_telegram_voice.sh | ogg/opus |
| Discord | send_discord_voice.sh | mp3 |
| WhatsApp | send_whatsapp_voice.sh | ogg/opus |
| Local playback | speak.sh "text" local | mp3 |

## Architecture

```
User message → Bot generates text reply → SiliconFlow TTS (cloned voice) → mp3
  → ffmpeg converts format → Upload to platform → Send audio message
```

## Prerequisites

1. **SiliconFlow API Key** — free tier available at https://siliconflow.cn
2. **ffmpeg** — install via `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)
3. **A messaging bot** — Feishu, Telegram, Discord, or WhatsApp (at least one)
4. **A voice sample** — 10–30s clear speech, mp3/wav, no background music

### Getting a Voice Sample

Extract audio from any video using https://www.abcdtools.com/video-to-audio

**Tips for best results:**
- 10–30 seconds of clear speech (single speaker)
- No background music, sound effects, or other voices
- Consistent volume, natural pace
- mp3 or wav format

## Setup (Step by Step)

### 1. Configure Environment

Create a config file at `{workspace}/skills/skill-soulsaying/config.env`:

```bash
# Required
SILICONFLOW_API_KEY="sk-your-key-here"

# Feishu bot credentials
FEISHU_APP_ID="cli_xxxx"
FEISHU_APP_SECRET="your-app-secret"

# Target user's open_id (who receives voice messages)
FEISHU_OPEN_ID="ou_xxxx"

# Voice URI (filled after cloning in step 2)
VOICE_URI=""

# TTS model (IndexTTS-2 recommended for cloned voices)
TTS_MODEL="IndexTeam/IndexTTS-2"
```

### 2. Clone a Voice

Place the voice sample mp3 in the workspace, then run:

```bash
bash scripts/clone_voice.sh path/to/sample.mp3 my-voice-name
```

This uploads the sample to SiliconFlow and returns a voice URI. Copy the URI into `config.env` as `VOICE_URI`.

### 3. Test Voice Generation

```bash
bash scripts/tts.sh "你好，这是语音测试" /tmp/test_voice.mp3
```

Verify the output sounds correct by playing locally (`afplay` on macOS, `aplay` on Linux).

### 4. Test Feishu Delivery

```bash
bash scripts/send_feishu_voice.sh /tmp/test_voice.mp3
```

Check Feishu — you should receive an audio message from the bot.

### 5. End-to-End Test

```bash
bash scripts/speak.sh "你好呀，语音模式已经开启了"
```

This generates TTS and sends to your configured platform. Specify platform explicitly:

```bash
bash scripts/speak.sh "Hello" feishu
bash scripts/speak.sh "Hello" telegram
bash scripts/speak.sh "Hello" discord
bash scripts/speak.sh "Hello" whatsapp
bash scripts/speak.sh "Hello" local    # just play on speakers
```

## Mode Switching

Add these instructions to the bot's `SOUL.md` to enable user-controlled mode switching:

```markdown
## Voice Mode 🎤

Support two reply modes: **text mode** (default) and **voice mode**.

### Switching
- User says "语音模式" / "开启语音" / "voice on" → switch to voice mode
- User says "文字模式" / "关闭语音" / "voice off" → switch to text mode

### Voice Mode Behavior
After sending the text reply, run:
\`\`\`bash
bash {workspace}/skills/skill-soulsaying/scripts/speak.sh "reply text"
\`\`\`
Keep voice text under 200 characters per call. For longer replies, only voice the key emotional parts.
```

## Troubleshooting

- **500 error on TTS**: Voice sample may be too long (over 30s) or corrupted. Re-clone with a shorter clip.
- **ffmpeg not found**: Install it — `brew install ffmpeg` or `apt install ffmpeg`.
- **Feishu upload fails**: Check bot has `im:message:create` and `im:file` permissions in Feishu developer console.
- **Voice sounds robotic**: Use a cleaner sample with no echo or background noise.
- **CosyVoice2 vs IndexTTS-2**: CosyVoice2 may return 500 for cloned voices. IndexTTS-2 is more stable for voice cloning; CosyVoice2 works well with built-in voices (alex/bella/claire/anna).

## Built-in Voices (No Cloning Needed)

If you don't need voice cloning, use SiliconFlow's preset voices:

| Voice | Style | Model |
|-------|-------|-------|
| bella | Warm female | CosyVoice2 |
| claire | Clear female | CosyVoice2 |
| anna | Sweet female | CosyVoice2 |
| alex | Neutral | CosyVoice2 |

Set `VOICE_URI` to e.g. `FunAudioLLM/CosyVoice2-0.5B:bella` and `TTS_MODEL` to `FunAudioLLM/CosyVoice2-0.5B`.

## API Reference

See [references/api-notes.md](references/api-notes.md) for SiliconFlow TTS & Feishu audio API details.
