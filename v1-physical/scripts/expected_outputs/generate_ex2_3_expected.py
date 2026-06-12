"""
Expected Output Generator: Exercise 2.3 — MiM Frequency Sweep (Bode)
======================================================================
Generates reference Bode plot using simulated loopback data.

Run: python generate_ex2_3_expected.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NUM_POINTS = 25
F_START = 10
F_STOP = 100e3
AMPLITUDE = 1.0

np.random.seed(123)
freqs = np.logspace(np.log10(F_START), np.log10(F_STOP), NUM_POINTS)

# Simulate flat response (loopback) with slight noise and HF rolloff
vpp = AMPLITUDE * np.ones(NUM_POINTS) + np.random.normal(0, 0.008, NUM_POINTS)
# Add mild rolloff above 50 kHz (typical of Moku:Go analog path)
for i, f in enumerate(freqs):
    if f > 50e3:
        vpp[i] *= (50e3 / f) ** 0.3

gain_db = 20 * np.log10(vpp / AMPLITUDE)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Amplitude response
ax1.semilogx(freqs, vpp, 'b-o', markersize=5, linewidth=1.5)
ax1.set_ylabel('Amplitude (Vpp)', fontsize=11)
ax1.set_title('MiM Frequency Sweep — Amplitude Response',
              fontsize=14, fontweight='bold', color='#1A365D')
ax1.grid(True, which='both', alpha=0.3)
ax1.axhline(y=AMPLITUDE * 0.707, color='red', linestyle='--',
            alpha=0.6, label='-3dB level (0.707V)')
ax1.legend(fontsize=10)

# Gain response
ax2.semilogx(freqs, gain_db, 'g-o', markersize=5, linewidth=1.5)
ax2.set_xlabel('Frequency (Hz)', fontsize=11)
ax2.set_ylabel('Gain (dB)', fontsize=11)
ax2.set_title('Gain Response', fontsize=12)
ax2.grid(True, which='both', alpha=0.3)
ax2.axhline(y=-3, color='red', linestyle='--', alpha=0.6, label='-3dB')
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig('ex2_3_expected.png', dpi=150, bbox_inches='tight')
print("✓ Saved: ex2_3_expected.png")

# Console output
print("\n--- Expected Console Output ---")
print(f"MiM Frequency Sweep: {F_START} Hz to {F_STOP/1e3:.0f} kHz "
      f"({NUM_POINTS} points)")
print(f"\n{'#':>3} | {'Freq (Hz)':>12} | {'Vpp (V)':>10} | {'Gain (dB)':>10}")
print("-" * 50)
for i, (f, v, g) in enumerate(zip(freqs, vpp, gain_db)):
    print(f"{i+1:>3} | {f:>12.1f} | {v:>10.4f} | {g:>10.2f}")

print(f"\nResults saved: mim_sweep_data.csv")
print(f"Bode plot saved: mim_sweep_bode.png")
print(f"No -3dB cutoff found in measurement range (flat response).")
