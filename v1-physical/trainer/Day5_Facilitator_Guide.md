# Day 5 Facilitator Guide — AI-Augmented Curriculum Design for SDI Labs

**5-Day SDI Lab Automation FDP (v2.0)**
**Trainer:** Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

This guide covers everything needed to run Day 5. It complements the
Trainer Script (timing + talking points) with logistics, coaching
technique, and failure-mode handling specific to the AI and MCC sessions.

---

## The Day at a Glance

| Time | Block | Output |
|------|-------|--------|
| 8:00 – 8:30 | Welcome & overview | expectations set |
| 8:30 – 10:30 | MCC session | completed threshold detector, run on hardware |
| 10:30 – 10:45 | Break | |
| 10:45 – 12:30 | AI curriculum mapping | 1–2 page map per faculty, HoD-ready |
| 12:30 – 1:30 | Lunch | |
| 1:30 – 4:30 | AI experiment design | 1 complete verified experiment per faculty |
| 4:30 – 5:00 | Sharing & certificates | 2–3 presentations, close |

**The two deliverables are the day.** Every facilitation decision should
protect them: a curriculum map and a new experiment, both AI-drafted and
faculty-verified, leaving with each participant.

## Audience Posture — read this first

Day 5 participants are **experienced educators**, not students. The tone
that works: *"You already know your subject and your students. The AI is
a fast but unreliable junior assistant; today you learn to manage it."*
Never frame AI as replacing their judgment — the whole workflow is built
around their judgment being the scarce resource.

---

## The Night Before — trainer prep checklist

- [ ] Compile `mcc_threshold_detector_solution.v` on the LI cloud portal;
      download the bitstream to the trainer laptop (fallback for slow
      venue internet)
- [ ] Verify your own Claude and ChatGPT free accounts log in from the
      venue network (or have a hotspot ready)
- [ ] Run the full Day 5 AI workflow yourself once, end to end, with a
      subject you don't teach — you'll coach better having felt the
      friction points
- [ ] Print spare copies of the four prompts (some faculty prefer typing
      from paper into a fresh chat)
- [ ] Have `scripts/day5/` on USB sticks for anyone whose repo copy is
      broken

## Session 1 — MCC (8:30–10:30)

Full step-by-step is in [scripts/day5/mcc_experiment_guide.md](../scripts/day5/mcc_experiment_guide.md).
Facilitation notes on top of that:

- **Part 2 (5 differences) is the heart of the session.** Run it as
  prediction, not lecture: show the lab-Verilog side, ask "what do you
  think MCC forces here?", then reveal. Faculty teach FPGA labs — let
  them be experts arriving at the differences.
- **Time discipline in Part 3:** TODO 1 and 2 are quick; TODO 3 (the
  counter) is where groups stall. At the 30-minute mark, walk the
  solution's counter logic on the projector and let groups patch theirs.
- **MCC build queue:** submit builds in waves (3–4 at a time). While
  waiting, groups read the host script — by the time bitstreams return,
  they understand Control0/Status0.
- **If the venue internet dies:** demo with your pre-compiled bitstream
  on the projector and have groups run the host script against it. The
  learning survives; only the "my own bitstream" moment is lost.

## Session 2 — Curriculum Mapping (10:45–12:30)

- **The primer step is non-negotiable.** Physically walk the room and
  confirm every participant pasted `sdi_context_primer_prompt.txt` into
  BOTH a new Claude chat and a new GPT chat and got the "Context loaded"
  reply. Every Day-5 failure mode traces back to a skipped primer.
- **Subject selection (15 min):** push for ONE concrete subject they
  currently teach. Resist "let me do two" — depth beats breadth, and the
  afternoon builds on this choice.
- **Coaching the mapping iteration:** the most valuable thing you can
  say at a shoulder is *"Do you actually agree with that row?"* Teach
  them to reject: forced fits, invented syllabus topics, unjustified
  Bloom's levels. An honest "weak fit" row is a sign of a good map.
- **Quality bar:** spot-check 4–5 maps. A good map has every experiment
  tied to a real unit, realistic lab-slot weeks, and at least one honest
  weak-fit admission.

## Session 3 — Experiment Design (1:30–4:30)

- **Role-split briefing (15 min):** GPT ideates, Claude designs, faculty
  judges. Say the last part twice. The failure mode is faculty accepting
  AI output passively; the success mode is faculty arguing with it.
- **Ideation (30 min):** 3 ideas from GPT, pick ONE. Coach toward the
  idea their students need, not the most impressive one. If all three
  ideas are weak, the fix is a more specific topic in the prompt — not
  more ideas.
- **Design (90 min):** faculty iterate with Claude on the full document.
  Common interventions:
  - Document too generic → "tell Claude your university's exact lab
    record format"
  - Code looks suspicious → "ask Claude to flag uncertain lines with
    `# TODO: verify against moku docs`, then check them yourself"
  - Bloom's mismatch → "Claude was told to push back on this; ask it
    directly whether the level fits"
- **Verification (45 min) — the quality gate.** The workbook section 6
  checklist is mandatory: try/finally cleanup, lists-not-arrays, MiM
  list-of-dicts + cleanup on `m`, no invented methods, 30 MHz limit,
  2–3 h feasibility. **You personally review every code scaffold before
  sign-off.** Budget ~3 minutes per participant; recruit fast finishers
  as peer reviewers if the room is large.

## Sharing & Close (4:30–5:00)

- Pick 2–3 volunteers with *different subjects* — the room should see
  the workflow generalize.
- 5 minutes each: the experiment, the syllabus unit it serves, one thing
  the AI got wrong that they caught. That last item is the day's lesson
  compressed into a sentence.
- Certificates, group photo, repo link, support contact (info@spruha.in).

## Failure Modes & Responses

| Symptom | Response |
|---------|----------|
| AI invents Moku API methods | Primer was skipped or chat is stale — new chat, re-paste primer |
| Free-tier rate limit mid-session | Switch to the other AI for 20 min (both have the primer); stagger heavy prompts across the room |
| Venue internet down | MCC: pre-compiled bitstream. AI: phone hotspots; prompts work on mobile browsers |
| Faculty member resists AI on principle | Pair them as the *verifier* for a colleague — the judging role usually converts them |
| Output documents look identical across the room | Prompts were pasted unfilled — the [BRACKETED] fields personalize everything; send them back to fill |
| Someone finishes everything early | Have them run the workflow for a second subject, or draft the HoD proposal paragraph from the mapping prompt |

## Assessment (informal, for your records)

A participant has "completed" Day 5 when: (1) their threshold detector
ran (own bitstream or fallback), (2) their curriculum map passed your
spot-check, and (3) their experiment document passed the verification
checklist with your sign-off.
