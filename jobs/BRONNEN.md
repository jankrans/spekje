# Vacaturebronnen

Onderzoek van 2026-10-04: meer dan 100 bronnen bekeken, waarvan 70+ live en relevant bevonden. De kolom **Pipeline** zegt hoe de bron in de dagelijkse run zit:

- `auto`: gescraped door de pipeline (adapter in `src/jobzoeker/sources/`, config in `bronnen.yaml`)
- `watch`: pagina-watch (wijziging in jobpagina wordt gemeld, geen losse vacatures)
- `alert`: blokkeert scrapers (Cloudflare/F5/login). Jobalert per mail instellen of manueel via de zoeklinks op de site
- `via X`: geen eigen bron nodig, vacatures verschijnen op aggregator X

Geteste toegang: **OK** = machine-leesbaar, **403-bot** = anti-bot, **unreach** = niet bereikbaar vanuit de cloud-sandbox (lokaal of via GitHub Actions wel te proberen).

## Kern: sector-aggregators

Samen met VDAB en jobsolutions dekken deze vier bijna alle relevante vacatures. Dezelfde vacature staat vaak op meerdere, de pipeline dedupliceert op titel + organisatie.

| Bron | Lijst | Dekking | Relevantie | Toegang | Pipeline |
|---|---|---|---|---|---|
| cultuurjobs.be | https://www.cultuurjobs.be/ | Alle cultuur, ~100 actief | hoog | WP REST API | auto |
| publiq vacaturebank | https://www.publiq.be/nl/vacaturebank | Cultuur + vrije tijd, ~165 | hoog | HTML, GET-filters | auto |
| podiumkunsten.be | https://www.podiumkunsten.be/vacatures | Podiumkunsten + muziek (PC 304), incl. flexi/freelance/stage | hoog | HTML (Drupal) | auto |
| mediarte.be | https://www.mediarte.be/nl/vacatures | Film/tv/AV (PC 227/303.01) | hoog | HTML | auto |
| H/LFTIJDS | https://www.halftijds.be/vacatures-all | Deeltijdse jobs, deels cultuur | middel | RSS | auto |
| CreativeSkills | https://www.creativeskills.be/ | Creatief/communicatie | middel | RSS | auto |
| Socius | https://socius.be/vacature/ | Sociaal-cultureel werk | laag-middel | RSS | auto |
| VI.BE | https://vi.be/vacatures | Muzieksector | middel | HTML (vaak PDF) | auto |
| cult! | https://www.cult.be/vacatures | Kleine selectie | laag-middel | HTML | auto |
| FARO | https://faro.be/vacatures | Erfgoed/musea | middel | RSS achter Cloudflare | auto (best effort) |
| VVBAD | https://www.vvbad.be/vacatures | Bib/archief/erfgoed | laag | HTML | watch |
| Circuscentrum | https://circuscentrum.be/nl/kansen | Circus | laag | HTML | watch |
| Brussels Museums | https://www.brusselsmuseums.be/nl/jobs | Brusselse musea | laag-middel | HTML | watch |
| Cinergie | https://www.cinergie.be/annonces | Film (FR) | laag-middel | HTML | auto |
| culture.be (FWB) | https://www.culture.be/vous-cherchez/emploi-stage/ | Franstalige cultuur | middel (FR) | 403-bot | alert |
| Theaterkrant (NL) | https://www.theaterkrant.nl/vacature/ | Nederlandse podiumkunsten | laag | RSS | uit (NL) |
| Kunstenpunt | https://www.kunsten.be/calls/ | Geen vacatures, wel open calls | laag | HTML | – |
| Cultuurloket | https://www.cultuurloket.be | Geen vacaturebank, wel advies statuut/freelance | – | – | – |

Bron om nieuwe bronnen te ontdekken: https://podiumkunsten.be/loopbaan/waar-kan-je-nog-terecht/520/andere-websites-met-vacatures/521

## Festivals en events

| Bron | Lijst | Relevantie | Pipeline |
|---|---|---|---|
| Tomorrowland | https://jobs.tomorrowland.com/ (+ /event-jobs, /Internship, /freelance) | hoog | auto |
| Kursaal Oostende | https://www.kursaaloostende.be/nl/jobs | hoog (lokaal) | auto |
| Film Fest Gent | https://www.filmfestival.be/nl/over-ffg/vrijwilligers-en-jobs | middel | watch |
| Wintercircus Gent | https://www.wintercircus.be/nl/jobs-at-wintercircus | middel | watch |
| Klarafestival | https://klarafestival.brussels/jobs | middel | watch |
| Paradise City | https://www.paradisecity.be/en/jobs | laag-middel | watch |
| Go4Jobs (Ostend Beach e.a.) | https://go4jobs.be | laag-middel | watch |
| Dour, Les Ardentes, MOOOV, eventplanner.be | zie onderzoek | laag | – |
| Live Nation (Rock Werchter, TW Classic) | Workday, 0 Belgische jobs | – | via VI.BE / cultuurjobs |
| Gentse Feesten, Lichtfestival | jobs.gent.be | – | via Stad Gent |
| TAZ, Pukkelpop, Graspop, Lokerse Feesten, Couleur Café, Boomtown, Gent Jazz | geen jobpagina | – | via aggregators, studentjob, interim |

## Film / tv / AV

| Bron | Lijst | Relevantie | Pipeline |
|---|---|---|---|
| mediarte | zie kern | hoog | auto |
| VRT Jobs | https://jobs.vrt.be/nl/vacatures | middel | auto (JSON) |
| VAF | https://www.vaf.be/vacatures | laag | watch |
| DPG Media | – | middel | alert (403-bot) |
| screen.brussels | https://screen.brussels/fr/jobs | ? | alert (403) |

## Venues en organisaties met eigen jobpagina

Bijna alles staat ook op cultuurjobs/publiq. Deze pagina's worden gewatcht zodat niets gemist wordt.

| Organisatie | Jobpagina | Pipeline |
|---|---|---|
| Concertgebouw Brugge | https://concertgebouw.recruitee.com/ | auto (Recruitee API) |
| NTGent | https://www.ntgent.be/nl/vacatures | watch |
| VIERNULVIER | https://www.viernulvier.gent/nl/werken-bij-viernulvier-9qn5 | watch |
| Bozar | https://www.bozar.be/nl/werken-bij-bozar | watch |
| KVS | https://www.kvs.be/nl/ons-huis/vacatures | watch |
| Opera Ballet Vlaanderen | https://www.operaballet.be/nl/werken-bij-opera-ballet-vlaanderen | watch |
| CAMPO | https://www.campo.nu/nl/vacatures-stages-9952 | watch |
| STUK | https://www.stuk.be/nl/vacatures | watch |
| 30CC | https://www.30cc.be/vacatures-stages | watch |
| Design Museum Gent | https://designmuseumgent.be/nl/vacatures | watch |
| MSK Gent | https://www.mskgent.be/over-het-msk/vacatures | watch |
| M HKA | https://www.muhka.be/vacatures/ | watch |
| Kanal | https://kanal.brussels/nl/jobs | watch |
| Mu.ZEE | https://www.muzee.be/nl/museum-1 | watch |
| Westtoer | https://www.westtoer.be/over-ons/werken-bij-westtoer/vacatures | watch |
| De Grote Post, KAAP, S.M.A.K., STAM, BUDA, Cinematek | eigen sites | unreach vanuit sandbox, via aggregators |
| Ancienne Belgique | nieuwsitems op abconcerts.be | via aggregators |

## Overheid

| Bron | Lijst | Relevantie | Pipeline |
|---|---|---|---|
| VDAB | https://www.vdab.be/vindeenjob/vacatures | hoog (incl. interim) | auto (JSON, per zoekterm) |
| jobsolutions.be | https://www.jobsolutions.be/jobs | hoog: cultuurcentra en gemeenten (Oostende, Knokke-Heist, Koksijde, De Panne, Nieuwpoort, Deinze, Kortrijk, Prov. W-Vl, ...) | auto (alle pagina's, lokaal gefilterd) |
| Werken voor Vlaanderen | https://www.vlaanderen.be/werken-voor-vlaanderen/vacatures | middel | auto (JSON) |
| Stad Gent | https://jobs.gent.be/ | middel | auto |
| Stad Oostende | https://jobs.oostende.be/vacatures | middel | auto |
| Stad Brugge (incl. Musea Brugge) | https://www.werkenbijbrugge.be/vacatures | middel | auto |
| Actiris (Brussel) | https://www.actiris.brussels/nl/burgers/vacatures/ | middel | auto (JSON, per zoekterm) |
| talent.brussels | https://www.talent.brussels/nl/vacatures | laag | auto |
| VGC (Brussel) | https://www.vgc.be/vacatures | middel | unreach, watch lokaal |
| Jobpunt Vlaanderen | https://www.jobpunt.be | middel | unreach |
| Provincie Oost-Vlaanderen | https://oost-vlaanderen.be/vacatures-provincie-oost-vlaanderen/alle-vacatures.html | middel | alert (403-bot) |
| werkenvoor.be (federaal) | https://werkenvoor.be/nl/vacatures | laag | alert (403-bot) |

## Generieke jobsites

| Bron | Toegang | Pipeline |
|---|---|---|
| LinkedIn | guest-endpoint, rate-limited | auto (beperkt) + jobalert |
| StepStone | SSR | auto (per zoekterm) |
| Talent.com | SSR | uit (dubbel met VDAB/StepStone) |
| Indeed | 403-bot | alert + zoeklink |
| Jobat | 403-bot | alert + zoeklink |
| Glassdoor, Jooble, Monster | 403-bot | – |
| StudentJob, Student.be | SSR | zoeklink (flexi/event) |
| JobTeaser | SSR | zoeklink (stages) |
| jobsinbrussels.com | HTML | zoeklink |

## Interim

Grotendeels ook zichtbaar in VDAB (leverancier `INTERMEDIAIREN`). Randstad (incl. Tempo-Team), Manpower, Accent, Adecco, Start People, Unique, Synergie, Proman, Daoust: zoeklinks op de site.

## Sociale media en nieuwsbrieven

Facebook-groepen (login nodig, manueel): Vlaanderen licht- en geluidstechnici (`facebook.com/groups/39568210959`), Freelance audio/lighting/visual techniekers Vlaanderen (`/groups/353917018151246`).

Aanbevolen alerts voor Nina zelf: LinkedIn jobalert, Indeed alert, Jobat alert, VDAB jobalert, Werken voor Vlaanderen nieuwsbrief, podiumkunsten.be e-news, publiq/mediarte/cult!/FARO nieuwsbrieven.

## Zoektermen

**NL:** productiemedewerker, productieassistent, productieleider, productiecoördinator, zakelijk medewerker, technisch-artistiek medewerker, podiumtechnicus, stagehand, regieassistent, tourmanager, eventcoördinator, evenementencoördinator, eventmanager, projectmedewerker cultuur, publiekswerking, zaalverantwoordelijke, venue manager, hospitality, artist relations, vrijwilligerscoördinator, festivalmedewerker, cultuurcentrum, kunstencentrum, erfgoedmedewerker, tentoonstellingsmedewerker, programmamedewerker, runner, opnameleider, setassistent, line producer, BIS-stage, flexi-job cultuur

**FR:** chargé(e) de production, assistant(e) de production, régisseur, coordinateur événementiel, chargé(e) de projets culturels, médiation culturelle, administrateur de production, assistant(e) de tournée

**EN:** production assistant, production coordinator, production manager, event coordinator, festival production, artist hospitality, venue coordinator, tour assistant, runner

**Uitsluiten** (industriële "productie"): operator, lijnwerker, ploegen, heftruck, CNC, voedingsindustrie, magazijnier, onderhoudstechnieker.
