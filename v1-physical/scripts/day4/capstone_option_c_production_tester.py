"""
Capstone Option C: Automated Production Test System
====================================================
Day 4 | ~2 hours | 5-Day SDI Lab Automation FDP (v2.0)

Real application: a manufacturer must test oscillator circuits before
shipping. Manual test: ~8 min/unit. Automated goal: < 90 s/unit.

What this does (per unit, fully automated):
  1. Captures the unit's output on the Oscilloscope
  2. Measures: frequency (FFT peak), amplitude (Vpp), distortion (THD)
  3. Compares against specifications:
       frequency  1 MHz +/- 1%
       amplitude  >= 0.8 Vpp
       THD        <= 5%
  4. Prints PASS/FAIL per metric and overall verdict
  5. Writes a test certificate (TXT) per unit and appends to a
     batch results CSV

Setup (demo): Output 1 -> Input 1 (BNC loopback); the Oscilloscope's
built-in waveform generator simulates the DUT (1 MHz sine, 1 Vpp).
For real DUTs: connect the oscillator output to Input 1 and remove
the generate_waveform call.

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
from moku.instruments import Oscilloscope

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT, FRONTEND

# ============================================================
# CONFIGURATION
# ============================================================
NUM_UNITS = 3               # Units in this batch (prompted between units)
NUM_HARMONICS = 5           # Harmonics included in THD

# Demo signal (simulated DUT via built-in WG) — remove for real DUTs
DEMO_FREQ = 1e6             # 1 MHz
DEMO_AMPLITUDE = 1.0        # Vpp

# Specifications
SPEC_FREQ = 1e6             # Target frequency (Hz)
SPEC_FREQ_TOL = 0.01        # +/- 1%
SPEC_VPP_MIN = 0.8          # Minimum amplitude (Vpp)
SPEC_THD_MAX = 5.0          # Maximum THD (%)

OUT_DIR = Path(__file__).parent

# ============================================================
# MEASUREMENT
# ============================================================
def measure_unit(osc):
    """Capture one frame and return measured frequency, Vpp, and THD%."""
    data = osc.get_data()                   # Python lists
    ch1 = np.array(data['ch1'])             # convert for numpy math
    t = np.array(data['time'])

    vpp = float(ch1.max() - ch1.min())

    # FFT with Hann window
    N = len(ch1)
    dt = t[1] - t[0]
    fft_mag = 2.0 / N * np.abs(np.fft.rfft(ch1 * np.hanning(N)))
    freqs = np.fft.rfftfreq(N, dt)

    peak_idx = int(np.argmax(fft_mag[1:]) + 1)   # skip DC
    freq_measured = float(freqs[peak_idx])
    peak_amp = fft_mag[peak_idx]

    # THD from harmonics 2..NUM_HARMONICS
    harmonics = [fft_mag[peak_idx * h]
                 for h in range(2, NUM_HARMONICS + 1)
                 if peak_idx * h < len(fft_mag)]
    thd_pct = float(np.sqrt(sum(h ** 2 for h in harmonics)) / peak_amp * 100)

    return freq_measured, vpp, thd_pct


def judge(freq, vpp, thd_pct):
    """Compare measurements to spec. Returns dict of per-metric verdicts."""
    freq_ok = abs(freq - SPEC_FREQ) / SPEC_FREQ <= SPEC_FREQ_TOL
    vpp_ok = vpp >= SPEC_VPP_MIN
    thd_ok = thd_pct <= SPEC_THD_MAX
    return {
        'frequency': freq_ok,
        'amplitude': vpp_ok,
        'thd': thd_ok,
        'overall': freq_ok and vpp_ok and thd_ok,
    }


def write_certificate(unit_id, freq, vpp, thd_pct, verdicts, test_time):
    """Write a per-unit test certificate."""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = OUT_DIR / f'capstone_c_certificate_unit{unit_id:03d}_{ts}.txt'

    def mark(ok):
        return 'PASS' if ok else 'FAIL'

    with open(path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("PRODUCTION TEST CERTIFICATE\n")
        f.write("=" * 60 + "\n")
        f.write(f"Unit ID:        {unit_id:03d}\n")
        f.write(f"Tested:         {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write(f"Test system:    Moku:Go Oscilloscope + FFT analysis\n")
        f.write(f"Test duration:  {test_time:.1f} s\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Metric':<12}{'Measured':>14}{'Specification':>22}"
                f"{'Result':>8}\n")
        f.write(f"{'Frequency':<12}{freq/1e6:>11.4f} MHz"
                f"{'1 MHz +/- 1%':>22}{mark(verdicts['frequency']):>8}\n")
        f.write(f"{'Amplitude':<12}{vpp:>10.4f} Vpp"
                f"{'>= 0.8 Vpp':>22}{mark(verdicts['amplitude']):>8}\n")
        f.write(f"{'THD':<12}{thd_pct:>12.2f} %"
                f"{'<= 5%':>22}{mark(verdicts['thd']):>8}\n")
        f.write("-" * 60 + "\n")
        f.write(f"OVERALL VERDICT: "
                f"{'PASS — unit approved for shipment' if verdicts['overall'] else 'FAIL — unit rejected'}\n")
        f.write("=" * 60 + "\n")
        f.write("Spruha Build-in Solutions | "
                "Powered by Moku:Go — Liquid Instruments\n")

    return path


# ============================================================
# MAIN — batch test loop
# ============================================================
if __name__ == '__main__':
    print("Capstone C — Production Test System")
    print(f"Specs: {SPEC_FREQ/1e6:.0f} MHz +/-{SPEC_FREQ_TOL*100:.0f}%, "
          f">= {SPEC_VPP_MIN} Vpp, <= {SPEC_THD_MAX}% THD")
    print(f"Batch size: {NUM_UNITS} units\n")

    osc = Oscilloscope(MOKU_IP, force_connect=FORCE_CONNECT)
    batch_results = []

    try:
        osc.set_frontend(channel=1, **FRONTEND)

        # Demo DUT: built-in WG generates a 1 MHz sine on Output 1.
        # Remove this call when testing real oscillator units.
        osc.generate_waveform(1, 'Sine', amplitude=DEMO_AMPLITUDE,
                              frequency=DEMO_FREQ)

        # ~10 cycles of a 1 MHz signal
        period = 1.0 / SPEC_FREQ
        osc.set_timebase(-5 * period, 5 * period)
        osc.set_trigger(type='Edge', source='Input1', level=0)

        for unit_id in range(1, NUM_UNITS + 1):
            input(f"Connect unit {unit_id:03d} and press Enter to test...")
            t0 = time.time()

            freq, vpp, thd_pct = measure_unit(osc)
            verdicts = judge(freq, vpp, thd_pct)
            test_time = time.time() - t0

            print(f"  Frequency: {freq/1e6:.4f} MHz "
                  f"[{'PASS' if verdicts['frequency'] else 'FAIL'}]")
            print(f"  Amplitude: {vpp:.4f} Vpp "
                  f"[{'PASS' if verdicts['amplitude'] else 'FAIL'}]")
            print(f"  THD:       {thd_pct:.2f} % "
                  f"[{'PASS' if verdicts['thd'] else 'FAIL'}]")
            print(f"  OVERALL:   "
                  f"{'PASS' if verdicts['overall'] else 'FAIL'} "
                  f"({test_time:.1f} s)\n")

            cert = write_certificate(unit_id, freq, vpp, thd_pct,
                                     verdicts, test_time)
            batch_results.append({
                'unit': unit_id,
                'frequency_Hz': freq,
                'vpp_V': vpp,
                'thd_pct': thd_pct,
                'verdict': 'PASS' if verdicts['overall'] else 'FAIL',
                'certificate': cert.name,
            })

        # --- Batch summary CSV ---
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = OUT_DIR / f'capstone_c_batch_{ts}.csv'
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(batch_results[0].keys()))
            writer.writeheader()
            writer.writerows(batch_results)

        passed = sum(1 for r in batch_results if r['verdict'] == 'PASS')
        print("=" * 50)
        print(f"BATCH COMPLETE: {passed}/{len(batch_results)} units passed")
        print(f"Batch log: {csv_path.name}")
        print("=" * 50)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        osc.relinquish_ownership()
        print("Connection released.")
