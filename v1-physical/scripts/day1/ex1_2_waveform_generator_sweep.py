"""
Exercise 1.2: Waveform Generator Parametric Sweep
===================================================
Day 1 | 30 minutes | 5-Day SDI Lab Automation FDP (v2.0)

Objective: Automate a frequency x waveform sweep using the standalone
           Waveform Generator and compare to manual operation time.

Setup: No cable needed (output only). Optionally connect
       Output 1 -> Input 1 to observe on external oscilloscope.

Verified against: Liquid Instruments Python API v4.x
Reference: https://apis.liquidinstruments.com/api/reference/waveformgenerator/

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import csv
import time
from pathlib import Path

from moku.instruments import WaveformGenerator

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT

# ============================================================
# CONFIGURATION
# ============================================================
AMPLITUDE = 1.0             # Vpp
SETTLE_TIME = 0.5           # Seconds between waveform changes
MANUAL_TIME_PER_CHANGE = 30 # Estimated seconds per manual config change
OUT_DIR = Path(__file__).parent

FREQUENCIES = [100, 500, 1000, 5000, 10000, 50000, 100000]  # Hz
WAVEFORMS = ['Sine', 'Square', 'Ramp']

# Waveform-specific required parameters (Moku API validation)
# Square requires 'duty', Ramp requires 'symmetry', Pulse requires 'duty'
WAVEFORM_PARAMS = {
    'Sine':     {},
    'Square':   {'duty': 50},       # 50% duty cycle (default symmetric)
    'Ramp':     {'symmetry': 50},   # 50% symmetry (triangle-like ramp)
    'Triangle': {},
    'Pulse':    {'duty': 50},
    'DC':       {},
}

# ============================================================
# MAIN SCRIPT
# ============================================================
wg = WaveformGenerator(MOKU_IP, force_connect=FORCE_CONNECT)

try:
    total_tests = len(FREQUENCIES) * len(WAVEFORMS)
    print(f"Parametric Sweep: {len(WAVEFORMS)} waveforms x "
          f"{len(FREQUENCIES)} frequencies = {total_tests} tests")
    print(f"\n{'Test':>5} | {'Waveform':>8} | {'Frequency':>12} | {'Amplitude':>10}")
    print("-" * 50)

    start_time = time.time()
    test_num = 0

    with open(OUT_DIR / 'wg_sweep_log.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['test_num', 'waveform', 'frequency_Hz',
                        'amplitude_Vpp', 'timestamp'])

        for wf_type in WAVEFORMS:
            for freq in FREQUENCIES:
                test_num += 1

                # Build params: add waveform-specific required fields
                params = dict(
                    channel=1,
                    type=wf_type,
                    amplitude=AMPLITUDE,
                    frequency=freq
                )
                params.update(WAVEFORM_PARAMS.get(wf_type, {}))
                wg.generate_waveform(**params)

                writer.writerow([
                    test_num, wf_type, freq, AMPLITUDE,
                    time.strftime('%H:%M:%S')
                ])

                print(f"{test_num:>5} | {wf_type:>8} | {freq:>10.0f} Hz | "
                      f"{AMPLITUDE:>8.1f} Vpp")

                time.sleep(SETTLE_TIME)

    # --- Timing Report ---
    elapsed = time.time() - start_time
    manual_time = total_tests * MANUAL_TIME_PER_CHANGE

    print(f"\n{'='*50}")
    print(f"EFFICIENCY REPORT")
    print(f"{'='*50}")
    print(f"  Total tests:       {total_tests}")
    print(f"  Automated time:    {elapsed:.1f} seconds")
    print(f"  Manual estimate:   {manual_time} seconds "
          f"({manual_time/60:.1f} min)")
    print(f"  Time saved:        {manual_time - elapsed:.1f} seconds")
    print(f"  Efficiency gain:   {manual_time/elapsed:.1f}x faster")
    print(f"\n  Data saved to: wg_sweep_log.csv")

except Exception as e:
    print(f"Error: {e}")

finally:
    wg.relinquish_ownership()
    print("Connection released.")
