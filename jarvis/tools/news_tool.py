"""News tool — fetches top headlines from NewsAPI (free tier)."""

from .base import Tool


_NEWS_SOURCES = {
    "general": "https://newsapi.org/v2/top-headlines?country=us&pageSize=5&apiKey=",
    "technology": "https://newsapi.org/v2/top-headlines?country=us&category=technology&pageSize=5&apiKey=",
    "ai": "https://newsapi.org/v2/everything?q=artificial+intelligence&pageSize=5&apiKey=",
    "sports": "https://newsapi.org/v2/top-headlines?country=us&category=sports&pageSize=5&apiKey=",
}


class NewsTool(Tool):
    """Fetch recent news headlines by topic."""

    def __init__(self):
        super().__init__(
            name="news",
            description="Fetch recent news headlines. Topics: general, technology, ai, sports, or any search topic.",
            category="Web",
            risk="safe",
        )

    def execute(self, topic: str = "general") -> dict:
        topic = topic.lower().strip()

        try:
            from ..config import AI_API_KEY
            api_key = AI_API_KEY

            if api_key and api_key != "local":
                url = _NEWS_SOURCES.get(topic, _NEWS_SOURCES["general"])
                url += api_key
            else:
                return self._fetch_rss(topic)

            import requests
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                return {"error": f"News API error: {data.get('message', 'unknown')}"}

            articles = data.get("articles", [])
            results = []
            for a in articles[:5]:
                results.append({
                    "title": a.get("title", ""),
                    "source": a.get("source", {}).get("name", ""),
                    "published": a.get("publishedAt", "")[:10],
                    "url": a.get("url", ""),
                })

            return {"topic": topic, "articles": results, "count": len(results)}

        except ImportError:
            return {"error": "requests not installed. Run: pip install requests"}
        except Exception as e:
            return {"error": f"News fetch failed: {e}"}

    def _fetch_rss(self, topic: str) -> dict:
        try:
            import requests
            from bs4 import BeautifulSoup

            rss_feeds = {
                "general": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
                "technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
                "sports": "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
                "ai": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            }

            feed_url = rss_feeds.get(topic, rss_feeds["general"])
            resp = requests.get(feed_url, timeout=15,
                                headers={"User-Agent": "JARVIS/1.4"})
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")[:5]
            results = []
            for item in items:
                title = item.find("title")
                link = item.find("link")
                pub_date = item.find("pubDate")
                results.append({
                    "title": title.text if title else "",
                    "source": "NY Times RSS",
                    "published": (pub_date.text[:10] if pub_date else ""),
                    "url": link.text if link else "",
                })

            return {"topic": topic, "articles": results, "count": len(results)}

        except Exception as e:
            return {"error": f"RSS news fallback failed: {e}"}
