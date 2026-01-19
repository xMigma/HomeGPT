from openai import OpenAI
import os
import re
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
        self.max_tokens = 500

        self.system_message = {
            "role": "system",
            "content": (
                "Eres un asistente de voz breve y claro. "
                "Responde en español, máximo 3 frases, y evita jerga técnica innecesaria."
            ),
        }

    def chat(self, user_text: str):
        """Envía texto al LLM y devuelve la respuesta."""

        query = (
            f"{user_text}\n\n"
            "Recuerda: respuesta breve, sin URLs ni enlaces, menciona fuentes de forma natural."
        )

        messages = [
            self.system_message,
            {"role": "user", "content": query}
        ]

        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_completion_tokens=self.max_tokens,
                )
                answer = (resp.choices[0].message.content or "").strip()
                if answer:
                    answer = self._clean_response(answer)
                    return answer
                return "Lo siento, no pude generar una respuesta."
            except Exception as e:
                if attempt == 2:
                    return f"Error de conexión: {str(e)}"
                time.sleep(0.6 * (attempt + 1))

    def _clean_response(self, text: str) -> str:
        """Elimina enlaces markdown y limpia el formato para voz."""
        # ([texto](url)) -> según texto
        text = re.sub(r'\(\[([^\]]+)\]\([^)]+\)\)', r'según \1', text)
        # [texto](url) -> texto
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # URLs sueltas
        text = re.sub(r'https?://\S+', '', text)
        # Doble "según según"
        text = re.sub(r'según\s+según', 'según', text)
        # Espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        return text


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv("config.env")
    assistant = VoiceAssistant()
    print(assistant.chat("Cuando juega el real madrid?"))
