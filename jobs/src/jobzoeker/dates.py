"""Datums uit Nederlandse/Franse/Engelse vacaturetekst halen. Nooit gokken: None als het niet zeker is."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

MAANDEN = {
    "januari": 1,
    "jan": 1,
    "janvier": 1,
    "january": 1,
    "februari": 2,
    "feb": 2,
    "février": 2,
    "fevrier": 2,
    "february": 2,
    "maart": 3,
    "mrt": 3,
    "mars": 3,
    "march": 3,
    "april": 4,
    "apr": 4,
    "avril": 4,
    "mei": 5,
    "mai": 5,
    "may": 5,
    "juni": 6,
    "jun": 6,
    "juin": 6,
    "june": 6,
    "juli": 7,
    "jul": 7,
    "juillet": 7,
    "july": 7,
    "augustus": 8,
    "aug": 8,
    "août": 8,
    "aout": 8,
    "august": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "septembre": 9,
    "oktober": 10,
    "okt": 10,
    "octobre": 10,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "novembre": 11,
    "december": 12,
    "dec": 12,
    "décembre": 12,
    "decembre": 12,
}
_MAAND_RE = "|".join(sorted(MAANDEN, key=len, reverse=True))

RE_NUM = re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b")
RE_ISO = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})")
RE_TXT = re.compile(rf"\b(\d{{1,2}})(?:e|ste|de|er)?\s+({_MAAND_RE})\.?(?:\s+(20\d{{2}}))?\b", re.I)


def today() -> date:
    return datetime.now(timezone.utc).astimezone().date()


def _mk(y: int, m: int, d: int) -> date | None:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def _infer_year(m: int, d: int, ref: date) -> int:
    # Datum zonder jaar: kies het jaar waarbij de datum het dichtst bij (en liefst na) vandaag valt.
    cand = _mk(ref.year, m, d)
    if cand and (ref - cand).days > 60:
        return ref.year + 1
    return ref.year


def parse_one(text: str | None, ref: date | None = None) -> date | None:
    """Eerste expliciete datum in de tekst."""
    if not text:
        return None
    ref = ref or today()
    if m := RE_ISO.search(text):
        return _mk(int(m[1]), int(m[2]), int(m[3]))
    if m := RE_NUM.search(text):
        y = int(m[3])
        y = y + 2000 if y < 100 else y
        return _mk(y, int(m[2]), int(m[1]))
    if m := RE_TXT.search(text):
        mo = MAANDEN[m[2].lower()]
        y = int(m[3]) if m[3] else _infer_year(mo, int(m[1]), ref)
        return _mk(y, mo, int(m[1]))
    return None


DEADLINE_CUES = [
    r"deadline",
    r"reageren (?:tot|voor|vóór|uiterlijk)",
    r"reageer tot",
    r"solliciteren (?:kan )?(?:tot|voor|vóór|uiterlijk)",
    r"kandidaatstellingen?",
    r"uiterlijk (?:op|tegen)",
    r"ten laatste",
    r"stuur .{0,60}? (?:voor|vóór|tegen|ten laatste)",
    r"date limite",
    r"jusqu'au",
    r"avant le",
    r"apply (?:before|by)",
    r"closing date",
    r"sollicitatie.{0,30}?(?:tot|voor|vóór)",
    r"inschrijven (?:kan )?tot",
    r"geldig tot",
]
START_CUES = [
    r"start(?:datum)?",
    r"indiensttreding",
    r"in dienst",
    r"aanvang",
    r"beschikbaar vanaf",
    r"vanaf",
    r"begin(?:datum)?",
    r"entrée en fonction",
    r"date de début",
    r"starting date",
    r"start date",
]
END_CUES = [
    r"tot en met",
    r"t\.e\.m\.",
    r"einddatum",
    r"loopt tot",
    r"contract tot",
    r"vervanging tot",
    r"until",
    r"jusqu'au",
]

_WINDOW = 90


def find_cued(
    text: str | None, cues: list[str], ref: date | None = None, stop: str | None = None
) -> tuple[date | None, str | None]:
    """Zoek een datum vlak na een signaalwoord. Geeft (datum, bewijs-snippet)."""
    if not text:
        return None, None
    low = text.lower()
    best: tuple[int, date, str] | None = None
    for cue in cues:
        for m in re.finditer(cue, low):
            window = text[m.start() : m.end() + _WINDOW]
            rest = window[len(m.group(0)) :]
            d = parse_one(rest, ref)
            if d and stop:
                # tekst tussen signaalwoord en datum mag geen ander signaal bevatten
                pos = next(
                    (x.start() for x in (RE_ISO.search(rest), RE_NUM.search(rest), RE_TXT.search(rest)) if x),
                    0,
                )
                if re.search(stop, rest[:pos], re.I):
                    continue
            if d:
                snippet = " ".join(window.split())[:140]
                if best is None or m.start() < best[0]:
                    best = (m.start(), d, snippet)
    if best:
        return best[1], best[2]
    return None, None


def iso(d: date | datetime | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


STOP_START = r"(asap|onmiddellijk|zo snel mogelijk|reageren|reageer|solliciteer|kandid|deadline|uiterlijk)"
STOP_END = r"(reageren|reageer|solliciteer|kandid|deadline|uiterlijk|inschrijven)"
