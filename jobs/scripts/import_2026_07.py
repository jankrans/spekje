"""Eenmalige import van de eerste zoektocht (juli 2026, archief-2026-07/jobs/*.md) in jobs.json.

- Elke vacature wordt een item met bron 'eerste-zoektocht' (dedup-geheugen + leren uit feedback).
- Afgevinkt (geen match) -> feedback geen_interesse, met datum.
- De Grote Post (gesolliciteerd) -> aanbod: werd haar huidige job.
- Sterren -> Claude-score (oud profiel): 3=85, 2=65, 1=45.
Idempotent: opnieuw draaien overschrijft niets wat al bestaat.
"""

import re
from pathlib import Path

from jobzoeker.store import FEEDBACK, REVIEWS, Store, load, save

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "archief-2026-07" / "jobs"
LINE = re.compile(r"^- \[(?P<x>.)\] (?P<stars>⭐+) \*\*(?P<titel>.+?)\*\* — (?P<rest>.*)$")
STAR_SCORE = {1: 45, 2: 65, 3: 85}


def parse(path: Path, sectie_default: str):
    sectie = sectie_default
    items = []
    lines = path.read_text().splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            sectie = ln[3:].strip()
        m = LINE.match(ln)
        if not m:
            continue
        rest = m["rest"]
        parts = [p.strip() for p in rest.split(" · ")]
        org_loc = parts[0]
        om = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", org_loc)
        org, loc = (om[1], om[2]) if om else (org_loc, None)
        url = re.search(r"\[vacature\]\((\S+?)\)", rest)
        dl = re.search(r"deadline (\d{4}-\d{2}-\d{2})", rest)
        added = re.search(r"\+(\d{4}-\d{2}-\d{2})", rest)
        nb = re.search(r"nb: (.*?)(?: · reden:|$)", rest)
        reden = re.search(r"reden: (.*)$", rest)
        typ = parts[1] if len(parts) > 1 else ""
        desc = lines[i + 1].strip().lstrip("↳").strip() if i + 1 < len(lines) and "↳" in lines[i + 1] else ""
        items.append(
            {
                "titel": m["titel"].strip(),
                "organisatie": org.strip(),
                "locatie": loc,
                "url": url[1] if url else None,
                "deadline": dl[1] if dl else None,
                "added": added[1] if added else "2026-07-05",
                "type": typ,
                "sterren": len(m["stars"]),
                "nb": nb[1].strip() if nb else None,
                "reden": reden[1].strip() if reden else None,
                "afgevinkt": m["x"].lower() == "x",
                "beschrijving": desc,
                "sectie": sectie,
            }
        )
    return items


def main():
    st = Store()
    fb = load(FEEDBACK, {})
    rv = load(REVIEWS, {})
    items = parse(SRC / "tracker.md", "Te bekijken") + parse(SRC / "archief.md", "Archief")
    n_new = 0
    for it in items:
        if not it["url"]:
            continue
        raw = {
            "titel": it["titel"],
            "organisatie": it["organisatie"],
            "url": it["url"],
            "locatie": it["locatie"],
            "contract_hint": it["type"],
            "regime_hint": it["type"],
            "deadline": it["deadline"],
            "beschrijving": " ".join(
                x for x in (it["beschrijving"], f"Notitie juli: {it['nb']}" if it["nb"] else "") if x
            ),
        }
        ts = f"{it['added']}T08:00:00+00:00"
        jid, nieuw = st.upsert(raw, "eerste-zoektocht", "Eerste zoektocht (juli 2026)", ts)
        job = st.jobs[jid]
        job["first_seen"] = min(job["first_seen"], ts)
        job["bronnen"]["eerste-zoektocht"]["weg_sinds"] = ts  # niet meer actief gevolgd
        if set(job["bronnen"]) == {"eerste-zoektocht"}:
            job["online"] = False
            job["offline_sinds"] = "2026-07-20T00:00:00+00:00"
        n_new += nieuw
        reden = it["reden"] or ""
        if "afgevinkt" in reden and jid not in fb:
            d = re.search(r"afgevinkt (\d{4}-\d{2}-\d{2})", reden)
            at = f"{d[1]}T12:00:00+00:00" if d else ts
            c = "Afgevinkt als geen match in de eerste zoektocht (juli 2026)"
            fb[jid] = {
                "status": "geen_interesse",
                "comment": c,
                "at": at,
                "door": "tracker-juli",
                "history": [{"at": at, "status": "geen_interesse", "comment": c, "door": "tracker-juli"}],
            }
        if it["sectie"] == "Gesolliciteerd" and jid not in fb:
            c = "Gesolliciteerd juli 2026, aangenomen: haar huidige job (aug-dec 2026)"
            at = "2026-07-20T12:00:00+00:00"
            fb[jid] = {
                "status": "aanbod",
                "comment": c,
                "at": at,
                "door": "tracker-juli",
                "history": [{"at": at, "status": "aanbod", "comment": c, "door": "tracker-juli"}],
            }
        if jid not in rv:
            rv[jid] = {
                "score": STAR_SCORE[min(3, it["sterren"])],
                "motivatie": f"{it['sterren']} ster(ren) in de eerste zoektocht (juli 2026, starterprofiel)."
                + (f" Reden archief: {reden}." if reden else ""),
                "samenvatting": it["beschrijving"] or None,
                "at": ts,
                "bron": "eerste-zoektocht",
            }
    st.save()
    save(FEEDBACK, fb)
    save(REVIEWS, rv)
    print(f"{len(items)} regels gelezen, {n_new} nieuwe items, feedback {len(fb)}, reviews {len(rv)}")


if __name__ == "__main__":
    main()
