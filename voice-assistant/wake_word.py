from collections import deque
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

SAMPLE_RATE = 16000
FRAME_MS = 80
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 1280


class WakeWordModel:
    def __init__(
        self,
        wakeword_model_paths: list[str] | None = None,
        threshold: float = 0.5,
    ):
        if wakeword_model_paths:
            self.model = Model(wakeword_model_paths=wakeword_model_paths)
        else:
            self.model = Model()
        self.threshold = threshold
        self.buf = deque(maxlen=1)  # guarda el último frame capturado

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        # Convierte de float32 [-1,1] a int16 PCM
        pcm = np.clip(indata[:, 0], -1.0, 1.0)
        pcm = (pcm * 32767.0).astype(np.int16)
        self.buf.append(pcm)

    def activate(self) -> bool:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            blocksize=FRAME_SAMPLES,
            dtype="float32",
            callback=self._callback,
        ):
            while True:
                if not self.buf:
                    sd.sleep(1)
                    continue
                frame = self.buf.popleft()
                prediction = self.model.predict(frame)
                if prediction:
                    name, score = next(iter(prediction.items()))
                    print(f"{name}: {score:.3f}", end="\r", flush=True)
                    if score >= self.threshold:
                        print(f"\nWake word detected: {name} (score={score:.3f})")
                        return True
