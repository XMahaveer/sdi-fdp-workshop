# V2 — Online Edition (Roadmap)

**Status: in development — Model A simulator core is DONE.** Every V1
Day 1–4 script (7 exercises + 3 capstones) runs unmodified against the
simulator in [`simulator/`](simulator/), with the hardware-verified
teaching rules enforced. See [`simulator/README.md`](simulator/README.md)
for usage and `simulator/run_all_v1.py` for the acceptance test
(currently: ALL PASS).

## What V2 Is

The same 5-day FDP, delivered remotely: participants connect via
browser and run the Days 1–4 experiments **without physical Moku:Go
hardware on their desk** — through simulation or cloud-connected lab
workstations. Day 5 (MCC concepts + AI-augmented curriculum design) is
already online by nature and carries over with minimal change.

## Delivery Models Under Consideration

| Model | How it works | Pros | Cons |
|-------|-------------|------|------|
| **A. Simulated instruments** | A Python package mimicking the `moku` API (`get_data()` returns synthesized waveforms; MiM routing modeled in software) | Zero hardware, infinitely scalable, offline-capable | Simulation fidelity work; no "real signal" feel |
| **B. Cloud lab workstations** | Real Moku:Go units racked at a hub site, loopback/DUT pre-wired; participants get remote desktop or API tunnel slots | Real hardware behavior, real API | Scheduling, concurrency limits, hub maintenance |
| **C. Hybrid** | Simulation for exercises; timed sessions on cloud hardware for capstones | Best of both | Two stacks to maintain |

**Decision: Model A first — and its core now exists** (`simulator/`).
Model B/C can layer on later for "real signal" capstone sessions.

## What Carries Over From V1 Unchanged

- All Day 1–4 exercise structure, workbook content, and slide decks
  (delivery notes change; content does not)
- The four Day 5 AI prompts and the facilitator guide
- `config.py` discipline (a simulator would honor the same constants)
- The hardware-verified API rules — the simulator must enforce them
  (e.g., reject plain-dict `set_connections`) so skills transfer to
  real devices

## What Must Be Built

1. ~~**Simulator package**~~ — **DONE**: `moku`-API-compatible classes
   (all six + CustomInstrument) with realistic noise/distortion, an
   optional simulated RC DUT (`MOKUSIM_DUT=rc:<fc>`), and enforcing
   error messages
2. **Remote delivery kit** — session plans re-timed for online cohorts
   (shorter blocks, async exercises), breakout-room facilitation notes
3. **Browser experience (stretch)** — virtual front panel showing the
   simulated signals live
4. **MCC adaptation** — Day 5 MCC session runs as guided code-reading +
   cloud-compile demo (compilation is already cloud-based; only the
   hardware observation step needs a recorded/simulated substitute)

## Sequencing (timeline TBD)

1. ~~Simulator core (all instruments) → Days 1-4 fully online~~ DONE
2. ~~Live workshop dashboard (Meet companion mode, free tier)~~ DONE —
   [`dashboard/`](dashboard/): live signal + FFT, cohort progress grid,
   device-rotation queue, trainer code-push, Join-Meet button
3. ~~Model B runbook~~ DONE — [`MODEL_B_CLOUD_WORKSTATION.md`](MODEL_B_CLOUD_WORKSTATION.md)
4. ~~Model C runbook~~ DONE — [`MODEL_C_HYBRID.md`](MODEL_C_HYBRID.md)
5. Google Meet Add-on wrapper (dashboard inside Meet) → NEXT —
   scaffold in [`meet-addon/`](meet-addon/)
6. Remote delivery kit (re-timed session plans) → then pilot cohort

Decisions and progress will be tracked in `docs/CHANGELOG.md` once V2
development starts.

---

*Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments*
