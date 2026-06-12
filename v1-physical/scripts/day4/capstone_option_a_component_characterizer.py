"""
Capstone Option A: Automated Component Characterization Station
================================================================
Day 4 | ~2 hours | 5-Day SDI Lab Automation FDP (v2.0)

Real application: an electronics teaching lab needs to characterize
RC filters and produce a complete mini-datasheet for each one.

What this does (fully automated):
  1. MiM: Waveform Generator (Slot 1) + Oscilloscope (Slot 2)
  2. Logarithmic frequency sweep 10 Hz - 100 kHz (30 points)
  3. Measures output amplitude at every frequency
  4. Computes gain (dB), -3dB cutoff, and roll-off rate (dB/decade)
  5. Saves CSV data, a Bode plot PNG, and a text datasheet report

Setup: Output 1 -> [DUT or BNC loopback] -> Input 1
       Loopback gives a flat ~0 dB response (sanity check).
       An RC low-pass filter shows the classic -20 dB/decade roll-off.

Manual time: ~40 min per component. Automated goal: < 5 min.

CRITICAL API NOTES (hardware-verified March 2026):
  - Connections are a LIST OF DICTS, never a plain dict
  - In MiM, 'Input1' is NOT a valid trigger source — auto-trigger works
  - Cleanup via m.relinquish_ownership() ONLY

Verified against: Liquid Instruments Python API v4.x

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import csv
import time
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from moku.instruments import MultiInstrument, WaveformGenerator, Oscilloscope

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT, PLATFORM_ID

# ============================================================
# CONFIGURATION
# ============================================================
COMPONENT_NAME = 'RC Low-Pass Filter'   # Appears on the datasheet
F_START = 10                # Hz
F_STOP = 100e3              # Hz
NUM_POINTS = 30             # Sweep points (>= 25 required)
AMPLITUDE = 1.0             # Vpp stimulus
SETTLE_TIME = 0.3           # Seconds after each frequency change
OUT_DIR = Path(__file__).parent

# ============================================================
# MEASUREMENT
# ============================================================
def run_sweep(wg, osc):
    """Sweep frequency, return list of {freq, vpp, gain_db} dicts."""
    freqs = np.logspace(np.log10(F_START), np.log10(F_STOP), NUM_POINTS)
    results = []

    print(f"\n{'#':>3} | {'Freq (Hz)':>12} | {'Vpp (V)':>10} | {'Gain (dB)':>10}")
    print("-" * 50)

    for i, freq in enumerate(freqs):
        wg.generate_waveform(channel=1, type='Sine',
                             amplitude=AMPLITUDE, frequency=freq)

        # Show ~10 cycles regardless of frequency
        period = 1.0 / freq
        osc.set_timebase(-5 * period, 5 * period)
        time.sleep(SETTLE_TIME)

        data = osc.get_data()              # Python lists
        ch1 = data['ch1']
        vpp = max(ch1) - min(ch1)
        gain_db = 20 * np.log10(vpp / AMPLITUDE) if vpp > 0 else -100

        results.append({'freq': freq, 'vpp': vpp, 'gain_db': gain_db})
        print(f"{i+1:>3} | {freq:>12.1f} | {vpp:>10.4f} | {gain_db:>10.2f}")

    return results


def analyze(results):
    """Extract -3dB cutoff and roll-off rate from sweep results."""
    ref_vpp = results[0]['vpp']
    ref_gain = results[0]['gain_db']

    # -3dB cutoff: first point where amplitude drops below 70.7% of reference
    cutoff = None
    for r in results:
        if r['vpp'] < ref_vpp * 0.707:
            cutoff = r['freq']
            break

    # Roll-off rate: slope of the last decade of the sweep (dB/decade)
    rolloff = None
    if cutoff:
        tail = [r for r in results if r['freq'] >= cutoff]
        if len(tail) >= 2:
            dg = tail[-1]['gain_db'] - tail[0]['gain_db']
            dlogf = np.log10(tail[-1]['freq']) - np.log10(tail[0]['freq'])
            if dlogf > 0:
                rolloff = dg / dlogf

    return {'ref_gain_db': ref_gain, 'cutoff_hz': cutoff,
            'rolloff_db_per_decade': rolloff}


# ============================================================
# REPORTING
# ============================================================
def save_outputs(results, analysis, elapsed):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = OUT_DIR / f'capstone_a_data_{ts}.csv'
    plot_path = OUT_DIR / f'capstone_a_bode_{ts}.png'
    report_path = OUT_DIR / f'capstone_a_datasheet_{ts}.txt'

    # --- CSV ---
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frequency_Hz', 'amplitude_Vpp', 'gain_dB'])
        for r in results:
            writer.writerow([r['freq'], r['vpp'], r['gain_db']])

    # --- Bode plot ---
    f_vals = [r['freq'] for r in results]
    gain_vals = [r['gain_db'] for r in results]

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.semilogx(f_vals, gain_vals, '-o', color='#0057B8',
                markersize=5, linewidth=1.5)
    ax.axhline(y=analysis['ref_gain_db'] - 3, color='#FF6B35',
               linestyle='--', alpha=0.7, label='-3 dB level')
    if analysis['cutoff_hz']:
        ax.axvline(x=analysis['cutoff_hz'], color='#FF6B35', linestyle=':',
                   alpha=0.7, label=f"fc ~ {analysis['cutoff_hz']:.0f} Hz")
    ax.set_xlabel('Frequency (Hz)', fontsize=11)
    ax.set_ylabel('Gain (dB)', fontsize=11)
    ax.set_title(f'{COMPONENT_NAME} — Frequency Response',
                 fontsize=14, fontweight='bold')
    ax.grid(True, which='both', alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)

    # --- Text datasheet ---
    with open(report_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("COMPONENT CHARACTERIZATION DATASHEET\n")
        f.write("=" * 60 + "\n")
        f.write(f"Component:        {COMPONENT_NAME}\n")
        f.write(f"Generated:        {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write(f"Test system:      Moku:Go MiM (WG + Oscilloscope)\n")
        f.write(f"Stimulus:         {AMPLITUDE} Vpp sine\n")
        f.write(f"Sweep:            {F_START:.0f} Hz - {F_STOP/1e3:.0f} kHz, "
                f"{NUM_POINTS} points (log)\n")
        f.write("-" * 60 + "\n")
        f.write(f"Passband gain:    {analysis['ref_gain_db']:.2f} dB\n")
        if analysis['cutoff_hz']:
            f.write(f"-3dB cutoff:      ~{analysis['cutoff_hz']:.0f} Hz\n")
        else:
            f.write("-3dB cutoff:      not found (flat in range)\n")
        if analysis['rolloff_db_per_decade']:
            f.write(f"Roll-off rate:    "
                    f"{analysis['rolloff_db_per_decade']:.1f} dB/decade\n")
        f.write("-" * 60 + "\n")
        f.write(f"Test duration:    {elapsed:.1f} s "
                f"(manual estimate: ~40 min)\n")
        f.write(f"Data file:        {csv_path.name}\n")
        f.write(f"Bode plot:        {plot_path.name}\n")
        f.write("=" * 60 + "\n")
        f.write("Spruha Build-in Solutions | "
                "Powered by Moku:Go — Liquid Instruments\n")

    print(f"\nSaved: {csv_path.name}")
    print(f"Saved: {plot_path.name}")
    print(f"Saved: {report_path.name}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print(f"Capstone A — Component Characterization: {COMPONENT_NAME}")
    start = time.time()

    m = MultiInstrument(MOKU_IP, platform_id=PLATFORM_ID,
                        force_connect=FORCE_CONNECT)
    try:
        wg = m.set_instrument(1, WaveformGenerator)
        osc = m.set_instrument(2, Oscilloscope)

        # WG -> Output1 -> [DUT/loopback] -> Input1 -> Scope
        m.set_connections(connections=[
            dict(source='Slot1OutA', destination='Output1'),
            dict(source='Input1', destination='Slot2InA'),
        ])

        results = run_sweep(wg, osc)
        analysis = analyze(results)
        elapsed = time.time() - start
        save_outputs(results, analysis, elapsed)

        print(f"\nDone in {elapsed:.1f} s "
              f"({40*60/elapsed:.0f}x faster than manual).")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        m.relinquish_ownership()
        print("Connection released.")
