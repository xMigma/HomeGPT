"""Pytest configuration and stubs for external/hardware modules.

This prevents tests from requiring real audio devices, network, or heavy libs.
Also ensures the repo's "voice-assistant" folder is importable as module path.
"""

from __future__ import annotations

import os
import sys
import types

# Make voice-assistant/ importable as top-level for tests collection time
repo_root = os.path.abspath(os.getcwd())
va_dir = os.path.join(repo_root, "voice-assistant")
if va_dir not in sys.path:
    sys.path.insert(0, va_dir)

# Provide dummy env vars expected by code
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("BRAVE_API_KEY", "test-brave")

# --- Stub dotenv ---
dotenv_mod = types.ModuleType("dotenv")
dotenv_mod.load_dotenv = lambda *a, **k: None
sys.modules.setdefault("dotenv", dotenv_mod)

# --- Stub trafilatura ---
trafilatura_mod = types.ModuleType("trafilatura")


def _extract(html: str) -> str:
    return "EXTRACTED"


trafilatura_mod.extract = _extract
sys.modules.setdefault("trafilatura", trafilatura_mod)

# --- Stub openai (provide minimal OpenAI client shape) ---
openai_mod = types.ModuleType("openai")


class _ChatCompletions:
    def create(self, **kwargs):  # noqa: D401 - shape only
        msg = types.SimpleNamespace(content="ok")
        choice = types.SimpleNamespace(message=msg)
        return types.SimpleNamespace(choices=[choice])


class _Chat:
    def __init__(self) -> None:
        self.completions = _ChatCompletions()


class OpenAI:  # noqa: N801 - match import style
    def __init__(self, *args, **kwargs) -> None:
        self.chat = _Chat()


openai_mod.OpenAI = OpenAI
sys.modules.setdefault("openai", openai_mod)

# --- Stub piper.voice ---
piper_mod = types.ModuleType("piper")
voice_mod = types.ModuleType("piper.voice")


class PiperVoice:
    sample_rate = 16000

    @classmethod
    def load(cls, model_path: str, config_path: str | None = None):
        return cls()

    def synthesize(self, text: str):
        class _Chunk:
            def __init__(self) -> None:
                self.audio_int16_bytes = b"\x00\x00" * 256

        # yield a couple of small chunks
        for _ in range(2):
            yield _Chunk()


voice_mod.PiperVoice = PiperVoice
sys.modules.setdefault("piper", piper_mod)
sys.modules.setdefault("piper.voice", voice_mod)

# --- Stub vosk ---
vosk_mod = types.ModuleType("vosk")
vosk_mod.Model = lambda path: object()


class _KaldiRecognizer:
    def __init__(self, model, rate):  # noqa: D401 - stub
        pass

    def AcceptWaveform(self, frame):  # noqa: D401 - stub
        pass

    def FinalResult(self):  # noqa: D401 - stub
        return '{"text": ""}'


vosk_mod.KaldiRecognizer = _KaldiRecognizer
vosk_mod.SetLogLevel = lambda level: None
sys.modules.setdefault("vosk", vosk_mod)

# --- Stub sounddevice ---
sd_mod = types.ModuleType("sounddevice")


class _DummyStream:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


sd_mod.RawInputStream = _DummyStream
sd_mod.InputStream = _DummyStream
sd_mod.sleep = lambda ms: None
sys.modules.setdefault("sounddevice", sd_mod)

# --- Stub webrtcvad ---
webrtcvad_mod = types.ModuleType("webrtcvad")


class _Vad:
    def __init__(self, level):
        pass

    def is_speech(self, frame, sample_rate):
        return False


webrtcvad_mod.Vad = _Vad
sys.modules.setdefault("webrtcvad", webrtcvad_mod)

# --- Stub openwakeword.model ---
oww_mod = types.ModuleType("openwakeword")
oww_model_mod = types.ModuleType("openwakeword.model")


class _OWWModel:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def predict(self, frame):
        return {}


oww_model_mod.Model = _OWWModel
sys.modules.setdefault("openwakeword", oww_mod)
sys.modules.setdefault("openwakeword.model", oww_model_mod)
