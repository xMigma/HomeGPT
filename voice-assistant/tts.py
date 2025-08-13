import subprocess
import os
import logging
from piper.voice import PiperVoice


class TTSEngine:
    """Motor de síntesis de voz usando Piper"""

    def __init__(
        self,
        model_path="models/piper/es_ES-mls_10246-low.onnx",
        config_path="models/piper/es_ES-mls_10246-low.onnx.json",
    ):
        """
        Inicializa el motor TTS

        Args:
            model_path: Ruta al modelo Piper
            config_path: Ruta al archivo de configuración
        """
        self.model_path = model_path
        self.config_path = config_path
        self.voice = None
        self.sample_rate = 16000

        self._load_voice()

    def _load_voice(self):
        """Carga el modelo de voz"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Modelo no encontrado: {self.model_path}")

            self.voice = PiperVoice.load(self.model_path, config_path=self.config_path)
            self.sample_rate = getattr(self.voice, "sample_rate", 16000)
            logging.info(f"Modelo TTS cargado: {self.model_path}")

        except Exception as e:
            logging.error(f"Error cargando modelo TTS: {e}")
            raise

    def reproduce(self, text):
        """
        Convierte texto a voz y lo reproduce

        Args:
            text (str): Texto a sintetizar y reproducir
        """
        if not self.voice:
            raise RuntimeError("Modelo TTS no está cargado")

        if not text or not text.strip():
            logging.warning("Texto vacío, no se reproduce nada")
            return

        try:
            aplay = subprocess.Popen(
                ["aplay", "-q", "-f", "S16_LE", "-r", str(self.sample_rate), "-c", "1"],
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            for chunk in self.voice.synthesize(text.strip()):
                aplay.stdin.write(chunk.audio_int16_bytes)

            aplay.stdin.close()
            aplay.wait()

            logging.info(f"Audio reproducido: '{text[:50]}...'")

        except Exception as e:
            logging.error(f"Error reproduciendo audio: {e}")
            if "aplay" in locals():
                aplay.terminate()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    tts = TTSEngine()
    tts.reproduce("Hola, este audio se reproduce mientras se genera.")
