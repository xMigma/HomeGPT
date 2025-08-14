from openwakeword.model import Model

import numpy as np
import sounddevice as sd


class WakeWordModel:
    def __init__(
        self,
        model_path: str = "models/openwakeword/alexa_v0.1.tflite",
        threshold: float = 0.3,
    ):
        self.model = Model(
            wakeword_models=[model_path],
        )
        self.threshold = threshold

    def _my_function_to_get_audio_frame(
        self, frame_ms: int = 80, samplerate: int = 16000
    ) -> np.ndarray:
        """Capture a single audio frame as 16-bit PCM mono at 16kHz.

        Returns a 1D numpy.ndarray with dtype=np.int16 and length N (multiple of 1280 for 80ms).
        """
        samples = int(samplerate * frame_ms / 1000)
        audio = sd.rec(
            samples,
            samplerate=samplerate,
            channels=1,
            dtype="int16",  # 16-bit PCM
            blocking=True,
        )
        return audio.reshape(-1)  # 1D int16b

    def activate(self) -> bool:
        while True:
            frame = self._my_function_to_get_audio_frame()
            prediction = self.model.predict(frame)
            # Print compact scores
            if prediction:
                # Show first (and usually only) model score
                name, score = next(iter(prediction.items()))
                print(f"{name}: {score:.3f}", end="\r", flush=True)
                if score >= self.threshold:
                    print(f"\nWake word detected: {name} (score={score:.3f})")
                    return True
