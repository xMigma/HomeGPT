from ddgs import DDGS
import requests
import trafilatura


def _fetch_full_text(url):
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            return trafilatura.extract(response.text)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None


def _web_search_full(query, max_results=4):
    with DDGS() as ddgs:
        results = ddgs.text(
            query, max_results=max_results // 2, region="es-ES", safesearch="moderate"
        )
        text_results = []
        for r in results:
            full_text = _fetch_full_text(r["href"])
            text_results.append(
                {
                    "title": r["title"],
                    "href": r["href"],
                    "snippet": r["body"],
                    "full_text": full_text,
                }
            )

        # Noticias
        news = ddgs.news(
            query, max_results=max_results // 2, region="es-ES", safesearch="moderate"
        )
        news_results = []
        for r in news:
            full_text = _fetch_full_text(r["url"])
            news_results.append(
                {
                    "title": r["title"],
                    "href": r["url"],
                    "snippet": r["body"],
                    "full_text": full_text,
                }
            )

        return text_results + news_results

def make_web_search(query, max_results=4):
    result = ""

    for r in _web_search_full("Cuando juega el real madrid"):
        result += f"{r['title']} - {r['href']}\n"
        result += f"Noticia:\n{(r['full_text'] or 'No se pudo extraer')[:1000]}\n\n"

    return result
