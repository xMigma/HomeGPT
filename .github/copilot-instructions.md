# Copilot Instructions – Voice Assistant Project

## Objective
Build a lightweight **always-listening** voice assistant in Python for **Raspberry Pi Zero / Zero 2 W**.  

The assistant:
1. Waits for a wake word ("Hey Chat").
2. Records the user's voice until silence (VAD).
3. Transcribes to text (offline preferred).
4. Sends the text to a remote LLM API (ChatGPT or similar).
5. Receives the response and converts it to speech (TTS).
6. Plays the audio output.

## Constraints
- **Hardware**: Raspberry Pi Zero / Zero 2 W (low RAM and CPU).
- **Audio**: 16 kHz mono, low latency.
- **Offline first**: STT/TTS should work without internet.
- **Minimal dependencies**: avoid heavy ML libraries if possible.

## Preferred Libraries
- **Wake Word**: `openwakeword` or Picovoice Porcupine.
- **VAD**: `webrtcvad`.
- **STT**: `vosk` (small model), `faster-whisper` only if Zero 2 W.
- **LLM API**: `openai` (GPT models) or similar.
- **TTS**: `piper` (preferred), `espeak-ng` fallback.

## Project Structure
```

voice-assistant/
├── main.py
├── config.yaml
├── audio_io.py
├── wake.py
├── vad.py
├── stt.py
├── llm.py
├── tts.py
└── models/

```

## Coding Style
- Python 3.9+, PEP8 compliant.
- Short, modular functions.
- Comments: brief but clear.
- Variables and function names in English.
- Logging over print statements.
- Avoid hardcoding paths or API keys; use `config.yaml` and env vars.
- Only do what I tell you to do, nothing else.

## Example Flow
```

if wake.detect():
audio\_clip = vad.record\_until\_silence(max\_s=10)
text = stt.transcribe(audio\_clip)
reply = llm.respond(text)
tts.say(reply)

```

## Notes for Copilot
- When suggesting code, prefer **offline-first** approaches.
- Assume **low resources** and avoid GPU-dependent solutions.
- Keep functions testable and independent.
- Do not store secrets in code.