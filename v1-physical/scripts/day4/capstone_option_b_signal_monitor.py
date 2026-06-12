"""
Capstone Option B: Automated Signal Quality Monitor
====================================================
Day 4 | ~2 hours | 5-Day SDI Lab Automation FDP (v2.0)

Real application: a research lab needs unattended monitoring of a
signal source, with alerts when quality degrades. Impossible manually.

What this does (runs unattended):
  1. Datalogger streams Input 1 continuously
  2. Each chunk: mean, std dev, Vpp, outlier count
  3. Alert when a metric crosses its threshold (console + alert log)
  4. At the end: full CSV of samples + monitoring report with
     alert history and overall statistics

Setup: Output 1 -> Input 1 (BNC loopback). The Datalogger's built-in
       waveform generator provides the test signal. For a real source,
       remove the generate_waveform call and connect the source to Input 1.

API NOTES (hardware-verified):
  - start_streaming(duration=..., sample_rate=...)
  - 'End of stream' exception is NORMAL completion — catch and exit

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
from moku.instruments import Datalogger

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT, FRONTEND

# ============================================================
# CONFIGURATION
# ============================================================
MONITOR_DURATION = 600      # Seconds (10 minutes minimum requirement)
SAMPLE_RATE = 1e3           # 1 kSa/s
SIGNAL_FREQ = 100           # Hz test signal (loopback demo)

# Alert thresholds — tune to your signal
VPP_MIN = 0.5               # V  — alert if chunk Vpp drops below this
VPP_MAX = 2.5               # V  — alert if chunk Vpp exceeds this
MEAN_DRIFT_MAX = 0.2        # V  — alert if |chunk mean| exceeds this
OUTLIER_SIGMA = 4.0         # samples beyond +/-4 sigma count as outliers
OUTLIER_MAX = 10            # alert if outliers per chunk exceed this

OUT_DIR = Path(__file__).parent

# ============================================================
# CHUNK ANALYSIS
# ============================================================
def check_chunk(ch1):
    """Compute metrics for one chunk and return (metrics, alert_list)."""
    arr = np.array(ch1)            # get_data/stream chunks are Python lists
    mean = float(np.mean(arr))
    std = float(np.std(arr))
    vpp = float(arr.max() - arr.min())
    outliers = int(np.sum(np.abs(arr - mean) > OUTLIER_SIGMA * std)) if std > 0 else 0

    alerts = []
    if vpp < VPP_MIN:
        alerts.append(f"LOW Vpp {vpp:.3f}V < {VPP_MIN}V")
    if vpp > VPP_MAX:
        alerts.append(f"HIGH Vpp {vpp:.3f}V > {VPP_MAX}V")
    if abs(mean) > MEAN_DRIFT_MAX:
        alerts.append(f"DC DRIFT mean {mean:+.3f}V beyond +/-{MEAN_DRIFT_MAX}V")
    if outliers > OUTLIER_MAX:
        alerts.append(f"OUTLIERS {outliers} > {OUTLIER_MAX}")

    return {'mean': mean, 'std': std, 'vpp': vpp, 'outliers': outliers}, alerts


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print(f"Capstone B — Signal Quality Monitor")
    print(f"Duration: {MONITOR_DURATION}s at {SAMPLE_RATE:.0f} Sa/s")
    print(f"Thresholds: Vpp [{VPP_MIN}, {VPP_MAX}]V, "
          f"|mean| < {MEAN_DRIFT_MAX}V, outliers < {OUTLIER_MAX}/chunk\n")

    dl = Datalogger(MOKU_IP, force_connect=FORCE_CONNECT)
    all_samples = []
    alert_log = []          # (timestamp, chunk_number, message)
    chunk_count = 0
    start_time = time.time()

    try:
        dl.set_frontend(channel=1, **FRONTEND)
        dl.generate_waveform(1, 'Sine', frequency=SIGNAL_FREQ)  # demo signal
        dl.enable_input(2, enable=False)

        dl.start_streaming(duration=MONITOR_DURATION,
                           sample_rate=SAMPLE_RATE)

        print(f"{'Chunk':>6} | {'Mean (V)':>9} | {'Std (V)':>8} | "
              f"{'Vpp (V)':>8} | {'Outl':>4} | Status")
        print("-" * 62)

        while True:
            try:
                data = dl.get_stream_data()
                if not data:
                    continue
                ch1 = data['ch1']
                all_samples.extend(ch1)
                chunk_count += 1

                metrics, alerts = check_chunk(ch1)
                status = 'OK' if not alerts else 'ALERT: ' + '; '.join(alerts)
                print(f"{chunk_count:>6} | {metrics['mean']:>9.4f} | "
                      f"{metrics['std']:>8.4f} | {metrics['vpp']:>8.4f} | "
                      f"{metrics['outliers']:>4} | {status}")

                for msg in alerts:
                    alert_log.append((datetime.now(), chunk_count, msg))

            except Exception as e:
                if 'End of stream' in str(e):
                    print("\nMonitoring window complete.")
                    break
                raise

        elapsed = time.time() - start_time

        # --- Save samples ---
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = OUT_DIR / f'capstone_b_samples_{ts}.csv'
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sample_index', 'voltage_V'])
            for i, v in enumerate(all_samples):
                writer.writerow([i, v])

        # --- Monitoring report ---
        arr = np.array(all_samples)
        report_path = OUT_DIR / f'capstone_b_report_{ts}.txt'
        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("SIGNAL QUALITY MONITORING REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated:       {datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write(f"Duration:        {elapsed:.1f} s "
                    f"({chunk_count} chunks)\n")
            f.write(f"Samples:         {len(all_samples):,} "
                    f"at {SAMPLE_RATE:.0f} Sa/s\n")
            f.write("-" * 60 + "\n")
            f.write(f"Overall mean:    {np.mean(arr):.6f} V\n")
            f.write(f"Overall std:     {np.std(arr):.6f} V\n")
            f.write(f"Overall Vpp:     {arr.max()-arr.min():.4f} V\n")
            f.write(f"Min / Max:       {arr.min():.4f} V / {arr.max():.4f} V\n")
            f.write("-" * 60 + "\n")
            f.write(f"Alerts raised:   {len(alert_log)}\n")
            for when, chunk, msg in alert_log:
                f.write(f"  [{when:%H:%M:%S}] chunk {chunk}: {msg}\n")
            if not alert_log:
                f.write("  (none — signal stayed within thresholds)\n")
            f.write("=" * 60 + "\n")
            f.write("Spruha Build-in Solutions | "
                    "Powered by Moku:Go — Liquid Instruments\n")

        print(f"\nSaved: {csv_path.name} ({len(all_samples):,} rows)")
        print(f"Saved: {report_path.name} ({len(alert_log)} alerts)")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        dl.relinquish_ownership()
        print("Connection released.")
