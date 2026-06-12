# Model B — Cloud Workstation Runbook (free tier)

Real Moku:Go units at a hub site (your lab / the college), shared by
remote participants in rotation. Everything below runs on free tiers.

**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

## Topology

```
participant laptop ──(internet)──┐
participant laptop ──────────────┤→  HUB MACHINE (Windows/Linux laptop
participant laptop ──────────────┘    at the lab, on the Moku's Wi-Fi)
                                        ├── Moku:Go #1 (loopback wired)
                                        ├── dashboard (app.py, live mode)
                                        └── tunnel / remote access
```

## Hub machine setup (once)

1. Connect the Moku:Go (Wi-Fi or USB-C), wire the standard
   Output 1 → Input 1 BNC loopback, note its IP.
2. Clone the repo, `pip install moku dash numpy matplotlib`,
   set the IP in `v1-physical/scripts/config.py`.
3. Start the dashboard in live mode:
   `MOKUDASH_MODE=live MOKU_IP=<ip> python v2-online/dashboard/app.py`
4. Expose it: `cloudflared tunnel --url http://localhost:8050`
   (free, no account) — share the URL with the cohort.

## Two access levels (pick per session)

**Level 1 — watch + rotate (recommended for cohorts > 6):**
participants watch the live dashboard; the **rotation queue** on the
dashboard decides whose turn it is. The participant whose turn it is
drives the hub machine via **Chrome Remote Desktop** (free) and runs
the exercise script for real; everyone else follows on mokusim locally.

**Level 2 — direct API slots (small cohorts):**
install **Tailscale** (free personal tier) on the hub machine and the
current participant's laptop; share the hub into their tailnet for
their slot. Their own laptop's scripts then reach the real device —
set `MOKU_IP` in `config.py` to the hub-side address Tailscale
provides. One participant at a time (`force_connect=True` evicts the
previous owner — that is the rotation working as intended).

## Session protocol

1. Everyone joins Meet + the dashboard URL; primer slides as usual.
2. Participants run exercises on **mokusim** at their own pace
   (the dashboard's progress grid shows the room where everyone is).
3. For each capstone, participants **join the queue**; the trainer
   clicks *next →* to hand the real device over; 10-minute slots.
4. The Live Signal panel shows the real device the whole time, so the
   room sees real hardware behavior even while waiting.

## Free-tier bill of materials

| Need | Tool | Cost |
|------|------|------|
| Public dashboard URL | Cloudflare quick tunnel | free, no account |
| Remote control of hub | Chrome Remote Desktop | free |
| Direct API access | Tailscale personal | free (3 users/100 devices) |
| Video | Google Meet | free (60-min group calls — schedule breaks around it, or restart the link) |

Known constraint: one Moku:Go = one owner at a time. That is a
hardware property, not a tooling gap — the queue exists because of it.
