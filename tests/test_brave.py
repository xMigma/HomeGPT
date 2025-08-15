from web.brave import BraveProvider


def test_dedupe_and_limit(monkeypatch):
    provider = BraveProvider(api_key="dummy", include_full_text=False)

    # monkeypatch the network call to return duplicates
    def fake_search_web(query: str, count: int):
        return [
            {"title": "A", "href": "http://x", "snippet": "s"},
            {"title": "A2", "href": "http://x", "snippet": "s2"},  # dup url
            {"title": "B", "href": "http://y", "snippet": "t"},
        ]

    monkeypatch.setattr(provider, "_search_web", fake_search_web)

    res = provider.search("hola", max_results=2)
    assert len(res) == 2
    assert {r["href"] for r in res} == {"http://x", "http://y"}


def test_search_no_results(monkeypatch):
    provider = BraveProvider(api_key="dummy", include_full_text=False)

    monkeypatch.setattr(provider, "_search_web", lambda q, c: [])
    res = provider.search("hola", max_results=3)
    assert res == []
