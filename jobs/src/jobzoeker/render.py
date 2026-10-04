"""Markdown-overzichten en de data voor de site."""

from __future__ import annotations

import json
import re
from datetime import date
from urllib.parse import quote

from . import ROOT, SITE, dates
from .classify import norm
from .pipeline import RUNS, bronnen, days_left, profiel
from .store import STATUS_LABEL, Store, load

ACTIEF_STATUS = ("interesse", "gesolliciteerd", "gesprek", "aanbod")


def _d(job: dict, veld: str) -> str | None:
    v = job["datums"].get(veld) or {}
    return v.get("waarde") or v.get("tekst")


def _fmt(iso: str | None) -> str:
    if not iso:
        return "?"
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        return iso
    return d.strftime("%d/%m/%Y")


def _dl_days(job: dict) -> int | None:
    dl = _d(job, "deadline")
    return days_left(dl) if dl and re.match(r"\d{4}-", dl) else None


def _deadline_cell(job: dict) -> str:
    dl = _d(job, "deadline")
    if not dl:
        return "onbekend"
    n = days_left(dl) if re.match(r"\d{4}-", dl) else None
    if n is None:
        return dl
    if n < 0:
        return f"{_fmt(dl)} (verlopen)"
    if n == 0:
        return f"{_fmt(dl)} (vandaag)"
    return f"{_fmt(dl)} ({n}d)"


def _esc(s: str | None) -> str:
    return (s or "").replace("|", "/").replace("\n", " ").strip()


def slug(job: dict) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", norm(f"{job['titel']} {job.get('organisatie') or ''}")).strip("-")[:60]
    return f"{s}-{job['id']}"


def _row(i: int, j: dict) -> str:
    return (
        f"| {i} | **{j['score']}**{'' if j['score_bron'] == 'claude' else '*'} "
        f"| [{_esc(j['titel'])}](vacatures/{slug(j)}.md) | {_esc(j.get('organisatie'))} "
        f"| {_esc(j.get('locatie'))} | {', '.join(j['contract'])} | {j['regime']} "
        f"| {_deadline_cell(j)} | [link]({j['url']}) |"
    )


HEADER = "| # | Score | Vacature | Organisatie | Locatie | Contract | Regime | Deadline | |\n|---|---|---|---|---|---|---|---|---|"


def render_markdown(st: Store) -> None:
    jobs = [j for j in st.jobs.values() if j.get("relevant")]
    open_ = sorted(
        [j for j in jobs if j["actief"] and j["status"] not in ("geen_interesse", "afgewezen")],
        key=lambda j: (-j["score"], _d(j, "deadline") or "9999"),
    )
    runs = load(RUNS, [])
    last = runs[-1] if runs else {}
    nieuw_ids = set(last.get("nieuw", []))
    today = dates.today().isoformat()

    out = [
        "# Vacatures voor Nina\n",
        f"Laatste run: **{(last.get('ts') or '-')[:16].replace('T', ' ')}** · {len(open_)} open relevante vacatures · "
        f"site: `/jobs`\n",
        "Score: 0-100, gerangschikt. `*` = nog enkel heuristische score (Claude heeft nog niet beoordeeld).\n",
    ]

    pipeline_ = [j for j in jobs if j["status"] in ACTIEF_STATUS]
    if pipeline_:
        out += [
            "## In behandeling\n",
            "| Status | Vacature | Organisatie | Deadline | Notitie |",
            "|---|---|---|---|---|",
        ]
        for j in sorted(pipeline_, key=lambda j: ACTIEF_STATUS.index(j["status"])):
            out.append(
                f"| {STATUS_LABEL[j['status']]} | [{_esc(j['titel'])}](vacatures/{slug(j)}.md) "
                f"| {_esc(j.get('organisatie'))} | {_deadline_cell(j)} | {_esc(j.get('feedback_comment'))} |"
            )
        out.append("")

    soon = [j for j in open_ if (n := _dl_days(j)) is not None and n <= 7]
    if soon:
        out += ["## Deadline binnen 7 dagen\n", HEADER]
        out += [_row(i, j) for i, j in enumerate(soon, 1)]
        out.append("")

    new = [j for j in open_ if j["id"] in nieuw_ids]
    out += [f"## Nieuw sinds vorige run ({len(new)})\n"]
    if new:
        out += [HEADER] + [_row(i, j) for i, j in enumerate(new, 1)]
    else:
        out.append("_Geen nieuwe relevante vacatures._")
    out.append("")

    out += ["## Ranking open vacatures\n", HEADER]
    out += [_row(i, j) for i, j in enumerate(open_, 1)]
    out += [
        "",
        "Zie ook: [Geen interesse](GEEN_INTERESSE.md) · [Archief](ARCHIEF.md) · [Bronnen](BRONNEN.md) · "
        "[Runs](runs/)",
        "",
    ]
    (ROOT / "OVERZICHT.md").write_text("\n".join(out))

    # Geen interesse: input voor volgende screenings
    gi = sorted(
        [j for j in st.jobs.values() if j["status"] == "geen_interesse"],
        key=lambda j: j.get("feedback_at") or "",
        reverse=True,
    )
    lines = [
        "# Geen interesse\n",
        "Vacatures die Nina heeft afgewezen, met haar reden. Wordt meegenomen in elke nieuwe screening "
        "(heuristiek: gelijkaardige titels -20; Claude leest de redenen).\n",
        "| Datum | Vacature | Organisatie | Reden |",
        "|---|---|---|---|",
    ]
    for j in gi:
        lines.append(
            f"| {(j.get('feedback_at') or '')[:10]} | [{_esc(j['titel'])}]({j['url']}) "
            f"| {_esc(j.get('organisatie'))} | {_esc(j.get('feedback_comment')) or '_geen reden_'} |"
        )
    (ROOT / "GEEN_INTERESSE.md").write_text("\n".join(lines) + "\n")

    arch = sorted([j for j in jobs if not j["actief"]], key=lambda j: _d(j, "deadline") or "", reverse=True)
    lines = [
        "# Archief\n",
        "Relevante vacatures die verlopen of offline zijn. Niets wordt verwijderd.\n",
        "| Score | Vacature | Organisatie | Deadline | Status | Reden |",
        "|---|---|---|---|---|---|",
    ]
    for j in arch:
        reden = (
            "deadline voorbij" if j["verlopen"] else f"offline sinds {(j.get('offline_sinds') or '')[:10]}"
        )
        lines.append(
            f"| {j['score']} | [{_esc(j['titel'])}](vacatures/{slug(j)}.md) | {_esc(j.get('organisatie'))} "
            f"| {_fmt(_d(j, 'deadline'))} | {STATUS_LABEL.get(j['status'], j['status'])} | {reden} |"
        )
    (ROOT / "ARCHIEF.md").write_text("\n".join(lines) + "\n")

    vdir = ROOT / "vacatures"
    vdir.mkdir(exist_ok=True)
    keep = set()
    for j in jobs:
        name = f"{slug(j)}.md"
        keep.add(name)
        (vdir / name).write_text(job_md(j))
    for f in vdir.glob("*.md"):
        if f.name not in keep:
            f.unlink()  # wordt opnieuw gegenereerd uit jobs.json; data zelf blijft bewaard

    if last:
        rdir = ROOT / "runs"
        rdir.mkdir(exist_ok=True)
        d = last["ts"][:10]
        rl = [
            f"# Run {last['ts'][:16].replace('T', ' ')}\n",
            "| Bron | OK | Items | Nieuw | Weg | Sec | Fout |",
            "|---|---|---|---|---|---|---|",
        ]
        for k, b in last["bronnen"].items():
            rl.append(
                f"| {b['naam']} | {'ja' if b['ok'] else 'NEE'} | {b.get('items', '')} | {b.get('nieuw', '')} "
                f"| {b.get('weg', '')} | {b.get('sec', '')} | {_esc(b.get('fout'))} |"
            )
        rel_new = [st.jobs[i] for i in last.get("nieuw", []) if i in st.jobs and st.jobs[i].get("relevant")]
        rl += ["", f"## Nieuwe relevante vacatures ({len(rel_new)})\n"]
        rl += [
            f"- **{j['score']}** [{_esc(j['titel'])}]({j['url']}) · {_esc(j.get('organisatie'))} · "
            f"{_esc(j.get('locatie'))}"
            for j in sorted(rel_new, key=lambda j: -j["score"])
        ]
        (rdir / f"{d}.md").write_text("\n".join(rl) + "\n")


def job_md(j: dict) -> str:
    def dl(veld, label):
        v = j["datums"].get(veld)
        if not v:
            return f"| {label} | onbekend | |"
        w = _fmt(v.get("waarde")) if v.get("waarde") else v.get("tekst", "?")
        return f"| {label} | {w} | {v['bron']}{(': ' + _esc(v.get('bewijs'))) if v.get('bewijs') else ''} |"

    fm = {
        "id": j["id"],
        "titel": j["titel"],
        "organisatie": j.get("organisatie"),
        "url": j["url"],
        "score": j["score"],
        "score_bron": j["score_bron"],
        "status": j["status"],
        "contract": j["contract"],
        "regime": j["regime"],
        "sector": j["sector"],
        "functietype": j["functietype"],
        "locatie": j.get("locatie"),
        "provincie": j.get("provincie"),
        "thuiswerk": j["thuiswerk"],
        "deadline": _d(j, "deadline"),
        "startdatum": _d(j, "startdatum"),
        "einddatum": _d(j, "einddatum"),
        "eerst_gezien": j["first_seen"][:10],
        "actief": j["actief"],
    }
    lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()] + ["---", ""]
    lines += [
        f"# {j['titel']}",
        "",
        f"**{j.get('organisatie') or '?'}** · {j.get('locatie') or '?'} · "
        f"score **{j['score']}** ({j['score_bron']}) · status: {STATUS_LABEL.get(j['status'], j['status'])}",
        "",
    ]
    lines += [f"[Vacature openen]({j['url']})", ""]
    if j.get("samenvatting"):
        lines += ["## Samenvatting", "", j["samenvatting"], ""]
    if j.get("motivatie"):
        lines += ["## Waarom deze score", "", j["motivatie"], ""]
        if j.get("pluspunten"):
            lines += ["**Plus:** " + "; ".join(j["pluspunten"])]
        if j.get("minpunten"):
            lines += ["**Min:** " + "; ".join(j["minpunten"])]
        lines.append("")
    lines += [
        "## Kenmerken",
        "",
        "| | |",
        "|---|---|",
        f"| Contract | {', '.join(j['contract'])} |",
        f"| Regime | {j['regime']}{(' (' + str(j['percentage']) + '%)') if j.get('percentage') else ''} |",
        f"| Sector | {', '.join(j['sector'])} |",
        f"| Functie | {', '.join(j['functietype'])} |",
        f"| Thuiswerk | {j['thuiswerk']} |",
        f"| Provincie | {j.get('provincie') or '?'} |",
        "",
    ]
    lines += [
        "## Datums",
        "",
        "| | Datum | Bron |",
        "|---|---|---|",
        dl("publicatiedatum", "Gepubliceerd"),
        dl("deadline", "Solliciteren tot"),
        dl("startdatum", "Start"),
        dl("einddatum", "Einde contract"),
        "",
    ]
    if j.get("feedback_comment"):
        lines += ["## Feedback Nina", "", f"> {j['feedback_comment']}", ""]
    lines += ["## Bronnen", ""] + [
        f"- [{b['naam']}]({b['url']}) (laatst gezien {b['last_seen'][:10]}"
        f"{', weg sinds ' + b['weg_sinds'][:10] if b.get('weg_sinds') else ''})"
        for b in {**j["bronnen"], **j.get("extra_bronnen", {})}.values()
    ]
    if j.get("beschrijving"):
        lines += ["", "## Beschrijving (uittreksel)", "", j["beschrijving"][:3000]]
    return "\n".join(lines) + "\n"


SITE_FIELDS = (
    "id",
    "titel",
    "organisatie",
    "url",
    "locatie",
    "provincie",
    "contract",
    "regime",
    "percentage",
    "sector",
    "functietype",
    "thuiswerk",
    "taal",
    "score",
    "score_bron",
    "score_heuristiek",
    "score_redenen",
    "motivatie",
    "pluspunten",
    "minpunten",
    "samenvatting",
    "status",
    "feedback_comment",
    "first_seen",
    "actief",
    "verlopen",
    "online",
    "pagewatch",
)


def render_site(st: Store) -> None:
    prof = profiel()
    cfg = bronnen()
    runs = load(RUNS, [])
    last = runs[-1] if runs else {}
    from datetime import datetime, timedelta, timezone

    grens = (datetime.now(timezone.utc) - timedelta(hours=36)).isoformat()
    items = []
    for j in st.jobs.values():
        if not j.get("relevant"):
            continue
        it = {k: j.get(k) for k in SITE_FIELDS}
        it["datums"] = {
            k: {"waarde": v.get("waarde"), "tekst": v.get("tekst"), "bron": v.get("bron")}
            for k, v in j["datums"].items()
        }
        it["bronnen"] = [
            {"naam": b["naam"], "url": b["url"]}
            for b in {**j["bronnen"], **j.get("extra_bronnen", {})}.values()
        ]
        it["nieuw"] = j["first_seen"] >= grens
        it["beschrijving"] = (j.get("beschrijving") or "")[:1200]
        items.append(it)
    items.sort(key=lambda x: -x["score"])
    termen = prof.get("zoektermen", {}).get("vdab", [])[:8]
    handmatig = [
        {
            "naam": h["naam"],
            "links": [{"q": t, "url": h["url"].replace("{q}", quote(t))} for t in termen]
            if "{q}" in h["url"]
            else [{"q": None, "url": h["url"]}],
        }
        for h in cfg.get("handmatig", [])
    ]
    meta = {
        "laatste_run": last.get("ts"),
        "bronnen": [
            {"key": k, **{x: v.get(x) for x in ("naam", "ok", "items", "nieuw", "fout")}}
            for k, v in last.get("bronnen", {}).items()
        ],
        "bron_urls": {b["key"]: b["url"] for b in cfg["bronnen"]},
        "handmatig": handmatig,
        "statussen": STATUS_LABEL,
        "totaal_gescand": len(st.jobs),
    }
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "data" / "jobs.json").write_text(json.dumps({"meta": meta, "jobs": items}, ensure_ascii=False))


def build() -> None:
    from .pipeline import compute

    st = compute()
    render_markdown(st)
    render_site(st)
