"""Organisaties met eigen jobpagina: Recruitee-API, Tomorrowland, Kursaal, Cinergie, en generieke pagina-watch."""

from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import urljoin

from .. import DATA, dates, net
from . import adapter


@adapter("recruitee")
def recruitee(cfg: dict, profiel: dict) -> list[dict]:
    d = net.get(f"https://{cfg['tenant']}.recruitee.com/api/offers/").json()
    out = []
    for o in d.get("offers", []):
        out.append(
            {
                "titel": o.get("title", ""),
                "organisatie": cfg.get("organisatie") or o.get("company_name", ""),
                "url": o.get("careers_url"),
                "locatie": o.get("city"),
                "publicatiedatum": (o.get("created_at") or "")[:10] or None,
                "contract_hint": o.get("employment_type_code"),
                "beschrijving": re.sub(r"<[^>]+>", " ", o.get("description") or "")[:4000],
                "thuiswerk_hint": "hybride" if o.get("hybrid") else ("ja" if o.get("remote") else None),
            }
        )
    return out


@adapter("tomorrowland")
def tomorrowland(cfg: dict, profiel: dict) -> list[dict]:
    out: dict[str, dict] = {}
    for path in ["", "event-jobs", "Internship", "freelance"]:
        try:
            s = net.soup(f"https://jobs.tomorrowland.com/{path}")
        except Exception:
            continue
        for a in s.select('a[href*="skeeled.com/offer"]'):
            href = a["href"].split("?")[0]
            tags = [net.text_of(t) for t in a.select(".collection-item__tag")]
            out[href] = {
                "titel": net.text_of(a.select_one(".collection-item__title")),
                "organisatie": "Tomorrowland",
                "url": href,
                "locatie": tags[0] if tags else None,
                "regime_hint": net.text_of(a.select_one(".collection-item__type")),
                "categorie_hint": tags[1] if len(tags) > 1 else None,
                "contract_hint": "stage"
                if path == "Internship"
                else ("freelance" if path == "freelance" else None),
            }
    return list(out.values())


@adapter("links")
def links(cfg: dict, profiel: dict) -> list[dict]:
    """Generiek: alle links die matchen met een selector op een jobpagina."""
    s = net.soup(cfg["url"])
    out: dict[str, dict] = {}
    for a in s.select(cfg["selector"]):
        href = urljoin(cfg["url"], a.get("href", ""))
        t = net.text_of(a.select_one(cfg["title_selector"]) if cfg.get("title_selector") else a)
        for strip in cfg.get("strip", []):
            t = re.sub(strip, "", t, flags=re.I).strip()
        if not t or href in out:
            continue
        out[href] = {
            "titel": t,
            "organisatie": cfg.get("organisatie", ""),
            "url": href,
            "locatie": cfg.get("locatie"),
        }
    return list(out.values())


@adapter("cinergie")
def cinergie(cfg: dict, profiel: dict) -> list[dict]:
    s = net.soup("https://www.cinergie.be/annonces", params={"isOffer": 1})
    out = []
    for art in s.select("article.card-job"):
        a = art.select_one('a[href^="/annonce/"]')
        if not a:
            continue
        typ = " ".join(net.text_of(x) for x in art.select("nav a"))
        if "Demande" in typ:
            continue
        out.append(
            {
                "titel": net.text_of(a.select_one("h5")),
                "url": urljoin("https://www.cinergie.be", a["href"]),
                "publicatiedatum": dates.iso(
                    dates.parse_one(net.text_of(art.select_one("small.date-casting")))
                ),
                "contract_hint": "betaald" if "Rémunéré" in typ else None,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Pagina-watch: jobpagina's zonder vaste structuur. We houden de koppen/links van de hoofdinhoud bij.
# Per wijziging (en bij de eerste keer) komt er EEN item "Jobpagina X: te checken" met de nieuwe regels.
# Claude beoordeelt dat item in de run: echte vacatures toevoegen met `jobzoeker add`, item als ruis markeren.

WATCH_FILE = DATA / "pagewatch.json"
JOBWORD = re.compile(
    r"(medewerk|co[oö]rdinat|productie|producer|verantwoordelijk|stage\b|stagiair|techni|vacature|"
    r"m/v/x|v/m/x|assistent|manager|leider|zakelijk|publieks|onthaal|freelance|hospitality|regie)",
    re.I,
)


def _main_lines(html_soup, selector: str | None) -> list[str]:
    root = html_soup.select_one(selector) if selector else None
    root = root or html_soup.select_one("main") or html_soup.body or html_soup
    for bad in root.select("script, style, nav, header, footer, form"):
        bad.decompose()
    lines = []
    for el in root.select("h1, h2, h3, h4, h5, a, strong, li > p:first-child"):
        t = net.text_of(el)
        if 6 <= len(t) <= 110 and not re.match(r"^(je |jij |wij |we |u |ben je|heb je|wil je)", t, re.I):
            lines.append(t)
    return list(dict.fromkeys(lines))


@adapter("pagewatch")
def pagewatch(cfg: dict, profiel: dict) -> list[dict]:
    state = json.loads(WATCH_FILE.read_text()) if WATCH_FILE.exists() else {}
    s = net.soup(cfg["url"])
    lines = _main_lines(s, cfg.get("selector"))
    digest = hashlib.sha1("\n".join(lines).encode()).hexdigest()[:10]
    prev = state.get(cfg["url"])
    known = set(prev.get("lines", [])) if prev else set()
    cand = [ln for ln in lines if ln not in known and JOBWORD.search(ln)]
    out = []
    if (prev is None or digest != prev.get("hash")) and cand:
        org = cfg.get("organisatie", "")
        out.append(
            {
                "titel": f"Jobpagina {org}: {len(cand)} vermelding(en) te checken",
                "organisatie": org,
                "url": cfg["url"],
                "locatie": cfg.get("locatie"),
                "pagewatch": True,
                "pagewatch_hash": digest,
                "beschrijving": "Nieuwe regels op de jobpagina:\n" + "\n".join(f"- {c}" for c in cand[:40]),
            }
        )
    state[cfg["url"]] = {"hash": digest, "lines": lines, "checked": dates.today().isoformat()}
    WATCH_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=1))
    return out
