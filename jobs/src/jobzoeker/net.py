"""Gedeelde HTTP-client met retries en nette defaults."""

from __future__ import annotations

import time

import httpx
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept-Language": "nl-BE,nl;q=0.9,en;q=0.8"}

_client: httpx.Client | None = None


def client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True)
    return _client


def request(method: str, url: str, retries: int = 2, **kw) -> httpx.Response:
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            r = client().request(method, url, **kw)
            if r.status_code in (429, 502, 503, 504) and attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            r.raise_for_status()
            return r
        except httpx.HTTPError as e:
            last = e
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
    assert last is not None
    raise last


def get(url: str, **kw) -> httpx.Response:
    return request("GET", url, **kw)


def post(url: str, **kw) -> httpx.Response:
    return request("POST", url, **kw)


def soup(url: str, **kw) -> BeautifulSoup:
    return BeautifulSoup(get(url, **kw).text, "lxml")


def text_of(el) -> str:
    if el is None:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())
