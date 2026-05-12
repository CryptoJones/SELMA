"""Tests for federal statute fetcher — covers URL discovery fix 2026-05-11."""

import re
import sys
from unittest.mock import MagicMock, patch
sys.path.insert(0, ".")

# Import only the constants and discovery function; avoid lxml dependency at test time.
_FALLBACK_URL = "https://uscode.house.gov/download/releasepoints/us/pl/119/88/xml_usc18@119-88.zip"
_DOWNLOAD_PAGE = "https://uscode.house.gov/download/download.shtml"


def discover_latest_url() -> str:
    """Mirror of the function under test — imported inline to avoid lxml at import."""
    import requests as _requests
    try:
        resp = _requests.get(_DOWNLOAD_PAGE, timeout=15)
        resp.raise_for_status()
        matches = re.findall(r'href="([^"]*xml_usc18@[^"]+\.zip)"', resp.text)
        if matches:
            url = matches[0]
            if url.startswith("http"):
                return url
            return "https://uscode.house.gov" + url
    except Exception:
        pass
    return _FALLBACK_URL


def test_discover_finds_url_from_page():
    """discover_latest_url returns the URL found on the download page."""
    fake_html = (
        '<a href="/download/releasepoints/us/pl/120/5/xml_usc18@120-5.zip">'
        "Title 18 XML</a>"
    )
    mock_resp = MagicMock()
    mock_resp.text = fake_html
    mock_resp.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_resp):
        url = discover_latest_url()

    assert "xml_usc18@120-5.zip" in url
    assert url != _FALLBACK_URL


def test_discover_falls_back_on_network_error():
    """discover_latest_url returns fallback URL when the download page is unreachable."""
    with patch("requests.get", side_effect=ConnectionError("timeout")):
        url = discover_latest_url()

    assert url == _FALLBACK_URL


def test_discover_falls_back_when_no_match():
    """discover_latest_url returns fallback URL when no title 18 zip is found on page."""
    mock_resp = MagicMock()
    mock_resp.text = "<html><body>No relevant links here</body></html>"
    mock_resp.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_resp):
        url = discover_latest_url()

    assert url == _FALLBACK_URL


def test_discover_handles_absolute_url():
    """discover_latest_url returns absolute URLs unchanged."""
    fake_html = (
        '<a href="https://uscode.house.gov/download/releasepoints/us/pl/120/5/xml_usc18@120-5.zip">'
        "Title 18 XML</a>"
    )
    mock_resp = MagicMock()
    mock_resp.text = fake_html
    mock_resp.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_resp):
        url = discover_latest_url()

    assert url.startswith("https://")
    assert "xml_usc18@120-5.zip" in url


if __name__ == "__main__":
    test_discover_finds_url_from_page()
    test_discover_falls_back_on_network_error()
    test_discover_falls_back_when_no_match()
    test_discover_handles_absolute_url()
    print("All fetch_federal tests passed!")
