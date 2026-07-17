from tools.base import Tool


class WebSearchTool(Tool):
    def __init__(self):
        super().__init__("web_search", "Search the web using DuckDuckGo. Returns title, snippet, URL.")

    def execute(self, query: str, max_results: int = 5) -> dict:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = [
                    {"title": r.get("title", ""), "snippet": r.get("body", ""), "url": r.get("href", "")}
                    for r in ddgs.text(query, max_results=max_results)
                ]
            return {"query": query, "results": results, "count": len(results)}
        except ImportError:
            return {"error": "duckduckgo_search not installed. Run: pip install duckduckgo_search"}
        except Exception as e:
            return {"error": f"Search failed: {e}"}


class WebFetchTool(Tool):
    def __init__(self):
        super().__init__("web_fetch", "Fetch the text content of a URL.")

    def execute(self, url: str) -> dict:
        try:
            import requests
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; JARVIS/1.1)"
            })
            resp.raise_for_status()
            text = resp.text
            ct = resp.headers.get("content-type", "")
            if "html" in ct or "text" in ct:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(text, "html.parser")
                    for tag in soup(["script", "style"]):
                        tag.decompose()
                    text = soup.get_text(separator="\n", strip=True)
                except ImportError:
                    pass
            max_len = 5000
            return {
                "url": url,
                "content": text[:max_len],
                "truncated": len(text) > max_len,
            }
        except ImportError:
            return {"error": "requests not installed. Run: pip install requests"}
        except Exception as e:
            return {"error": f"Failed to fetch {url}: {e}"}
