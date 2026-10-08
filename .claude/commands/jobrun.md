---
description: Dagelijkse vacature-run voor Nina (scrapen, beoordelen, publiceren)
---

Voer de dagelijkse vacature-run uit. Werk in `jobs/`. Volg de stappen exact; sla niets over.

## 1. Pipeline draaien

```bash
cd jobs && uv run jobzoeker run
```

Dit haalt eerst Nina's feedback van de site (`/jobs/api/feedback`), scrapet alle bronnen uit `bronnen.yaml`,
haalt detailpagina's op, classificeert, scoort heuristisch en schrijft `data/review_queue.json`.
Vereist `JOBS_SITE_URL` en `JOBS_AUTH` (in `jobs/.env` of als env var). Ontbreken ze: ga verder, maar meld het.

## 2. Kapotte bronnen herstellen

Lees `runs/<vandaag>.md`. Bron met `NEE` en niet `optional`: open de pagina, pas de adapter in
`src/jobzoeker/sources/` aan en test met `uv run jobzoeker scrape --only <key>`. Lukt het niet binnen redelijke tijd:
noteer het in je rapport. Een bron met 0 items die normaal items heeft, is ook verdacht.

## 3. Review-queue beoordelen

Lees eerst: `profiel.yaml`, `INTAKE.md` (antwoorden van Nina), `GEEN_INTERESSE.md` (haar redenen, belangrijk),
en dan `data/review_queue.json`.

Per item beslis je (desnoods via WebFetch op de url als de info in de queue te mager is):

- **score** 0-100 voor Nina specifiek (zie `INTAKE.md`):
  - 90+: productie, events/festival, zaal/publiek, communicatie, redactie of projectwerk in podiumkunsten of
    een cultuurhuis; starter/junior haalbaar; Gent/Antwerpen/Leuven/Brussel; geen "enkel mails"-job
  - 70-89: sterke match met één compromis (locatie, kort/deeltijds contract, 3+ jaar ervaring gevraagd, media
    of events buiten kunsten)
  - 50-69: misschien; meerdere compromissen of grotendeels administratief
  - 30-49: zwak
  - <30: niet voor haar. Altijd <30: technische functies (licht/geluid/podiumtechniek/stagehand), stages (ook BIS),
    pure contentcreatie (video/design/foto als kern), boekhouding, onbetaald/vrijwilligerswerk, buiten cultuur/media/events
  - Weeg haar "geen interesse"-redenen (`GEEN_INTERESSE.md`, incl. 37 afgevinkte uit juli) mee, maar mild: een
    reden is een voorkeur, geen harde uitsluiting. Ze wil de markt blijven zien. Bv. "barema C is te laag" of "niet
    in Kortrijk" → een paar punten minder en het vermelden als minpunt, niet onder de 50 duwen of verbergen.
  - Loon: haar huidige job is PC 304 loongroep C+ (zie `BAREMAS.md`). Vermeld barema als plus- of minpunt
    als het in de vacature staat; nooit een reden om een verder goede match laag te scoren.
- **samenvatting**: 1 zin, wat de job concreet is (geen marketingtaal).
- **motivatie**: 1-2 zinnen, waarom deze score.
- **pluspunten** / **minpunten**: korte lijstjes.
- Corrigeer categorieën als de heuristiek fout zit: `contract` (lijst uit: vast, tijdelijk, vervanging, freelance,
  interim, stage, bis-stage, flexi, studentenjob, vrijwilliger), `regime` (voltijds/deeltijds), `percentage`,
  `sector`, `functietype`, `thuiswerk` (ja/hybride/nee/onbekend), `provincie`.
- **datums**: enkel invullen als je ze letterlijk in de vacaturetekst zag: `{"deadline": "YYYY-MM-DD",
  "startdatum": "YYYY-MM-DD", "einddatum": "YYYY-MM-DD"}` + `datum_bewijs` met het citaat. Nooit gokken.
  Bij score ≥ 60 en onbekende deadline of start: open de vacature en zoek ze op.
- **duplicaat_van**: id van hetzelfde vacature-item uit een andere bron (zelfde job, andere titel). Het beste/meest
  complete item blijft, het andere krijgt `duplicaat_van`.
- **ruis**: `true` als het geen vacature is.
- **Pagina-watch items** ("Jobpagina X: n vermelding(en) te checken"): open de url, bekijk de vermeldingen. Echte
  vacatures die nog niet in de lijst staan: `uv run jobzoeker add <url> "<titel>" --organisatie ... --locatie ...
  --deadline YYYY-MM-DD --bron <key>`. Het pagina-watch item zelf krijgt `ruis: true`.

Schrijf alles als JSON-lijst naar `data/reviews_in/<YYYY-MM-DD>.json`:

```json
[{"id": "abc123def0", "score": 82, "samenvatting": "...", "motivatie": "...", "pluspunten": ["..."],
  "minpunten": ["..."], "contract": ["tijdelijk"], "regime": "voltijds", "datums": {"deadline": "2026-10-20"},
  "datum_bewijs": {"deadline": "Solliciteren kan tot 20 oktober 2026"}}]
```

Daarna: `uv run jobzoeker review-import data/reviews_in/<YYYY-MM-DD>.json` (dit bouwt ook markdown + site).
Grote queue (eerste run): werk in batches van ~40, importeer per batch.

## 4. Publiceren

```bash
cd .. && git add -A && git commit -m "jobrun <YYYY-MM-DD>: <n> nieuw, <m> beoordeeld" && git push
```

Netlify deployt automatisch. Root `index.html` nooit aanpassen.

## 5. Rapport

Kort, in het Nederlands, geen opvulling:
- Top nieuwe vacatures (score ≥ 70) met deadline en link
- Deadlines binnen 7 dagen voor items met interesse of score ≥ 70
- Kapotte bronnen en wat je deed
- Link naar de site: `<JOBS_SITE_URL>/jobs/`
