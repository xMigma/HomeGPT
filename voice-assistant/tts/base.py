from abc import ABC, abstractmethod


class BaseTTS(ABC):
    """Abstract TTS interface.

    Contract:
    - Implementations must load any resources in __init__ (fast) or lazily on first use.
    - reproduce(text): synthesize and play audio for the given text.
    - sample_rate: int property indicating playback sample rate (Hz).
    """

    sample_rate: int = 16000

    @abstractmethod
    def reproduce(self, text: str) -> None:
        """Synthesize and play audio for the given text.

        Implementations should be resilient to empty text and log/return early.
        Should raise RuntimeError when the engine isn't loaded/configured.
        """
        raise NotImplementedError

    def close(self) -> None:
        pass
