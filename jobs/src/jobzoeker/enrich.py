"""Detailpagina's ophalen voor relevante vacatures: beschrijving + datums (deadline, start, einde contract)."""

from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup

from . import dates, net
from .store import Store


def _jsonld_jobposting(s: BeautifulSoup) -> dict | None:
    for tag in s.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = (
            data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        )
        for it in items:
            if isinstance(it, dict) and it.get("@type") in ("JobPosting", ["JobPosting"]):
                return it
    return None


def _main_text(s: BeautifulSoup) -> str:
    for bad in s.select("script, style, nav, header, footer, form, noscript, aside"):
        bad.decompose()
    for sel in ["[itemprop=description]", "article", "main", ".content", "#content", "body"]:
        el = s.select_one(sel)
        if el and len(el.get_text(strip=True)) > 200:
            return net.text_of(el)
    return net.text_of(s)


def enrich_job(job: dict) -> bool:
    url = job["url"]
    if url.lower().endswith(".pdf") or job.get("pagewatch"):
        return False
    try:
        r = net.get(url, retries=1)
    except Exception as e:
        job["enrich_fout"] = str(e)[:200]
        return False
    if "pdf" in r.headers.get("content-type", ""):
        return False
    s = BeautifulSoup(r.text, "lxml")
    jp = _jsonld_jobposting(s)
    if jp:
        if jp.get("validThrough"):
            Store.set_datum(
                job, "deadline", str(jp["validThrough"])[:10], "detail-jsonld", "JSON-LD validThrough"
            )
        if jp.get("datePosted"):
            Store.set_datum(
                job, "publicatiedatum", str(jp["datePosted"])[:10], "detail-jsonld", "JSON-LD datePosted"
            )
        et = jp.get("employmentType")
        if et and not job.get("contract_hint"):
            job["contract_hint"] = et if isinstance(et, str) else ", ".join(et)
        if jp.get("description") and len(job.get("beschrijving") or "") < 300:
            job["beschrijving"] = BeautifulSoup(jp["description"], "lxml").get_text(" ", strip=True)[:8000]
    text = _main_text(s)
    if len(text) > len(job.get("beschrijving") or ""):
        job["beschrijving"] = text[:8000]
    extract_dates(job)
    job["verrijkt"] = True
    return True


def extract_dates(job: dict) -> None:
    text = job.get("beschrijving") or ""
    pub = (job["datums"].get("publicatiedatum") or {}).get("waarde")
    ref = dates.parse_one(pub) if pub else None
    for veld, cues in (
        ("deadline", dates.DEADLINE_CUES),
        ("startdatum", dates.START_CUES),
        ("einddatum", dates.END_CUES),
    ):
        d, bewijs = dates.find_cued(text, cues, ref)
        if (
            d
            and veld == "einddatum"
            and "deadline" in job["datums"]
            and job["datums"]["deadline"]["waarde"] == d.isoformat()
        ):
            continue  # "tot en met <deadline>" is geen contracteinde
        if d:
            Store.set_datum(job, veld, d.isoformat(), "detail-tekst", bewijs)
    # Expliciete "onmiddellijk" / "zo snel mogelijk" als start
    if "startdatum" not in job["datums"] and re.search(
        r"(onmiddellijk|zo snel mogelijk|asap|dès que possible)", text.lower()
    ):
        job["datums"]["startdatum"] = {
            "waarde": None,
            "tekst": "zo snel mogelijk",
            "bron": "detail-tekst",
            "bewijs": None,
        }
