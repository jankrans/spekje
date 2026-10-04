"""Orkestratie: scrape -> verrijk -> classificeer/scoor -> review-queue -> build."""

from __future__ import annotations

import json
import time
import traceback
from datetime import date

import yaml

from . import DATA, ROOT, dates, feedback
from .classify import classify
from .enrich import enrich_job, extract_dates
from .score import Scorer
from .sources import ADAPTERS
from .store import REVIEWS, Store, load, now_iso, save

RUNS = DATA / "runs.json"
QUEUE = DATA / "review_queue.json"


def profiel() -> dict:
    return yaml.safe_load((ROOT / "profiel.yaml").read_text())


def bronnen() -> dict:
    return yaml.safe_load((ROOT / "bronnen.yaml").read_text())


def scrape(only: list[str] | None = None) -> dict:
    prof = profiel()
    cfg = bronnen()
    st = Store()
    run_ts = now_iso()
    log: dict = {"ts": run_ts, "bronnen": {}, "nieuw": []}
    for b in cfg["bronnen"]:
        if b.get("enabled") is False or (only and b["key"] not in only):
            continue
        fn = ADAPTERS[b["type"]]
        t0 = time.time()
        try:
            items = fn(b, prof)
        except Exception as e:
            log["bronnen"][b["key"]] = {
                "naam": b["naam"],
                "ok": False,
                "fout": f"{type(e).__name__}: {e}"[:300],
                "optional": bool(b.get("optional")),
            }
            if not b.get("optional"):
                traceback.print_exc(limit=1)
            continue
        n_new = 0
        for raw in items:
            if not raw.get("url") or not raw.get("titel"):
                continue
            jid, nieuw = st.upsert(raw, b["key"], b["naam"], run_ts)
            if nieuw:
                n_new += 1
                log["nieuw"].append(jid)
        weg = 0 if b["type"] == "pagewatch" else st.mark_offline(b["key"], run_ts)
        log["bronnen"][b["key"]] = {
            "naam": b["naam"],
            "ok": True,
            "items": len(items),
            "nieuw": n_new,
            "weg": weg,
            "sec": round(time.time() - t0, 1),
        }
        print(f"  {b['naam']:<32} {len(items):>4} items, {n_new:>3} nieuw")
    st.save()
    runs = load(RUNS, [])
    runs.append(log)
    save(RUNS, runs[-200:])
    return log


def compute(st: Store | None = None) -> Store:
    """Feedback toepassen, classificeren, scoren. Idempotent."""
    st = st or Store()
    prof = profiel()
    fb = load(DATA / "feedback.json", {})
    for job in st.jobs.values():  # status komt volledig uit feedback.json
        job["status"] = "nieuw"
        job["feedback_comment"] = None
        job["feedback_at"] = None
        job.pop("notitie", None)
    feedback.apply(st.jobs, fb)
    reviews = load(REVIEWS, {})
    fb_jobs = [st.jobs[j] for j in fb if j in st.jobs]
    scorer = Scorer(prof, fb_jobs)
    today = dates.today().isoformat()
    drempel = prof.get("scoring", {}).get("drempel_relevant", 35)
    for jid, job in st.jobs.items():
        k = classify(job)
        rv = reviews.get(jid, {})
        for veld in ("contract", "regime", "sector", "functietype", "thuiswerk", "provincie", "percentage"):
            if rv.get(veld):
                k[veld] = rv[veld]
        job.update(k)
        for veld, val in (rv.get("datums") or {}).items():
            if val:
                Store.set_datum(job, veld, val, "claude", rv.get("datum_bewijs", {}).get(veld), force=True)
        if job.get("pagewatch"):
            h, why = prof.get("scoring", {}).get("drempel_review", 45), ["jobpagina gewijzigd: te checken"]
        else:
            h, why = scorer.score(job)
        job["score_heuristiek"] = h
        job["score_redenen"] = why
        job["uitgesloten"] = why[0] if why and why[0].startswith("uitgesloten") else None
        if rv.get("score") is not None:
            job["score"] = int(rv["score"])
            job["score_bron"] = "claude"
            job["motivatie"] = rv.get("motivatie")
            job["pluspunten"] = rv.get("pluspunten", [])
            job["minpunten"] = rv.get("minpunten", [])
            job["samenvatting"] = rv.get("samenvatting")
            job["reviewed_at"] = rv.get("at")
        else:
            job["score"] = h
            job["score_bron"] = "heuristiek"
        job["ruis"] = bool(rv.get("ruis"))
        job["duplicaat_van"] = rv.get("duplicaat_van")
        dl = (job["datums"].get("deadline") or {}).get("waarde")
        job["verlopen"] = bool(dl and dl < today)
        job["actief"] = bool(job.get("online", True)) and not job["verlopen"]
        job["relevant"] = (
            not job["ruis"]
            and not job["duplicaat_van"]
            and (
                job["status"] != "nieuw"
                or (rv.get("score") is not None and not job["uitgesloten"])
                or h >= drempel
            )
        )
    for job in st.jobs.values():
        job["extra_bronnen"] = {}
    for job in st.jobs.values():
        parent = st.jobs.get(job.get("duplicaat_van") or "")
        if parent:
            for k, b in job["bronnen"].items():
                if k not in parent["bronnen"]:
                    parent["extra_bronnen"][k] = b
    st.save()
    return st


def enrich(limit: int = 60, only_new: bool = False) -> int:
    st = compute()
    prof = profiel()
    drempel = prof.get("scoring", {}).get("drempel_review", 45) - 10
    todo = [
        j
        for j in st.jobs.values()
        if j["actief"]
        and not j.get("verrijkt")
        and not j.get("pagewatch")
        and not j.get("uitgesloten")
        and j["score_heuristiek"] >= drempel
    ]
    todo.sort(key=lambda j: -j["score_heuristiek"])
    n = 0
    for job in todo[:limit]:
        if enrich_job(job):
            n += 1
        time.sleep(0.5)
    for job in st.jobs.values():
        if job.get("beschrijving") and not job.get("verrijkt"):
            extract_dates(job)
    st.save()
    compute(st)
    return n


def queue() -> list[dict]:
    st = compute()
    prof = profiel()
    reviews = load(REVIEWS, {})
    drempel = prof.get("scoring", {}).get("drempel_review", 45)
    q = []
    for j in st.jobs.values():
        if (
            not j["actief"]
            or j.get("uitgesloten")
            or j["id"] in reviews
            or j["status"] in ("geen_interesse", "afgewezen")
        ):
            continue
        if j["score_heuristiek"] < drempel and j["status"] == "nieuw":
            continue
        q.append(
            {
                "id": j["id"],
                "titel": j["titel"],
                "organisatie": j.get("organisatie"),
                "url": j["url"],
                "locatie": j.get("locatie"),
                "provincie": j.get("provincie"),
                "bronnen": sorted(j["bronnen"]),
                "pagewatch": j.get("pagewatch", False),
                "score_heuristiek": j["score_heuristiek"],
                "redenen": j["score_redenen"],
                "contract": j["contract"],
                "regime": j["regime"],
                "sector": j["sector"],
                "functietype": j["functietype"],
                "thuiswerk": j["thuiswerk"],
                "datums": {k: v.get("waarde") or v.get("tekst") for k, v in j["datums"].items()},
                "hints": {
                    k: j.get(k) for k in ("contract_hint", "regime_hint", "categorie_hint") if j.get(k)
                },
                "beschrijving": (j.get("beschrijving") or "")[:3000],
            }
        )
    q.sort(key=lambda x: -x["score_heuristiek"])
    save(QUEUE, q)
    return q


def import_reviews(path) -> int:
    data = json.loads(open(path).read())
    if isinstance(data, list):
        data = {d["id"]: d for d in data}
    reviews = load(REVIEWS, {})
    st = Store()
    n = 0
    for jid, rv in data.items():
        if jid not in st.jobs:
            print(f"  onbekend id {jid}, overgeslagen")
            continue
        rv = {k: v for k, v in rv.items() if k != "id"}
        rv["at"] = now_iso()
        reviews[jid] = {**reviews.get(jid, {}), **rv}
        n += 1
    save(REVIEWS, reviews)
    compute(st)
    return n


def days_left(iso: str | None) -> int | None:
    if not iso:
        return None
    return (date.fromisoformat(iso) - dates.today()).days
