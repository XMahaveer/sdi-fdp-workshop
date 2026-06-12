"""
Exercise 2.3: Multi-Instrument Mode — WG + Oscilloscope Sweep
==============================================================
Day 2 | 45 minutes | 5-Day SDI Lab Automation FDP (v2.0)

Objective: Run WG and Oscilloscope simultaneously via MiM,
           perform automated frequency sweep, measure amplitude
           response, and generate a Bode-style plot.

Setup: Internal routing (no external cables needed for loopback).
       For DUT testing, connect Output 1 -> DUT -> Input 1.

CRITICAL API NOTES (hardware-verified March 2026):
  - platform_id=2 for Moku:Go (2 slots)
  - Connections MUST be list of dicts: [dict(source='...', destination='...')]
  - In MiM, 'Input1' is NOT a valid trigger source — auto-trigger works
  - Always relinquish on MultiInstrument object (m), NOT on wg or osc

Verified against: Liquid Instruments Python API v4.x
Reference: https://apis.liquidinstruments.com/starting-mim.html

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import csv
import time
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from moku.instruments import MultiInstrument, WaveformGenerator, Oscilloscope

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT, PLATFORM_ID

# ============================================================
# CONFIGURATION
# ============================================================
NUM_POINTS = 25             # Frequency sweep points
F_START = 10                # Hz
F_STOP = 100e3              # Hz
AMPLITUDE = 1.0             # Vpp
SETTLE_TIME = 0.3           # Seconds between measurements
OUT_DIR = Path(__file__).parent

# ============================================================
# MAIN SCRIPT
# ============================================================
m = MultiInstrument(MOKU_IP, platform_id=PLATFORM_ID, force_connect=FORCE_CONNECT)

try:
    # --- Deploy Instruments ---
    wg = m.set_instrument(1, WaveformGenerator)
    osc = m.set_instrument(2, Oscilloscope)

    # --- Configure Internal Routing ---
    # CORRECT FORMAT: list of dicts with source/destination keys
    # CORRECT ROUTING FOR DUT TESTING (HARDWARE VERIFIED March 2026):
    # WG -> Output1 -> [DUT/Loopback] -> Input1 -> Oscilloscope
    connections = [
        dict(source='Slot1OutA', destination='Output1'),    # WG -> physical Output 1
        dict(source='Input1', destination='Slot2InA'),      # physical Input 1 -> Scope
    ]
    m.set_connections(connections=connections)

    # --- Configure Oscilloscope ---
    # NOTE: In MiM, 'Input1' is NOT a valid trigger source. Auto-trigger works.

    # --- Frequency Sweep ---
    freqs = np.logspace(
        np.log10(F_START),
        np.log10(F_STOP),
        NUM_POINTS
    )
    results = []

    print(f"MiM Frequency Sweep: {F_START} Hz to {F_STOP/1e3:.0f} kHz "
          f"({NUM_POINTS} points)")
    print(f"\n{'#':>3} | {'Freq (Hz)':>12} | {'Vpp (V)':>10} | {'Gain (dB)':>10}")
    print("-" * 50)

    for i, freq in enumerate(freqs):
        # Set waveform generator
        wg.generate_waveform(
            channel=1,
            type='Sine',
            amplitude=AMPLITUDE,
            frequency=freq
        )

        # Adjust timebase to show ~10 cycles
        period = 1.0 / freq
        osc.set_timebase(-5 * period, 5 * period)

        time.sleep(SETTLE_TIME)

        # Capture and measure (get_data() returns Python lists)
        data = osc.get_data()
        ch1 = data['ch1']
        vpp = max(ch1) - min(ch1)
        gain_db = 20 * np.log10(vpp / AMPLITUDE) if vpp > 0 else -100

        results.append({
            'freq': freq,
            'vpp': vpp,
            'gain_db': gain_db
        })
        print(f"{i+1:>3} | {freq:>12.1f} | {vpp:>10.4f} | {gain_db:>10.2f}")

    # --- Save Results ---
    with open(OUT_DIR / 'mim_sweep_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frequency_Hz', 'amplitude_Vpp', 'gain_dB'])
        for r in results:
            writer.writerow([r['freq'], r['vpp'], r['gain_db']])

    # --- Find -3dB Point ---
    ref_vpp = results[0]['vpp']
    cutoff_3db = None
    for r in results:
        if r['vpp'] < ref_vpp * 0.707:  # -3dB = 70.7%
            cutoff_3db = r['freq']
            break

    # --- Generate Bode Plot ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    f_vals = [r['freq'] for r in results]
    vpp_vals = [r['vpp'] for r in results]
    gain_vals = [r['gain_db'] for r in results]

    # Amplitude vs Frequency
    ax1.semilogx(f_vals, vpp_vals, 'b-o', markersize=5, linewidth=1.5)
    ax1.set_ylabel('Amplitude (Vpp)', fontsize=11)
    ax1.set_title('MiM Frequency Sweep — Amplitude Response',
                 fontsize=14, fontweight='bold')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.axhline(y=ref_vpp * 0.707, color='#FF6B35', linestyle='--',
               alpha=0.7, label='-3dB level')
    if cutoff_3db:
        ax1.axvline(x=cutoff_3db, color='#FF6B35', linestyle=':',
                    alpha=0.7, label=f'fc ~ {cutoff_3db:.0f} Hz')
    ax1.legend()

    # Gain (dB) vs Frequency
    ax2.semilogx(f_vals, gain_vals, 'g-o', markersize=5, linewidth=1.5)
    ax2.set_xlabel('Frequency (Hz)', fontsize=11)
    ax2.set_ylabel('Gain (dB)', fontsize=11)
    ax2.set_title('Gain Response', fontsize=12)
    ax2.grid(True, which='both', alpha=0.3)
    ax2.axhline(y=-3, color='#FF6B35', linestyle='--', alpha=0.7, label='-3dB')
    ax2.legend()

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'mim_sweep_bode.png', dpi=150)

    print(f"\nResults saved: mim_sweep_data.csv")
    print(f"Bode plot saved: mim_sweep_bode.png")
    if cutoff_3db:
        print(f"-3dB cutoff frequency: ~{cutoff_3db:.0f} Hz")
    else:
        print("No -3dB cutoff found in measurement range (flat response).")

except Exception as e:
    print(f"Error: {e}")

finally:
    # CRITICAL: Always relinquish on MultiInstrument object, NOT instruments
    m.relinquish_ownership()
    print("Connection released.")
