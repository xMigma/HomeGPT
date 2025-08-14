from __future__ import annotations

from typing import List, Dict

from ddgs import DDGS

from .base import WebSearchProvider, fetch_full_text


class DuckDuckGoProvider(WebSearchProvider):
    """Implementación de búsqueda usando DuckDuckGo."""

    def __init__(self, region: str = "es-es"):
        self.region = region

    def _process_results(self, results, url_key):
        """Procesa una lista de resultados y extrae el texto completo de cada URL."""
        processed: List[Dict] = []
        for r in results:
            full_text = fetch_full_text(r[url_key])
            processed.append(
                {
                    "title": r["title"],
                    "href": r[url_key],
                    "snippet": r["body"],
                    "full_text": full_text,
                }
            )
        return processed

    def search(self, query: str, max_results: int = 6) -> list:
        """Realiza búsqueda en DuckDuckGo combinando resultados de texto y noticias."""
        with DDGS() as ddgs:
            text_results = ddgs.text(
                query, max_results=max_results // 2, region=self.region
            )
            news_results = ddgs.news(
                query, max_results=max_results // 2, region=self.region
            )

            processed_text = self._process_results(text_results, url_key="href")
            processed_news = self._process_results(news_results, url_key="url")

            return processed_text + processed_news
