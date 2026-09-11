# 🦐 SoulSaying — Give Your AI Bot a Voice

**Clone any voice and let your bot speak with it.**

SoulSaying is an [OpenClaw](https://github.com/openclaw/openclaw) skill that adds voice messaging to your bot using SiliconFlow's TTS engine with voice cloning support. Works with **Feishu, Telegram, Discord, and WhatsApp**.

[中文](#中文说明) | [English](#features)

---

## ✨ Features

- 🎤 **Voice Cloning** — Upload a 10-30s audio sample, get a cloned voice
- 🗣️ **Text-to-Speech** — Convert any text to natural speech
- 💬 **Multi-Platform** — Feishu, Telegram, Discord, WhatsApp
- 🔀 **Mode Switching** — Users can toggle between text and voice modes
- 🆓 **Free Tier Available** — SiliconFlow offers free API credits
- 🇨🇳 **China-friendly** — No VPN needed, all APIs are domestic

## 🏗️ Architecture

```
User message → Bot generates text → SiliconFlow TTS (cloned voice) → mp3
  → ffmpeg → platform format → Upload → Send as voice message

Supported: Feishu · Telegram · Discord · WhatsApp · Local playback
```

## 📦 Quick Start

### 1. Install the Skill

Copy the `skill-soulsaying` folder into your OpenClaw workspace:

```bash
cp -r skill-soulsaying /path/to/your/openclaw-workspace/skills/
```

### 2. Configure

```bash
cp skills/skill-soulsaying/config.env.example skills/skill-soulsaying/config.env
# Edit config.env with your API keys
```

### 3. Get a Voice Sample

Extract audio from any video using [abcdtools](https://www.abcdtools.com/video-to-audio):
- **Duration**: 10-30 seconds
- **Quality**: Clear speech, single speaker, no background music
- **Format**: mp3 or wav

### 4. Clone the Voice

```bash
bash skills/skill-soulsaying/scripts/clone_voice.sh sample.mp3 my-voice
# Copy the returned voice URI into config.env
```

### 5. Test It

```bash
# Generate speech
bash skills/skill-soulsaying/scripts/tts.sh "Hello world" /tmp/test.mp3

# Send to Feishu
bash skills/skill-soulsaying/scripts/speak.sh "你好，语音模式已开启"

# Or Telegram / Discord / WhatsApp
bash skills/skill-soulsaying/scripts/speak.sh "Hello" telegram
bash skills/skill-soulsaying/scripts/speak.sh "Hello" discord
bash skills/skill-soulsaying/scripts/speak.sh "Hello" whatsapp
```

## 🔧 Prerequisites

| Requirement | How to Get |
|------------|------------|
| SiliconFlow API Key | Free at [siliconflow.cn](https://siliconflow.cn) |
| ffmpeg | `brew install ffmpeg` (macOS) / `apt install ffmpeg` (Linux) |
| A bot (at least one) | [Feishu](https://open.feishu.cn/app) · [Telegram](https://t.me/BotFather) · [Discord](https://discord.com/developers) · [WhatsApp](https://developers.facebook.com) |
| OpenClaw | [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw) |

## 📂 Skill Structure

```
skill-soulsaying/
├── SKILL.md                        # Skill definition (OpenClaw reads this)
├── config.env.example              # Configuration template
├── scripts/
│   ├── clone_voice.sh              # Upload sample → get voice URI
│   ├── tts.sh                      # Text → speech audio
│   ├── send_feishu_voice.sh        # Audio → Feishu voice message
│   ├── send_telegram_voice.sh      # Audio → Telegram voice message
│   ├── send_discord_voice.sh       # Audio → Discord audio attachment
│   ├── send_whatsapp_voice.sh      # Audio → WhatsApp voice message
│   ├── speak.sh                    # One-step: text → platform voice
│   ├── list_voices.sh              # List your cloned voices
│   └── delete_voice.sh             # Remove a cloned voice
└── references/
    └── api-notes.md                # SiliconFlow & Feishu API reference
```

## 🎭 Mode Switching

Add voice mode instructions to your bot's `SOUL.md`:

- User says **"语音模式"** / **"voice on"** → bot replies with text + voice
- User says **"文字模式"** / **"voice off"** → bot replies with text only

See SKILL.md for the exact instructions to paste.

## 🎵 Built-in Voices (No Cloning Needed)

Don't have a voice sample? Use SiliconFlow's preset voices:

| Voice | Style |
|-------|-------|
| bella | Warm female |
| claire | Clear female |
| anna | Sweet female |
| alex | Neutral |

Set `VOICE_URI="FunAudioLLM/CosyVoice2-0.5B:bella"` in config.env.

## 🤝 Contributing

PRs welcome! Ideas for improvement:
- Support for more TTS providers (Edge TTS, Bark, etc.)
- Support for more messaging platforms (Signal, Slack, Line, etc.)
- Streaming voice for long text
- Voice effect presets (speed, pitch)

## 📄 License

MIT

---

## 中文说明

### 🦐 SoulSaying — 让你的AI机器人开口说话

**克隆任何声音，让飞书机器人用它说话。**

SoulSaying 是一个 [OpenClaw](https://github.com/openclaw/openclaw) 技能，通过硅基流动的TTS引擎和声音克隆功能，让你的飞书机器人拥有语音回复能力。

### 核心功能
- 🎤 声音克隆 — 上传10-30秒音频，克隆任何声音
- 🗣️ 文字转语音 — 自然流畅的中文语音
- 💬 飞书/Telegram/Discord/WhatsApp 多平台集成
- 🔀 模式切换 — 用户可在文字和语音模式间切换
- 🆓 免费可用 — 硅基流动提供免费额度
- 🇨🇳 国内服务 — 无需VPN，全部国内API

### 获取声音素材
使用 [abcdtools](https://www.abcdtools.com/video-to-audio) 从视频中提取音频：
- 10-30秒清晰人声
- 无背景音乐
- 单人说话

### 快速开始
详见上方 [Quick Start](#-quick-start) 部分。

---

**Made with 🦐 by an interdimensional lobster**
