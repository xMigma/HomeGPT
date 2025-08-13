# brave_provider.py
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional

import requests
from web_search import WebSearchProvider, fetch_full_text


class BraveProvider(WebSearchProvider):
    """Proveedor de búsqueda Brave (solo resultados WEB, sin noticias)."""

    BASE = "https://api.search.brave.com/res/v1"

    def __init__(
        self,
        config_path: str = "config.env",
        api_key: Optional[str] = None,
        freshness: str = "week",
        country: str = "es",
        lang: str = "es",
        timeout: int = 6,
        include_full_text: bool = True,
    ):
        load_dotenv(config_path)
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("Falta BRAVE_API_KEY en entorno o parámetro.")
        self.freshness = freshness
        self.country = country
        self.lang = lang
        self.timeout = timeout
        self.include_full_text = include_full_text
        self.session = requests.Session()
        self.session.headers.update({"X-Subscription-Token": self.api_key})

    def search(self, query: str, max_results: int) -> List[Dict]:
        """Realiza búsqueda web y retorna resultados deduplicados.

        Args:
            query: texto a buscar
            max_results: límite de resultados a devolver
        """
        items = self._search_web(query, max_results)
        deduped = self._dedupe(items, max_results)

        if self.include_full_text:
            for it in deduped:
                it["full_text"] = fetch_full_text(it["href"]) or ""
        else:
            for it in deduped:
                it["full_text"] = ""

        return deduped

    def _dedupe(self, items: List[Dict], limit: int) -> List[Dict]:
        """Deduplica por URL y aplica límite."""
        seen, out = set(), []
        for it in items:
            href = it.get("href", "")
            if href and href not in seen:
                seen.add(href)
                out.append(it)
            if len(out) >= limit:
                break
        return out

    def _search_web(self, query: str, count: int) -> List[Dict]:
        if count <= 0:
            return []
        try:
            r = self.session.get(
                f"{self.BASE}/web/search",
                params={
                    "q": query,
                    "count": count,
                    "freshness": self.freshness,
                    "country": self.country,
                    "lang": self.lang,
                    "spellcheck": 1,
                    "safesearch": "moderate",
                },
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logging.warning("Brave web search error: %s", e)
            return []

        out = []
        for it in data.get("web", {}).get("results", []):
            out.append(
                {
                    "title": it.get("title", "") or "",
                    "href": it.get("url", "") or "",
                    "snippet": it.get("description", "") or "",
                }
            )
        return out
