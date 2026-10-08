"""Heuristische score (0-100) + leren uit Nina's feedback. Claude's score overschrijft dit waar aanwezig."""

from __future__ import annotations

import re

from .classify import norm

CULTUUR_SIGNAAL = re.compile(
    r"(cultu|kunst|theat|podium|festival|\bevent|evenement|muziek|music|concert|\bfilm|muse|erfgoed|\bdans|circus|"
    r"opera|orkest|orchestr|tentoonstel|\bexpo|bibliothe|toeris|\bmedia|televisie|\btv\b|\bvrt\b|audiovisu|"
    r"productiehuis|artiest|artist|backstage|stagehand|\bvenue|schouwburg|creati|scenograf|\bdecor|jeugdhuis|"
    r"vrije tijd|feesten|hospitality|ticketing|publiekswerking|\bshow|entertainment)"
)

SECTOR_BRONNEN = {
    "cultuurjobs",
    "publiq",
    "podiumkunsten",
    "mediarte",
    "cult",
    "vibe",
    "tomorrowland",
    "concertgebouw",
    "kursaal",
    "cinergie",
}


def _wordre(term: str) -> re.Pattern:
    t = norm(term)
    if t.endswith("*"):
        return re.compile(rf"\b{re.escape(t[:-1])}")
    return re.compile(rf"\b{re.escape(t)}\b")


def _tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", norm(s))}


class Scorer:
    def __init__(self, profiel: dict, feedback_jobs: list[dict]):
        self.p = profiel
        self.excl = [_wordre(t) for t in profiel.get("uitsluiten", [])]
        kw = profiel.get("trefwoorden", {})
        seen: set[str] = set()
        self.kw = []
        for lvl, w in (("sterk", 30), ("middel", 18), ("zwak", 8)):
            for t in kw.get(lvl, []):
                if norm(t) not in seen:
                    seen.add(norm(t))
                    self.kw.append((norm(t), w))
        self.loc = [
            (norm(t), w)
            for lvl, w in (("voorkeur", 15), ("ok", 5), ("ver", -15))
            for t in profiel.get("locaties", {}).get(lvl, [])
        ]
        self.contract = {norm(k): v for k, v in (profiel.get("contract") or {}).items()}
        self.regime = {norm(k): v for k, v in (profiel.get("regime") or {}).items()}
        # Feedback: titels/organisaties die Nina goed of slecht vond.
        self.neg = [
            (_tokens(j["titel"]), norm(j.get("organisatie")))
            for j in feedback_jobs
            if j.get("status") == "geen_interesse"
        ]
        self.pos = [
            (_tokens(j["titel"]), norm(j.get("organisatie")))
            for j in feedback_jobs
            if j.get("status") in ("interesse", "gesolliciteerd", "gesprek", "aanbod")
        ]

    def excluded(self, job: dict) -> str | None:
        t = norm(job.get("titel"))
        for rx in self.excl:
            if rx.search(t):
                return rx.pattern.replace("\\b", "")
        return None

    def score(self, job: dict) -> tuple[int, list[str]]:
        why: list[str] = []
        titel = norm(job.get("titel"))
        desc = norm(job.get("beschrijving"))[:5000]
        if ex := self.excluded(job):
            return 0, [f"uitgesloten ({ex})"]

        pts = 0.0
        hit_t = [(t, w) for t, w in self.kw if t in titel]
        if hit_t:
            # Beste twee titeltreffers tellen volledig.
            best = sorted(hit_t, key=lambda x: -x[1])[:2]
            pts += sum(w for _, w in best)
            why.append("titel: " + ", ".join(t for t, _ in best))
        hit_d = [w for t, w in self.kw if t in desc and (t, w) not in hit_t]
        if hit_d:
            pts += min(15, sum(hit_d) / 3)
        if set(job.get("bronnen", {})) & SECTOR_BRONNEN:
            pts += 12
            why.append("cultuursector-bron")
        elif not CULTUUR_SIGNAAL.search(f"{titel} {norm(job.get('organisatie'))} {desc[:3000]}"):
            pts -= 50
            why.append("geen cultuur/event-signaal -50")

        loc = norm(f"{job.get('locatie') or ''}")
        locpts = [w for t, w in self.loc if t and re.search(rf"\b{re.escape(t)}\b", loc)]
        if locpts:
            lp = max(locpts) if max(locpts) > 0 else min(locpts)
            pts += lp
            why.append(f"locatie {'+' if lp >= 0 else ''}{lp}")

        cpts = [self.contract.get(c, 0) for c in job.get("contract", []) if c != "onbekend"]
        if cpts:
            cp = max(cpts) if max(cpts) > -20 else min(cpts)
            pts += cp
            if cp:
                why.append(f"contract {'+' if cp >= 0 else ''}{cp}")
        pts += self.regime.get(job.get("regime") or "", 0)

        # Leren uit feedback (gelijkaardige titels/organisaties)
        tok = _tokens(job.get("titel", ""))
        org = norm(job.get("organisatie"))
        for toks, o in self.neg:
            sim = len(tok & toks) / max(1, len(tok | toks))
            if sim >= 0.5:
                pts -= 10
                why.append("lijkt op afgewezen vacature -10")
                break
        for toks, o in self.pos:
            sim = len(tok & toks) / max(1, len(tok | toks))
            if sim >= 0.5 or (o and o == org):
                pts += 10
                why.append("lijkt op vacature met interesse")
                break

        return max(0, min(100, round(pts))), why
