// Basic auth voor /jobs. Werkt op het gratis Netlify-plan (geen Pro "password protection" nodig).
// Credentials staan niet in de repo: enkel de SHA-256 van "gebruiker:wachtwoord".
// Overschrijfbaar via env var JOBS_AUTH_SHA256 in Netlify (Site settings > Environment variables).
import type { Config, Context } from "https://edge.netlify.com";

const DEFAULT_HASH = "fa77d34a50bc6f50048b4eafdd5fdb752a193e313fa07b493c7313ecd4db7532";

async function sha256Hex(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

export default async (req: Request, context: Context) => {
  const expected = Netlify.env.get("JOBS_AUTH_SHA256") || DEFAULT_HASH;
  const h = req.headers.get("authorization") || "";
  if (h.startsWith("Basic ")) {
    try {
      const creds = atob(h.slice(6).trim());
      if (safeEqual(await sha256Hex(creds), expected)) return context.next();
    } catch (_) {
      // val door naar 401
    }
  }
  return new Response("Login vereist", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Jobs Nina", charset="UTF-8"', "Cache-Control": "no-store" },
  });
};

export const config: Config = { path: ["/jobs", "/jobs/*"] };
