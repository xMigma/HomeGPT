from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Optional

import requests
from dotenv import load_dotenv

from .base import BaseTTS


class OpenAITTS(BaseTTS):
    """TTS engine using OpenAI's streaming audio endpoint.

    Notes:
    - Streams compressed audio (mp3 by default) to ffplay for low-latency playback.
    - Requires OPENAI_API_KEY in environment or passed via constructor.
    - sample_rate is not enforced (compressed stream). Kept for interface compatibility.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        model: str = "gpt-4o-mini-tts",
        voice: str = "alloy",
        audio_format: str = "mp3",
        endpoint: str = "https://api.openai.com/v1/audio/speech",
        chunk_size: int = 8192,
        timeout: int = 60,
    ) -> None:
        # Load env once to support repo's config.env convention
        load_dotenv("config.env")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.voice = voice
        self.audio_format = audio_format
        self.endpoint = endpoint
        self.chunk_size = chunk_size
        self.timeout = timeout
        self.sample_rate = 16000

        if not self.api_key:
            logging.warning(
                "OPENAI_API_KEY no encontrado; OpenAITTS no podrá reproducir."
            )

    def reproduce(self, text: str) -> None:
        if not text or not text.strip():
            logging.warning("Texto vacío, no se reproduce nada")
            return

        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY no configurado")

        # Prepare playback process (ffplay reads from stdin)
        try:
            ffplay = subprocess.Popen(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-loglevel",
                    "quiet",
                    "-",
                ],
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise RuntimeError(
                "ffplay no encontrado. Instala ffmpeg o ajusta el reproductor."
            ) from e

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "voice": self.voice,
            "input": text.strip(),
            "format": self.audio_format,
        }

        try:
            with requests.post(
                self.endpoint,
                headers=headers,
                data=json.dumps(payload),
                stream=True,
                timeout=self.timeout,
            ) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        # mypy: ignore[union-attr] for stdin Optional
                        ffplay.stdin.write(chunk)  # type: ignore[union-attr]

            # Close stdin to signal EOF to ffplay and wait for it to finish
            if ffplay.stdin:
                ffplay.stdin.close()
            ffplay.wait()
            logging.info(f"Audio reproducido (OpenAI): '{text[:50]}...'")
        except Exception as e:  # noqa: BLE001
            logging.error(f"Error en reproducción OpenAI TTS: {e}")
            ffplay.terminate()
            raise

    def close(self) -> None:  # pragma: no cover - nothing persistent to close
        pass
