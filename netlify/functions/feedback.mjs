// Feedback van Nina (interesse / geen interesse + comment, notities) in Netlify Blobs.
// GET  /jobs/api/feedback        -> { feedback: { <id>: {status, comment, notitie, at, history[]} } }
// POST /jobs/api/feedback {id, status?, comment?, notitie?, door?}
// Elke wijziging wordt ook apart gelogd (log/<timestamp>) zodat niets verloren gaat.
import { getStore } from "@netlify/blobs";
import { createHash, timingSafeEqual } from "node:crypto";

const DEFAULT_HASH = "fa77d34a50bc6f50048b4eafdd5fdb752a193e313fa07b493c7313ecd4db7532";
const STATUSSEN = ["nieuw", "bekeken", "interesse", "gesolliciteerd", "gesprek", "aanbod", "afgewezen", "geen_interesse"];

function authorized(req) {
  const expected = Buffer.from(process.env.JOBS_AUTH_SHA256 || DEFAULT_HASH);
  const h = req.headers.get("authorization") || "";
  if (!h.startsWith("Basic ")) return false;
  const creds = Buffer.from(h.slice(6).trim(), "base64").toString("utf8");
  const got = Buffer.from(createHash("sha256").update(creds).digest("hex"));
  return got.length === expected.length && timingSafeEqual(got, expected);
}

export default async (req) => {
  if (!authorized(req)) {
    return new Response("Login vereist", { status: 401, headers: { "WWW-Authenticate": 'Basic realm="Jobs Nina"' } });
  }
  const store = getStore({ name: "nina-jobs", consistency: "strong" });

  if (req.method === "GET") {
    const data = (await store.get("feedback", { type: "json" })) || {};
    return Response.json({ feedback: data }, { headers: { "Cache-Control": "no-store" } });
  }

  if (req.method === "POST") {
    let body;
    try {
      body = await req.json();
    } catch {
      return Response.json({ error: "ongeldige JSON" }, { status: 400 });
    }
    const { id, status, comment, notitie } = body || {};
    if (!id || typeof id !== "string" || id.length > 40) return Response.json({ error: "id ontbreekt" }, { status: 400 });
    if (status && !STATUSSEN.includes(status)) return Response.json({ error: "onbekende status" }, { status: 400 });
    const door = typeof body.door === "string" ? body.door.slice(0, 20) : "site";
    const at = new Date().toISOString();
    const data = (await store.get("feedback", { type: "json" })) || {};
    const entry = data[id] || { history: [] };
    if (status) {
      entry.status = status;
      entry.at = at;
      entry.door = door;
    }
    if (comment !== undefined) entry.comment = typeof comment === "string" ? comment.slice(0, 2000) : null;
    if (notitie !== undefined) entry.notitie = typeof notitie === "string" ? notitie.slice(0, 4000) : null;
    if (!entry.at) entry.at = at;
    entry.history = [...(entry.history || []), { at, status: status || null, comment: comment ?? null, notitie: notitie ?? null, door }];
    data[id] = entry;
    await store.setJSON("feedback", data);
    await store.setJSON(`log/${at}-${id}`, { id, ...body, at });
    return Response.json({ ok: true, entry });
  }

  return new Response("Method not allowed", { status: 405 });
};

export const config = { path: "/jobs/api/feedback" };
