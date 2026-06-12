"""
Expected Output Generator: Exercise 1.2 — Waveform Generator Sweep
====================================================================
Generates reference console output (no plot — this exercise is text-only).
Trainers use this to show participants what their output SHOULD look like.

Run: python generate_ex1_2_expected.py
"""

import time

FREQUENCIES = [100, 500, 1000, 5000, 10000, 50000, 100000]
WAVEFORMS = ['Sine', 'Square', 'Ramp']
AMPLITUDE = 1.0
SETTLE_TIME = 0.5
MANUAL_TIME_PER_CHANGE = 30

total_tests = len(FREQUENCIES) * len(WAVEFORMS)

print("--- Expected Console Output ---")
print(f"Parametric Sweep: {len(WAVEFORMS)} waveforms × "
      f"{len(FREQUENCIES)} frequencies = {total_tests} tests")
print(f"\n{'Test':>5} | {'Waveform':>8} | {'Frequency':>12} | {'Amplitude':>10}")
print("-" * 50)

test_num = 0
for wf_type in WAVEFORMS:
    for freq in FREQUENCIES:
        test_num += 1
        print(f"{test_num:>5} | {wf_type:>8} | {freq:>10.0f} Hz | "
              f"{AMPLITUDE:>8.1f} Vpp")

# Simulated timing
automated_time = total_tests * SETTLE_TIME + 2.0  # ~12.5s typical
manual_time = total_tests * MANUAL_TIME_PER_CHANGE

print(f"\n{'='*50}")
print(f"EFFICIENCY REPORT")
print(f"{'='*50}")
print(f"  Total tests:       {total_tests}")
print(f"  Automated time:    {automated_time:.1f} seconds")
print(f"  Manual estimate:   {manual_time} seconds "
      f"({manual_time/60:.1f} min)")
print(f"  Time saved:        {manual_time - automated_time:.1f} seconds")
print(f"  Efficiency gain:   {manual_time/automated_time:.1f}× faster")
print(f"\n  Data saved to: wg_sweep_log.csv")
print(f"\n✓ No plot generated (this exercise produces CSV + console output only)")
