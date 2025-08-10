from voice import VoiceRecognizer

recognizer = VoiceRecognizer()
text = recognizer.record_and_transcribe()

print(f"Transcription: {text}")
