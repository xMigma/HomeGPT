# HomeGPT – Lightweight Voice Assistant (Raspberry Pi–ready)

HomeGPT is a small, offline‑first Spanish voice assistant designed to run on low‑power boards like Raspberry Pi Zero / Zero 2 W.

It listens for speech, detects voice activity (VAD), transcribes locally with Vosk, sends the text to a remote LLM (OpenAI), synthesizes speech with Piper, and plays it back—looping for the next turn.


## Features

- Offline speech‑to‑text (STT) with Vosk small Spanish model
- Low‑latency voice activity detection (WebRTC VAD)
- Natural TTS using Piper (local, fast) and ALSA `aplay`
- LLM integration via OpenAI API (concise Spanish replies)
- Optional web context via Brave Search API + content extraction (Trafilatura)
- 16 kHz mono audio pipeline tuned for low resources


## How it works

1. Capture mic audio at 16 kHz and segment with WebRTC VAD until silence.
2. Transcribe locally using Vosk.
3. Call the LLM with a short system prompt and optional web snippets.
4. Synthesize the response with Piper and play via `aplay`.
5. Repeat.

Code entrypoint: `voice-assistant/main.py`.


## Repository layout

```
HomeGPT/
├── models/
│   ├── piper/
│   │   ├── xx_XX-mls_10246-low.onnx
│   │   └── xx_XX-mls_10246-low.onnx.json
│   └── vosk-model-small-xx-0.42/    # Vosk small model
└── voice-assistant/
    ├── main.py                      # Loop: STT -> LLM -> TTS
    ├── assistant.py                 # OpenAI client + web context
    ├── voice_recognizer.py          # VAD + Vosk transcription
    ├── tts.py                       # Piper synth + aplay output
    ├── web_search.py                # Provider interface + formatting
    └── providers/
        ├── brave.py                 # Brave Search API provider
        └── ddgs.py                  # DuckDuckGo (optional)
```


## Requirements

- Python 3.9+
- Linux with ALSA (for `aplay`)
- Microphone and speaker/headphones configured as default ALSA/Pulse devices

System packages (Debian/Raspberry Pi OS suggested):

- `alsa-utils` (for `aplay`)
- `portaudio19-dev` (recommended for sounddevice)
- `build-essential` (general build tools)

Python packages:

- `sounddevice`, `vosk`, `webrtcvad`
- `openai`, `python-dotenv`
- `requests`, `trafilatura`
- `piper-tts`
- Optional: `duckduckgo-search` (for `providers/ddgs.py`)


## Setup

1) Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

2) Install Python dependencies

```bash
pip install sounddevice vosk webrtcvad openai python-dotenv requests trafilatura piper-tts duckduckgo-search
```

3) Ensure system audio tools are available

```bash
sudo apt-get update
sudo apt-get install -y alsa-utils portaudio19-dev
```

4) Place the models (already included here)

- Vosk: `models/vosk-model-small-es-0.42`
- Piper: `models/piper/es_ES-mls_10246-low.onnx` and its `.json`

5) Provide API keys in `config.env`

```
OPENAI_API_KEY=sk-...            # required for LLM replies
BRAVE_API_KEY=...                # optional (web snippets); safe to omit
```

If `BRAVE_API_KEY` is missing, the assistant will skip web context.


## Usage

- Connect mic and speakers, then run:

```bash
python voice-assistant/main.py
```

- Speak after “Comenzando a grabar…”. The app stops recording on silence, prints the transcript, calls the LLM, then speaks the reply. Press Ctrl+C to stop.

Notes
- Default audio device is used. If you have multiple devices, configure ALSA/Pulse defaults or set a device in `sounddevice`.
- This loop does not include a wake word yet; it records on demand and ends on silence.


## Configuration knobs (code)

`voice_recognizer.py`
- `sample_rate`: 16000
- `chunk_ms`: 20 (WebRTC VAD supported frame size)
- `vad_aggressiveness`: 0–3 (default 2)
- `speech_threshold_ms`: minimum speech onset (default 250 ms)
- `silence_threshold_ms`: end of utterance (default 700 ms)

`assistant.py`
- Model: `gpt-5-nano` (adjust per your OpenAI account/models)
- Max tokens/turns, basic retry with backoff
- Optional Brave web context (summaries via Trafilatura)

`tts.py`
- Piper model paths and playback via `aplay` at detected sample rate


## Performance tips for Raspberry Pi Zero / Zero 2 W

- Keep sample rate at 16 kHz mono.
- Use the Vosk “small” model (already included).
- Prefer the Piper “low” voice (already included).
- Increase `vad_aggressiveness` to reduce false positives in noisy rooms.