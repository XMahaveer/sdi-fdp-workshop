# Workshop Scripts — 5-Day SDI Lab Automation FDP (v2.0)

All Python exercise code for Days 1–5, hardware-verified against the
Liquid Instruments Python API v4.x on Moku:Go.

**Trainer:** Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

## Setup

Requires **Python 3.10+** (Windows, macOS, or Linux).

```
pip install moku numpy matplotlib
mokucli instrument download      # one-time bitstream download (~500 MB)
```

### Configure your Moku:Go IP — once

Every script imports its connection settings from [config.py](config.py).
Find your device's IP with `mokucli list` (or on the device screen) and
edit one line:

```python
MOKU_IP = '192.168.0.101'   # <-- your device's IP
```

Do **not** edit IPs inside individual scripts — there aren't any.

### Run

```
python day1/ex1_1_oscilloscope_logging.py
```

Scripts can be run from any working directory; outputs (CSV, PNG, TXT)
are saved next to the script that produced them.

## Contents

| Folder | Script | Time | What It Teaches |
|--------|--------|------|-----------------|
| day1 | `ex1_1_oscilloscope_logging.py` | 30 min | Oscilloscope capture, CSV logging, Vpp statistics |
| day1 | `ex1_2_waveform_generator_sweep.py` | 30 min | WG parametric sweep, efficiency vs manual |
| day2 | `ex2_1_awg_custom_waveforms.py` | 30 min | AWG custom waveform library (numpy → LUT) |
| day2 | `ex2_2_logic_analyzer_spi.py` | 30 min | Logic Analyzer pattern generation (SPI-like) |
| day2 | `ex2_3_mim_frequency_sweep.py` | 45 min | Multi-Instrument Mode, internal routing, Bode plot |
| day3 | `ex3_1_datalogger_streaming.py` | 30 min | Real-time streaming, live statistics |
| day3 | `ex3_2_fft_snr_thd.py` | 45 min | FFT, SNR, THD signal-quality analysis |
| day4 | `capstone_option_a_component_characterizer.py` | ~2 h | Full datasheet: sweep + cutoff + roll-off + report |
| day4 | `capstone_option_b_signal_monitor.py` | ~2 h | Unattended monitoring, thresholds, alert log |
| day4 | `capstone_option_c_production_tester.py` | ~2 h | Pass/fail batch testing with test certificates |
| day5 | AI prompts (`*.txt`) + MCC experiment files | — | See `day5/` and the Day 5 Facilitator Guide |

## Expected Outputs (no hardware needed)

`expected_outputs/` contains the reference result for every exercise
(`ex1_1_expected.png`, …, `capstone_a_expected.png`) **and** the generator
scripts that produce them from simulated data:

```
cd expected_outputs
python generate_ex1_1_expected.py      # oscilloscope logging plot
python generate_ex1_2_expected.py      # WG sweep (console output only)
python generate_ex2_1_expected.py      # AWG waveform library
python generate_ex2_2_expected.py      # SPI logic analyzer
python generate_ex2_3_expected.py      # MiM Bode plot
python generate_ex3_1_expected.py      # datalogger streaming stats
python generate_ex3_2_expected.py      # FFT/SNR/THD analysis
python generate_capstone_a_expected.py # capstone A frequency response
```

Use these to (a) show participants what a correct run looks like,
(b) regenerate reference images after changing an exercise, and
(c) rehearse the workshop without a Moku:Go on the desk.

## Critical API Rules (hardware-verified)

These were verified on real Moku:Go hardware (moku v4.1.2, MokuOS 4.1.2)
and override anything older you may find in documentation or AI output:

1. **Always release the device** — `relinquish_ownership()` in a
   `finally` block. In MiM, release via `m.relinquish_ownership()` on the
   MultiInstrument object, **never** on the slot instruments.
2. **MiM connections are a LIST of dicts** —
   `m.set_connections(connections=[dict(source='Slot1OutA', destination='Output1'), ...])`.
   A plain dict silently drops duplicate keys and fails.
3. **`platform_id=2`** for Moku:Go (2-slot MiM).
4. **In MiM, `'Input1'` is NOT a valid trigger source** — use auto-trigger
   (simply don't call `set_trigger`).
5. **`get_data()` returns Python lists, not numpy arrays** — `min()`/`max()`
   work directly; convert with `np.array(data['ch1'])` before numpy math.
6. **Logic Analyzer:** all pins go in ONE
   `set_pattern_generator(channel=1, patterns=[{"pin": n, "pattern": [...]}], divider=...)`
   call, and pin mode is `set_pin_mode(pin, 'PG1')` — not `'Pattern'`.
7. **AWG:** `generate_waveform(channel=1, sample_rate='Auto', lut_data=list(...), ...)`
   — pass a plain Python list normalized to [-1, 1].
8. **Datalogger:** `start_streaming(duration=..., sample_rate=...)`; the
   `'End of stream'` exception is normal completion, not an error.
9. **Wait ≥ 50 ms after changing a waveform** before capturing
   (scripts use `SETTLE_TIME` from config.py).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Connection refused / timeout | Check IP in `config.py`; same network as the Moku:Go? |
| Instrument busy / locked | Another session holds it — `force_connect=True` (already set) or wait ~60 s |
| `ModuleNotFoundError: moku` | `pip install moku` |
| Bitstream not found | `mokucli instrument download` (needs internet, one time) |
| `get_data()` returns noise | Check BNC loopback cable and `set_frontend` range |
| Values clipped at rail | Signal exceeds input range — increase `range` in frontend settings |
