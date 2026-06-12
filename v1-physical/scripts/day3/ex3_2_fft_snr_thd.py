"""
Exercise 3.2: FFT, SNR & THD Analysis
=======================================
Day 3 | 45 minutes | 5-Day SDI Lab Automation FDP (v2.0)

Objective: Capture oscilloscope data, compute FFT to find
           dominant frequency, then calculate SNR and THD.

Setup: Connect Output 1 -> Input 1 (BNC loopback).

API NOTE: get_data() returns Python lists — convert with np.array()
before any numpy math (FFT, mean, etc.).

Verified against: Liquid Instruments Python API v4.x

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from moku.instruments import Oscilloscope

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT

# ============================================================
# CONFIGURATION
# ============================================================
SIGNAL_FREQ = 1e3           # 1 kHz test signal
AMPLITUDE = 0.5             # Vpp
NUM_HARMONICS = 5           # Harmonics to include in THD
OUT_DIR = Path(__file__).parent

# ============================================================
# MAIN SCRIPT
# ============================================================
osc = Oscilloscope(MOKU_IP, force_connect=FORCE_CONNECT)

try:
    # --- Generate & Configure ---
    osc.generate_waveform(1, 'Sine', amplitude=AMPLITUDE,
                          frequency=SIGNAL_FREQ)
    osc.set_timebase(-5e-3, 5e-3)
    osc.set_trigger(type='Edge', source='Input1', level=0)

    # --- Capture Data ---
    # Explicit np.array() conversion: get_data() returns Python lists
    data = osc.get_data()
    ch1 = np.array(data['ch1'])
    time_axis = np.array(data['time'])
    N = len(ch1)
    dt = time_axis[1] - time_axis[0]
    fs = 1.0 / dt  # Sample rate

    print(f"Captured: {N} samples at {fs/1e3:.1f} kSa/s")

    # --- Compute FFT ---
    window = np.hanning(N)
    fft_vals = np.fft.rfft(ch1 * window)
    fft_mag = 2.0 / N * np.abs(fft_vals)
    freqs = np.fft.rfftfreq(N, dt)

    # --- Dominant Frequency ---
    peak_idx = np.argmax(fft_mag[1:]) + 1  # Skip DC
    f_dominant = freqs[peak_idx]
    peak_amp = fft_mag[peak_idx]

    print(f"\nDominant frequency: {f_dominant:.1f} Hz")
    print(f"Peak FFT amplitude: {peak_amp:.4f} V")

    # --- SNR Calculation ---
    signal_power = peak_amp ** 2
    noise_indices = [i for i in range(1, len(fft_mag))
                     if abs(i - peak_idx) > 2]
    noise_power = np.mean([fft_mag[i] ** 2 for i in noise_indices])
    snr_db = 10 * np.log10(signal_power / max(noise_power, 1e-20))

    print(f"\nSNR: {snr_db:.1f} dB")
    print(f"  Signal power: {signal_power:.6e}")
    print(f"  Noise power:  {noise_power:.6e}")

    # --- THD Calculation ---
    harmonics = []
    for h in range(2, NUM_HARMONICS + 1):
        h_idx = int(peak_idx * h)
        if h_idx < len(fft_mag):
            h_amp = fft_mag[h_idx]
            harmonics.append(h_amp)
            print(f"  Harmonic {h}: {freqs[h_idx]:.0f} Hz, "
                  f"amplitude = {h_amp:.6f} V")

    thd = np.sqrt(sum(h ** 2 for h in harmonics)) / peak_amp
    thd_pct = thd * 100

    print(f"\nTHD: {thd_pct:.2f}%")

    # --- Quality Assessment ---
    print(f"\n{'='*50}")
    print(f"SIGNAL QUALITY REPORT")
    print(f"{'='*50}")
    print(f"  Frequency:    {f_dominant:.1f} Hz "
          f"(expected: {SIGNAL_FREQ:.0f} Hz, "
          f"error: {abs(f_dominant-SIGNAL_FREQ)/SIGNAL_FREQ*100:.2f}%)")
    print(f"  SNR:          {snr_db:.1f} dB "
          f"({'GOOD' if snr_db > 40 else 'FAIR' if snr_db > 20 else 'POOR'})")
    print(f"  THD:          {thd_pct:.2f}% "
          f"({'GOOD' if thd_pct < 1 else 'FAIR' if thd_pct < 5 else 'POOR'})")

    # --- Generate Plot ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Time domain
    axes[0, 0].plot(time_axis * 1e3, ch1, color='#0057B8', linewidth=0.8)
    axes[0, 0].set_xlabel('Time (ms)')
    axes[0, 0].set_ylabel('Voltage (V)')
    axes[0, 0].set_title('Time Domain')
    axes[0, 0].grid(True, alpha=0.3)

    # FFT spectrum
    axes[0, 1].semilogy(freqs / 1e3, fft_mag, color='#0D9488', linewidth=0.8)
    axes[0, 1].set_xlabel('Frequency (kHz)')
    axes[0, 1].set_ylabel('Magnitude (V)')
    axes[0, 1].set_title('FFT Spectrum')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].axvline(x=f_dominant / 1e3, color='#FF6B35', linestyle='--',
                       alpha=0.7, label=f'f0={f_dominant:.0f} Hz')
    axes[0, 1].legend()

    # FFT zoomed (harmonic content)
    max_harm_freq = f_dominant * (NUM_HARMONICS + 1)
    mask = freqs <= max_harm_freq
    axes[1, 0].stem(freqs[mask] / 1e3, fft_mag[mask], linefmt='-',
                    markerfmt='o', basefmt='gray')
    axes[1, 0].set_xlabel('Frequency (kHz)')
    axes[1, 0].set_ylabel('Magnitude (V)')
    axes[1, 0].set_title('Harmonic Content')
    axes[1, 0].grid(True, alpha=0.3)

    # Quality metrics summary
    axes[1, 1].axis('off')
    summary_text = (
        f"Signal Quality Report\n"
        f"{'-' * 30}\n"
        f"Frequency:  {f_dominant:.1f} Hz\n"
        f"Amplitude:  {max(ch1)-min(ch1):.4f} Vpp\n"
        f"SNR:        {snr_db:.1f} dB\n"
        f"THD:        {thd_pct:.2f}%\n"
        f"{'-' * 30}\n"
        f"Samples:    {N}\n"
        f"Sample Rate:{fs/1e3:.1f} kSa/s\n"
    )
    axes[1, 1].text(0.1, 0.9, summary_text, transform=axes[1, 1].transAxes,
                    fontsize=13, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.suptitle('FFT, SNR & THD Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fft_snr_thd_analysis.png', dpi=150)
    print(f"\nPlot saved: fft_snr_thd_analysis.png")

except Exception as e:
    print(f"Error: {e}")

finally:
    osc.relinquish_ownership()
    print("Connection released.")
