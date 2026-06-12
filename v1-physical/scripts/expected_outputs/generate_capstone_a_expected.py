"""
Expected Output Generator: Day 4 Capstone — Option A (Freq Response)
=====================================================================
Generates reference Bode plot for capstone project.

Run: python generate_capstone_a_expected.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(200)

# Simulate component characterization (RC low-pass filter response)
freqs = np.logspace(1, 5, 30)  # 10 Hz to 100 kHz
# RC filter: H(f) = 1 / sqrt(1 + (f/fc)^2), fc = 10 kHz
fc = 10e3
amplitude = 1.0
vpp = amplitude / np.sqrt(1 + (freqs / fc) ** 2)
vpp += np.random.normal(0, 0.005, len(freqs))  # measurement noise
vpp = np.clip(vpp, 0.01, 2.0)
gain_db = 20 * np.log10(vpp / amplitude)

# Find -3dB point
cutoff = None
ref_vpp = vpp[0]
for f, v in zip(freqs, vpp):
    if v < ref_vpp * 0.707:
        cutoff = f
        break

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Amplitude
ax1.semilogx(freqs, vpp, 'b-o', markersize=5, linewidth=1.5)
ax1.set_ylabel('Amplitude (Vpp)', fontsize=11)
ax1.set_title('Capstone A: Component Frequency Response',
              fontsize=14, fontweight='bold', color='#1A365D')
ax1.grid(True, which='both', alpha=0.3)
ax1.axhline(y=ref_vpp * 0.707, color='red', linestyle='--',
            alpha=0.6, label=f'-3dB level ({ref_vpp*0.707:.3f}V)')
if cutoff:
    ax1.axvline(x=cutoff, color='red', linestyle=':', alpha=0.5,
                label=f'fc ≈ {cutoff:.0f} Hz')
ax1.legend(fontsize=10)

# Gain
ax2.semilogx(freqs, gain_db, 'g-o', markersize=5, linewidth=1.5)
ax2.set_xlabel('Frequency (Hz)', fontsize=11)
ax2.set_ylabel('Gain (dB)', fontsize=11)
ax2.set_title('Gain Response', fontsize=12)
ax2.grid(True, which='both', alpha=0.3)
ax2.axhline(y=-3, color='red', linestyle='--', alpha=0.6, label='-3dB')
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig('capstone_a_expected.png', dpi=150, bbox_inches='tight')
print("✓ Saved: capstone_a_expected.png")

print("\n--- Expected Console Output ---")
print(f"[1/30] 10 Hz: {vpp[0]:.4f}V ({gain_db[0]:.1f}dB)")
print(f"  ...")
print(f"[30/30] {freqs[-1]:.0f} Hz: {vpp[-1]:.4f}V ({gain_db[-1]:.1f}dB)")
print(f"\nAnalysis:")
print(f"  Reference Vpp: {ref_vpp:.4f}V")
if cutoff:
    print(f"  -3dB cutoff: ~{cutoff:.0f} Hz")
print(f"  Points measured: {len(freqs)}")
