# 5-Day SDI Lab Automation FDP — Master Design Document

**Version:** 2.0 (full rebuild — replaces the v1.0 Industrial-Visit-based design)
**Author & Trainer:** Mahaveer. Rajendra. Savanur
**Designation:** Head of Engineering & AI Systems
**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

**Duration:** 5 days, 40 hours
**Days 1–4:** Hands-on automation training (32 h) | **Day 5:** MCC + AI-Augmented Curriculum Design (8 h)
**Audience:** ECE/ETCE faculty in engineering colleges (students welcome as secondary audience)
**Platform:** Moku:Go (Liquid Instruments) + Python API
**Format:** Hands-on, project-based, with every participant leaving with working code and curriculum artifacts

---

## Executive Summary

This FDP teaches **test and measurement automation** — not product
training. Faculty learn to control software-defined instruments
(Oscilloscope, Waveform Generator, AWG, Logic Analyzer, Datalogger,
Multi-Instrument Mode) from Python, progress through guided exercises to
complete automated test systems, and finish with two take-home curriculum
artifacts produced in an AI-assisted workflow on Day 5.

**What changed from v1.0:**

| Area | v1.0 | v2.0 |
|------|------|------|
| Day 5 | Industrial visit (transport-dependent, not reproducible) | MCC session + AI-augmented curriculum design (runs anywhere, produces artifacts) |
| IP configuration | edited per script | single `scripts/config.py` (`MOKU_IP`) |
| Logic Analyzer API | legacy per-pin calls | hardware-verified `patterns=[…]` + `'PG1'` (moku v4.1.2) |
| MiM trigger | `set_trigger(source='Input1')` | auto-trigger (Input1 invalid in MiM — hardware-verified) |
| Day 4 capstone | thin skeleton | three complete runnable options (A/B/C) |
| Exercise numbering | mixed | matches `scripts/dayN/exN_M_*.py` |
| Expected outputs | static PNGs | PNGs + simulated-data generator scripts |

**Source of truth:** the Python files in `../scripts/` are
hardware-verified and override any code fragment in any document,
including this one.

---

## Workshop Structure Overview

| Day | Theme | Core content |
|-----|-------|--------------|
| 1 | Foundations Part 1 — "From Manual to Automated" | Setup, config.py, Oscilloscope (Ex 1.1), Waveform Generator (Ex 1.2) |
| 2 | Foundations Part 2 — "Expanding Your Toolkit" | AWG (Ex 2.1), Logic Analyzer (Ex 2.2), Capstone 1, MiM intro (Ex 2.3) |
| 3 | Integration & Advanced — "Professional Analysis" | MiM hands-on (AM, filter), streaming (Ex 3.1), FFT/SNR/THD (Ex 3.2), Capstone 2 |
| 4 | Real-World Applications — "Industry Ready" | Case studies, 5 patterns, final capstone (A/B/C), presentations |
| 5 | AI-Augmented Curriculum Design | MCC threshold detector, AI curriculum mapping, AI experiment design |

Daily rhythm: 8:00 AM – 5:00 PM, 15-min breaks mid-morning and
mid-afternoon, 60-min lunch.

---

# DAY 1 — FOUNDATIONS PART 1

**8:00–9:00 · Introduction & Workshop Overview.** Objectives, team
formation (pairs), the case for automation (100-point sweep: 2 hours
manual vs 2 minutes automated), ROI framing (40 h investment → 200 h/yr
saved), applications in research / manufacturing / teaching labs.
Moku:Go platform overview: 2 analog in (30 MHz, 125 MSa/s), 2 analog
out, 16 DIO, MiM with 2 slots, optional PPSU (unit-specific — never
assume).

**9:15–10:30 · Environment Setup & Verification.** Python 3.10+,
`pip install moku numpy matplotlib`, `mokucli instrument download`
(one-time, ~500 MB), find device IP via `mokucli list`, set `MOKU_IP`
in `scripts/config.py` **once**, run the connection test. Session ends
only when every station prints "Connected!".

**10:45–12:30 · Oscilloscope & Waveform Generator Automation.**
The core pattern, taught explicitly and used all week:

```
CONNECT → CONFIGURE → ACQUIRE → CLEANUP
```

```python
from moku.instruments import Oscilloscope
from config import MOKU_IP, FORCE_CONNECT

osc = Oscilloscope(MOKU_IP, force_connect=FORCE_CONNECT)
try:
    osc.set_frontend(channel=1, impedance='1MOhm', coupling='DC', range='10Vpp')
    osc.set_timebase(-5e-3, 5e-3)
    osc.set_trigger(type='Edge', source='Input1', level=0)   # standalone only
    data = osc.get_data()        # dict of Python LISTS: 'time','ch1','ch2'
    vpp = max(data['ch1']) - min(data['ch1'])
finally:
    osc.relinquish_ownership()   # ALWAYS — or the device stays locked
```

- **Exercise 1.1 — Oscilloscope Data Logging (30 min).**
  `day1/ex1_1_oscilloscope_logging.py`. Loopback Out1→In1, capture 10
  frames, per-frame CSV, Vpp statistics, summary plot. Bonus: ±3σ SPC
  limits. Expected result: `expected_outputs/ex1_1_expected.png`.
- **Exercise 1.2 — WG Parametric Sweep (30 min).**
  `day1/ex1_2_waveform_generator_sweep.py`. 7 frequencies × 3 waveforms
  = 21 tests with CSV log and a measured efficiency gain vs manual
  (typical 10–30×). API note: `Square` requires `duty=`, `Ramp` requires
  `symmetry=`, `Pulse` requires `duty=`.

**1:30–3:30 · Practice & Office Hours.** Bonus challenges, pair
programming, instructor circulation.

**3:45–5:00 · Code Review & Wrap-Up.** Organization, error handling,
CSV/plot quality, settle-time discipline (≥ 50 ms after waveform
changes). Preview Day 2.

---

# DAY 2 — FOUNDATIONS PART 2 & INTEGRATION BEGINS

**8:00–8:15 · Day 1 recap quiz.**

**8:15–9:00 · Arbitrary Waveform Generator + Exercise 2.1 (30 min).**
`day2/ex2_1_awg_custom_waveforms.py`. Define waveforms mathematically
with numpy, normalize to [-1, 1], build a JSON library, output each.

```python
awg.generate_waveform(channel=1, sample_rate='Auto',
                      lut_data=list(wf),       # Python LIST, not ndarray
                      frequency=1e3, amplitude=1.0)
```

**9:15–10:30 · Logic Analyzer + Exercise 2.2 (30 min).**
`day2/ex2_2_logic_analyzer_spi.py`. Generate a 4-pin SPI-like bus and
capture it. **Hardware-verified API (moku v4.1.2, March 2026):**

```python
la.set_pattern_generator(
    channel=1,                                  # PG channel, NOT a pin
    patterns=[{"pin": 1, "pattern": clock},     # ALL pins in ONE call
              {"pin": 4, "pattern": mosi}],
    divider=5)
la.set_pin_mode(1, 'PG1')                       # 'PG1' — NOT 'Pattern'
```

**10:45–12:30 · Day 1 Capstone: Automated Frequency Response Tester.**
Teams build: WG sine sweep (20+ log points, 100 Hz–10 MHz) → loopback →
Oscilloscope capture → gain in dB → Bode plot + CSV + short report.
Evaluation: Functionality 40 / Code 20 / Documentation 20 / Results 20.
Checkpoints at 15/30/60 minutes.

**1:30–2:30 · Capstone presentations** (5 min/team, live demo required).

**2:45–5:00 · Multi-Instrument Mode Fundamentals + Exercise 2.3 (45 min).**
`day2/ex2_3_mim_frequency_sweep.py`. The three critical MiM rules,
hardware-verified:

```python
m = MultiInstrument(MOKU_IP, platform_id=2, force_connect=True)  # 2 slots on Moku:Go
wg  = m.set_instrument(1, WaveformGenerator)
osc = m.set_instrument(2, Oscilloscope)

# RULE 1 — connections are a LIST OF DICTS (a plain dict silently
# drops duplicate keys and fails):
m.set_connections(connections=[
    dict(source='Slot1OutA', destination='Output1'),   # WG → physical Out 1
    dict(source='Input1',    destination='Slot2InA'),  # physical In 1 → scope
])

# RULE 2 — in MiM, 'Input1' is NOT a valid trigger source.
# Auto-trigger works: simply do not call set_trigger.

# RULE 3 — cleanup on the MultiInstrument object, never the slots:
m.relinquish_ownership()
```

Routing nodes (Moku:Go): sources `Input1/2`, `Slot1OutA/B`, `Slot2OutA/B`;
destinations `Output1/2`, `Slot1InA/B`, `Slot2InA/B`. Frontend in MiM is
configured via `m.set_frontend(...)`. MIM fabric clock is 31.25 MHz
(relevant for custom-instrument timing; system clock remains 125 MHz).

---

# DAY 3 — INTEGRATION & ADVANCED TECHNIQUES

**8:00–10:30 · MiM hands-on.** Complete Ex 2.3 sweep; then:

- **AM Modulation System (45 min).** WG slot 1 (100 kHz carrier,
  `set_modulation(channel=1, type='Amplitude', source='Internal',
  frequency=1e3, depth=50)`), Oscilloscope slot 2, ±2.5 ms window.
  Verify ~100 carrier cycles per modulation cycle; measured depth
  `(Vmax−Vmin)/(Vmax+Vmin)` within ±5 % of setting.
- **Automated Filter Characterization (45 min).** Loopback sanity (flat
  ≈ 0 dB), then a physical RC low-pass between Out1 and In1: −3 dB
  cutoff vs 1/(2πRC), roll-off ≈ −20 dB/decade.

**10:45–12:15 · Real-Time Streaming + Exercise 3.1 (30 min).**
`day3/ex3_1_datalogger_streaming.py`. Snapshot vs stream; deque-based
buffering for live displays.

```python
dl.start_streaming(duration=10, sample_rate=10e3)
while True:
    try:
        data = dl.get_stream_data()
        if data: process(data['ch1'])
    except Exception as e:
        if 'End of stream' in str(e):
            break          # NORMAL completion — not an error
        raise
```

**1:15–3:15 · Advanced Analysis + Exercise 3.2 (45 min).**
`day3/ex3_2_fft_snr_thd.py`. Convert lists → arrays
(`np.array(data['ch1'])`), Hann window, FFT, dominant frequency, SNR
(benchmark > 40 dB), THD over harmonics 2–5 (benchmark < 1 %), graded
4-panel quality report.

**3:30–5:00 · Day 2 Capstone development.** Combine MiM + sweep +
quality metrics into one professional test system; presentations next
morning.

---

# DAY 4 — REAL-WORLD APPLICATIONS & FINAL PROJECTS

**8:00–9:15 · Journey review + Day 2 Capstone presentations**
(5–6 min/team; Functionality 35 / Code 20 / Analysis 15 / Savings 15 /
Presentation 15).

**9:30–11:00 · Industry case studies & the 5 automation patterns.**

| Pattern | When | Example |
|---------|------|---------|
| Parameter Sweep | characterize across a range | Bode plot, V-I curves |
| Pass/Fail Testing | QC against spec limits | go/no-go, certificates |
| Continuous Monitoring | long-duration with alerts | drift, burn-in |
| Calibration Routine | known input → correction | sensor cal, zeroing |
| Batch Testing | same sequence, N devices | production, lab groups |

Case studies: production line (8 min/board manual → 90 s automated, 83 %
time cut), research lab (48-hour unattended dataset — impossible
manually), teaching lab (2.5 h of knob-turning → 10 min, students
analyze instead).

**11:15–12:30 · Pattern matching exercise + final capstone planning.**
Five scenarios mapped to patterns (most need more than one); teams choose
a capstone option and get plan approval.

**1:30–3:30 · Final Capstone.** All three options ship as complete,
runnable scripts in `scripts/day4/` — teams run, understand, then extend:

| Option | Script | System | Goal |
|--------|--------|--------|------|
| A | `capstone_option_a_component_characterizer.py` | MiM sweep → gain, −3 dB, roll-off → datasheet | manual ~40 min → < 5 min |
| B | `capstone_option_b_signal_monitor.py` | streaming monitor, thresholds, alert log, report | impossible manually → unattended |
| C | `capstone_option_c_production_tester.py` | FFT pass/fail vs spec (1 MHz ±1 %, ≥0.8 Vpp, ≤5 % THD), certificates | 8 min/unit → < 90 s |

Rubric: Automation 50 / Technical 30 / Documentation 20 (+10 bonus).
Development phases: connect 20 → loop 40 → analysis 30 → report 20 →
test 10 minutes, trainer checkpoint at 2:30 PM.

**3:45–5:00 · Final presentations** (3 min/team, strictly timed), awards,
Day 5 preview.

---

# DAY 5 — AI-AUGMENTED CURRICULUM DESIGN FOR SDI LABS

Replaces the v1.0 industrial visit. Two blocks, both reproducible at any
institution, producing two take-home artifacts per participant.

## Schedule

| Time | Session |
|------|---------|
| 8:00 – 8:30 | Welcome & Day 5 overview |
| 8:30 – 10:30 | **Moku Custom Instrument (MCC) session** |
| 10:45 – 12:30 | **AI-assisted curriculum mapping** |
| 1:30 – 4:30 | **AI-assisted experiment design** |
| 4:30 – 5:00 | Sharing, wrap-up, certificates |

## MCC Session (120 min)

Faculty learn how custom Verilog runs *inside* the Moku infrastructure —
and how that differs from their FPGA labs. Files in `scripts/day5/`:
`mcc_threshold_detector_skeleton.v` (3 guided TODOs),
`mcc_threshold_detector_solution.v` (trainer only),
`mcc_threshold_detector_host.py`, `mcc_experiment_guide.md`.

Structure: context (20 min, ASK modulator walk-through) → the 5 key
differences (30 min, prediction-style) → threshold detector hands-on
(60 min: complete TODOs, cloud-compile, run host script, observe
Status0 ≈ 100 crossings/sec for a 100 Hz sine) → teaching discussion
(10 min). The five differences:

1. Top module is always `CustomWrapper` — hardcoded
2. `Clk` = 125 MHz system clock, fixed (MIM fabric clock 31.25 MHz is a
   separate, MIM-level concern)
3. Fixed port list — Control0–19 in, Status0–3 out, all declared
4. Signals are Q1.15 signed 16-bit (32767 = +1.0 V)
5. Python ⇄ FPGA via `set_control_register` / `get_status_register` —
   no JTAG; synthesis happens on the Liquid Instruments cloud

Moku:Go cautions: OutputD is not physical; OutputC disconnects in 3-slot
MIM; LUTs initialize via `initial begin` with `$rtoi/$sin/$cos`, not
`.mif` files.

## AI Curriculum Workflow (morning + afternoon)

Four self-contained prompts in `scripts/day5/`, all working on **free
tiers** of Claude and ChatGPT:

1. **`sdi_context_primer_prompt.txt`** — pasted FIRST into new chats in
   BOTH AIs; loads hardware facts, verified API patterns, the Days 1–4
   experiment list, and hard constraints so the AI cannot hallucinate.
2. **`curriculum_mapping_prompt.txt`** — maps the Days 1–4 experiments
   onto the faculty member's own subject (default VTU), with Bloom's
   levels, lab slots, prerequisites, and an honest "weak fit" rule.
   Output: a 1–2 page map ready for their HoD.
3. **`gpt_ideation_prompt.txt`** — 3 genuinely different experiment ideas
   for their subject/topic (GPT used for ideation breadth). Faculty
   pick ONE.
4. **`claude_design_prompt.txt`** — full experiment document: Aim,
   Apparatus, Theory, pre-lab questions, procedure, Python code scaffold
   (verified patterns only, uncertain lines flagged
   `# TODO: verify against moku docs`), expected output, 5 viva
   questions, Bloom's level with justification.

**Role split:** GPT ideates, Claude designs, **faculty judges**. Every
code scaffold passes the verification checklist (workbook §6) and a
trainer review before sign-off. Facilitation detail, failure modes, and
the trainer prep checklist live in `trainer/Day5_Facilitator_Guide.md`.

**Deliverables per participant:** a faculty-verified curriculum map and
one complete, faculty-owned SDI experiment — both ready for submission
to their institution.

---

# APPENDICES

## A. Materials (per station = participant pair)

1× Moku:Go (firmware updated) · 2× BNC cables · 1× RC filter kit
(Day 3) · USB-C cable (backup) · laptop with Python 3.10+ · printed
Participant Workbook v2. Venue: projector, Wi-Fi AP (all devices on one
network), power strips, whiteboard. Day 5 adds: Claude + ChatGPT free
accounts per participant, LI cloud-build access + pre-compiled fallback
bitstream (trainer).

## B. Repository Map

```
v1-physical/
├── design/     this document
├── slides/     Day1…Day5 PPTX (v2.0 visual system)
├── workbooks/  Participant_Workbook_v2.docx, Pre_Workshop_Checklist_v2.docx
├── trainer/    Trainer_Script_v2.docx, SDI_5Day_Workshop_Agenda_v2.pdf,
│               Day5_Facilitator_Guide.md
├── scripts/    config.py + day1…day5 + expected_outputs (see scripts/README.md)
└── diagrams/   day1 loopback, day2 MiM routing, day3 streaming, day5 AI workflow
```

## C. Budget Notes (v2.0 deltas from v1.0)

The v1.0 industrial-visit line items (transport $300–800, facility fees
$200–500, visitor safety equipment $100) are removed. Day 5 v2.0 adds
zero marginal cost: AI free tiers and the MCC cloud build are free; the
only new requirement is reliable internet at the venue. All other
budget categories (equipment, instruction, materials, facility,
refreshments) carry over from v1.0 unchanged.

## D. Learning Outcomes

| Day | Outcomes |
|-----|----------|
| 1 | Connect/configure/acquire/cleanup pattern; Oscilloscope + WG automation; CSV logging |
| 2 | AWG LUT waveforms; verified Logic Analyzer patterns; frequency response tester; MiM routing rules |
| 3 | Two-instrument systems; real-time streaming; FFT/SNR/THD signal grading |
| 4 | The 5 industry patterns; a complete automated test system; ROI quantification |
| 5 | MCC architecture vs bare-FPGA flow; managing AI as a curriculum co-designer; verified curriculum artifacts |

Success metrics: ≥ 90 % completion, ≥ 85 % capstone pass, ≥ 4.5/5
satisfaction, every participant leaves with both Day 5 artifacts.

## E. References

- Liquid Instruments Python API: https://apis.liquidinstruments.com/
- Educational resources: https://liquidinstruments.com/coursework/
- Knowledge base: https://knowledge.liquidinstruments.com/
- All scripts hardware-verified on Moku:Go (moku v4.1.2, MokuOS 4.1.2);
  the `scripts/` directory is the canonical source for every API call.

---

**DOCUMENT VERSION:** 2.0
**STATUS:** Production — V1 (physical workshop)
*Focus: automation concepts using software-defined instrumentation — not product training.*
