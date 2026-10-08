# spekje

Twee dingen in deze repo:

1. `index.html` in de root: persoonlijke site. **Niet aanpassen** tenzij Jan het expliciet vraagt.
2. `jobs/`: vacature-zoeker voor Nina, gepubliceerd op `/jobs` (login via `netlify/edge-functions/jobs-auth.ts`).

## Jobs-workflow

- Dagelijkse run: `/jobrun` (zie `.claude/commands/jobrun.md`). Volledige uitleg: `jobs/README.md`.
- CLI: `cd jobs && uv run jobzoeker <run|scrape|enrich|queue|review-import|feedback|add|build|stats|show>`.
- Bron van waarheid: `jobs/data/jobs.json` (alle gescrapete vacatures, nooit verwijderen), `data/feedback.json`
  (Nina's statussen + redenen, gesynct met Netlify Blobs), `data/reviews.json` (Claude-scores).
  Markdown (`OVERZICHT.md`, `vacatures/`, `GEEN_INTERESSE.md`, `ARCHIEF.md`) en `site/data/jobs.json` worden
  gegenereerd: niet met de hand bewerken, wel `profiel.yaml` en `bronnen.yaml`.
- Nina's feedback via chat: "geen interesse in X want Y" → `uv run jobzoeker feedback <id> geen_interesse "Y"`.
  Haar redenen nooit super streng toepassen (zie `/jobrun` stap 3): ze wil blijven zien wat er op de markt komt.
  Statussen: nieuw, bekeken, interesse, gesolliciteerd, gesprek, aanbod, afgewezen, geen_interesse.
- Vacature die ze zelf vond: `uv run jobzoeker add <url> "<titel>" --organisatie ... --bron manueel`.
- Nieuwe bron: adapter in `jobs/src/jobzoeker/sources/`, entry in `bronnen.yaml`, rij in `BRONNEN.md`.
- Na wijzigingen: `uv run jobzoeker build`, commit, push. Netlify bouwt via `scripts/netlify-build.sh`
  (publiceert enkel root-site + `jobs/site`, nooit data/markdown).
- Env (in `jobs/.env`, niet in git): `JOBS_SITE_URL=https://<site>.netlify.app`, `JOBS_AUTH=gebruiker:wachtwoord`.
