from web.base import WebSearchProvider, make_web_search


class DummyProvider(WebSearchProvider):
    def search(self, query: str, max_results: int) -> list:
        return [
            {"title": "T1", "href": "http://a", "snippet": "s1", "full_text": "F1"},
            {"title": "T2", "href": "http://b", "snippet": "s2", "full_text": "F2"},
        ][:max_results]


def test_make_web_search_formats_results():
    out = make_web_search("hola", 1, DummyProvider())
    assert "T1 - http://a" in out
    assert "Noticia/artículo" in out
