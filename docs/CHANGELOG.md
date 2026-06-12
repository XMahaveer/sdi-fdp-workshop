# Changelog

All notable changes to the 5-Day SDI Lab Automation FDP are documented here.

## [v1.0.0] — 2026-06-12 — Production-ready V1 release

### Added
- Repository scaffold: directory structure, MIT license, `.gitignore`,
  `config.py` as the single source of truth for `MOKU_IP`
- Days 1–3: 7 hardware-verified exercise scripts (config-based IP,
  pathlib outputs)
- Day 4: three complete capstone scripts (component characterizer,
  signal monitor, production tester with certificates)
- Day 5: four AI workflow prompts + MCC threshold-detector experiment
  (skeleton, solution, Python host, guide)
- `expected_outputs/`: 8 simulated-data generators + 7 reference PNGs
- Slides v2.0 for all 5 days (61 slides, branded visual system)
- Documents v2.0: participant workbook, trainer script, agenda PDF,
  Day 5 facilitator guide, pre-workshop checklist
- Diagrams: day1 loopback, day2 MiM routing, day3 streaming,
  day5 AI workflow
- Master design document v2.0

### Changed (vs the pre-repo v1.0 materials)
- Day 5 rebuilt: off-site visit replaced by MCC session +
  AI-augmented curriculum design
- Logic Analyzer / AWG / MiM-trigger / Datalogger calls updated to the
  hardware-verified API (moku v4.1.2)
- All terminology updated ("Moku Custom Instrument"); branding unified

## Versioning

- **v2.0** is the content version of the workshop materials (this rebuild,
  replacing the original Industrial-Visit-based design v1.0).
- Git tags track release milestones (`v1.0.0` = first production-ready release
  of this repository).
