# 5-Day SDI Lab Automation FDP

**A 5-day, 40-hour Faculty Development Program on test & measurement automation
using software-defined instrumentation (SDI) and the Python API.**

**Author & Trainer:** Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
**Version:** v2.0

---

## What This Is

A complete, ready-to-deliver Faculty Development Program for ECE/ETCE faculty in
engineering colleges. Participants learn to automate lab instruments
(Oscilloscope, Waveform Generator, AWG, Logic Analyzer, Datalogger,
Multi-Instrument Mode) using Python, then translate that into curriculum
artifacts for their own institutions.

The focus is **test and measurement automation** — not product training.

| Day | Theme |
|-----|-------|
| 1 | Foundations Part 1 — Oscilloscope & Waveform Generator automation |
| 2 | Foundations Part 2 — AWG, Logic Analyzer, Multi-Instrument Mode |
| 3 | Integration & Advanced — Streaming, FFT, SNR/THD signal quality |
| 4 | Real-World Applications — Industry patterns, final capstone projects |
| 5 | AI-Augmented Curriculum Design — Moku Custom Instrument (MCC) intro + AI-assisted curriculum mapping and experiment design |

## Two Versions

| Version | Status | Description |
|---------|--------|-------------|
| **[V1 — Physical](v1-physical/README.md)** | Active | In-person, hands-on, Moku:Go hardware-based delivery |
| **[V2 — Online](v2-online/README.md)** | Planned | Remote/cloud delivery via simulation or cloud-connected workstations — built after V1 is complete and verified |

## Repository Layout

```
sdi-fdp-workshop/
├── v1-physical/
│   ├── design/       Master workshop design document
│   ├── slides/       Day 1–5 presentation decks
│   ├── workbooks/    Participant workbook, pre-workshop checklist
│   ├── trainer/      Trainer script, agenda, Day 5 facilitator guide
│   ├── scripts/      All Python exercise code (config.py sets the Moku IP)
│   └── diagrams/     Connection and workflow diagrams (SVG)
├── v2-online/        V2 roadmap placeholder
└── docs/             Changelog and contribution guide
```

## Quick Start (V1)

1. `pip install moku numpy matplotlib`
2. `mokucli instrument download` (one-time bitstream download)
3. Set your device IP in [v1-physical/scripts/config.py](v1-physical/scripts/config.py)
4. Start with [v1-physical/scripts/README.md](v1-physical/scripts/README.md)

## License

MIT — see [LICENSE](LICENSE).
