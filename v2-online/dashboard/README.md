# SDI FDP Live Workshop Dashboard (V2)

One Plotly Dash app serving trainer + participants during remote
delivery — the visual hub for **all three V2 models**, designed to sit
beside Google Meet (companion mode), entirely on free tiers.

**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

## What's on it

| Panel | Who | What |
|-------|-----|------|
| **Live Signal** | all | the trainer's selected waveform + live FFT, streamed from mokusim (Model A/C) or a real Moku:Go (Model B/C) |
| **Join Google Meet** | all | one-click into the cohort call (`MEET_URL`) |
| **My Exercise Progress** | participant | self-mark Ex 1.1 → Cap C |
| **Cohort Progress** | all | live ✓-grid of everyone's progress |
| **Moku:Go Rotation** | all | Model B/C device queue — join/leave; trainer advances who holds the real unit |
| **Code Push** | trainer → all | trainer pastes a snippet; it appears on every screen in a dark code panel |

## Run it (trainer laptop + free tunnel)

```
pip install dash                      # one-time
cd v2-online/dashboard
python app.py
```

- Participants: `http://localhost:8050` → share publicly with a free
  Cloudflare quick tunnel (no account needed):
  `cloudflared tunnel --url http://localhost:8050`
  → give participants the printed `https://….trycloudflare.com` URL.
- Trainer view: append `/?role=trainer&key=spruha`
  (set your own key: `TRAINER_KEY=… python app.py`).

## Modes

| Env | Effect |
|-----|--------|
| `MOKUDASH_MODE=sim` (default) | signals from **mokusim** — Model A, zero hardware |
| `MOKUDASH_MODE=live MOKU_IP=…` | signals from a **real Moku:Go** — Models B/C; identical code path because mokusim is API-compatible |
| `MEET_URL=https://meet.google.com/xxx-xxxx-xxx` | the Join-Meet button target |
| `MOKUSIM_DUT=rc:2500` | (sim mode) put a simulated RC filter in the loopback |

## Google Meet integration

**Now (companion mode):** trainer screen-shares the dashboard in Meet
and/or participants open the tunnel URL in a second tab; the Join-Meet
button closes the loop. Zero approval process, free accounts.

**Add-on (built):** `meet_addon.py` adds `/addon/sidepanel`,
`/addon/mainstage`, and `/addon/manifest` routes that render the
dashboard *inside* Meet via the Add-ons SDK (main stage uses the
`?view=signal` signal-only layout). Launch with `PUBLIC_URL=` and
`GCP_PROJECT_NUMBER=` set; finish with a free GCP registration — see
[`../meet-addon/README.md`](../meet-addon/README.md).

## Cloud hosting upgrade (optional, still free)

The app exposes `server` for WSGI hosts. To get an always-on URL:
deploy to Hugging Face Spaces or Render free tier with
`requirements.txt` and start command `gunicorn app:server`
(Linux hosts). Note: `live` mode still requires a tunnel from wherever
the physical Moku:Go sits; `sim` mode works anywhere.
