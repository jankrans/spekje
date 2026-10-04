"""CLI: uv run --project jobs jobzoeker <commando>."""

from __future__ import annotations

import argparse
import json

from . import feedback, pipeline, render
from .store import STATUSSEN, Store


def _load_env() -> None:
    """jobs/.env (niet in git): JOBS_SITE_URL en JOBS_AUTH=gebruiker:wachtwoord."""
    import os

    from . import ROOT

    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def main() -> None:
    _load_env()
    ap = argparse.ArgumentParser(prog="jobzoeker")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("run", help="sync-feedback + scrape + enrich + queue + build (zonder Claude-review)")
    s.add_argument("--only", nargs="*")
    s.add_argument("--enrich-limit", type=int, default=80)
    s = sub.add_parser("scrape")
    s.add_argument("--only", nargs="*")
    s = sub.add_parser("enrich")
    s.add_argument("--limit", type=int, default=80)
    sub.add_parser("sync-feedback")
    sub.add_parser("queue", help="schrijf data/review_queue.json voor Claude")
    s = sub.add_parser("review-import", help="importeer Claude-reviews (JSON lijst of map)")
    s.add_argument("file")
    s = sub.add_parser("feedback", help="status zetten vanuit chat")
    s.add_argument("id")
    s.add_argument("status", choices=STATUSSEN)
    s.add_argument("comment", nargs="?")
    s = sub.add_parser("add", help="vacature manueel toevoegen (gevonden op site/alert/pagina-watch)")
    s.add_argument("url")
    s.add_argument("titel")
    s.add_argument("--organisatie", default="")
    s.add_argument("--locatie")
    s.add_argument("--deadline", help="YYYY-MM-DD")
    s.add_argument("--beschrijving")
    s.add_argument("--bron", default="manueel")
    sub.add_parser("build")
    s = sub.add_parser("show")
    s.add_argument("id")
    sub.add_parser("stats")
    a = ap.parse_args()

    if a.cmd == "run":
        _, msg = feedback.pull()
        print(f"feedback: {msg}")
        print("scrape:")
        log = pipeline.scrape(a.only)
        print(f"enrich: {pipeline.enrich(a.enrich_limit)} detailpagina's")
        q = pipeline.queue()
        render.build()
        fails = [b["naam"] for b in log["bronnen"].values() if not b["ok"] and not b.get("optional")]
        print(
            f"klaar: {len(log['nieuw'])} nieuwe items, {len(q)} in review-queue"
            + (f", MISLUKT: {', '.join(fails)}" if fails else "")
        )
    elif a.cmd == "scrape":
        pipeline.scrape(a.only)
    elif a.cmd == "enrich":
        print(pipeline.enrich(a.limit))
    elif a.cmd == "sync-feedback":
        print(feedback.pull()[1])
    elif a.cmd == "queue":
        q = pipeline.queue()
        print(f"{len(q)} vacatures in data/review_queue.json")
        for x in q[:50]:
            print(f"  {x['id']}  {x['score_heuristiek']:>3}  {x['titel'][:60]} · {x['organisatie'] or ''}")
    elif a.cmd == "review-import":
        print(f"{pipeline.import_reviews(a.file)} reviews geïmporteerd")
        render.build()
    elif a.cmd == "feedback":
        st = Store()
        if a.id not in st.jobs:
            matches = [j for j in st.jobs if j.startswith(a.id)]
            if len(matches) != 1:
                raise SystemExit(f"id {a.id} niet gevonden")
            a.id = matches[0]
        feedback.set_local(a.id, a.status, a.comment)
        render.build()
        print(f"{st.jobs[a.id]['titel']}: {a.status}")
    elif a.cmd == "add":
        from .store import now_iso

        st = Store()
        raw = {
            "url": a.url,
            "titel": a.titel,
            "organisatie": a.organisatie,
            "locatie": a.locatie,
            "deadline": a.deadline,
            "beschrijving": a.beschrijving,
        }
        jid, nieuw = st.upsert(raw, a.bron, a.bron, now_iso())
        st.save()
        render.build()
        print(f"{jid} {'toegevoegd' if nieuw else 'bestond al'}: {a.titel}")
    elif a.cmd == "build":
        render.build()
    elif a.cmd == "show":
        st = Store()
        print(json.dumps(st.jobs[a.id], ensure_ascii=False, indent=1))
    elif a.cmd == "stats":
        st = pipeline.compute()
        js = list(st.jobs.values())
        rel = [j for j in js if j["relevant"]]
        print(
            f"totaal {len(js)} · relevant {len(rel)} · relevant+actief {sum(j['actief'] for j in rel)} · "
            f"door Claude beoordeeld {sum(j['score_bron'] == 'claude' for j in rel)}"
        )


if __name__ == "__main__":
    main()
