import sounddevice as sd
import queue
import json
import collections
import logging
from vosk import Model, KaldiRecognizer, SetLogLevel
import webrtcvad

# Silenciar los logs de Vosk
SetLogLevel(-1)


class VoiceRecognizer:
    """Voice recognition class using Vosk STT and WebRTC VAD."""

    def __init__(
        self,
        model_path="models/vosk-model-small-es-0.42",
        sample_rate=16000,
        chunk_ms=20,
        vad_aggressiveness=2,
        preroll_ms=300,
        speech_threshold_ms=250,
        silence_threshold_ms=700,
    ):
        """
        Initialize voice recognizer.

        Args:
            model_path: Path to Vosk model
            sample_rate: Audio sample rate (Hz)
            chunk_ms: Audio chunk duration (ms)
            vad_aggressiveness: WebRTC VAD aggressiveness (0-3)
            preroll_ms: Pre-roll buffer duration (ms)
            speech_threshold_ms: Min speech duration to start listening (ms)
            silence_threshold_ms: Silence duration to stop recording (ms)
        """
        self.sample_rate = sample_rate
        self.chunk_ms = chunk_ms
        self.frame_samples = sample_rate * chunk_ms // 1000
        self.speech_threshold_ms = speech_threshold_ms
        self.silence_threshold_ms = silence_threshold_ms

        logging.info(f"Loading Vosk model from {model_path}")

        self.model = Model(model_path)
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.preroll_frames = collections.deque(maxlen=preroll_ms // chunk_ms)

    def _audio_callback(self, indata, frames, time, status):
        """Audio input callback - receives exactly frame_samples (20 ms)."""
        if status:
            logging.warning(f"Audio callback status: {status}")
        self.audio_q.put(bytes(indata))

    def record_and_transcribe(self) -> str:
        """
        Record audio until silence and transcribe to text.

        Returns:
            str: Transcribed text or empty string if no speech detected
        """
        # Initialize state for this recording session
        in_speech_ms = 0
        silence_ms = 0
        listening = False
        preroll_frames = collections.deque(maxlen=self.preroll_frames.maxlen)
        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        audio_q = queue.Queue()

        def callback(indata, frames, time, status):
            """Audio input callback - receives exactly frame_samples (20 ms)."""
            if status:
                logging.warning(f"Audio callback status: {status}")
            audio_q.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.frame_samples,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                logging.info("Started voice recording")

                while True:
                    frame = audio_q.get()
                    speech = self.vad.is_speech(frame, self.sample_rate)

                    if not listening:
                        # Pre-listening phase: collect frames and wait for speech
                        preroll_frames.append(frame)
                        in_speech_ms += self.chunk_ms if speech else 0

                        if in_speech_ms >= self.speech_threshold_ms:
                            logging.info("Speech detected, starting transcription")
                            listening = True
                            # Add preroll frames to recognizer
                            for f in preroll_frames:
                                recognizer.AcceptWaveform(f)
                    else:
                        # Listening phase: transcribe and detect end of speech
                        recognizer.AcceptWaveform(frame)

                        if speech:
                            silence_ms = 0  # Reset silence counter on speech
                        else:
                            silence_ms += self.chunk_ms  # Increment silence counter

                            if silence_ms >= self.silence_threshold_ms:
                                # End of speech detected
                                final = json.loads(recognizer.FinalResult())
                                text = final.get("text", "").strip()
                                logging.info(f"Transcription complete: '{text}'")
                                return text

        except Exception as e:
            logging.error(f"Error in voice recognition: {e}")
            return ""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    recognizer = VoiceRecognizer()
    text = recognizer.record_and_transcribe()
    print(f"Transcription: {text}")
