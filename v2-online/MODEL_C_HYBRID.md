# Model C — Hybrid Runbook (one Moku:Go, trainer live, cohort on simulator)

The college has **one** Moku:Go. The trainer drives it live; every
participant follows along on their own laptop with **mokusim**. Free
tier throughout.

**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

## Setup (trainer, 10 minutes)

1. Moku:Go connected, loopback wired, IP in `config.py`.
2. Dashboard in **live** mode on the trainer laptop:
   `MOKUDASH_MODE=live MOKU_IP=<ip> python v2-online/dashboard/app.py`
3. `cloudflared tunnel --url http://localhost:8050` → share the URL.
4. Open Google Meet; pin the dashboard's Join-Meet button to the
   cohort link (`MEET_URL=… python app.py`).

## Participant setup (5 minutes, no hardware)

```
git clone https://github.com/XMahaveer/sdi-fdp-workshop
pip install moku numpy matplotlib
cd sdi-fdp-workshop/v2-online/simulator
python simrun.py ../../v1-physical/scripts/day1/ex1_1_oscilloscope_logging.py
```

They also open the dashboard URL (progress grid + live signal +
pushed snippets) and the Meet call.

## The hybrid rhythm (per exercise)

1. **Trainer demos on the REAL device** — the dashboard's Live Signal
   panel shows the actual hardware trace to everyone (this is the
   "real signal feel" Model A alone can't give).
2. **Trainer pushes the key snippet** via Code Push.
3. **Participants run the same script on mokusim** locally —
   identical API, identical output shape — and mark progress.
4. Spot-the-difference moment: compare the simulator's clean trace to
   the real device's (noise floor, mains pickup, cable wiggle) — that
   contrast IS the teaching content about real measurements.
5. For capstones, volunteers can take a real-device slot via the
   rotation queue (Chrome Remote Desktop into the trainer laptop, or
   simply driving by voice while the trainer types).

## Why this model is the default recommendation for Indian colleges

- Matches the actual constraint (1 unit per institution is common)
- Zero participant hardware, zero participant cost
- Real-hardware credibility is preserved through the live panel
- Day 5 (MCC + AI curriculum design) is unchanged — already online
