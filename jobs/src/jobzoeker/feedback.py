"""Feedback van Nina: synchronisatie tussen de site (Netlify Blobs) en data/feedback.json."""

from __future__ import annotations

import base64
import os

from . import net
from .store import FEEDBACK, STATUSSEN, load, now_iso, save


def _auth_headers() -> dict:
    auth = os.environ.get("JOBS_AUTH")  # "gebruiker:wachtwoord"
    if not auth:
        return {}
    return {"Authorization": "Basic " + base64.b64encode(auth.encode()).decode()}


def site_url() -> str | None:
    return os.environ.get("JOBS_SITE_URL", "").rstrip("/") or None


def merge(local: dict, remote: dict) -> dict:
    out = dict(local)
    for jid, r in remote.items():
        l = out.get(jid)
        if not l or (r.get("at") or "") >= (l.get("at") or ""):
            hist = {
                (h.get("at"), h.get("status")): h for h in (l or {}).get("history", []) + r.get("history", [])
            }
            out[jid] = {**r, "history": sorted(hist.values(), key=lambda h: h.get("at") or "")}
    return out


def pull() -> tuple[dict, str]:
    local = load(FEEDBACK, {})
    base = site_url()
    if not base:
        return local, "geen JOBS_SITE_URL: enkel lokale feedback"
    try:
        remote = net.get(f"{base}/jobs/api/feedback", headers=_auth_headers(), retries=1).json()
    except Exception as e:
        return local, f"site-feedback niet opgehaald: {e}"
    merged = merge(local, remote.get("feedback", remote))
    save(FEEDBACK, merged)
    return merged, f"{len(remote.get('feedback', remote))} feedback-items van site"


def set_local(jid: str, status: str, comment: str | None, door: str = "chat") -> dict:
    if status not in STATUSSEN:
        raise SystemExit(f"Onbekende status {status!r}. Kies uit: {', '.join(STATUSSEN)}")
    fb = load(FEEDBACK, {})
    entry = fb.get(jid, {"history": []})
    at = now_iso()
    entry.update({"status": status, "comment": comment or entry.get("comment"), "at": at, "door": door})
    entry["history"] = entry.get("history", []) + [
        {"at": at, "status": status, "comment": comment, "door": door}
    ]
    fb[jid] = entry
    save(FEEDBACK, fb)
    base = site_url()
    if base:
        try:
            net.post(
                f"{base}/jobs/api/feedback",
                json={"id": jid, "status": status, "comment": comment, "door": door},
                headers=_auth_headers(),
                retries=1,
            )
        except Exception as e:
            print(f"Let op: niet naar site gepusht ({e}); wordt bij volgende build meegenomen.")
    return entry


def apply(jobs: dict, fb: dict) -> None:
    for jid, f in fb.items():
        job = jobs.get(jid)
        if not job:
            continue
        if f.get("status"):
            job["status"] = f["status"]
        job["feedback_comment"] = f.get("comment")
        job["feedback_at"] = f.get("at")
        if f.get("notitie") is not None:
            job["notitie"] = f.get("notitie")
