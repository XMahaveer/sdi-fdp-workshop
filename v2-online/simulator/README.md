# mokusim — Moku:Go Simulator (V2 Model A)

A `moku`-API-compatible simulator: **every V1 workshop script runs
unmodified, with zero hardware.** This is the core of the V2 online
edition — participants do the Days 1–4 exercises from any laptop.

**Organization:** Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments

## Quick Start

```
cd v2-online/simulator
python simrun.py ../../v1-physical/scripts/day1/ex1_1_oscilloscope_logging.py
```

You'll see `[mokusim] MOKU SIMULATOR ACTIVE` followed by the script's
normal output — same CSVs, same plots, no Moku:Go on the desk. The
script file itself is untouched: take it to real hardware and it runs
as-is.

Alternative (no runner): put the simulator directory on `PYTHONPATH`:

```
PYTHONPATH=v2-online/simulator python v1-physical/scripts/day1/ex1_1_oscilloscope_logging.py
```

## How It Works

The `moku/` package here **shadows** the real `moku` package when the
simulator directory comes first on `sys.path`. It implements the
workshop's instrument surface:

| Class | Simulated behavior |
|-------|--------------------|
| `Oscilloscope` | synthesizes frames from the generated/routed signal: 1024 points across the timebase, ~0.5 mV noise, 0.3% 3rd-harmonic distortion (so FFT/SNR/THD exercises return realistic numbers); returns **Python lists** like hardware |
| `WaveformGenerator` | Sine/Square/Ramp/Triangle/Pulse/DC with per-type parameter validation (`duty=`, `symmetry=`), AM via `set_modulation` |
| `ArbitraryWaveformGenerator` | `lut_data` playback; **rejects numpy arrays** and out-of-range LUTs |
| `LogicAnalyzer` | verified `patterns=[{"pin":…}]` API; pattern playback on `get_data` |
| `Datalogger` | chunked streaming; raises `'End of stream'` at the end, like hardware |
| `MultiInstrument` | 2-slot routing matrix with node-name validation; models the physical Output 1 → Input 1 loopback |
| `CustomInstrument` | Day 5 threshold-detector semantics: `set_control(0, …)` threshold, `get_status()[0]` ≈ crossings/sec |

### The loopback & DUT model

The workshop's standard BNC loopback (Output 1 → Input 1) is assumed
present. To put a device-under-test in that path:

```
MOKUSIM_DUT=rc:2500 python simrun.py ../../v1-physical/scripts/day2/ex2_3_mim_frequency_sweep.py
```

simulates a first-order RC low-pass with fc = 2.5 kHz — the Bode sweep
finds the cutoff and the capstone characterizer measures ≈ −20 dB/decade
roll-off, just like wiring a real RC network.

## Teaching Rules Are Enforced

The simulator fails the same way hardware (or the real API) fails, with
instructive messages, so skills transfer:

| Wrong call | Simulator response |
|------------|--------------------|
| `set_connections(connections={…})` plain dict | error: must be a LIST of dicts (#1 MiM mistake) |
| `set_trigger(source='Input1')` inside MiM | error: not a valid trigger source in MiM — use auto-trigger |
| `wg.relinquish_ownership()` on a slot instrument | error: release via `m.relinquish_ownership()` |
| `set_pin_mode(pin, 'Pattern')` | error: use `'PG1'` (hardware-verified) |
| `set_pattern_generator(pin=…, pattern=…)` legacy call | error: use `channel=` + `patterns=[…]` |
| numpy array as `lut_data` | error: wrap with `list(...)` |
| `type='Square'` without `duty=` | error: API validates per-type params |

## Acceptance Test

```
python run_all_v1.py
```

Runs all 10 Day 1–4 scripts (exercises + the three capstones) through
the simulator in subprocesses, checks exit codes, output markers, and
artifacts, then asserts all seven teaching-rule rejections. Current
status: **ALL PASS**.

## Fidelity Notes (what this is and isn't)

- Timing is not simulated: streams return instantly, so "effective
  rate" printouts exceed real-time rates. Settle times (`time.sleep`)
  still run for real.
- Signal model is intentional-but-simple: additive Gaussian noise,
  fixed 3rd-harmonic distortion, ideal trigger at t=0, first-order DUT
  only. Good enough for every Day 1–4 measurement; not a circuit
  simulator.
- `get_data()['ch2']` is noise unless routed; phase is not modeled.
- The Day 5 MCC *compile* flow is inherently cloud-based and is not
  simulated — `CustomInstrument` simulates the deployed instrument's
  register behavior so the host script demonstrates Control/Status
  round-trips.
