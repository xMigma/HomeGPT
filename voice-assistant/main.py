from voice_recognizer import VoiceRecognizer
from assistant import VoiceAssistant
from tts.openai_tts import OpenAITTS
from wake_word import WakeWordModel

wake_word_model = WakeWordModel()

if wake_word_model.activate():
    print("Presiona Ctrl+C para detener la grabación.")
    print("Comenzando a grabar...")

    recognizer = VoiceRecognizer()
    text = recognizer.record_and_transcribe()

    print(f"Transcription: {text}")

    assistant = VoiceAssistant()
    response = assistant.chat(text)

    print(f"Response: {response}")

    tts = OpenAITTS()
    tts.reproduce(response)
