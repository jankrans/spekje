"""jobs.json = bron van waarheid. Niets wordt ooit verwijderd: offline/verlopen vacatures krijgen enkel een vlag."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import DATA
from .classify import norm

JOBS = DATA / "jobs.json"
FEEDBACK = DATA / "feedback.json"
REVIEWS = DATA / "reviews.json"

# Status die Nina zet (via site of chat). 'nieuw' = nog niet beoordeeld.
STATUSSEN = [
    "nieuw",
    "bekeken",
    "interesse",
    "gesolliciteerd",
    "gesprek",
    "aanbod",
    "afgewezen",
    "geen_interesse",
]
STATUS_LABEL = {
    "nieuw": "Nieuw",
    "bekeken": "Bekeken",
    "interesse": "Interesse",
    "gesolliciteerd": "Gesolliciteerd",
    "gesprek": "Gesprek",
    "aanbod": "Aanbod",
    "afgewezen": "Afgewezen (door werkgever)",
    "geen_interesse": "Geen interesse",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(path: Path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True))
    tmp.replace(path)


def canon_url(url: str) -> str:
    u = re.sub(r"^https?://(www\.)?", "", (url or "").strip()).rstrip("/")
    u = re.sub(r"[?#].*$", "", u) if "vdab.be" not in u else u
    return u.lower()


def job_id(raw: dict) -> str:
    key = canon_url(raw["url"])
    if raw.get("pagewatch"):
        key += "|" + raw.get("pagewatch_hash", "")
    return hashlib.sha1(key.encode()).hexdigest()[:10]


_STOP = re.compile(r"\b(m/v/x|v/m/x|m/v|h/f/x|f/h/x|m/f/x|\(.*?\)|vacature|bij|de|het|een|en|voor|-)\b")


def dedupe_key(titel: str, org: str) -> str:
    t = _STOP.sub(" ", norm(titel))
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    o = re.sub(r"\b(vzw|nv|bv|bvba|asbl|cvba)\b", "", norm(org))
    o = re.sub(r"[^a-z0-9]", "", o)[:20]
    return " ".join(t.split()) + "|" + o


class Store:
    def __init__(self) -> None:
        self.jobs: dict[str, dict] = load(JOBS, {})
        self._by_dedupe = {j["dedupe_key"]: jid for jid, j in self.jobs.items() if j.get("dedupe_key")}

    def save(self) -> None:
        save(JOBS, self.jobs)

    def upsert(self, raw: dict, bron_key: str, bron_naam: str, run_ts: str) -> tuple[str, bool]:
        """Voeg ruwe vacature toe of werk bij. Geeft (id, is_nieuw)."""
        jid = job_id(raw)
        dk = dedupe_key(raw.get("titel", ""), raw.get("organisatie", ""))
        # Zelfde vacature via andere bron? Dan koppelen aan bestaande.
        if (
            jid not in self.jobs
            and not raw.get("pagewatch")
            and dk in self._by_dedupe
            and len(dk) > 8
            and dk.split("|")[1]
        ):
            jid = self._by_dedupe[dk]
        job = self.jobs.get(jid)
        nieuw = job is None
        if nieuw:
            job = {
                "id": jid,
                "titel": raw.get("titel", "").strip(),
                "organisatie": (raw.get("organisatie") or "").strip(),
                "url": raw["url"],
                "status": "nieuw",
                "first_seen": run_ts,
                "bronnen": {},
                "datums": {},
                "pagewatch": bool(raw.get("pagewatch")),
                "dedupe_key": dk,
            }
            self.jobs[jid] = job
            self._by_dedupe.setdefault(dk, jid)
        job["last_seen"] = run_ts
        job["online"] = True
        job.pop("offline_sinds", None)
        job["bronnen"][bron_key] = {"naam": bron_naam, "url": raw["url"], "last_seen": run_ts}
        # Velden aanvullen, nooit een bestaande waarde overschrijven met leeg.
        for k in ("locatie", "contract_hint", "regime_hint", "categorie_hint", "thuiswerk_hint", "niveau"):
            v = raw.get(k)
            if v and (not job.get(k) or bron_key == job.get("primaire_bron")):
                job[k] = v
        if raw.get("organisatie") and not job.get("organisatie"):
            job["organisatie"] = raw["organisatie"].strip()
        if raw.get("beschrijving") and len(raw["beschrijving"]) > len(job.get("beschrijving") or ""):
            job["beschrijving"] = raw["beschrijving"][:8000]
        job.setdefault("primaire_bron", bron_key)
        for veld in ("publicatiedatum", "deadline"):
            if raw.get(veld):
                self.set_datum(job, veld, raw[veld], f"lijst:{bron_key}", None)
        return jid, nieuw

    @staticmethod
    def set_datum(
        job: dict, veld: str, waarde: str | None, bron: str, bewijs: str | None, force: bool = False
    ) -> None:
        """Datums met herkomst. Rangorde: claude/nina > lijst > detail-jsonld > detail-tekst."""
        if not waarde:
            return
        rang = {"nina": 5, "claude": 4, "lijst": 3, "detail-jsonld": 2, "detail-tekst": 1}
        cur = job["datums"].get(veld)
        nieuw_rang = rang.get(bron.split(":")[0], 0)
        if cur and not force and rang.get(cur["bron"].split(":")[0], 0) > nieuw_rang:
            return
        job["datums"][veld] = {"waarde": waarde, "bron": bron, "bewijs": bewijs}

    def mark_offline(self, bron_key: str, run_ts: str) -> int:
        """Vacatures die een succesvolle bron niet meer toont: bron als weg markeren."""
        n = 0
        for job in self.jobs.values():
            b = job.get("bronnen", {}).get(bron_key)
            if b and b.get("last_seen") != run_ts and not b.get("weg_sinds"):
                b["weg_sinds"] = run_ts
                n += 1
            if job.get("pagewatch"):
                continue
            if job.get("bronnen") and all(x.get("weg_sinds") for x in job["bronnen"].values()):
                if job.get("online"):
                    job["online"] = False
                    job["offline_sinds"] = run_ts
        return n
