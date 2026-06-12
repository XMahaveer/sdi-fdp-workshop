# Google Meet Add-on Wrapper (phase 2 — scaffold)

Goal: the workshop dashboard rendered **inside** Google Meet's side
panel / main stage, via the free [Google Meet Add-ons SDK](https://developers.google.com/workspace/meet/add-ons).
Companion mode (see `../dashboard/README.md`) ships first; this wrapper
is the showpiece layer on top of the exact same Dash app.

## Why this is free

- Meet Add-ons SDK: free.
- Google Cloud project to register the add-on: free tier.
- Unlisted/dev deployment (your own cohort installs via link): free —
  public Marketplace listing review is only needed for public
  distribution, which a private FDP does not require.

## Build steps (when scheduled)

1. **HTTPS origin for the dashboard** — the add-on iframe requires
   HTTPS: either the Cloudflare tunnel URL (already HTTPS) or the
   free-tier cloud deployment (`gunicorn app:server`).
2. **Two thin HTML pages** served by the Dash app:
   `/addon/sidepanel` (roster + queue + snippet, narrow layout) and
   `/addon/mainstage` (Live Signal panels, wide layout). Dash supports
   extra Flask routes via `app.server.route(...)` — these pages embed
   the existing components with a compact CSS.
3. **Add-on manifest** in a free GCP project (Workspace Marketplace
   SDK → Meet Add-on, unlisted): point side-panel and main-stage URLs
   at the routes above, scope `meetings.addon`.
4. **Session hand-off**: the side panel exposes "open on main stage"
   (SDK `exposeToMainStage()`), so the trainer can throw the live
   waveform onto everyone's stage next to the video tiles.
5. Pilot with the cohort account; collect feedback before any
   Marketplace listing.

## Constraints to design around

- Participants must use Meet on **Chrome desktop** for add-ons.
- The add-on iframe cannot capture the meeting's media — the dashboard
  never needs to (it brings its own data), so this costs nothing.
- Keep the tunnel URL stable for the manifest: use a named (still
  free) Cloudflare tunnel or the cloud deployment rather than
  quick-tunnel URLs, which change per run.
