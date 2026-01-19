import logging

from dotenv import load_dotenv

from assistant import VoiceAssistant
from tts.openai_tts import OpenAITTS
from voice_recognizer import VoiceRecognizer
from wake_word import WakeWordModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    load_dotenv("config.env")
    wake = WakeWordModel()
    recognizer = VoiceRecognizer()
    assistant = VoiceAssistant()
    tts = OpenAITTS()

    logger.info("Asistente listo. Esperando wake word...")

    try:
        while True:
            if not wake.activate():
                continue

            logger.info("Wake word detectado. Grabando...")

            try:
                text = recognizer.record_and_transcribe()
                if not text:
                    logger.warning("No se detectó texto.")
                    continue

                logger.info(f"Transcripción: {text}")

                response = assistant.chat(text)
                logger.info(f"Respuesta: {response}")

                tts.reproduce(response)

            except Exception as e:
                logger.error(f"Error procesando: {e}")

    except KeyboardInterrupt:
        logger.info("Deteniendo asistente...")


if __name__ == "__main__":
    main()
