from unittest import mock

import pytest

from tts.openai_tts import OpenAITTS
from tts.piper import PiperTTS


def test_openai_tts_empty_text_returns():
    t = OpenAITTS(api_key="x", endpoint="http://localhost")
    # mock out subprocess so ffplay isn't launched
    with mock.patch("subprocess.Popen"):
        t.reproduce("")
    # should not raise
    assert True


def test_openai_tts_requires_key():
    t = OpenAITTS(api_key=None)
    with pytest.raises(RuntimeError):
        t.reproduce("hola")


def test_piper_raises_when_model_missing(monkeypatch):
    # make os.path.exists return False
    with mock.patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            PiperTTS(model_path="/nope.onnx")
