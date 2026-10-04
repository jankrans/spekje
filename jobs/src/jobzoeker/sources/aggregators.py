"""Sector-aggregators: cultuurjobs, publiq, podiumkunsten.be, mediarte, cult!, VI.BE, RSS-feeds."""

from __future__ import annotations

import re
from urllib.parse import urljoin

import feedparser
from bs4 import BeautifulSoup

from .. import dates, net
from . import adapter

CJ_CATS = {
    3: "erfgoed",
    4: "artistiek",
    5: "communicatie en publiek",
    6: "beheer en administratie",
    7: "productie en logistiek",
    9: "onderwijs",
    11: "verkoop",
    12: "beleid",
    13: "programmatie",
}


@adapter("cultuurjobs")
def cultuurjobs(cfg: dict, profiel: dict) -> list[dict]:
    # Lijst + meta (plaats/regime/deadline) uit de homepage, inhoud + publicatiedatum uit de WP REST API.
    s = net.soup("https://www.cultuurjobs.be/")
    out: dict[str, dict] = {}
    for li in s.select("li.item"):
        a = li.select_one("a[href]")
        if not a:
            continue
        comp = li.select_one("span.company")
        for n in comp.select(".nuovo3") if comp else []:
            n.decompose()
        meta = net.text_of(li.select_one("span.metadata"))
        parts = [p.strip() for p in meta.split(" - ")]
        deadline = None
        if m := re.search(r"Deadline:\s*(\S+)", meta):
            deadline = dates.iso(dates.parse_one(m[1]))
        url = a["href"].split("?")[0]
        out[url] = {
            "titel": net.text_of(li.select_one("span.cultuurjob")) or a.get("title", ""),
            "organisatie": net.text_of(comp),
            "url": url,
            "locatie": parts[0] if parts else None,
            "regime_hint": parts[1] if len(parts) > 1 else None,
            "contract_hint": parts[1] if len(parts) > 1 else None,
            "deadline": deadline,
        }
    try:
        posts = net.get(
            "https://www.cultuurjobs.be/wp-json/wp/v2/posts",
            params={"per_page": 100, "_fields": "id,date,link,title,content,categories"},
        ).json()
    except Exception:
        posts = []
    for p in posts:
        url = p["link"].split("?")[0]
        item = out.setdefault(
            url, {"titel": BeautifulSoup(p["title"]["rendered"], "lxml").get_text(), "url": url}
        )
        item["publicatiedatum"] = p["date"][:10]
        item["beschrijving"] = net.text_of(BeautifulSoup(p["content"]["rendered"], "lxml"))
        item["categorie_hint"] = ", ".join(
            CJ_CATS.get(c, "") for c in p.get("categories", []) if c in CJ_CATS
        )
    return list(out.values())


@adapter("publiq")
def publiq(cfg: dict, profiel: dict) -> list[dict]:
    base = "https://www.publiq.be/nl/vacaturebank"
    out = []
    page = 1
    while page <= cfg.get("max_pages", 30):
        url = base if page == 1 else f"{base}/p{page}"
        s = net.soup(url)
        cards = s.select(".card")
        if not cards:
            break
        for c in cards:
            a = c.select_one("h4.card__title a")
            if not a:
                continue
            full = net.text_of(a)
            titel, org = (full.rsplit(" - ", 1) + [""])[:2] if " - " in full else (full, "")
            meta = {}
            for mi in c.select(".meta__item"):
                divs = mi.find_all("div", recursive=False)
                if len(divs) >= 2:
                    meta[net.text_of(divs[0]).lower()] = net.text_of(divs[1])
            out.append(
                {
                    "titel": titel.strip(),
                    "organisatie": org.strip(),
                    "url": a["href"],
                    "locatie": meta.get("regio"),
                    "deadline": dates.iso(dates.parse_one(meta.get("reageren voor"))),
                    "categorie_hint": meta.get("categorie"),
                }
            )
        if not s.select_one(f'a[href$="/vacaturebank/p{page + 1}"]'):
            break
        page += 1
    return out


@adapter("podiumkunsten")
def podiumkunsten(cfg: dict, profiel: dict) -> list[dict]:
    out = []
    for page in range(cfg.get("max_pages", 15)):
        s = net.soup("https://www.podiumkunsten.be/vacatures", params={"page": page})
        cards = s.select("article.p-card")
        if not cards:
            break
        for c in cards:
            a = c.select_one("a.js-card-action")
            if not a:
                continue
            full = net.text_of(c.select_one(".p-card__content__title"))
            titel, _, org = full.partition(" bij ")
            infos = [net.text_of(x) for x in c.select(".p-card__content__details__info span")]
            out.append(
                {
                    "titel": titel.strip(),
                    "organisatie": org.strip(),
                    "url": urljoin("https://www.podiumkunsten.be", a["href"]),
                    "locatie": infos[0] if infos else None,
                    "contract_hint": infos[1] if len(infos) > 1 else None,
                    "deadline": dates.iso(
                        dates.parse_one(net.text_of(c.select_one(".p-card__content__text")))
                    ),
                    "categorie_hint": ", ".join(net.text_of(li) for li in c.select(".item-list li")),
                }
            )
        if len(cards) < 9:
            break
    return out


@adapter("mediarte")
def mediarte(cfg: dict, profiel: dict) -> list[dict]:
    out = []
    for page in range(1, cfg.get("max_pages", 10) + 1):
        url = "https://www.mediarte.be/nl/vacatures" + (f"/p{page}" if page > 1 else "")
        s = net.soup(url)
        links = s.select("h3 > a.link--extended")
        if not links:
            break
        for a in links:
            h3 = a.parent
            org = net.text_of(h3.select_one("span"))
            org = re.sub(r"\s+zoekt$", "", org, flags=re.I)
            box = h3.parent.parent if h3.parent else None
            spans = [net.text_of(x) for x in box.select("span.pr-2")] if box else []
            out.append(
                {
                    "titel": net.text_of(a),
                    "organisatie": org,
                    "url": a["href"],
                    "locatie": spans[0] if spans else None,
                    "categorie_hint": spans[1] if len(spans) > 1 else None,
                    "regime_hint": spans[2] if len(spans) > 2 else None,
                }
            )
        if not s.select_one(f'a[href$="/vacatures/p{page + 1}"]'):
            break
    return out


@adapter("cult")
def cult(cfg: dict, profiel: dict) -> list[dict]:
    s = net.soup("https://www.cult.be/vacatures")
    out = []
    for a in s.select("div.card.card--jobs a[href]"):
        txt = net.text_of(a)
        m = re.search(r"reageer tot en met (.+)$", txt)
        titel = txt[: m.start()].strip() if m else txt
        out.append(
            {
                "titel": titel,
                "url": urljoin("https://www.cult.be", a["href"]),
                "deadline": dates.iso(dates.parse_one(m[1])) if m else None,
            }
        )
    return out


@adapter("vibe")
def vibe(cfg: dict, profiel: dict) -> list[dict]:
    s = net.soup("https://vi.be/vacatures")
    out = []
    section = None
    for el in s.select("h3, li"):
        if el.name == "h3":
            section = net.text_of(el)
            continue
        a = next((x for x in el.select("a[href]") if net.text_of(x).lower() == "meer info"), None)
        if not a:
            continue
        em = net.text_of(el.select_one("em"))
        head = net.text_of(el).replace("Meer info", "")
        head = head.replace(em, "").strip(" —-")
        bits = re.split(r"\s+[—–]\s+", head, maxsplit=1)
        titel = re.sub(r"\s+", " ", bits[0]).strip()
        org = bits[1].strip() if len(bits) > 1 else ""
        titel = re.sub(r"^(\w) (\w)", r"\1\2", titel)  # "m edewerker" -> "medewerker"
        out.append(
            {
                "titel": titel,
                "organisatie": org,
                "url": a["href"].split("?mc_")[0],
                "deadline": dates.iso(dates.parse_one(em)),
                "contract_hint": "stage" if section and "stage" in section.lower() else None,
            }
        )
    return out


@adapter("rss")
def rss(cfg: dict, profiel: dict) -> list[dict]:
    r = net.get(cfg["url"])
    feed = feedparser.parse(r.content)
    out = []
    for e in feed.entries:
        titel = e.get("title", "").strip()
        org, loc = "", None
        if cfg.get("title_split"):  # bv. "Titel - (ORG), Plaats"
            if m := re.match(r"^(.*?)\s*-\s*\((.*?)\),\s*(.*)$", titel):
                titel, org, loc = m[1], m[2], m[3]
        summary = BeautifulSoup(e.get("summary", ""), "lxml").get_text(" ", strip=True)
        pub = None
        if e.get("published_parsed"):
            pub = "%04d-%02d-%02d" % tuple(e.published_parsed[:3])
        out.append(
            {
                "titel": titel,
                "organisatie": org,
                "url": e.get("link"),
                "locatie": loc,
                "publicatiedatum": pub,
                "beschrijving": summary[:4000],
                "categorie_hint": ", ".join(t.get("term", "") for t in e.get("tags", [])),
            }
        )
    return out
