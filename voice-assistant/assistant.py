from openai import OpenAI
from dotenv import load_dotenv
import os
import time


class VoiceAssistant:
    def __init__(self, config_path: str = "config.env"):
        load_dotenv(config_path)
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY no encontrada. Verifica tu archivo config.env"
            )

        self.client = OpenAI(api_key=api_key)

        # Configuración
        self.model = (
            "gpt-5-nano"  # rápido/barato; cambia a gpt-4o si quieres mejor calidad
        )
        self.max_tokens = 300
        self.max_turns = 12

        # Historial en memoria (lista de mensajes ChatML)
        self.history = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente de voz breve y claro. "
                    "Responde en español, máximo 3 frases, y evita jerga técnica innecesaria."
                ),
            }
        ]

    def chat(self, user_text: str) -> str:
        """Envía texto al LLM y devuelve la respuesta."""
        # Añade el turno del usuario
        self.history.append({"role": "user", "content": user_text})

        # Recorta historial si crece demasiado
        if len(self.history) > self.max_turns:
            # conserva system + los últimos turnos
            keep = [self.history[0]] + self.history[-(self.max_turns - 1) :]
            self.history[:] = keep

        # Llama a la API
        for attempt in range(3):  # pequeños reintentos simples
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.history,
                    max_completion_tokens=self.max_tokens,
                )
                answer = resp.choices[0].message.content
                if answer:
                    answer = answer.strip()
                    self.history.append({"role": "assistant", "content": answer})
                    return answer
                else:
                    return "Lo siento, no pude generar una respuesta."
            except Exception as e:
                if attempt == 2:
                    return f"Error de conexión: {str(e)}"
                time.sleep(0.6 * (attempt + 1))  # backoff básico

    def clear_history(self):
        """Limpia el historial manteniendo solo el mensaje del sistema."""
        system_msg = self.history[0]
        self.history.clear()
        self.history.append(system_msg)


if __name__ == "__main__":
    assistant = VoiceAssistant()
    print(assistant.chat("En que equipos ha jugado Cristiano Ronaldo?"))
