"""Overheid en publieke omroep: VDAB, jobsolutions, Werken voor Vlaanderen, steden, VRT."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from .. import dates, net
from . import adapter

VDAB_KEY = "b277002f-e1fa-4fc5-868a-fdab633c3851"  # publieke key uit de VDAB-webapp


@adapter("vdab")
def vdab(cfg: dict, profiel: dict) -> list[dict]:
    termen = cfg.get("zoektermen") or profiel.get("zoektermen", {}).get("vdab", [])
    headers = {"Content-Type": "application/json", "vej-key-monitor": VDAB_KEY}
    out: dict[int, dict] = {}
    for term in termen:
        for page in range(cfg.get("max_pages", 2)):
            body = {"criteria": {"trefwoord": f'"{term}"'}, "pageable": {"page": page, "size": 50}}
            d = net.post(
                "https://www.vdab.be/rest/vindeenjob/v4/vacatureLight/zoek", json=body, headers=headers
            ).json()
            res = d.get("resultaten", [])
            for v in res:
                vid = v["id"]["id"]
                if v.get("gesloten"):
                    continue
                f = v.get("vacaturefunctie", {})
                out[vid] = {
                    "titel": f.get("naam", ""),
                    "organisatie": v.get("vacatureBedrijfsnaam") or "",
                    "url": f"https://www.vdab.be/vindeenjob/vacatures/{vid}",
                    "locatie": (v.get("tewerkstellingsLocatieRegioOfAdres") or "").title() or None,
                    "publicatiedatum": (v.get("eerstePublicatieDatum") or "")[:10] or None,
                    "contract_hint": f.get("arbeidscircuitLijn"),
                    "regime_hint": ", ".join(v.get("tijdsregeling") or []),
                    "categorie_hint": (v.get("leverancier") or {}).get("type"),
                }
            if len(res) < 50:
                break
    return list(out.values())


@adapter("jobsolutions")
def jobsolutions(cfg: dict, profiel: dict) -> list[dict]:
    # Server-side filters werken niet: alles ophalen, filteren gebeurt later in de pipeline.
    out = []
    for page in range(1, cfg.get("max_pages", 40) + 1):
        s = net.soup("https://www.jobsolutions.be/jobs", params={"page": page})
        cards = s.select("a.card[href^='/jobs/']")
        if not cards:
            break
        for a in cards:
            p = a.select_one("p")
            lines = [x.strip() for x in p.get_text("\n", strip=True).split("\n")] if p else []
            org, loc = "", None
            if lines:
                org, _, loc = lines[0].rpartition(" - ")
                org = org or lines[0]
            rng = " ".join(lines[1:])
            ds = re.findall(r"\d{2}/\d{2}/\d{4}", rng)
            out.append(
                {
                    "titel": net.text_of(a.select_one("h3")),
                    "organisatie": org.strip(),
                    "url": urljoin("https://www.jobsolutions.be", a["href"]),
                    "locatie": (loc or "").strip() or None,
                    "publicatiedatum": dates.iso(dates.parse_one(ds[0])) if ds else None,
                    "deadline": dates.iso(dates.parse_one(ds[1])) if len(ds) > 1 else None,
                }
            )
        if not s.select_one(f'a[href="/jobs?page={page + 1}"]'):
            break
    return out


@adapter("werkenvoorvlaanderen")
def werkenvoorvlaanderen(cfg: dict, profiel: dict) -> list[dict]:
    out = []
    offset = 0
    while True:
        body = {
            "page": {"offset": offset, "limit": 100},
            "filter": {
                "contentType": {"IN": ["Job"]},
                "visibility": {"hub": "cc0f4502-9afd-42cf-b71f-31e43937d855"},
                "collectionFilters": {
                    "contentSubtypeData__sources": {"IN": ["VO"]},
                    "contentSubtypeData__internal": {"EQUAL": False},
                },
            },
            "orderBy": {"publicationDate": "DESC"},
            "resolverContext": {"language": "nl"},
        }
        d = net.post("https://www.vlaanderen.be/api/overview-search", json=body).json()
        for it in d.get("items", []):
            locs = [x.get("address", {}).get("city") for x in it.get("embeddedLocations") or []]
            vt = it.get("validThroughDate")
            deadline = datetime.fromtimestamp(int(vt), tz=timezone.utc).date().isoformat() if vt else None
            out.append(
                {
                    "titel": it.get("displayTitle", ""),
                    "organisatie": it.get("hiringOrganization", ""),
                    "url": "https://www.vlaanderen.be" + it.get("link", ""),
                    "locatie": ", ".join(x for x in locs if x) or None,
                    "deadline": deadline,
                    "categorie_hint": it.get("domain"),
                    "beschrijving": re.sub(r"<[^>]+>", " ", (it.get("description") or {}).get("raw") or ""),
                    "niveau": (it.get("degreeLevel") or {}).get("name"),
                }
            )
        if d.get("isLastPage", True) or not d.get("items"):
            break
        offset += 100
    return out


@adapter("stad_gent")
def stad_gent(cfg: dict, profiel: dict) -> list[dict]:
    seen = {}
    for page in range(cfg.get("max_pages", 5)):
        s = net.soup("https://jobs.gent.be/", params={"page": page})
        new = 0
        for a in s.select('a[href^="/vacature/"]'):
            url = urljoin("https://jobs.gent.be", a["href"])
            t = net.text_of(a)
            if t.lower().startswith("lees meer") or url in seen:
                continue
            seen[url] = {"titel": t, "organisatie": "Stad Gent", "url": url, "locatie": "Gent"}
            new += 1
        if not new:
            break
    return list(seen.values())


@adapter("stad_oostende")
def stad_oostende(cfg: dict, profiel: dict) -> list[dict]:
    s = net.soup("https://jobs.oostende.be/vacatures")
    out = []
    for art in s.select("article.article--vacature"):
        a = art.select_one("a[href]")
        if not a:
            continue
        txt = net.text_of(art)
        titel = net.text_of(art.select_one("h2, h3")) or txt.split(" Type Contract")[0]
        contract = re.search(r"Type Contract (.+?) Categorie", txt)
        out.append(
            {
                "titel": titel,
                "organisatie": "Stad Oostende",
                "url": urljoin("https://jobs.oostende.be", a["href"]),
                "locatie": "Oostende",
                "contract_hint": contract[1] if contract else None,
                "deadline": dates.iso(dates.find_cued(titel, dates.DEADLINE_CUES)[0]),
            }
        )
    return out


@adapter("stad_brugge")
def stad_brugge(cfg: dict, profiel: dict) -> list[dict]:
    out = []
    for page in range(1, cfg.get("max_pages", 6) + 1):
        url = "https://www.werkenbijbrugge.be/vacatures" + (f"/page-{page}" if page > 1 else "")
        try:
            s = net.soup(url)
        except Exception:
            break
        items = s.select("h3.itemTitle a")
        new = [a for a in items if a["href"] not in {o["url"] for o in out}]
        if not new:
            break
        for a in new:
            t = net.text_of(a)
            titel, _, org = t.partition(" bij ")
            out.append(
                {"titel": titel, "organisatie": org or "Stad Brugge", "url": a["href"], "locatie": "Brugge"}
            )
    return out


@adapter("talent_brussels")
def talent_brussels(cfg: dict, profiel: dict) -> list[dict]:
    s = net.soup("https://www.talent.brussels/nl/vacatures")
    out = []
    for a in s.select("ul.job-list a.stretched-link"):
        parts = a["href"].strip("/").split("/")
        org = parts[-2].replace("-", " ").title() if len(parts) >= 3 else ""
        out.append(
            {
                "titel": net.text_of(a),
                "organisatie": org,
                "url": urljoin("https://www.talent.brussels", a["href"]),
                "locatie": "Brussel",
            }
        )
    return out


@adapter("vrt")
def vrt(cfg: dict, profiel: dict) -> list[dict]:
    d = net.get(
        "https://jobs.vrt.be/nl/ajax/dto/37/data?sortBy=publishStart&sortingDirection=desc-asc"
    ).json()
    out = []
    for it in d.get("hub", {}).get("dtos", []):
        out.append(
            {
                "titel": it.get("title", ""),
                "organisatie": it.get("brandName") or "VRT",
                "url": it.get("hrefDetail"),
                "publicatiedatum": dates.iso(dates.parse_one(it.get("publishStart"))),
                "contract_hint": it.get("contractTypeName"),
                "beschrijving": it.get("shortDescription"),
            }
        )
    return out
