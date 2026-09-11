# API Notes

## SiliconFlow TTS API

### Text-to-Speech
```
POST https://api.siliconflow.cn/v1/audio/speech
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "model": "IndexTeam/IndexTTS-2",   // or "FunAudioLLM/CosyVoice2-0.5B"
  "input": "text to speak",
  "voice": "<voice-uri or preset>",
  "response_format": "mp3"           // mp3, wav, opus, flac
}
→ Returns binary audio file
```

### Voice Cloning (Upload)
```
POST https://api.siliconflow.cn/v1/uploads/audio/voice
Authorization: Bearer <api-key>
Content-Type: multipart/form-data

file: <audio-file>
model: FunAudioLLM/CosyVoice2-0.5B
customName: <name>
→ {"uri": "speech:<name>:<account>:<id>"}
```

### List Cloned Voices
```
GET https://api.siliconflow.cn/v1/audio/voice/list
Authorization: Bearer <api-key>
→ {"result": [{"model": "...", "customName": "...", "uri": "..."}]}
```

### Delete Cloned Voice
```
POST https://api.siliconflow.cn/v1/uploads/audio/voice/deletions
Authorization: Bearer <api-key>
Content-Type: application/json

{"uri": "<voice-uri>"}
```

### Available TTS Models
| Model | Cloned Voice Support | Built-in Voices |
|-------|---------------------|-----------------|
| IndexTeam/IndexTTS-2 | ✅ Stable | Uses cloned only |
| FunAudioLLM/CosyVoice2-0.5B | ⚠️ May 500 | alex, bella, claire, anna |

### Built-in Voice Format
`FunAudioLLM/CosyVoice2-0.5B:bella` — use as both model and voice.

### Cloned Voice Format
`speech:<name>:<account-id>:<voice-id>` — returned by upload API.

**Important**: Cloned voices uploaded via CosyVoice2 can be used with IndexTTS-2 for generation. Upload always uses CosyVoice2; generation can use either model.

---

## Feishu Audio Message API

### 1. Get Tenant Access Token
```
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Content-Type: application/json

{"app_id": "<app-id>", "app_secret": "<app-secret>"}
→ {"tenant_access_token": "t-xxx", "expire": 7200}
```
Token expires in 2 hours. Re-fetch as needed.

### 2. Upload Audio File
```
POST https://open.feishu.cn/open-apis/im/v1/files
Authorization: Bearer <token>
Content-Type: multipart/form-data

file_type: opus
file_name: voice.opus
file: <opus-file>
duration: <milliseconds>
→ {"data": {"file_key": "file_v3_xxx"}}
```

**Audio must be opus format.** Convert with ffmpeg:
```bash
ffmpeg -y -i input.mp3 -c:a libopus -b:a 32k output.opus
```

### 3. Send Audio Message
```
POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id
Authorization: Bearer <token>
Content-Type: application/json

{
  "receive_id": "<open_id>",
  "msg_type": "audio",
  "content": "{\"file_key\":\"<file_key>\"}"
}
→ {"code": 0, "msg": "success"}
```

Use `receive_id_type=chat_id` and pass `chat_id` as `receive_id` to send to a group or existing conversation.

### Required Feishu Bot Permissions
- `im:message:create` — Send messages
- `im:file` — Upload files

Enable these in [Feishu Developer Console](https://open.feishu.cn/app) → Your App → Permissions.

### Finding open_id
The user's `open_id` is included in Feishu webhook/WebSocket events when they message the bot. Check OpenClaw gateway logs for `received message from ou_xxx`.
