(() => {
  "use strict";
  const BASE = "/jobs";
  const API = BASE + "/api/feedback";
  const ACTIEF = ["interesse", "gesolliciteerd", "gesprek", "aanbod"];
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  let DATA = { meta: {}, jobs: [] };
  let FB = {};
  let tab = "top";

  const store = {
    get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* privémodus */ } },
  };

  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("on");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => t.classList.remove("on"), 2200);
  }

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (iso) => { if (!iso) return null; const [y, m, d] = iso.split("-"); return `${d}/${m}/${y}`; };
  const daysLeft = (iso) => { if (!iso) return null; const t = new Date(); t.setHours(0, 0, 0, 0); return Math.round((new Date(iso + "T00:00:00") - t) / 864e5); };
  const dval = (j, k) => j.datums?.[k]?.waarde || null;
  const dtxt = (j, k) => j.datums?.[k]?.waarde ? fmt(j.datums[k].waarde) : (j.datums?.[k]?.tekst || null);

  function status(j) { return FB[j.id]?.status || j.status || "nieuw"; }
  function comment(j) { return FB[j.id]?.comment ?? j.feedback_comment ?? null; }

  // ---------- data ----------
  async function load() {
    const [d, f] = await Promise.all([
      fetch(BASE + "/data/jobs.json", { cache: "no-store" }).then((r) => r.json()),
      fetch(API, { cache: "no-store" }).then((r) => (r.ok ? r.json() : { feedback: {} })).catch(() => ({ feedback: {} })),
    ]);
    DATA = d;
    FB = f.feedback || {};
    await flushPending();
    initFilters();
    renderTabsCounts();
    render();
    const lr = d.meta.laatste_run;
    $("#lastrun").textContent = lr ? "Update " + new Date(lr).toLocaleString("nl-BE", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) : "";
  }

  async function post(body) {
    try {
      const r = await fetch(API, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (!r.ok) throw new Error(r.status);
      const { entry } = await r.json();
      FB[body.id] = entry;
      return true;
    } catch (e) {
      const q = store.get("pending", []);
      q.push(body);
      store.set("pending", q);
      toast("Offline: bewaard, wordt later verstuurd");
      return false;
    }
  }

  async function flushPending() {
    const q = store.get("pending", []);
    if (!q.length) return;
    store.set("pending", []);
    for (const b of q) await post(b);
  }

  async function setStatus(j, s, c) {
    const prev = FB[j.id];
    FB[j.id] = { ...(prev || {}), status: s, comment: c === undefined ? prev?.comment : c, at: new Date().toISOString() };
    render();
    renderTabsCounts();
    const body = { id: j.id, status: s };
    if (c !== undefined) body.comment = c;
    if (await post(body)) toast(s === "nieuw" ? "Teruggezet" : "Opgeslagen: " + (DATA.meta.statussen?.[s] || s));
  }

  // ---------- filters ----------
  function initFilters() {
    const opts = { "f-contract": new Set(), "f-regime": new Set(), "f-sector": new Set(), "f-functie": new Set(), "f-provincie": new Set(), "f-thuiswerk": new Set() };
    for (const j of DATA.jobs) {
      (j.contract || []).forEach((x) => opts["f-contract"].add(x));
      opts["f-regime"].add(j.regime);
      (j.sector || []).forEach((x) => opts["f-sector"].add(x));
      (j.functietype || []).forEach((x) => opts["f-functie"].add(x));
      opts["f-provincie"].add(j.provincie || "onbekend");
      opts["f-thuiswerk"].add(j.thuiswerk);
    }
    for (const [id, set] of Object.entries(opts)) {
      const sel = $("#" + id);
      sel.length = 1;
      [...set].filter(Boolean).sort().forEach((v) => sel.add(new Option(v, v)));
    }
    const saved = store.get("filters", {});
    for (const el of $$("#filters select, #filters input")) {
      if (saved[el.id] !== undefined) el.value = saved[el.id];
      el.addEventListener("input", () => {
        const s = {};
        $$("#filters select, #filters input").forEach((x) => (s[x.id] = x.value));
        store.set("filters", s);
        $("#minscore-v").textContent = $("#minscore").value;
        render();
      });
    }
    $("#minscore-v").textContent = $("#minscore").value;
  }

  function matches(j) {
    const q = $("#q").value.trim().toLowerCase();
    if (q && !`${j.titel} ${j.organisatie} ${j.locatie} ${(j.sector || []).join(" ")}`.toLowerCase().includes(q)) return false;
    const f = (id) => $("#" + id).value;
    if (f("f-contract") && !(j.contract || []).includes(f("f-contract"))) return false;
    if (f("f-regime") && j.regime !== f("f-regime")) return false;
    if (f("f-sector") && !(j.sector || []).includes(f("f-sector"))) return false;
    if (f("f-functie") && !(j.functietype || []).includes(f("f-functie"))) return false;
    if (f("f-provincie") && (j.provincie || "onbekend") !== f("f-provincie")) return false;
    if (f("f-thuiswerk") && j.thuiswerk !== f("f-thuiswerk")) return false;
    if (j.score < +$("#minscore").value) return false;
    return true;
  }

  function inTab(j, t) {
    const s = status(j);
    switch (t) {
      case "top": return j.actief && !["geen_interesse", "afgewezen"].includes(s);
      case "nieuw": return j.nieuw && j.actief && s === "nieuw";
      case "mijn": return ACTIEF.includes(s);
      case "nee": return s === "geen_interesse" || s === "afgewezen";
      case "archief": return !j.actief;
    }
    return false;
  }

  function sorted(list) {
    const s = $("#sort").value;
    if (s === "deadline") return list.sort((a, b) => (dval(a, "deadline") || "9999").localeCompare(dval(b, "deadline") || "9999") || b.score - a.score);
    if (s === "nieuwste") return list.sort((a, b) => (b.first_seen || "").localeCompare(a.first_seen || "") || b.score - a.score);
    return list.sort((a, b) => b.score - a.score || (dval(a, "deadline") || "9999").localeCompare(dval(b, "deadline") || "9999"));
  }

  function renderTabsCounts() {
    for (const b of $$("#tabs button")) {
      const t = b.dataset.tab;
      if (["zoeken", "bronnen"].includes(t)) continue;
      const n = DATA.jobs.filter((j) => inTab(j, t)).length;
      b.innerHTML = `${b.textContent.replace(/\s*\d+$/, "")}<span class="n">${n}</span>`;
    }
  }

  // ---------- render ----------
  function chip(text, cls = "") { return `<span class="chip ${cls}">${esc(text)}</span>`; }

  function card(j) {
    const el = $("#card-tpl").content.firstElementChild.cloneNode(true);
    const s = status(j);
    el.classList.add("st-" + s);
    if (j.nieuw && s === "nieuw") el.classList.add("is-new");
    const sc = $(".score", el);
    $("b", sc).textContent = j.score;
    $("small", sc).textContent = j.score_bron === "claude" ? "score" : "score*";
    if (j.score >= 75) sc.classList.add("hi");

    const meta = [];
    if (s !== "nieuw") meta.push(`<span class="status-tag s-${s}">${esc(DATA.meta.statussen?.[s] || s)}</span>`);
    meta.push(esc((j.bronnen || []).map((b) => b.naam).join(" · ")));
    $(".meta", el).innerHTML = meta.join(" ");

    const a = $("h3 a", el);
    a.href = j.url;
    a.textContent = j.titel;
    $(".org", el).textContent = [j.organisatie, j.locatie].filter(Boolean).join(" — ");

    const chips = [];
    (j.contract || []).forEach((c) => chips.push(chip(c, c === "onbekend" ? "unk" : "c-contract")));
    chips.push(chip(j.regime + (j.percentage && j.percentage < 100 ? ` ${j.percentage}%` : ""), j.regime === "onbekend" ? "unk" : ""));
    (j.sector || []).forEach((c) => c !== "andere" && chips.push(chip(c)));
    (j.functietype || []).forEach((c) => c !== "andere" && chips.push(chip(c)));
    if (j.thuiswerk && j.thuiswerk !== "onbekend") chips.push(chip("thuiswerk: " + j.thuiswerk));
    if (j.provincie) chips.push(chip(j.provincie));
    $(".chips", el).innerHTML = chips.join("");

    const dl = dval(j, "deadline");
    const n = daysLeft(dl);
    const dates = [];
    dates.push(dl ? `<span class="${n !== null && n <= 7 ? "urgent" : ""}">Deadline ${fmt(dl)}${n !== null ? (n < 0 ? " (voorbij)" : n === 0 ? " (vandaag)" : ` (${n}d)`) : ""}</span>` : `<span class="unk">Deadline onbekend</span>`);
    const st = dtxt(j, "startdatum");
    dates.push(st ? `<span>Start ${esc(st)}</span>` : `<span class="unk">Start onbekend</span>`);
    const ed = dtxt(j, "einddatum");
    if (ed) dates.push(`<span>Einde ${esc(ed)}</span>`);
    if (dval(j, "publicatiedatum")) dates.push(`<span class="unk">Online ${fmt(dval(j, "publicatiedatum"))}</span>`);
    $(".dates", el).innerHTML = dates.join("");

    $(".why", el).textContent = j.samenvatting || j.motivatie || (j.score_redenen || []).join(" · ");

    const more = [];
    if (j.motivatie && j.samenvatting) more.push(`<h4>Waarom deze score</h4><p>${esc(j.motivatie)}</p>`);
    if (j.pluspunten?.length) more.push(`<h4>Plus</h4><ul>${j.pluspunten.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>`);
    if (j.minpunten?.length) more.push(`<h4>Min</h4><ul>${j.minpunten.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>`);
    const drows = Object.entries(j.datums || {}).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v.waarde ? fmt(v.waarde) : v.tekst)}</td><td>${esc(v.bron)}</td></tr>`).join("");
    if (drows) more.push(`<h4>Datums (met bron)</h4><table>${drows}</table>`);
    more.push(`<h4>Links</h4><ul>${(j.bronnen || []).map((b) => `<li><a href="${esc(b.url)}" target="_blank" rel="noopener">${esc(b.naam)}</a></li>`).join("")}</ul>`);
    if (j.beschrijving) more.push(`<h4>Uittreksel</h4><p class="desc">${esc(j.beschrijving)}…</p>`);
    const note = FB[j.id]?.notitie;
    if (note) more.push(`<h4>Notitie</h4><p>${esc(note)}</p>`);
    $(".more", el).innerHTML = more.join("");

    const c = comment(j);
    $(".fb-comment", el).textContent = c ? "“" + c + "”" : "";

    $$(".actions button, .extra button", el).forEach((b) => {
      if (b.dataset.s === s) b.classList.add("on");
      b.addEventListener("click", () => {
        const v = b.dataset.s;
        if (v === "more") { $(".extra", el).classList.toggle("hidden"); $(".note", el).classList.toggle("hidden"); $(".note textarea", el).value = FB[j.id]?.notitie || ""; return; }
        if (v === "geen_interesse") { $(".nee", el).classList.remove("hidden"); $(".nee textarea", el).focus(); return; }
        setStatus(j, v === s ? "nieuw" : v);
      });
    });
    $(".nee", el).addEventListener("submit", (e) => { e.preventDefault(); setStatus(j, "geen_interesse", $(".nee textarea", el).value.trim() || null); });
    $(".nee .cancel", el).addEventListener("click", () => $(".nee", el).classList.add("hidden"));
    $(".note", el).addEventListener("submit", async (e) => {
      e.preventDefault();
      const v = $(".note textarea", el).value.trim();
      FB[j.id] = { ...(FB[j.id] || {}), notitie: v };
      if (await post({ id: j.id, notitie: v })) toast("Notitie opgeslagen");
      render();
    });
    return el;
  }

  function render() {
    const list = $("#list");
    const panes = { zoeken: $("#zoeken"), bronnen: $("#bronnen") };
    const isPane = tab in panes;
    list.classList.toggle("hidden", isPane);
    $("#filters").classList.toggle("hidden", isPane);
    Object.entries(panes).forEach(([k, el]) => el.classList.toggle("hidden", k !== tab));
    if (tab === "zoeken") return renderZoeken();
    if (tab === "bronnen") return renderBronnen();

    const items = sorted(DATA.jobs.filter((j) => inTab(j, tab) && matches(j)));
    list.replaceChildren(...items.map(card));
    if (!items.length) list.innerHTML = `<p class="empty">Niets te tonen${tab === "nieuw" ? ": geen nieuwe vacatures sinds de vorige run." : "."}</p>`;
    $("#count").textContent = `${items.length} getoond · ${DATA.meta.totaal_gescand || 0} gescand`;
    const open = DATA.jobs.filter((j) => inTab(j, "top")).length;
    const nieuw = DATA.jobs.filter((j) => inTab(j, "nieuw")).length;
    $("#summary").textContent = `${open} open vacatures · ${nieuw} nieuw · ${DATA.jobs.filter((j) => inTab(j, "mijn")).length} in behandeling`;
  }

  function renderZoeken() {
    const h = DATA.meta.handmatig || [];
    $("#zoeken").innerHTML = `<h2>Zelf zoeken</h2>
      <p>Deze sites blokkeren automatische scrapers (o.a. FARO, VGC, Jobpunt, DPG Media) of zijn interim/generiek. Eén klik opent de zoekopdracht. Iets gevonden? Zeg het in de chat met Claude ("voeg toe: &lt;link&gt;"), dan komt het in de lijst.</p>
      ${h.map((x) => `<div class="srch"><b>${esc(x.naam)}</b>${x.links.map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.q || "Openen")}</a>`).join("")}</div>`).join("")}
      <h2>Jobpagina's van organisaties</h2>
      <p>Hier checkt de run enkel of de pagina verandert (en soms lukt dat niet, bv. door JavaScript of blokkades). Loop ze af en toe zelf even langs.</p>
      <div class="srch">${(DATA.meta.jobpaginas || []).map((x) => `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.naam)}${x.locatie ? " · " + esc(x.locatie) : ""}</a>`).join("")}</div>`;
  }

  function renderBronnen() {
    const b = DATA.meta.bronnen || [];
    const urls = DATA.meta.bron_urls || {};
    $("#bronnen").innerHTML = `<h2>Bronnen</h2>
      <p>Status van de laatste run. Volledige lijst en aanpak per bron: BRONNEN.md in de repo.</p>
      <table class="btable"><tr><th>Bron</th><th>Items</th><th>Nieuw</th><th>Status</th></tr>
      ${b.map((x) => `<tr><td><a href="${esc(urls[x.key] || "#")}" target="_blank" rel="noopener">${esc(x.naam)}</a></td><td>${x.items ?? ""}</td><td>${x.nieuw ?? ""}</td><td class="${x.ok ? "" : "bad"}">${x.ok ? "ok" : esc(x.fout || "fout")}</td></tr>`).join("")}
      </table>`;
  }

  $("#tabs").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    tab = b.dataset.tab;
    $$("#tabs button").forEach((x) => x.classList.toggle("on", x === b));
    store.set("tab", tab);
    render();
  });
  $("#ftoggle").addEventListener("click", () => $("#filters").classList.toggle("open"));
  tab = store.get("tab", "top");
  $$("#tabs button").forEach((x) => x.classList.toggle("on", x.dataset.tab === tab));

  load().catch((e) => { $("#list").innerHTML = `<p class="empty">Kon data niet laden (${esc(e.message)}).</p>`; });
})();
