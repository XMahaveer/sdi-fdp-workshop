# Changelog

All notable changes to the 5-Day SDI Lab Automation FDP are documented here.

## [Unreleased] — V2 development

### Added
- `v2-online/simulator/` — mokusim, a moku-API-compatible simulator
  (V2 Model A): all six workshop instrument classes + CustomInstrument,
  realistic noise/distortion, MiM routing with loopback model, optional
  simulated RC DUT (`MOKUSIM_DUT=rc:<fc>`), and enforced
  hardware-verified teaching rules. All 10 V1 Day 1-4 scripts run
  unmodified and hardware-free (`simulator/run_all_v1.py`: ALL PASS).
- `v2-online/dashboard/` — live workshop dashboard (Plotly Dash, free
  tier): trainer/participant roles, live signal + FFT from mokusim or
  a real Moku:Go (sim/live modes), cohort progress grid, Model B/C
  device-rotation queue, trainer code-push, Google Meet companion
  integration (Join-Meet button; Add-on wrapper scaffolded in
  `v2-online/meet-addon/`). Share via free Cloudflare quick tunnel.
- `v2-online/dashboard/meet_addon.py` + `v2-online/meet-addon/manifest.json`
  — Google Meet Add-on surface: `/addon/sidepanel`, `/addon/mainstage`
  (signal-only `?view=signal` layout), `/addon/manifest` routes that
  dock the dashboard inside Meet via the Add-ons SDK, with graceful
  standalone fallback. Only a free GCP registration remains.
- `v2-online/dashboard/` persistence — `supabase_store.py` (requests-based
  Supabase REST layer, fail-silent in-memory fallback), `schema.sql`
  (sessions / participants / progress with unique(participant_id,
  exercise_id) + RLS anon policies), and `trainer_view.py`: a
  password-gated `/trainer` console (Name · College · Ex1.1–Cap C ·
  Score % · Last Active, CSV export, 30 s auto-refresh, session create
  -> 4-digit join code). Participants get a join-code field; progress
  persists across refresh. Env: SUPABASE_URL, SUPABASE_KEY,
  TRAINER_PASSWORD. Rebranded SDI Lab Cloud | Xenith Brand Labs.
- `v2-online/REMOTE_DELIVERY_KIT.md` — online delivery playbook: all
  five days re-timed into <=45-min live blocks with breaks, self-paced
  async exercise windows, breakout-room facilitation notes, a
  per-exercise hardware marker (Simulator OK / Real-HW optional / Cloud
  required), screen-share demo discipline, and the Day 5 MCC + AI
  workflow adapted for screen-share (MCC host verified against the
  simulator's CustomInstrument).
- `v2-online/MODEL_B_CLOUD_WORKSTATION.md` and
  `v2-online/MODEL_C_HYBRID.md` — free-tier runbooks for the real-
  hardware delivery models (Chrome Remote Desktop / Tailscale rotation;
  single-unit hybrid with trainer live + cohort on simulator).

## [1.0.0] — 2026-06-13

First production release of the v2.0 workshop rebuild.

### Added
- `v1-physical/scripts/` — 7 hardware-verified Day 1–3 exercises, three
  complete Day 4 capstones (component characterizer, signal monitor,
  production tester), shared `config.py` (single `MOKU_IP`), and 8
  simulated-data expected-output generators with reference PNGs
- `v1-physical/scripts/day5/` — four AI workflow prompts (SDI context
  primer, curriculum mapping, GPT ideation, Claude design; dry-run
  tested) and the MCC threshold-detector experiment (skeleton, trainer
  solution, Python host, step-by-step guide)
- `v1-physical/slides/` — Day 1–5 decks rebuilt to the original decks'
  visual standard (filled red/teal comparison headers, numbered badges,
  dark Consolas code panels, icon title slides, brand footer bars)
- `v1-physical/design/` — master design document v2.0
- `v1-physical/workbooks/` — Participant Workbook v2 (with Day 5 AI
  worksheets) and Pre-Workshop Checklist v2 (Claude/GPT free accounts)
- `v1-physical/trainer/` — Trainer Script v2, agenda PDF, and the Day 5
  Facilitator Guide
- `v1-physical/diagrams/` — day1/day2 connection diagrams (recolored),
  new day3 streaming setup and day5 AI workflow diagrams

### Changed vs the original workshop files
- Day 5 industrial visit replaced by the MCC session + AI-augmented
  curriculum design (Section 12 schedule)
- All scripts import their IP from `config.py`; no per-script editing
- Logic Analyzer, AWG, MiM-trigger, and Datalogger calls updated to the
  hardware-verified API (moku v4.1.2); custom-instrument host uses the
  verified `CustomInstrument` class with `set_control` / `get_status`
  (`CloudCompile` deprecated in moku 4.1.1)
- Branding unified: "Spruha Build-in Solutions | Powered by Moku:Go —
  Liquid Instruments", Calibri, #0057B8 / #FF6B35, v2.0

### Known open items
- V2 online edition: roadmap placeholder only (`v2-online/README.md`);
  built after V1 field feedback
- Live free-tier GPT behavior of the ideation prompt is verified by the
  trainer during night-before prep (see Day 5 Facilitator Guide)

## Versioning

- **v2.0** is the content version of the workshop materials (this
  rebuild, replacing the original Industrial-Visit-based design v1.0).
- Git tags track release milestones (`v1.0.0` = first production-ready
  release of this repository).
