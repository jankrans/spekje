# Jobzoeker Nina

Dagelijkse screening van vacatures in de culturele sector (en daarbuiten waar relevant), gescoord op Nina's profiel,
gepubliceerd op `/jobs` van de spekje-site achter login.

## Voor Nina

1. Open `https://<site>/jobs/` en log in.
2. **Ranking**: alle open vacatures, hoogste score eerst. **Nieuw**: wat sinds de vorige run binnenkwam.
3. Per vacature: **Interesse**, **Gesolliciteerd**, **Gesprek**, of **Geen interesse** (met korte reden).
   Via `…`: Aanbod, Afgewezen door werkgever, Bekeken, Reset, en een notitieveld.
   Alles wordt meteen bewaard en bij de volgende run meegenomen: afgewezen types zakken in score.
4. **Mijn lijst**: alles waar ze mee bezig is. **Zelf zoeken**: één-klik zoekopdrachten op sites die niet
   automatisch kunnen (Indeed, Jobat, interim, ...). Iets gevonden? Aan Claude doorgeven, dan komt het in de lijst.

Score met `*` = voorlopige heuristische score; zonder `*` = beoordeeld door Claude met motivatie.

## Hoe het werkt

```
bronnen.yaml ──► scrape (45+ bronnen) ──► jobs.json (alles, nooit verwijderd)
                                              │
site-feedback (Netlify Blobs) ──► feedback.json
                                              │
                    classificeren + heuristische score (profiel.yaml, feedback)
                                              │
                    detailpagina's ophalen (beschrijving, deadline/start/einde met bron)
                                              │
                    review_queue.json ──► Claude beoordeelt ──► reviews.json
                                              │
             OVERZICHT.md · vacatures/*.md · GEEN_INTERESSE.md · ARCHIEF.md · runs/*.md · site/data/jobs.json
                                              │
                                git push ──► Netlify ──► /jobs (login)
```

- **Dagelijks**: scheduled task start een Claude-sessie die `/jobrun` uitvoert (`.claude/commands/jobrun.md`).
- **Manueel**: in Claude Code in deze repo `/jobrun`, of enkel de pipeline: `cd jobs && uv run jobzoeker run`.

## Categorieën

| Veld | Waarden |
|---|---|
| contract | vast, tijdelijk, vervanging, freelance, interim, stage, bis-stage, flexi, studentenjob, vrijwilliger, onbekend |
| regime | voltijds, deeltijds (+ percentage), onbekend |
| sector | festival/events, film/AV, muziek, podiumkunsten, museum/erfgoed, cultuurcentrum/lokaal, toerisme, beeldende kunst, sociaal-cultureel, andere |
| functietype | productie, techniek, events/logistiek, hospitality/onthaal, publiekswerking, communicatie/marketing, zakelijk/administratie, programmatie/artistiek, project/coördinatie |
| thuiswerk | ja, hybride, nee, onbekend |
| provincie | afgeleid uit locatie |

## Datums

Elke datum (publicatie, deadline, start, einde contract) heeft een bron: `lijst:<bron>` (gestructureerd veld op de
vacaturesite), `detail-jsonld`, `detail-tekst` (met citaat), `claude` (geverifieerd in de tekst) of `nina`.
Onbekend blijft onbekend: er wordt niet gegokt.

## Niets gaat verloren

- `data/jobs.json` bewaart elke gescrapete vacature, ook irrelevante. Verlopen of offline gegane vacatures krijgen
  een vlag en verhuizen naar het archief.
- Elke feedback-klik wordt in Netlify Blobs bewaard mét historiek en apart gelogd, en bij elke run naar
  `data/feedback.json` in git gesynct. Offline klikken worden in de browser gebufferd.
- `data/runs.json` + `runs/<datum>.md`: log per run en per bron.

## Commando's

```bash
cd jobs
uv run jobzoeker run                         # alles behalve Claude-review
uv run jobzoeker scrape --only cultuurjobs   # één bron testen
uv run jobzoeker queue                       # review-queue tonen
uv run jobzoeker review-import data/reviews_in/2026-10-05.json
uv run jobzoeker feedback <id> geen_interesse "te ver"
uv run jobzoeker add <url> "<titel>" --organisatie X --locatie Gent --deadline 2026-10-31
uv run jobzoeker stats
```

## Configuratie

- `profiel.yaml`: trefwoorden, uitsluitingen, locatievoorkeur, contractvoorkeur, zoektermen.
- `bronnen.yaml`: bronnen + handmatige zoeklinks. Onderzoek en status per bron: `BRONNEN.md`.
- `jobs/.env` (niet in git): `JOBS_SITE_URL`, `JOBS_AUTH`.
- Login wijzigen: `JOBS_AUTH_SHA256` env var in Netlify = sha256 van `gebruiker:wachtwoord`.
