"""Categorisatie: contract, regime, sector, functietype, provincie, thuiswerk. Regelgebaseerd, Claude corrigeert."""

from __future__ import annotations

import re
import unicodedata


def norm(s: str | None) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower()).strip()


def has(text: str, *pats: str) -> bool:
    return any(re.search(p, text) for p in pats)


CONTRACT_RULES = [
    ("bis-stage", [r"\bbis\b", r"beroepsinlevingsstage", r"\bbis-stag"]),
    ("stage", [r"\bstage", r"\bstagiair", r"\binternship", r"\bintern\b", r"\bstagiaire"]),
    ("flexi", [r"\bflexi"]),
    ("studentenjob", [r"\bstudent(en)?job", r"\bjobstudent", r"studentenarbeid"]),
    ("vrijwilliger", [r"\bvrijwillig(?!erscoor|ers?coord|erswerking)", r"\bbenevol"]),
    (
        "freelance",
        [
            r"\bfreelance",
            r"\bzelfstandig",
            r"\bstatuut zelfstandige",
            r"\bindependant",
            r"kunstwerkattest",
            r"bijzonder statuut",
            r"\bsmart\b",
        ],
    ),
    ("interim", [r"\binterim", r"\buitzend", r"intermediair"]),
    ("vervanging", [r"\bvervang", r"\bremplacement", r"zwangerschap", r"moederschapsrust"]),
    (
        "tijdelijk",
        [
            r"\btijdelijk",
            r"bepaalde duur",
            r"\bcdd\b",
            r"\bseizoen",
            r"\bprojectcontract",
            r"\btemporary",
            r"fixed.term",
        ],
    ),
    ("vast", [r"\bvast\b", r"\bvaste\b", r"onbepaalde duur", r"\bcdi\b", r"\bpermanent", r"vaste job"]),
]

SECTOR_RULES = [
    (
        "festival/events",
        [r"\bfestival", r"\bevent", r"\bevenement", r"tomorrowland", r"\bkermis", r"feesten\b"],
    ),
    (
        "film/AV",
        [
            r"\bfilm",
            r"\btelevisie",
            r"\btv\b",
            r"\bvrt\b",
            r"\baudiovisu",
            r"\bvideo",
            r"\bomroep",
            r"banijay",
            r"\bdpg",
            r"\bmedia\b",
            r"\bopname",
        ],
    ),
    (
        "muziek",
        [r"\bmuziek", r"\bconcert", r"\borkest", r"\bmusic", r"\bclub\b", r"\bopera", r"symphony", r"\bkoor"],
    ),
    (
        "podiumkunsten",
        [
            r"\btheater",
            r"\btheatre",
            r"\bdans",
            r"\bpodium",
            r"\bvoorstelling",
            r"\bcircus",
            r"\bschouwburg",
            r"kunstencentrum",
            r"\bgezelschap",
            r"\bntgent",
            r"\bkvs\b",
            r"\bcampo",
            r"\bperformance",
        ],
    ),
    (
        "museum/erfgoed",
        [r"\bmuse", r"\berfgoed", r"\bcollectie", r"\btentoonstelling", r"\barchief", r"\bbibliothe"],
    ),
    (
        "cultuurcentrum/lokaal",
        [
            r"cultuurcentrum",
            r"\bcc\b",
            r"gemeenschapscentrum",
            r"\bstad\b",
            r"\bgemeente",
            r"\bocmw",
            r"\bprovincie",
            r"vrije tijd",
        ],
    ),
    ("toerisme", [r"\btoeris", r"\bwesttoer", r"visit\."]),
    ("beeldende kunst", [r"beeldende kunst", r"\bgalerie", r"\bkunstenaar", r"\bkunsthal"]),
    ("sociaal-cultureel", [r"sociaal-cultureel", r"socius", r"\bjeugd", r"\bvormingplus", r"\bbuurt"]),
]

FUNCTIE_RULES = [
    (
        "productie",
        [r"\bproduc", r"\bproductie", r"\bregie", r"\bregisseur", r"line producer", r"\bopnameleider"],
    ),
    (
        "techniek",
        [
            r"\btechni",
            r"\bstagehand",
            r"\bpodiumtech",
            r"\blicht",
            r"\bgeluid",
            r"\bsound",
            r"\brigger",
            r"\bdecor",
            r"\batelier",
        ],
    ),
    (
        "events/logistiek",
        [r"\bevent", r"\bevenement", r"\blogisti", r"\brunner", r"\bopbouw", r"\bsite manag", r"\bfestival"],
    ),
    (
        "hospitality/onthaal",
        [
            r"\bhospitality",
            r"\bonthaal",
            r"\bticket",
            r"\bzaalverantw",
            r"\bvenue",
            r"\bhoreca",
            r"\bbar\b",
            r"\bartist relations",
            r"\bbackstage",
            r"\bfront.?of.?house",
        ],
    ),
    ("publiekswerking", [r"\bpubliek", r"\beducati", r"\bbemiddel", r"\bparticipat", r"\bgids"]),
    (
        "communicatie/marketing",
        [r"\bcommunicatie", r"\bmarketing", r"\bsocial media", r"\bcontent", r"\bpers\b", r"\bredact"],
    ),
    (
        "zakelijk/administratie",
        [
            r"\bzakelijk",
            r"\badministrat",
            r"\bfinanc",
            r"\bboekhoud",
            r"\bsecretari",
            r"\bhr\b",
            r"\bpersoneel",
            r"\bbeheer",
        ],
    ),
    (
        "programmatie/artistiek",
        [r"\bprogramm", r"\bcurat", r"\bdramaturg", r"\bartistiek", r"\bcompany manager", r"\bmanager dans"],
    ),
    (
        "project/coördinatie",
        [r"\bcoordinat", r"\bcoordinator", r"\bproject", r"\bmanager", r"\bleider", r"\bverantwoordelijke"],
    ),
]

PROVINCIES = {
    "Oost-Vlaanderen": [
        "gent",
        "aalst",
        "sint-niklaas",
        "dendermonde",
        "lokeren",
        "eeklo",
        "deinze",
        "oudenaarde",
        "zottegem",
        "ninove",
        "geraardsbergen",
        "wetteren",
        "merelbeke",
        "melle",
        "destelbergen",
        "lochristi",
        "evergem",
        "de pinte",
        "sint-martens-latem",
        "nazareth",
        "zele",
        "hamme",
        "temse",
        "beveren",
        "ronse",
        "lede",
        "erpe-mere",
        "wichelen",
        "laarne",
        "zelzate",
        "maldegem",
        "aalter",
        "kruisem",
        "nevele",
        "lovendegem",
        "gentbrugge",
        "ledeberg",
        "mariakerke",
        "drongen",
        "oost-vlaanderen",
        "kruibeke",
        "zwijndrecht",
    ],
    "West-Vlaanderen": [
        "oostende",
        "brugge",
        "kortrijk",
        "roeselare",
        "ieper",
        "waregem",
        "knokke",
        "blankenberge",
        "middelkerke",
        "de panne",
        "koksijde",
        "nieuwpoort",
        "veurne",
        "diksmuide",
        "torhout",
        "tielt",
        "poperinge",
        "menen",
        "wevelgem",
        "harelbeke",
        "izegem",
        "bredene",
        "de haan",
        "jabbeke",
        "oostkamp",
        "zedelgem",
        "damme",
        "houthulst",
        "kortemark",
        "koekelare",
        "west-vlaanderen",
        "avelgem",
        "anzegem",
        "zwevegem",
        "beernem",
        "torhout",
        "gistel",
        "oudenburg",
    ],
    "Antwerpen": [
        "antwerpen",
        "antwerp",
        "mechelen",
        "turnhout",
        "boom",
        "lier",
        "herentals",
        "geel",
        "mol",
        "brasschaat",
        "schoten",
        "berchem",
        "borgerhout",
        "deurne",
        "hoboken",
        "wilrijk",
        "merksem",
        "kontich",
        "mortsel",
        "edegem",
        "bornem",
        "willebroek",
        "puurs",
        "duffel",
        "aartselaar",
    ],
    "Vlaams-Brabant": [
        "leuven",
        "vilvoorde",
        "halle",
        "dilbeek",
        "zaventem",
        "asse",
        "tienen",
        "aarschot",
        "diest",
        "grimbergen",
        "beersel",
        "vlaams-brabant",
        "machelen",
        "overijse",
        "tervuren",
    ],
    "Brussel": [
        "brussel",
        "bruxelles",
        "brussels",
        "molenbeek",
        "schaarbeek",
        "anderlecht",
        "elsene",
        "ixelles",
        "etterbeek",
        "sint-gillis",
        "saint-gilles",
        "vorst",
        "forest",
        "ukkel",
        "uccle",
        "jette",
        "laken",
        "evere",
        "sint-joost",
        "oudergem",
        "woluwe",
    ],
    "Limburg": [
        "hasselt",
        "genk",
        "sint-truiden",
        "tongeren",
        "beringen",
        "lommel",
        "maasmechelen",
        "bilzen",
        "limburg",
        "heusden-zolder",
        "houthalen",
    ],
    "Wallonië": [
        "liege",
        "luik",
        "namur",
        "namen",
        "charleroi",
        "mons",
        "bergen",
        "tournai",
        "doornik",
        "wavre",
        "louvain-la-neuve",
        "mouscron",
        "moeskroen",
        "arlon",
        "dour",
        "wallonie",
        "wallonia",
        "nivelles",
        "tubize",
        "waterloo",
    ],
}


def provincie(loc: str | None) -> str | None:
    t = norm(loc)
    if not t:
        return None
    if "brussels hoofdstedelijk" in t:
        return "Brussel"
    for prov, steden in PROVINCIES.items():
        for s in steden:
            if re.search(rf"\b{re.escape(s)}\b", t):
                return prov
    if "nederland" in t or "netherlands" in t:
        return "Nederland"
    return None


def _tags(text: str, rules) -> list[str]:
    return [name for name, pats in rules if has(text, *pats)]


def classify(job: dict) -> dict:
    titel = norm(job.get("titel"))
    hints = norm(" ".join(str(job.get(k) or "") for k in ("contract_hint", "regime_hint", "categorie_hint")))
    desc = norm(job.get("beschrijving"))[:6000]
    org = norm(job.get("organisatie"))
    head = f"{titel} | {hints}"

    # Uit de beschrijving enkel het begin gebruiken (footers/sidebars noemen vaak flexi/freelance/stage).
    contract = _tags(head, CONTRACT_RULES) or _tags(desc[:1200], CONTRACT_RULES)
    if "bis-stage" in contract and "stage" in contract:
        contract.remove("stage")
    if hints and "tijdelijke jobs met optie vast" in hints:
        contract = ["tijdelijk", "vast"]

    regime = None
    pct = re.search(r"\b(\d{2,3})\s?%", f"{titel} {hints}") or re.search(r"\b(\d{2,3})\s?%", desc[:1500])
    if has(head, r"\bvoltijd", r"full.?time", r"temps plein", r"\b100\s?%"):
        regime = "voltijds"
    elif has(
        head,
        r"\bdeeltijd",
        r"part.?time",
        r"mi-temps",
        r"temps partiel",
        r"halftijd",
        r"\b4/5",
        r"\b[1-9]0\s?%",
    ):
        regime = "deeltijds"
    elif has(desc[:3000], r"\bvoltijd", r"full.?time", r"\b38u", r"38 uur"):
        regime = "voltijds"
    elif has(desc[:3000], r"\bdeeltijd", r"part.?time", r"halftijd", r"\b4/5"):
        regime = "deeltijds"
    percentage = int(pct[1]) if pct and 10 <= int(pct[1]) <= 100 else None
    if percentage and percentage < 100 and not regime:
        regime = "deeltijds"

    sector = _tags(f"{titel} {org} {hints}", SECTOR_RULES) or _tags(desc[:2000], SECTOR_RULES)
    functie = _tags(f"{titel} {hints}", FUNCTIE_RULES) or _tags(desc[:1500], FUNCTIE_RULES)

    thuiswerk = job.get("thuiswerk_hint")
    if not thuiswerk:
        if has(desc, r"\bvolledig (?:van )?thuis", r"fully remote", r"100\s?% remote"):
            thuiswerk = "ja"
        elif has(
            desc,
            r"\bthuiswerk",
            r"\btelewerk",
            r"\bhybride",
            r"\bhybrid",
            r"\bremote",
            r"plaatsonafhankelijk",
        ):
            thuiswerk = "hybride"
        else:
            thuiswerk = "onbekend"

    taal = "nl"
    if has(f"{titel} {desc[:800]}", r"\b(nous|vous|chargé|poste|emploi|offre)\b"):
        taal = "fr"
    elif has(f"{titel} {desc[:800]}", r"\b(we are|you will|looking for|the role)\b"):
        taal = "en"

    return {
        "contract": contract or ["onbekend"],
        "regime": regime or "onbekend",
        "percentage": percentage,
        "sector": sector[:3] or ["andere"],
        "functietype": functie[:3] or ["andere"],
        "provincie": provincie(job.get("locatie")) or provincie(job.get("organisatie")),
        "thuiswerk": thuiswerk,
        "taal": taal,
    }
