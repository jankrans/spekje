"""Generieke jobsites met zoektermen: LinkedIn (guest), StepStone."""

from __future__ import annotations

import re
import time
from datetime import timedelta
from urllib.parse import quote

from .. import dates, net
from . import adapter


def _ago(txt: str) -> str | None:
    """'3 dagen geleden' -> ISO-datum. Alleen dagen/weken/uren, anders None."""
    t = (txt or "").lower()
    if m := re.search(r"(\d+)\s*(uur|uren|minuten|minuut)", t):
        return dates.today().isoformat()
    if m := re.search(r"(\d+)\s*(dag|dagen)", t):
        return (dates.today() - timedelta(days=int(m[1]))).isoformat()
    if m := re.search(r"(\d+)\s*(week|weken)", t):
        return (dates.today() - timedelta(weeks=int(m[1]))).isoformat()
    return None


@adapter("linkedin")
def linkedin(cfg: dict, profiel: dict) -> list[dict]:
    termen = cfg.get("zoektermen") or profiel.get("zoektermen", {}).get("linkedin", [])
    loc = cfg.get("location", "Belgium")
    out: dict[str, dict] = {}
    for term in termen:
        for start in range(0, cfg.get("max_results", 50), 25):
            url = (
                "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={quote(term)}&location={quote(loc)}&f_TPR=r2592000&start={start}"
            )
            try:
                s = net.soup(url, retries=1)
            except Exception:
                break
            cards = s.select("li")
            if not cards:
                break
            for li in cards:
                a = li.select_one("a.base-card__full-link")
                if not a:
                    continue
                href = a["href"].split("?")[0]
                t = li.select_one("time")
                out[href] = {
                    "titel": net.text_of(li.select_one(".base-search-card__title")),
                    "organisatie": net.text_of(li.select_one(".base-search-card__subtitle")),
                    "url": href,
                    "locatie": net.text_of(li.select_one(".job-search-card__location")),
                    "publicatiedatum": t.get("datetime") if t else None,
                }
            time.sleep(1.5)
            if len(cards) < 25:
                break
    return list(out.values())


@adapter("stepstone")
def stepstone(cfg: dict, profiel: dict) -> list[dict]:
    termen = cfg.get("zoektermen") or profiel.get("zoektermen", {}).get("stepstone", [])
    out: dict[str, dict] = {}
    for term in termen:
        slug = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
        try:
            s = net.soup(f"https://www.stepstone.be/vacatures/{slug}")
        except Exception:
            continue
        for it in s.select("[data-at=job-item]"):
            a = it.select_one("a[data-at=job-item-title]")
            if not a:
                continue
            href = a["href"].split("?")[0]
            out[href] = {
                "titel": net.text_of(a),
                "organisatie": net.text_of(it.select_one("[data-at=job-item-company-name]")),
                "url": href,
                "locatie": net.text_of(it.select_one("[data-at=job-item-location]")).title() or None,
                "publicatiedatum": _ago(net.text_of(it.select_one("[data-at=job-item-timeago]"))),
            }
        time.sleep(1)
    return list(out.values())
