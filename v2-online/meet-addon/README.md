# Google Meet Add-on Wrapper

The workshop dashboard rendered **inside** Google Meet's side panel and
main stage, via the free [Google Meet Add-ons SDK](https://developers.google.com/workspace/meet/add-ons) —
the "dashboard inside the call" showpiece. Companion mode (see
`../dashboard/README.md`) is the always-works fallback; this layer docks
the same Dash app into Meet itself.

## Status: BUILT (pending live GCP registration)

The add-on **surface is implemented** — the dashboard's Flask server
serves the Meet pages, the signal-only main-stage view works, and the
side panel exposes the "show on main stage" hand-off. What remains is
account-side: registering it in a (free) Google Cloud project, which
needs your credentials.

| Piece | State |
|-------|-------|
| `/addon/sidepanel`, `/addon/mainstage`, `/addon/manifest` routes | done (`../dashboard/meet_addon.py`) |
| Meet Add-ons SDK boot + graceful standalone fallback | done |
| Main-stage signal-only view (`/?view=signal`) | done & verified |
| `manifest.json` config template | done (this folder) |
| GCP project registration | **you do this** (steps below) |

## Why it's free

- Meet Add-ons SDK: free. Google Cloud project to register it: free tier.
- Unlisted/dev deployment (your cohort installs via link): free.
  Public Marketplace review is only for public distribution — a private
  FDP doesn't need it.

## Deploy steps (≈30 min, one-time)

1. **Stable HTTPS origin** for the dashboard. Two free options:
   - a **named** Cloudflare tunnel (`cloudflared tunnel create …`) so the
     URL is stable (quick-tunnel URLs change per run and would break the
     manifest), or
   - the free cloud host (`gunicorn app:server` on Render / HF Spaces).
2. **Launch the dashboard with the add-on env vars** so its pages emit
   correct absolute URLs:
   ```
   PUBLIC_URL=https://your-stable-origin \
   GCP_PROJECT_NUMBER=123456789012 \
   python ../dashboard/app.py
   ```
   Visit `https://your-stable-origin/addon/manifest` — it returns the
   exact config values to paste in the next step.
3. **Register in a free GCP project:** enable the *Google Workspace
   Marketplace SDK*, add a *Meet Add-on*, set:
   - Side Panel URI → `https://your-stable-origin/addon/sidepanel`
   - Main Stage URI → `https://your-stable-origin/addon/mainstage`
   - Add-on origins → `https://your-stable-origin`
   - scope → `https://www.googleapis.com/auth/meetings.space.created`
   (`manifest.json` here has all of this.)
4. **Install to your cohort** (unlisted): share the install link;
   participants on **Chrome desktop** click the add-on icon in Meet.
5. **In the call:** the side panel shows roster / queue / code-push;
   the trainer clicks *Show live signal on main stage* to throw the
   live waveform onto everyone's stage beside the video tiles.

## How the hand-off works (in `meet_addon.py`)

- Both pages load the SDK and call `createAddonSession({cloudProjectNumber})`.
- Side panel → `createSidePanelClient()`, and the button calls
  `startActivity({ mainStageUrl: ORIGIN + '/addon/mainstage' })`.
- Main stage → `createMainStageClient()` and embeds the dashboard with
  `?view=signal` so only the signal/FFT shows.
- If `window.meet` is absent (opened outside Meet), the page degrades to
  a normal standalone view — nothing breaks.

## Constraints

- Participants must use Meet on **Chrome desktop** for add-ons.
- The add-on never needs the meeting's media (it brings its own data),
  so no media scopes are requested.
- Pin the SDK version (`MEET_ADDON_SDK_VERSION`) to match the manifest;
  verify the current version on the SDK docs before going live.
