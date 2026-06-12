"""
Exercise 1.1: Oscilloscope Data Logging
========================================
Day 1 | 30 minutes | 5-Day SDI Lab Automation FDP (v2.0)

Objective: Capture 10 oscilloscope frames, save each to CSV,
           compute Vpp statistics, and generate a summary plot.

Setup: Connect Moku:Go Output 1 -> Input 1 (BNC loopback cable)

Verified against: Liquid Instruments Python API v4.x
Reference: https://apis.liquidinstruments.com/api/reference/oscilloscope/

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import csv
import time
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from moku.instruments import Oscilloscope

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT, FRONTEND

# ============================================================
# CONFIGURATION
# ============================================================
NUM_FRAMES = 10                # Number of frames to capture
FREQUENCY = 1e3                # 1 kHz test signal
AMPLITUDE = 0.5                # 0.5 Vpp
SETTLE_TIME = 0.5              # Seconds between captures
OUT_DIR = Path(__file__).parent  # Outputs saved next to this script

# ============================================================
# MAIN SCRIPT
# ============================================================
osc = Oscilloscope(MOKU_IP, force_connect=FORCE_CONNECT)

try:
    # --- Configure Frontend ---
    osc.set_frontend(channel=1, **FRONTEND)

    # --- Generate Test Signal (built-in Waveform Generator) ---
    osc.generate_waveform(
        1, 'Sine',
        amplitude=AMPLITUDE,
        frequency=FREQUENCY
    )

    # --- Set Timebase: +/-5ms (covers ~10 cycles at 1kHz) ---
    osc.set_timebase(-5e-3, 5e-3)

    # --- Set Trigger: Rising edge on Input 1 ---
    osc.set_trigger(type='Edge', source='Input1', level=0)

    # --- Capture Loop ---
    # get_data() returns plain Python lists ('ch1', 'ch2', 'time'),
    # so min()/max() work directly; convert with np.array() only
    # when numpy math is needed.
    all_data = []
    print(f"Capturing {NUM_FRAMES} frames...")
    print(f"{'Frame':>6} | {'Vpp (V)':>10} | {'Vmin (V)':>10} | {'Vmax (V)':>10}")
    print("-" * 50)

    for frame in range(NUM_FRAMES):
        data = osc.get_data()
        ch1 = data['ch1']
        time_axis = data['time']

        v_min = min(ch1)
        v_max = max(ch1)
        v_pp = v_max - v_min

        print(f"{frame+1:>6} | {v_pp:>10.4f} | {v_min:>10.4f} | {v_max:>10.4f}")

        # Save frame to CSV
        filename = OUT_DIR / f'frame_{frame+1:02d}.csv'
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time_s', 'voltage_V'])
            for t, v in zip(time_axis, ch1):
                writer.writerow([t, v])

        all_data.append({
            'frame': frame + 1,
            'vpp': v_pp,
            'vmin': v_min,
            'vmax': v_max
        })
        time.sleep(SETTLE_TIME)

    # --- Summary Statistics ---
    vpps = [d['vpp'] for d in all_data]
    print(f"\n{'='*50}")
    print(f"SUMMARY ({NUM_FRAMES} frames)")
    print(f"{'='*50}")
    print(f"  Mean Vpp:  {np.mean(vpps):.4f} V")
    print(f"  Std Dev:   {np.std(vpps):.4f} V")
    print(f"  Min Vpp:   {min(vpps):.4f} V")
    print(f"  Max Vpp:   {max(vpps):.4f} V")

    # --- Generate Summary Plot ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart of Vpp per frame
    frames = [d['frame'] for d in all_data]
    ax1.bar(frames, vpps, color='#0057B8', alpha=0.85)
    ax1.set_xlabel('Frame Number')
    ax1.set_ylabel('Vpp (V)')
    ax1.set_title('Peak-to-Peak Voltage per Frame')
    ax1.axhline(y=np.mean(vpps), color='#FF6B35', linestyle='--',
                label=f'Mean: {np.mean(vpps):.4f}V')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Last captured waveform
    ax2.plot(data['time'], data['ch1'], color='#0057B8', linewidth=0.8)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Voltage (V)')
    ax2.set_title(f'Last Frame (Frame {NUM_FRAMES})')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'oscilloscope_summary.png', dpi=150)
    print(f"\nPlot saved: oscilloscope_summary.png")
    print(f"CSV files saved: frame_01.csv through frame_{NUM_FRAMES:02d}.csv")

except Exception as e:
    print(f"Error: {e}")

finally:
    osc.relinquish_ownership()
    print("Connection released.")
