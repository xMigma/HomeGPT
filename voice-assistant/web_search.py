from abc import ABC, abstractmethod

import requests
import trafilatura


class WebSearchProvider(ABC):
    """Clase abstracta para proveedores de búsqueda web."""

    @abstractmethod
    def search(self, query: str, max_results: int = 6) -> list:
        """
        Realiza una búsqueda web y retorna una lista de resultados.

        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados

        Returns:
            Lista de diccionarios con keys: title, href, snippet, full_text
        """
        pass

    def format_results(self, results: list) -> str:
        """Formatea los resultados en texto legible."""
        formatted = ""
        for r in results:
            formatted += f"{r['title']} - {r['href']}\n"
            formatted += f"Noticia/artículo:\n{(r['full_text'] or 'No se pudo extraer')[:1000]}\n\n"
        return formatted


def make_web_search(
    query: str, max_results: int = 6, provider: WebSearchProvider = None
) -> str:
    """
    Realiza una búsqueda web usando el proveedor especificado.

    Args:
        query: Término de búsqueda
        max_results: Número máximo de resultados
        provider: Proveedor de búsqueda (por defecto DuckDuckGo)

    Returns:
        Resultados formateados como string
    """
    if provider is None:
        raise ValueError("Un proveedor de búsqueda debe ser especificado.")

    results = provider.search(query, max_results)
    return provider.format_results(results)


def fetch_full_text(url):
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            return trafilatura.extract(response.text)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None


if __name__ == "__main__":
    from ddgs import DuckDuckGoProvider

    query = "Cuando es el proximo gran premio de formula 1"
    provider = DuckDuckGoProvider()
    print(make_web_search(query, provider=provider))
