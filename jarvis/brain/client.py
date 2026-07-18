from openai import OpenAI

_client = None

def get_client():
    global _client
    if _client is None:
        from ..config import AI_BASE_URL, AI_API_KEY, AI_TIMEOUT
        _client = OpenAI(
            base_url=AI_BASE_URL,
            api_key=AI_API_KEY,
            timeout=AI_TIMEOUT,
        )
    return _client

def close_client():
    global _client
    _client = None
