from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import requests
import trafilatura


class WebSearchProvider(ABC):
    """Clase abstracta para proveedores de búsqueda web."""

    @abstractmethod
    def search(self, query: str, max_results: int) -> list:
        """
        Realiza una búsqueda web y retorna una lista de resultados.

        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados

        Returns:
            Lista de diccionarios con keys: title, href, snippet, full_text
        """
        raise NotImplementedError

    def format_results(self, results: list) -> str:
        """Formatea los resultados en texto legible."""
        formatted = ""
        for r in results:
            formatted += f"{r['title']} - {r['href']}\n"
            formatted += f"Noticia/artículo:\n{(r['full_text'] or 'No se pudo extraer')[:1000]}\n\n"
        return formatted


def make_web_search(
    query: str, max_results: int = 2, provider: Optional[WebSearchProvider] = None
) -> str:
    """
    Realiza una búsqueda web usando el proveedor especificado.

    Args:
        query: Término de búsqueda
        max_results: Número máximo de resultados
        provider: Proveedor de búsqueda (requerido)

    Returns:
        Resultados formateados como string
    """
    if provider is None:
        raise ValueError("Un proveedor de búsqueda debe ser especificado.")

    results = provider.search(query, max_results)
    return provider.format_results(results)


def fetch_full_text(url: str) -> Optional[str]:
    try:
        response = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            return trafilatura.extract(response.text)
    except Exception as e:  # noqa: BLE001
        print(f"Error fetching {url}: {e}")
    return None
