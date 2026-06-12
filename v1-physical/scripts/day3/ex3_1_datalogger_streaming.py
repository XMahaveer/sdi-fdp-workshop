"""
Exercise 3.1: Datalogger Streaming
====================================
Day 3 | 30 minutes | 5-Day SDI Lab Automation FDP (v2.0)

Objective: Stream real-time voltage data from the Datalogger,
           compute live statistics, and save all samples to CSV.

Setup: Connect Output 1 -> Input 1 (BNC loopback) for test signal.

API NOTE: the 'End of stream' exception is NORMAL completion of a
fixed-duration stream — catch it to exit the loop gracefully.

Verified against: Liquid Instruments Python API v4.x
Reference: https://apis.liquidinstruments.com/api/reference/datalogger/

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import csv
import time
from pathlib import Path

import numpy as np
from moku.instruments import Datalogger

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT, FRONTEND

# ============================================================
# CONFIGURATION
# ============================================================
STREAM_DURATION = 10        # Seconds
SAMPLE_RATE = 10e3          # 10 kSa/s
SIGNAL_FREQ = 100           # Hz test signal
OUT_DIR = Path(__file__).parent

# ============================================================
# MAIN SCRIPT
# ============================================================
dl = Datalogger(MOKU_IP, force_connect=FORCE_CONNECT)

try:
    # --- Configure Frontend ---
    dl.set_frontend(channel=1, **FRONTEND)

    # --- Generate Test Signal ---
    dl.generate_waveform(1, 'Sine', frequency=SIGNAL_FREQ)

    # --- Disable Input 2 (stream only Input 1) ---
    dl.enable_input(2, enable=False)

    # --- Start Streaming ---
    print(f"Streaming: {STREAM_DURATION}s at {SAMPLE_RATE/1e3:.0f} kSa/s")
    print(f"Test signal: {SIGNAL_FREQ} Hz sine wave\n")

    dl.start_streaming(duration=STREAM_DURATION,
                       sample_rate=SAMPLE_RATE)

    all_samples = []
    chunk_count = 0
    start_time = time.time()

    print(f"{'Chunk':>6} | {'Samples':>8} | {'Mean (V)':>10} | "
          f"{'Std (V)':>10} | {'Vpp (V)':>10}")
    print("-" * 58)

    while True:
        try:
            data = dl.get_stream_data()
            if data:
                ch1 = data['ch1']
                all_samples.extend(ch1)
                chunk_count += 1

                v_mean = np.mean(ch1)
                v_std = np.std(ch1)
                v_pp = max(ch1) - min(ch1)

                print(f"{chunk_count:>6} | {len(ch1):>8} | "
                      f"{v_mean:>10.4f} | {v_std:>10.4f} | "
                      f"{v_pp:>10.4f}")

        except Exception as e:
            if 'End of stream' in str(e):
                print("\nStream complete!")
                break
            raise

    elapsed = time.time() - start_time

    # --- Final Statistics ---
    all_np = np.array(all_samples)
    print(f"\n{'='*58}")
    print(f"STREAMING SUMMARY")
    print(f"{'='*58}")
    print(f"  Total samples:   {len(all_samples):,}")
    print(f"  Total chunks:    {chunk_count}")
    print(f"  Actual duration: {elapsed:.1f} seconds")
    print(f"  Effective rate:  {len(all_samples)/elapsed:,.0f} Sa/s")
    print(f"  Overall Mean:    {np.mean(all_np):.6f} V")
    print(f"  Overall Std:     {np.std(all_np):.6f} V")
    print(f"  Overall Vpp:     {max(all_np)-min(all_np):.4f} V")
    print(f"  Min:             {min(all_np):.4f} V")
    print(f"  Max:             {max(all_np):.4f} V")

    # --- Save to CSV ---
    with open(OUT_DIR / 'stream_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sample_index', 'voltage_V'])
        for i, v in enumerate(all_samples):
            writer.writerow([i, v])

    print(f"\n  Data saved: stream_data.csv ({len(all_samples):,} rows)")

except Exception as e:
    print(f"Error: {e}")

finally:
    dl.relinquish_ownership()
    print("Connection released.")
