"""OpenAI client singleton — connection reuse, configurable timeouts, retry."""

import logging
import httpx

from openai import OpenAI

_client = None
_log = logging.getLogger("jarvis.client")


def get_client():
    global _client
    if _client is None:
        from ..config import AI_BASE_URL, AI_API_KEY, AI_TIMEOUT, AI_CONNECT_TIMEOUT

        # Reuse HTTP connections via a persistent httpx client
        http_client = httpx.Client(
            timeout=httpx.Timeout(
                connect=AI_CONNECT_TIMEOUT,
                read=AI_TIMEOUT,
                write=AI_TIMEOUT,
                pool=AI_TIMEOUT,
            ),
            follow_redirects=True,
        )
        _client = OpenAI(
            base_url=AI_BASE_URL,
            api_key=AI_API_KEY,
            http_client=http_client,
            max_retries=0,  # We handle retries ourselves
        )
        _log.info("OpenAI client created (base_url=%s)", AI_BASE_URL)
    return _client


def close_client():
    global _client
    if _client is not None:
        try:
            if _client._client is not None:
                _client._client.close()
        except Exception:
            pass
    _client = None


def check_connection() -> str | None:
    """Test connectivity to the AI server.

    Returns ``None`` on success, or an error message string on failure.
    """
    from ..config import AI_BASE_URL, AI_CONNECT_TIMEOUT
    try:
        base = AI_BASE_URL.rstrip("/v1").rstrip("/")
        resp = httpx.get(
            f"{base}/models",
            timeout=httpx.Timeout(connect=AI_CONNECT_TIMEOUT, read=10.0, write=10.0, pool=10.0),
        )
        resp.raise_for_status()
        return None
    except httpx.ConnectError:
        return (
            f"Cannot connect to {base}. "
            "Check that KoboldCpp is running and reachable at pop-os.local:5001."
        )
    except httpx.TimeoutException:
        return f"Connection to {base} timed out after {AI_CONNECT_TIMEOUT}s."
    except Exception as e:
        return f"Connection check failed: {e}"
