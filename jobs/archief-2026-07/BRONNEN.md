# Bronnen

> **Alle tiers worden elke dag gecheckt.** Tiers geven enkel de zoekvolgorde aan: meest gerichte bronnen eerst.

## Tier 1 — gespecialiseerde boards

| Bron | URL | Focus |
|---|---|---|
| Cultuurjobs | https://www.cultuurjobs.be/ | Hét board voor de culturele sector Vlaanderen |
| mediarte | https://www.mediarte.be/nl/vacatures | Audiovisuele sector: TV, radio, film, productiehuizen |
| Podiumkunsten.be | https://www.podiumkunsten.be/vacatures | Podiumkunsten & muziek |
| Kunstenpunt | https://www.kunsten.be/ | Vacatures & stages kunstenveld |
| cult! | https://www.cult.be/vacatures | Cultuur- en gemeenschapscentra |
| Socius | https://socius.be/vacaturebank/ | Sociaal-cultureel werk (vacaturebank, ook lijst op https://socius.be/vacature/) |
| 11.be | https://11.be/vacatures | Non-profit/social profit, betaald én vrijwillig (dagelijkse/wekelijkse mail mogelijk) |
| publiq | https://www.publiq.be/nl/vacaturebank | Cultuur- & vrijetijdssector, filterbaar op provincie/categorie (toegevoegd 2026-07-07) |
| FARO | https://faro.be/vacatures | Erfgoedsector: musea, archieven — sterk voor kunstwetenschappen; RSS: https://faro.be/vacatures/rss.xml (toegevoegd 2026-07-07) |
| VI.BE | https://vi.be/pages/vacatures | Muzieksector: venues, boekers, management — gecureerd, klein maar gericht (toegevoegd 2026-07-07) |

## Tier 2 — algemene boards (met filters)

| Bron | Zoektermen |
|---|---|
| VDAB — https://www.vdab.be/vindeenjob/jobs/cultuur | "cultuur", "productiemedewerker", "communicatiemedewerker cultuur" |
| LinkedIn Jobs | "productiemedewerker", "redacteur", "projectmedewerker cultuur" — regio Gent/Antwerpen/Brussel/Leuven |
| Indeed België | "media televisie", "productiehuis", "cultuurcentrum" |

## Tier 3 — rechtstreeks bij organisaties

**Omroepen & media:** VRT (jobs.vrt.be), DPG Media, Play Media/SBS, regionale zenders (AVS, ATV, ROB, BRUZZ)

**Productiehuizen:** Woestijnvis, Hotel Hungaria, De Mensen, Panenka, Geronimo, Shelter, Bargoens

**Podiumkunsten & cultuurhuizen:** NTGent, Viernulvier (Vooruit), Opera Ballet Vlaanderen, Toneelhuis, deSingel, hetpaleis, Ancienne Belgique, Bozar, KVS, Kaaitheater, Flagey, 30CC (Leuven), OPEK, nona (Mechelen), De Bijloke, Handelsbeurs, Kunstencentrum Vooruit, STUK Leuven (stuk.be/nl/vacatures + aparte stagepagina stuk.be/nl/stages), Concertgebouw Brugge (concertgebouw.recruitee.com), De Warande (Turnhout), Beursschouwburg (Brussel), CAMPO (Gent), Het Depot (Leuven)

**Literatuur:** Passa Porta (passaporta.be/nl/stages-en-vacatures), deBuren (deburen.eu/nieuws-en-oproepen?type=oproepen), Poëziecentrum Gent — sporadisch vacatures, sluit aan bij master letterkunde

**Musea & erfgoed:** M Leuven, MSK Gent, S.M.A.K., KMSKA, MAS — posten doorgaans op FARO (Tier 1), dus daar checken volstaat meestal

**Entertainment & events:** Studio 100, Live Nation Belgium, Greenhouse Talent, Sportpaleis Group, festivals (Gent Festival, Boekenbeurs, Theaterfestival)

**Overheid & fondsen:** Departement Cultuur, Jeugd & Media (vlaanderen.be/cjm), Literatuur Vlaanderen, steden (Gent, Antwerpen, Leuven, Mechelen — cultuurdiensten)

## Notities

- **Live-verificatie verplicht (les van 2026-07-06):** zoekresultaat-snippets en aggregator-caches (Indeed, LinkedIn, 11.be, Google) tonen vaak weken oude of al ingevulde vacatures. Alleen toevoegen wat vandaag op een live gefetchte detail- of Tier 1-lijstpagina staat. Bij Indeed/LinkedIn-vondsten: altijd doorklikken naar de werkgeversite en die URL gebruiken. Let op verouderingssignalen: "vacature verlopen", oude "online sinds"-datum, oude datum in paginatitel.
- **jobs.vrt.be rendert client-side** (webfetch + directe job-URL's komen beide leeg terug, ondanks een "X functies"-teller die wél server-side meekomt) → zonder Chrome-toegang niet betrouwbaar te checken. Retry-poging 2026-07-07: WebSearch site:jobs.vrt.be geeft kandidaat-URL's, maar die job-detailpagina's renderen ook client-side dus niet verifieerbaar als "live". Enige server-side content is het "Job(s) in de kijker"-blok op de listingpagina (vandaag: onthaalmedewerker kinderdagverblijf vzw Ukkepuk — geen match).
- 11.be en job.antwerpen.be renderen client-side → webfetch komt leeg terug; vacatures daar alleen via een andere verifieerbare bron toevoegen
- Ook client-side (webfetch leeg): warande.be, beursschouwburg.be, campo.nu, kunsten.be/vacatures → checken via de cultuurjobs organisatie-index: https://www.cultuurjobs.be/organisaties/ (handige index van alle organisaties die op Cultuurjobs posten). Werkt ook voor STUK, Concertgebouw Brugge, Poëziecentrum, Het Depot, M Leuven, Kunstenpunt — elke organisatie heeft een eigen `/organisatie/<naam>/`-pagina met actuele + afgesloten vacatures, ook als de eigen site client-side rendert of geen eigen vacaturepagina heeft.
- **VDAB:** de statische landingpagina's `vdab.be/vindeenjob/jobs/<trefwoord>` (bv. `/cultuur`) zijn server-side gerenderd en dus prima live te fetchen — maar de gerichte zoekfilter (`vindeenjob/vacatures?query=...`) is client-side (toont enkel "Toepassing laden..."). Voor gerichte trefwoorden dus altijd de `/jobs/<trefwoord>`-pagina's gebruiken, niet de query-parameter.
- publiq (19 pagina's), FARO en VI.BE zijn alle drie volledig server-side gerenderd en dus vlot te fetchen — bevestigd 2026-07-07, goede vaste toevoeging aan Tier 1.
- Culturele sector publiceert vaak vrijdag/maandag → maandag extra grondig zoeken
- Veel vacatures verschijnen alleen op eigen site, niet op boards → Tier 3 niet overslaan
- Nieuwe bron ontdekt? Hier toevoegen met datum
- **VDAB `/jobs/cultuur`** (2026-07-08): 3674 treffers, overweldigend generieke ruis (boekhouder, techniek, verkoop...) door brede trefwoordmatch. Niet efficiënt om dagelijks te doorzoeken — Tier 1-boards (cultuurjobs, publiq, FARO) geven vrijwel altijd dezelfde vacatures sneller en gerichter.
- Cult!, publiq, FARO en VI.BE tonen structureel dezelfde vacatures als cultuurjobs.be (zelfde postings, andere aggregator) — bevestigd 2026-07-08. Bij overlap telt de cultuurjobs-URL als canoniek voor dedup.
- **talents.vaia.com (StudySmarter/Vaia jobboard) — NIET betrouwbaar, niet gebruiken** (ontdekt 2026-07-09): scraper/aggregator met AI-gegenereerde bedrijfsomschrijvingen (bv. "Podiumkunsten is a leading organization... in de USA" — onzin) en fake USD-salarisschattingen voor Belgische jobs. Alle vacatures op de podiumkunsten-pagina tonen "Posted 3-4 days ago" ongeacht werkelijke leeftijd: STUK copywriter-vacature had sollicitatiedeadline 7 juni 2026 (al verstreken), Muziekmozaïek-projectmedewerker had deadline 1 maart 2026 (al verstreken) — beide dus stale scrapes. Geen nieuwe/live bron toevoegen.
- **VI.BE-vacaturelijst is zelf vaak stale** (2026-07-12): de "Jobs"-lijst op vi.be/vacatures bevatte enkel al lang verlopen/gearchiveerde postings (Democrazy deadline 5 juli, Greenhouse Talent en 5to9 Management deadline 10-14 juli) — geen van de vermelde vacatures was nog nieuw. Wel nuttig als kruisverwijzing, maar niet blind vertrouwen op de deadline die er vermeld staat; altijd de onderliggende cultuurjobs/werkgever-URL zelf checken.
- **deBuren.eu heeft twee "evergreen" stagepagina's zonder deadline** (stage digitale contentcreatie, literaire stage — beide gedateerd sept. 2024 maar permanent online): dit zijn doorlopende oproepen, geen concrete nieuwe vacatures. Al gearchiveerd als gewone stage (enkel BIS-stages) — niet elke dag opnieuw hoeven te fetchen, herkenbaar aan de vaste URL's `stage-digitale-contentcreatie-en-storytelling-bij-deburen` en `literaire-stage-bij-deburen2024`.
- **web_fetch vereist provenance:** een URL kan pas gefetcht worden nadat hij is opgedoken in een WebSearch-resultaat (of eerdere fetch) in dezelfde sessie — rechtstreeks fetchen van een bekende bron-URL zonder voorafgaande WebSearch geeft een "URL not in provenance set"-fout. Werkwijze: eerst kort `WebSearch` met `allowed_domains` op de doelsite, dan pas `web_fetch` op de exacte listing-URL.
- **cultuurjobs.be, mediarte.be, podiumkunsten.be, cult.be, faro.be en publiq.be zijn alle server-side gerenderd en vlot te fetchen** (bevestigd 2026-07-13) — hun volledige live listings overlappen sterk (zelfde vacatures via meerdere aggregators), cultuurjobs.be blijft de meest complete lijst. Kruisverwijzing tussen deze bronnen bevestigt dedup betrouwbaar.
- **ntgent.be rendert client-side** (2026-07-13): zowel `/nl/vacatures` als `/en/vacancies` komen leeg terug (enkel nav/afbeeldingen, geen vacature-content); losse nieuwsartikel-URL's over vacatures (bv. "NTGent zoekt een Productieleider") redirecten naar de algemene nieuwspagina, dus niet meer individueel opvraagbaar — teken dat de post verwijderd/verlopen is. Cultuurjobs.be's NTGent-organisatiepagina toont enkel oude (2021-2022) postings. NTGent dus voorlopig niet betrouwbaar te checken zonder Chrome-toegang.
- **dpgmedia.be is geblokkeerd voor WebSearch** ("domain not accessible to our user agent") — DPG Media-vacatures enkel via generieke zoekopdrachten (zonder allowed_domains) of aggregators checken.
- **woestijnvis.be/en/vacatures rendert client-side** (leeg bij fetch, 2026-07-13); LinkedIn-vacature "Regie/Productie Assistent(e)" bij Woestijnvis heeft een job-ID (3824667636) uit een veel oudere reeks dan huidige 2026 LinkedIn-ID's (~4,4 miljard) — duidelijk verlopen/stale, niet gebruikt.
- **passaporta.be publiceert een oude PDF-vacature die via Google nog jaren blijft opduiken** (ontdekt 2026-07-14): "Publieksmedewerker_PassaPorta_vacature.pdf" had deadline 27 augustus **2023** — de live pagina `passaporta.be/nl/stages-en-vacatures` bevestigt "geen stages/vacatures beschikbaar op dit moment". PDF-bestanden van organisatiesites altijd op interne datum/deadline checken, niet enkel op het feit dat de zoekmachine ze toont.
- **VI.BE-vacaturelijst opnieuw stale bevonden** (2026-07-14, na eerdere vaststelling 2026-07-12): alle 4 vermelde "Jobs" hadden deadlines die al voorbij waren (5, 10, 10, 14 juli) — pagina wordt duidelijk niet consequent bijgewerkt. Blijven overslaan tenzij een vacature ook via cultuurjobs/werkgever-URL bevestigd wordt.
- **cultuurjobs.be, mediarte.be, faro.be, podiumkunsten.be en publiq.be geven elk een deel unieke vacatures** (bevestigd 2026-07-14): overlap is groot maar niet volledig — publiq.be had als enige de BIS-communicatiestage bij Histories, cult.be als enige de communicatie- en projectmedewerker bij cult! zelf. Alle vijf dus dagelijks blijven checken, niet enkel cultuurjobs.be.
- **studio100.com vacature-detailpagina's redirecten naar een client-side gerenderde algemene vacaturelijst** (ontdekt 2026-07-15): directe URL naar een specifieke vacature (bv. "Productieassistent Theater / Company Manager") komt leeg terug met enkel Vue-templateplaceholders (`v{publication.title}` e.d.) — niet live te verifiëren zonder Chrome-toegang. Interessante vacatures wel via WebSearch vindbaar, maar niet toevoegen zolang de detailpagina niet leesbaar is.
- **flagey.be vacaturepagina's geven een lege/onleesbare fetch** (2026-07-15): individuele vacature-URL's (bv. "coördinator publicaties & redacteur") komen zonder bruikbare content terug — niet live te verifiëren, voorlopig overslaan.
- **Toneelhuis, KVS en hetpaleis gecheckt (2026-07-15), geen nieuwe matches**: Toneelhuis heeft momenteel geen open vacatures (enkel doorlopende stageplekken, geen BIS); KVS en hetpaleis tonen enkel oudere/gearchiveerde vacatures of nemen geen spontane sollicitaties aan buiten techniek. Wel bruikbaar als Tier 3-bron, periodiek blijven checken.
- **VI.BE-vacaturelijst bevat nog steeds enkel verlopen postings** (2026-07-15, derde keer na 2026-07-12 en 2026-07-14): alle 4 vermelde jobs waren al lang verstreken deadlines (5, 10, 10, 14 juli). Blijft een zwakke bron, enkel als kruisverwijzing bruikbaar.
- **Socius-vacaturebank leunt sterk naar algemeen sociaal-cultureel werk** (2026-07-15): merendeel van de vacatures (welzijnswerk, kringwinkels, gemeenschapswerk) valt buiten Nina's sectoren; wel nuttig voor kruisverwijzing naar reeds bekende vacatures (bv. Docwerkers), zelden een unieke goede match.
- **publiq.be-vacaturebank blijft een goede unieke bron** (2026-07-16): "Administratief assistent artistieke programmering" bij KANAL (nieuw Kanal-Centre Pompidou-museum Brussel) stond enkel op publiq, niet op cultuurjobs/mediarte/faro/podiumkunsten — de moeite waard om de volledige 22-pagina's-lijst periodiek te doorbladeren, niet enkel pagina 1.
- **mediarte-vacaturelijst pagina 2 bevat doorgaans enkel schoolstages** (2026-07-16): "Schoolstage Figuratie-assistent" en "Schoolstage Productie-assistent" bij A Team Productions — geen BIS, dus niet relevant; wel bevestigt dit dat de volledige (2 paginas) lijst elke dag gecheckt moet blijven worden voor volledigheid.
- **Cross-posting bevestigd** (2026-07-16): Histories vzw's BIS-communicatiemedewerker-stage staat zowel op publiq (deadline 10/8) als cultuurjobs (deadline 9/8) — kleine deadline-afwijkingen tussen aggregators zijn normaal bij dezelfde vacature, dedup op organisatie+functie i.p.v. exacte deadline.
- **Tier 2/3-ronde 2026-07-17 leverde geen nieuwe live matches op** — vrijwel alle Tier 3-organisatiesites tonen ofwel geen open vacatures, ofwel enkel vacatures die niet matchen (technisch, boekhouding, vrijwilligerswerk, design), ofwel vacatures met reeds verstreken deadline. Concreet:
  - **Bozar** (bozar.be): jobdetailpagina's (Digital Project Officer, Production Supervisor Music, Digital Coordinator, Education Officer) blijven online lang na de sollicitatiedeadline (gevonden deadlines: 2023-04-12, 2024-07-15, 2024-08-25, 2025-10-26 — alle al lang verstreken). Google/WebSearch blijft ze indexeren als "actueel". Altijd de deadline in de tekst zelf checken, niet enkel of de pagina bestaat.
  - **Kaaitheater** (kaaitheater.be): "Junior Programma Medewerker" en "Coördinator Publieke Activiteiten" zijn beide **2021**-postings (herkenbaar aan de URL-datum op cultuurjobs.be: `/2021/...`), nog steeds live en goed geïndexeerd. Enige actuele Kaaitheater-vacature (via cultuurjobs.be-kruisverwijzing): Medewerker Theatertechniek (technisch, geen match, deadline 2026-08-23).
  - **Gent Festival van Vlaanderen** (gentfestival.be/nl/crew/vacatures): de live vacaturelijst-pagina toont expliciet "**Geen resultaten gevonden**" — alle via WebSearch gevonden functies (Halftijdse medewerker partnerships, Manager Communicatie, Assistent communicatie STROOM) zijn dus stale snippets, geen actuele vacatures.
  - **het TheaterFestival** (theaterfestival.be): "Productiecoördinator"-vacature (gepost 16/01/2026) had sollicitatiedeadline "zondag 8 februari" — al lang verstreken ondanks recente postdatum. Festivalcoördinator-detailpagina gaf lege fetch.
  - **S.M.A.K.** (smak.be/en/about-s.m.a.k/work-at-s.m.a.k) en **Concertgebouw Brugge** (concertgebouw.recruitee.com): beide bevestigen expliciet geen open vacatures op dit moment.
  - **Literatuur Vlaanderen**: expliciet niet aan het aanwerven.
  - **Poëziecentrum Gent**: enige gevonden vacature (administratief medewerker) dateert van 12/2024, deadline toen al 31/12/2024 — en betreft bovendien boekhouding/personeelsadministratie (rode vlag).
  - **KMSKA** (kmska.be/nl/jobs): huidige vacatures zijn Teamhoofd Facility (technisch) en twee stages (Pers&PR, Marketing) — geen van beide expliciet BIS, dus niet toegevoegd.
  - **Geronimo** (geronimo.be/jobs): "Stagiair" is een evergreen algemene oproep zonder BIS-vermelding of deadline (spontaan solliciteren); "Boekhouder" is rode vlag.
  - **De Bijloke** (bijloke.be/nl/onze-vacatures): enige vacatures zijn onbezoldigd bestuursmandaat en vrijwilligerswerk (ticketing/onthaal) — geen van beide een match.
  - Client-side/onleesbaar bij fetch (nieuw bevestigd 2026-07-17, nog steeds niet betrouwbaar te verifiëren): desingel.be/nl/blog/item/vacature-*, nona.be/nl/vacatures, job.mleuven.be, shelter.be/vacatures, jobs.hotelhungaria.be + hotelhungaria.be/nl/jobaanbiedingen, vlaanderen.be/cjm/nl/over-cjm/jobs.
  - **CAMPO** (campo.nu): geen vacaturepagina en geen cultuurjobs.be-organisatiepagina gevonden; niet te verifiëren via huidige methodes.
  - VDAB, LinkedIn en Indeed leverden voor de Tier 2-zoektermen geen nieuwe, concreet naar een werkgever-detailpagina te herleiden matches op (enkel generieke aggregator-listingpagina's).
