import logging
from dotenv import load_dotenv

load_dotenv("config.env")

from voice_recognizer import VoiceRecognizer
from assistant import VoiceAssistant
from tts.openai_tts import OpenAITTS
from wake_word import WakeWordModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wake_word_model = WakeWordModel()

while True:
    if wake_word_model.activate():
        logger.info("Presiona Ctrl+C para detener la grabación.")
        logger.info("Comenzando a grabar...")

        recognizer = VoiceRecognizer()
        text = recognizer.record_and_transcribe()

        logger.info(f"Transcription: {text}")

        assistant = VoiceAssistant()
        response = assistant.chat(text)

        logger.info(f"Response: {response}")

        tts = OpenAITTS()
        tts.reproduce(response)
