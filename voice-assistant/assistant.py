from openai import OpenAI
import os
import time


class VoiceAssistant:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY no encontrada. Verifica tu archivo config.env"
            )

        self.client = OpenAI(api_key=api_key)

        # Configuración
        self.model = "gpt-5-search-api"
        self.max_tokens = 10000
        self.max_turns = 12

        self.history = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente de voz breve y claro. "
                    "Responde en español, máximo 3 frases, y evita jerga técnica innecesaria."
                ),
            }
        ]

    def chat(self, user_text: str):
        """Envía texto al LLM y devuelve la respuesta."""

        query = (
            f"Pregunta del usuario: {user_text}\n\n"
            "Responde en español, máximo 3 frases, sin jerga técnica. "
            "Si usas datos de la web, indícalo con un 'Según X' o 'Fuentes web' sin enlaces largos."
        )

        self.history.append({"role": "user", "content": query})

        if len(self.history) > self.max_turns:
            keep = [self.history[0]] + self.history[-(self.max_turns - 1) :]
            self.history[:] = keep

        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.history,
                    max_completion_tokens=self.max_tokens,
                )
                answer = (resp.choices[0].message.content or "").strip()
                if answer:
                    self.history.append({"role": "assistant", "content": answer})
                    return answer
                return "Lo siento, no pude generar una respuesta."
            except Exception as e:
                # opcional: log de e
                if attempt == 2:
                    return f"Error de conexión: {str(e)}"
                time.sleep(0.6 * (attempt + 1))  # backoff básico

    def clear_history(self):
        """Limpia el historial manteniendo solo el mensaje del sistema."""
        system_msg = self.history[0]
        self.history.clear()
        self.history.append(system_msg)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("config.env")
    assistant = VoiceAssistant()
    print(assistant.chat("Cuando juega el real madrid?"))
