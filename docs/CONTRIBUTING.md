# Contributing

This repository contains the delivery materials for the 5-Day SDI Lab
Automation FDP by Spruha Build-in Solutions. Contributions that improve the
exercises, fix API drift, or add institution-specific adaptations are welcome.

## Ground Rules

1. **Never invent Moku API methods.** Every API call in `v1-physical/scripts/`
   must match the official Liquid Instruments Python API
   (https://apis.liquidinstruments.com/). If unsure, mark it
   `# TODO: verify API method name against moku docs` rather than guessing.
2. **`get_data()` returns Python lists, not numpy arrays.** Convert explicitly
   (`np.array(data['ch1'])`) before numpy operations.
3. **MIM cleanup is always `m.relinquish_ownership()`** on the MultiInstrument
   object — never on individual slot instruments.
4. **IP addresses come from `config.py`.** No hardcoded IPs in scripts.
5. **Windows-friendly paths.** Use `pathlib`; scripts must run on
   Python 3.10+ on Windows.
6. Keep participant-facing language respectful of experienced educators —
   the audience is engineering faculty, not students.

## Workflow

1. Fork / branch from `main`
2. Make your change; test against real Moku:Go hardware where possible and
   note the firmware + moku package version you verified against
3. Update `docs/CHANGELOG.md`
4. Open a pull request describing what changed and why

## Reporting Issues

Open a GitHub issue with: script name, moku package version
(`python -c "import moku; print(moku.__version__)"`), firmware version, and
the full traceback.
