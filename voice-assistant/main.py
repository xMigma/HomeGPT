from voice_recognizer import VoiceRecognizer
from assistant import VoiceAssistant

while True:
    print("Presiona Ctrl+C para detener la grabación.")
    print("Comenzando a grabar...")
    
    recognizer = VoiceRecognizer()
    text = recognizer.record_and_transcribe()

    print(f"Transcription: {text}")

    assistant = VoiceAssistant()
    response = assistant.chat(text)
    print(f"Assistant response: {response}")
