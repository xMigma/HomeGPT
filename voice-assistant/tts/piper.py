from __future__ import annotations

import logging
import os
import subprocess
from typing import Optional

from piper.voice import PiperVoice

from .base import BaseTTS


class PiperTTS(BaseTTS):
    """TTS engine using Piper.

    Mirrors previous TTSEngine behavior for backward compatibility.
    """

    def __init__(
        self,
        model_path: str = "models/piper/es_ES-mls_10246-low.onnx",
        config_path: str = "models/piper/es_ES-mls_10246-low.onnx.json",
    ) -> None:
        self.model_path = model_path
        self.config_path = config_path
        self.voice: Optional[PiperVoice] = None
        self.sample_rate: int = 16000
        self._load_voice()

    def _load_voice(self) -> None:
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Modelo no encontrado: {self.model_path}")

            self.voice = PiperVoice.load(self.model_path, config_path=self.config_path)
            self.sample_rate = getattr(self.voice, "sample_rate", 16000)
            logging.info(f"Modelo TTS cargado: {self.model_path}")
        except Exception as e:  # noqa: BLE001 - propagate as runtime error
            logging.error(f"Error cargando modelo TTS: {e}")
            raise

    def reproduce(self, text: str) -> None:
        if not self.voice:
            raise RuntimeError("Modelo TTS no está cargado")

        if not text or not text.strip():
            logging.warning("Texto vacío, no se reproduce nada")
            return

        aplay = None
        try:
            aplay = subprocess.Popen(
                ["aplay", "-q", "-f", "S16_LE", "-r", str(self.sample_rate), "-c", "1"],
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            for chunk in self.voice.synthesize(text.strip()):
                aplay.stdin.write(chunk.audio_int16_bytes)  # type: ignore[union-attr]

            aplay.stdin.close()  # type: ignore[union-attr]
            aplay.wait()

            logging.info(f"Audio reproducido: '{text[:50]}...'")
        except Exception as e:  # noqa: BLE001
            logging.error(f"Error reproduciendo audio: {e}")
            if aplay is not None:
                aplay.terminate()
