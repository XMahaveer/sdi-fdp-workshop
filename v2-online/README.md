# V2 — Online Edition (Roadmap)

**Status: planned — not yet in development.** V1 reached its production
release (`v1.0.0`); this document records the V2 vision so design
decisions are captured while V1 delivery experience is fresh.

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

Current leaning: **start with Model A** (a `moku`-compatible simulator),
because the v1 repo already contains the seed — the 8
`expected_outputs/generate_*_expected.py` scripts produce realistic
simulated results for every exercise with zero hardware. Model B/C can
layer on later.

## What Carries Over From V1 Unchanged

- All Day 1–4 exercise structure, workbook content, and slide decks
  (delivery notes change; content does not)
- The four Day 5 AI prompts and the facilitator guide
- `config.py` discipline (a simulator would honor the same constants)
- The hardware-verified API rules — the simulator must enforce them
  (e.g., reject plain-dict `set_connections`) so skills transfer to
  real devices

## What Must Be Built

1. **Simulator package** — `moku`-API-compatible classes (Oscilloscope,
   WaveformGenerator, AWG, LogicAnalyzer, Datalogger, MultiInstrument)
   with realistic noise, settle behavior, and error messages
2. **Remote delivery kit** — session plans re-timed for online cohorts
   (shorter blocks, async exercises), breakout-room facilitation notes
3. **Browser experience (stretch)** — virtual front panel showing the
   simulated signals live
4. **MCC adaptation** — Day 5 MCC session runs as guided code-reading +
   cloud-compile demo (compilation is already cloud-based; only the
   hardware observation step needs a recorded/simulated substitute)

## Sequencing (timeline TBD)

1. Simulator core for Oscilloscope + WG → Day 1 fully online
2. AWG, Logic Analyzer, MiM routing → Day 2
3. Datalogger streaming + FFT path → Day 3, capstones
4. Pilot cohort → feedback → Model B/C evaluation

Decisions and progress will be tracked in `docs/CHANGELOG.md` once V2
development starts.

---

*Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments*
