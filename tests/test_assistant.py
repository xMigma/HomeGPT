import types

from assistant import VoiceAssistant


def test_clear_history_keeps_system_only():
    a = VoiceAssistant()
    a.history.append({"role": "user", "content": "hola"})
    a.clear_history()
    assert len(a.history) == 1
    assert a.history[0]["role"] == "system"


def test_history_trim_on_max_turns(monkeypatch):
    a = VoiceAssistant()
    a.max_turns = 4

    # patch client to avoid network
    calls = {"n": 0}

    def fake_create(**kwargs):
        calls["n"] += 1
        msg = types.SimpleNamespace(content="ok")
        choice = types.SimpleNamespace(message=msg)
        return types.SimpleNamespace(choices=[choice])

    monkeypatch.setattr(a.client.chat.completions, "create", fake_create)

    for i in range(6):
        a.chat(f"q{i}")

    # system + last (max_turns-1) messages should be kept in history
    assert len(a.history) <= a.max_turns
    assert a.history[0]["role"] == "system"


def test_chat_retries_then_success(monkeypatch):
    a = VoiceAssistant()
    attempts = {"n": 0}

    def flaky_create(**kwargs):
        if attempts["n"] < 2:
            attempts["n"] += 1
            raise RuntimeError("boom")
        msg = types.SimpleNamespace(content="ok")
        choice = types.SimpleNamespace(message=msg)
        return types.SimpleNamespace(choices=[choice])

    monkeypatch.setattr(a.client.chat.completions, "create", flaky_create)
    out = a.chat("hola")
    assert out == "ok"


def test_chat_fails_after_retries(monkeypatch):
    a = VoiceAssistant()

    def always_fail(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(a.client.chat.completions, "create", always_fail)
    out = a.chat("hola")
    assert out.startswith("Error de conexión:")
