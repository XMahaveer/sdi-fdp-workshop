# V1 — Physical Workshop (In-Person, Hardware-Based)

The production version of the 5-Day SDI Lab Automation FDP, delivered in person
with one Moku:Go device per participant or pair.

**Trainer:** Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

## Contents

| Folder | What's Inside |
|--------|---------------|
| `design/` | Master design document — full day-by-day schedule, session plans, rubrics |
| `slides/` | Day 1–5 PPTX decks |
| `workbooks/` | Participant workbook + pre-workshop setup checklist |
| `trainer/` | Trainer delivery script, agenda, Day 5 facilitator guide |
| `scripts/` | All Python exercise code — see [scripts/README.md](scripts/README.md) |
| `diagrams/` | Connection diagrams and the Day 5 AI workflow diagram (SVG) |

## Hardware Requirements (per station)

- 1× Moku:Go (Liquid Instruments) — firmware updated
- 2× BNC cables (loopback Output 1 → Input 1, plus DUT testing)
- USB-C cable (backup connection) — Wi-Fi/Ethernet preferred
- Laptop with Python 3.10+

## Before Day 1

Work through `workbooks/Pre_Workshop_Checklist_v2.docx`. The short version:

```
pip install moku numpy matplotlib
mokucli instrument download        # one-time, ~500 MB, needs internet
```

Then set your device's IP address in [scripts/config.py](scripts/config.py)
(default placeholder is `192.168.0.101`).

## Day 5 Is Different

Day 5 replaces the traditional industrial visit with two sessions faculty can
run anywhere:

1. **Moku Custom Instrument (MCC) introduction** — how custom Verilog runs
   inside the Moku infrastructure, and how that differs from a standard FPGA lab.
2. **AI-augmented curriculum design** — faculty use Claude and GPT (free tiers)
   with the four ready-made prompts in `scripts/day5/` to map the workshop
   experiments onto their own syllabus and design one new SDI experiment for
   their institution.

See `trainer/Day5_Facilitator_Guide.md` for how to run it.
