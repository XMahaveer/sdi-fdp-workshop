# Remote Delivery Kit — 5-Day SDI Lab Automation FDP (V2 Online)

How to run the V1 workshop **online**, over Google Meet, with the
mokusim simulator and the live dashboard. Same learning outcomes, same
exercises, re-timed for remote attention spans and self-paced practice.

**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

---

## The online format at a glance

In-person days were one 8-hour block. Online, that does not hold
attention. This kit restructures each day into:

- **Live blocks ≤ 45 minutes**, each followed by a 5–10 min break.
- **Async exercise windows** — the trainer poses the exercise, then
  everyone runs it on the **simulator at their own pace** while the
  trainer staffs breakout rooms / office hours. Faculty can pause,
  re-run, and rewind a recording without holding up the room.
- **Live regroups** — short, to share results and clear blockers.

A typical online day is **~3.5 h live + ~1.5–2 h async**, runnable as a
half-day (e.g. 9:00 AM – 1:30 PM live, async after) or split across a
morning/evening to suit working faculty. Times below are *offsets from
day start* (T+0:00), not clock times — slot them into your cohort's
calendar.

### Hardware markers — read once

Because the **simulator runs every Day 1–4 exercise**, the default for
online delivery is **🟢 Simulator OK** — nobody waits for a hardware
slot. Two other markers appear:

- **🟢 Simulator OK** — runs fully on mokusim; no Moku:Go needed.
- **🔵 Real-HW optional** — simulator-OK, *and* a nice candidate for a
  real-device slot via the Model B/C rotation (the contrast is
  instructive). Never required.
- **☁️ Cloud required** — needs internet to a cloud service (MCC
  compile, or Claude/ChatGPT on Day 5), but no local Moku:Go.

Every exercise below carries one marker.

### Platform setup (all participants, before Day 1)

See `Pre_Workshop_Checklist_v2.docx` plus these online additions:
- Install the repo + `pip install moku numpy matplotlib dash`.
- Run one simulator smoke test:
  `cd v2-online/simulator && python simrun.py ../../v1-physical/scripts/day1/ex1_1_oscilloscope_logging.py`
  — seeing `[mokusim] MOKU SIMULATOR ACTIVE` means they're ready.
- Open the **dashboard URL** (trainer shares the Cloudflare tunnel link)
  and the **Meet link**. Two tabs, or the Meet add-on if deployed.

### Trainer's standing setup

- Dashboard in the mode that matches the day:
  `MOKUDASH_MODE=sim` for pure-simulator cohorts, or
  `MOKUDASH_MODE=live MOKU_IP=…` for hybrid/cloud-workstation days.
- Screen-share = the dashboard + a code editor. **All live demos are
  screen-shared**, not in-room — see "Screen-share demo discipline."
- Record every live block; drop the link in chat for the async windows.

### Screen-share demo discipline (replaces in-room demos)

1. Share the **editor + terminal** side by side (not the whole desktop).
2. Zoom the editor font to ≥ 16 pt; terminal to ≥ 14 pt.
3. Narrate every command before you run it ("I'm setting the timebase
   to ±5 ms now") — remote viewers can't see your hands point.
4. After a demo, **push the snippet** via the dashboard Code-Push so it
   lands on every screen — remote participants can't photograph a board.
5. Paste expected output / the `expected_outputs/*.png` reference in
   chat so async runners can self-check.

### Breakout-room facilitation (the async engine)

- Open **breakout rooms of 3–4** during every async window. Name them
  by exercise (e.g. "Ex 2.3 help").
- Trainer + any assistant **rotate** through rooms every 4–5 min;
  announce "broadcasting: 5 min left" before regroup.
- The dashboard **progress grid** is your radar — watch who hasn't
  ticked the exercise and visit that room first.
- Coaching line that works remotely: ask them to **share their screen
  in the room** and read the error aloud; most fixes are a one-line
  API-rule reminder (the simulator's error messages quote the rule).
- "Done early" → point them at the bonus challenge or the
  `MOKUSIM_DUT=rc:<fc>` variant; don't let them idle.

---

## DAY 1 — Foundations Part 1

Theme: *From manual to automated.* Goal: everyone connected to the
simulator and running both Day-1 exercises.

| T+ | Block (≤45 min) | Format |
|----|-----------------|--------|
| 0:00 | **Welcome + why automate** (25 min) | live, screen-share ROI slide |
| 0:25 | break (5) | |
| 0:30 | **Simulator setup live-check** (30 min) | live — everyone runs the smoke test; breakout for stragglers |
| 1:00 | break (10) | |
| 1:10 | **Demo: oscilloscope automation** (35 min) | live screen-share of `ex1_1`, then push snippet |
| 1:45 | break (5) | |
| 1:50 | **ASYNC: Exercise 1.1** (45 min) | self-paced + breakout rooms |
| 2:35 | **Regroup 1.1** (20 min) | live — 2–3 screens shared, Q&A |
| 2:55 | break (10) | |
| 3:05 | **Demo + ASYNC: Exercise 1.2** (40 min) | 10 min demo, 30 async |
| 3:45 | **Day-1 close + async homework brief** (15 min) | live |

**Exercises**
- **Ex 1.1 — Oscilloscope data logging 🟢 Simulator OK**
  Async card: "Run `simrun.py … day1/ex1_1_oscilloscope_logging.py`.
  You should get `frame_01..10.csv` and `oscilloscope_summary.png`.
  Compare your PNG to `expected_outputs/ex1_1_expected.png` (pasted in
  chat). Tick **Ex 1.1** on the dashboard. Stuck > 5 min → join the
  'Ex 1.1 help' room."
- **Ex 1.2 — WG parametric sweep 🟢 Simulator OK**
  Async card: "Run the sweep; read the efficiency-gain number at the
  end and type it in chat. Bonus: add the amplitude sweep."

**Breakout notes:** the #1 Day-1 blocker is environment, not concepts —
keep one room as a permanent "setup ER." Most simulator import errors
are a wrong working directory; have them `cd v2-online/simulator` and
use `simrun.py`.

---

## DAY 2 — Foundations Part 2 & MiM

Theme: *Expanding the toolkit; two instruments at once.*

| T+ | Block (≤45 min) | Format |
|----|-----------------|--------|
| 0:00 | **Day-1 recap quiz** (15 min) | live, chat-poll |
| 0:15 | **Demo: AWG** (25 min) | live screen-share `ex2_1` |
| 0:40 | break (10) | |
| 0:50 | **ASYNC: Exercise 2.1** (40 min) | self-paced + breakouts |
| 1:30 | break (5) | |
| 1:35 | **Demo: Logic Analyzer** (25 min) | live, stress the verified API |
| 2:00 | **ASYNC: Exercise 2.2** (35 min) | self-paced |
| 2:35 | break (10) | |
| 2:45 | **Demo: Multi-Instrument Mode** (40 min) | live — show the WRONG plain-dict first, then list-of-dicts |
| 3:25 | break (5) | |
| 3:30 | **ASYNC: Exercise 2.3** (40 min) | self-paced + breakouts |
| 4:10 | **Regroup + Day-2 close** (20 min) | live |

**Exercises**
- **Ex 2.1 — AWG custom waveform library 🟢 Simulator OK**
  Async card: "Build the 5 waveforms; the simulator rejects a numpy
  `lut_data` — if you hit that error, you've learned the rule. Tick
  Ex 2.1."
- **Ex 2.2 — Logic Analyzer SPI patterns 🟢 Simulator OK**
  Async card: "All pins in ONE `set_pattern_generator(channel=1,
  patterns=[…])` call; pin mode `'PG1'`. The simulator errors with the
  rule if you use the old form."
- **Ex 2.3 — MiM frequency sweep 🟢 Simulator OK 🔵 Real-HW optional**
  Async card: "Run loopback first (flat ~0 dB). Then re-run with
  `MOKUSIM_DUT=rc:2500` to see a real cutoff appear. If a hardware slot
  is offered, take it and compare." (Hybrid/Model-B cohorts: this is
  the natural first real-device rotation.)

**Breakout notes:** MiM is the conceptual peak of Day 2. In rooms, have
them *say out loud* what each connection dict routes — verbalizing
catches the source/destination mix-ups. The simulator's
`set_connections` error quotes the list-of-dicts rule verbatim; point to
it rather than re-explaining.

---

## DAY 3 — Integration & Advanced

Theme: *Streaming and signal quality.*

| T+ | Block (≤45 min) | Format |
|----|-----------------|--------|
| 0:00 | **Day-2 recap + finish Ex 2.3** (20 min) | live/breakout |
| 0:20 | **Demo: MiM AM modulation** (30 min) | live screen-share |
| 0:50 | break (10) | |
| 1:00 | **ASYNC: AM + filter characterization** (45 min) | self-paced + breakouts |
| 1:45 | break (5) | |
| 1:50 | **Demo: Datalogger streaming** (30 min) | live — stress 'End of stream' is normal |
| 2:20 | **ASYNC: Exercise 3.1** (35 min) | self-paced |
| 2:55 | break (10) | |
| 3:05 | **Demo: FFT / SNR / THD** (30 min) | live screen-share `ex3_2` |
| 3:35 | **ASYNC: Exercise 3.2** (40 min) | self-paced + breakouts |
| 4:15 | **Regroup + Day-2-capstone brief** (20 min) | live |

**Exercises**
- **AM modulation system 🟢 Simulator OK** — async card: "Measured
  depth should land 50 % ± 5 %. Try depths 25/75/100 %."
- **Filter characterization 🟢 Simulator OK 🔵 Real-HW optional** —
  "Use `MOKUSIM_DUT=rc:2500`; find the −3 dB cutoff and compare to
  1/(2πRC). Real-RC slot optional."
- **Ex 3.1 — Datalogger streaming 🟢 Simulator OK** — "~100k samples to
  CSV; catch the End-of-stream exception. Note: the simulator streams
  faster than real time — that's expected."
- **Ex 3.2 — FFT/SNR/THD 🟢 Simulator OK** — "Read SNR and THD; both
  should grade GOOD on the clean simulated signal. Bonus: bump
  amplitude to 2.5 V and watch THD rise."

**Breakout notes:** streaming exercises feel 'stuck' because the
simulator returns instantly and the loop ends fast — reassure them the
short runtime is correct. For FFT, the common error is forgetting
`np.array()` before the transform; the workbook callout covers it.

---

## DAY 4 — Real-World Applications & Capstone

Theme: *Industry patterns; build a complete automated system.*

| T+ | Block (≤45 min) | Format |
|----|-----------------|--------|
| 0:00 | **Day-2 capstone show-and-tell** (30 min) | live — 2–3 shared screens |
| 0:30 | break (10) | |
| 0:40 | **Industry patterns + case studies** (35 min) | live screen-share |
| 1:15 | **ASYNC: pattern-matching worksheet** (25 min) | self-paced, then chat |
| 1:40 | break (10) | |
| 1:50 | **Final capstone brief: choose A/B/C** (25 min) | live — walk each script |
| 2:15 | **ASYNC: capstone build block 1** (45 min) | self-paced + breakouts |
| 3:00 | break (10) | |
| 3:10 | **ASYNC: capstone build block 2** (45 min) | self-paced + breakouts |
| 3:55 | **Final presentations + close** (35+ min) | live — 3 min/team |

**Exercises**
- **Capstone A — Component Characterizer 🟢 Simulator OK 🔵 Real-HW optional**
- **Capstone B — Signal Quality Monitor 🟢 Simulator OK**
- **Capstone C — Production Tester 🟢 Simulator OK** (note: prompts for
  Enter between units — async runners just press Enter 3×)

All three ship complete in `scripts/day4/`; online faculty **extend**
rather than build from scratch. Real-device slots (Model B/C) are a
bonus for whoever wants the "real signal" capstone run.

**Breakout notes:** capstones are long; split each async block with a
30-second broadcast check-in ("you should have data flowing by now").
Encourage screen-share *within* rooms so peers debug each other — that
halves trainer load. Presentations: have presenters share the dashboard
or their plot, not just talk.

---

## DAY 5 — MCC + AI-Augmented Curriculum Design (online-adapted)

Day 5 is the most online-native day — the AI workflow was always going
to be each faculty on their own machine. The two in-room moments (MCC
hardware observation, and the trainer's AI demo) are re-done as
screen-shares. Full facilitation logic stays in
`v1-physical/trainer/Day5_Facilitator_Guide.md`; the deltas for online
are below.

| T+ | Block (≤45 min) | Format |
|----|-----------------|--------|
| 0:00 | **Day-5 overview + the two deliverables** (20 min) | live |
| 0:20 | **MCC part 1–2: why + the 5 differences** (40 min) | live screen-share, prediction-style |
| 1:00 | break (10) | |
| 1:10 | **MCC part 3: complete the threshold detector** (40 min) | demo + ASYNC |
| 1:50 | break (5) | |
| 1:55 | **MCC compile + observe** (30 min) | ☁️ cloud — screen-share the result |
| 2:25 | break (10) | |
| 2:35 | **AI step 1–2: prime + map** (45 min) | live brief, then ASYNC |
| 3:20 | break (10) | |
| 3:30 | **AI step 3–4: ideate + design** (60 min, may run long) | ASYNC + breakouts |
| 4:30 | **Verification + sharing + certificates** (40 min) | live |

**MCC online adaptation**
- **Threshold detector 🟢 Simulator OK for the host script /
  ☁️ Cloud required for the real build.** Online faculty complete the
  Verilog TODOs and read the host script; they run
  `mcc_threshold_detector_host.py` against the **mokusim
  `CustomInstrument`** (`Status0` ≈ signal frequency) to see the
  Control/Status round-trip without any FPGA. The actual cloud compile
  + real-device observation is **screen-shared by the trainer** (or a
  pre-recorded 3-min clip if venue internet is shaky) — the learning
  goal is the architecture, which the simulated round-trip already
  delivers.
- Screen-share the `mcc_threshold_detector_solution.v` counter logic at
  the 20-min mark of part 3, exactly as the in-person guide says.

**AI workflow online adaptation**
- **Steps 1–4 (prime / map / ideate / design): no hardware, no Meet
  add-on needed** — each faculty works in their own Claude + ChatGPT
  tabs. ☁️ Cloud required (the AI services), free tiers.
- Replace the in-room "trainer walks to each laptop" with: **trainer
  screen-shares one full pass** of the workflow first (prime → map →
  ideate → design) so remote faculty see the rhythm, then everyone goes
  async in breakout rooms.
- **Verification is the quality gate, online too:** faculty
  **share their screen in the breakout room** and the trainer reads the
  AI-generated code against the Days 1–4 rules live. The workbook
  section-6 checklist is the script. Budget the same ~3 min/participant;
  use the dashboard progress grid (add ad-hoc "map done" / "experiment
  done" ticks) to track who still needs sign-off.
- **Sharing:** 2–3 volunteers screen-share their designed experiment;
  certificates issued in-call; repo link + `info@spruha.in` in chat.

**Breakout notes (Day 5):** the failure modes from the in-person guide
all still apply (skipped primer → invented APIs; identical outputs →
unfilled `[BRACKETED]` fields). Online-specific: a faculty member who
goes quiet in async is usually rate-limited on one AI — have them
switch to the other (both hold the primer). Keep a "primer re-paste"
message pinned in chat.

---

## Trainer pre-flight (the online night-before)

- [ ] Dashboard launches in the right mode; tunnel URL live and pasted
      in the Meet invite.
- [ ] Recording on; chat moderation set so links are allowed.
- [ ] Breakout rooms pre-created and named per the day's exercises.
- [ ] Expected-output PNGs ready to paste per exercise.
- [ ] (Day 5) MCC compile screen-share rehearsed or the fallback clip
      queued; your Claude + ChatGPT free accounts logged in.
- [ ] Smoke-tested `simrun.py` on a clean machine to mirror a
      participant's environment.

## What stays identical to V1

Content, exercises, the four Day-5 prompts, the workbook, the slides,
and the assessment bar are unchanged — this kit only changes *timing,
delivery medium, and the hardware-vs-simulator routing*. A participant
who finishes the online cohort has produced the same artifacts as an
in-person one: working code for every exercise, a completed capstone,
and (Day 5) a curriculum map + a new verified experiment.
