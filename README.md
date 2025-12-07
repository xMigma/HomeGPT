# HomeGPT – Asistente de Voz en Español

Asistente de voz simple que escucha, transcribe, consulta a ChatGPT y responde con voz.

## ¿Qué hace?

1. **Detecta una palabra de activación** ("Alexa" con OpenWakeWord)
2. **Graba tu voz** hasta que haya silencio (WebRTC VAD)
3. **Transcribe** el audio localmente con Vosk (español)
4. **Envía el texto** a OpenAI (GPT) con contexto web opcional (Brave Search)
5. **Responde con voz** usando OpenAI TTS

## Estado actual

**Implementado:**
- Detección de palabra de activación (wake word)
- Grabación con detección de actividad de voz (VAD)
- Transcripción offline en español (Vosk)
- Integración con OpenAI (chat + TTS)
- Búsqueda web opcional (Brave API)

**Próximamente:**
- Optimización para Raspberry Pi Zero / Zero 2 W
- TTS local con Piper (alternativa offline)
- Modo de conversación continua

## Instalación rápida

1. **Clona el repositorio y crea el entorno virtual:**

```bash
git clone https://github.com/xMigma/HomeGPT.git
cd HomeGPT
python3 -m venv .venv
source .venv/bin/activate
```

2. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

3. **Descarga los modelos necesarios:**

**Vosk (Transcripción en español):**
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip -d models/
```

**OpenWakeWord (Palabra de activación):**
```bash
mkdir -p models/openwakeword
wget https://github.com/dscripka/openWakeWord/releases/download/v0.1.0/alexa_v0.1.tflite -O models/openwakeword/alexa_v0.1.tflite
```

**Piper (TTS local - opcional):**
```bash
mkdir -p models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx -O models/piper/es_ES-mls_10246-low.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/mls_10246/low/es_ES-mls_10246-low.onnx.json -O models/piper/es_ES-mls_10246-low.onnx.json
```

4. **Configura tus claves API en `config.env`:**

```env
OPENAI_API_KEY=sk-...           # Obligatorio
BRAVE_API_KEY=...               # Opcional
```

5. **Ejecuta el asistente:**

```bash
python voice-assistant/main.py
```

Di "Alexa" y luego tu pregunta. El asistente responderá con voz.

## Estructura del proyecto

```
HomeGPT/
├── voice-assistant/
│   ├── main.py                  # Punto de entrada
│   ├── wake_word.py             # Detección de palabra de activación
│   ├── voice_recognizer.py      # Grabación + VAD + Vosk
│   ├── assistant.py             # OpenAI + búsqueda web
│   ├── tts/                     # Síntesis de voz
│   │   ├── openai_tts.py        # OpenAI TTS (actual)
│   │   └── piper.py             # Piper TTS (futuro)
│   └── web/                     # Proveedores de búsqueda
│       ├── brave.py
│       └── ddgs.py
└── models/                      # Modelos offline
    ├── vosk-model-small-es-0.42/
    ├── piper/
    └── openwakeword/
```

## Requisitos

- **Python 3.9+**
- **Micrófono y altavoces** configurados como dispositivos por defecto
- **Linux recomendado** (probado en Ubuntu/Debian)

### Paquetes del sistema (opcional):

```bash
sudo apt-get install portaudio19-dev ffmpeg
```

## Configuración avanzada

Puedes ajustar parámetros en el código:

**`voice_recognizer.py`:**
- `vad_aggressiveness`: 0-3 (sensibilidad del VAD)
- `speech_threshold_ms`: milisegundos mínimos de voz
- `silence_threshold_ms`: silencio para terminar grabación

**`assistant.py`:**
- `model`: modelo de OpenAI a usar
- `max_tokens`: límite de respuesta

## Licencia

MIT
