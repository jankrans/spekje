# Werkwijze — dagelijkse jobsearch

## Bestandsstructuur

```
Jobzoeker Nina/
├── PROFIEL.md        # wie/wat we zoeken — bron van waarheid
├── BRONNEN.md        # waar we zoeken (tiers + rotatie)
├── WERKWIJZE.md      # dit bestand: proces + dagelijkse prompt
└── jobs/
    ├── tracker.md    # actieve lijst, afvinkbaar
    └── archief.md    # afgewezen/verlopen — dedup-geheugen
```

## Dagelijks stappenplan

1. **Lees** `PROFIEL.md` (criteria) en `jobs/tracker.md` + `jobs/archief.md` (wat we al hebben).
2. **Zoek** volgens `BRONNEN.md`: alle tiers, elke dag (Tier 1 eerst — meest gericht).
3. **Dedup vóór toevoegen** — een vacature is dubbel als in tracker.md of archief.md al staat:
   - dezelfde vacature-URL, **of**
   - dezelfde slug `organisatie--functietitel` (kleine letters, spaties → `-`).
   Zelfde job op meerdere boards? Eén entry, link naar de originele werkgever-URL.
4. **Scoor** elke nieuwe vacature (⭐–⭐⭐⭐, criteria in PROFIEL.md). Rode vlaggen → direct naar archief met reden. **Stages: enkel BIS-stages** — gewone stages niet toevoegen.
5. **Voeg toe** in de juiste subsectie van "Te bekijken" (Productie & podium / Events & project / Communicatie & redactie / BIS-stages), gesorteerd op score en dan deadline.
6. **Onderhoud**: deadline verstreken → verplaats naar archief.md met `reden: verlopen`.
7. **Rapporteer** kort: X nieuwe (waarvan Y ⭐⭐⭐), deadlines die deze week vervallen.

## Dagelijkse prompt (voor manueel gebruik / backup)

```
Dagelijkse jobsearch voor Nina. Werk in de map "Jobzoeker Nina".

1. Lees PROFIEL.md, BRONNEN.md, jobs/tracker.md en jobs/archief.md.
2. Zoek nieuwe vacatures op alle bronnen in BRONNEN.md (Tier 1 → 2 → 3).
3. Dedup: sla alles over waarvan de URL of de slug (organisatie--functietitel)
   al in tracker.md of archief.md staat.
4. Scoor nieuwe matches (⭐–⭐⭐⭐) volgens de criteria in PROFIEL.md.
   Enkel BIS-stages; gewone stages overslaan.
5. Voeg ze toe in de juiste subsectie van "Te bekijken" in jobs/tracker.md
   (Productie & podium / Events & project / Communicatie & redactie / BIS-stages),
   gesorteerd op score en dan deadline.
6. Verplaats verlopen deadlines naar archief.md.
7. Geef een korte samenvatting: aantal nieuw, toppers, deadlines deze week.
```

## Wekelijks (zondag)

- Tracker opschonen: alles afgevinkt zonder vervolg → archief
- PROFIEL.md bijstellen als Nina's voorkeuren scherper worden
- Nieuwe bronnen uit de week toevoegen aan BRONNEN.md

## Afspraken

- Tracker "Te bekijken" heeft **vaste subsecties**: Productie & podium / Events & project / Communicatie & redactie / BIS-stages. Nieuwe jobs in de juiste subsectie, gesorteerd op score (⭐⭐⭐ eerst) en dan deadline. Lege subsectie krijgt `_geen openstaande vacatures_`
- Archief nooit leegmaken (dedup-geheugen)
- Elke entry heeft een deadline indien bekend — geen deadline = `deadline —`
- Bij twijfel over een match: toevoegen met ⭐ en laten beslissen door Nina, niet stilzwijgend weglaten
