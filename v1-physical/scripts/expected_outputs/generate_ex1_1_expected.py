"""
Expected Output Generator: Exercise 1.1 — Oscilloscope Data Logging
=====================================================================
Generates reference plot using simulated data (no hardware needed).
Trainers use this to show participants what their output SHOULD look like.

Run: python generate_ex1_1_expected.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Simulated 10-frame Vpp data (near 0.5 Vpp with slight noise)
np.random.seed(42)
NUM_FRAMES = 10
FREQUENCY = 1e3
AMPLITUDE = 0.25  # ±0.25V = 0.5 Vpp

frames = range(1, NUM_FRAMES + 1)
vpps = 0.50 + np.random.normal(0, 0.005, NUM_FRAMES)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# --- Bar chart: Vpp per frame ---
ax1.bar(frames, vpps, color='#2B6CB0', alpha=0.8, edgecolor='#1A365D', linewidth=0.5)
ax1.axhline(y=np.mean(vpps), color='red', linestyle='--',
            linewidth=1.5, label=f'Mean: {np.mean(vpps):.4f}V')
ax1.set_xlabel('Frame Number', fontsize=11)
ax1.set_ylabel('Vpp (V)', fontsize=11)
ax1.set_title('Peak-to-Peak Voltage per Frame', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0.48, 0.52)
ax1.set_xticks(range(1, 11))

# --- Last frame waveform ---
t = np.linspace(-5e-3, 5e-3, 1024)
v = AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t) + np.random.normal(0, 0.002, len(t))
ax2.plot(t * 1e3, v, color='#0D9488', linewidth=0.8)
ax2.set_xlabel('Time (ms)', fontsize=11)
ax2.set_ylabel('Voltage (V)', fontsize=11)
ax2.set_title(f'Last Frame (Frame {NUM_FRAMES})', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.suptitle('Expected Output: Exercise 1.1 — Oscilloscope Data Logging',
             fontsize=13, fontweight='bold', color='#1A365D')
plt.tight_layout()
plt.savefig('ex1_1_expected.png', dpi=150, bbox_inches='tight')
print("✓ Saved: ex1_1_expected.png")

# --- Print expected console output ---
print("\n--- Expected Console Output ---")
print(f"Capturing {NUM_FRAMES} frames...")
print(f"{'Frame':>6} | {'Vpp (V)':>10} | {'Vmin (V)':>10} | {'Vmax (V)':>10}")
print("-" * 50)
for i, vpp in enumerate(vpps):
    vmin = -(vpp / 2)
    vmax = vpp / 2
    print(f"{i+1:>6} | {vpp:>10.4f} | {vmin:>10.4f} | {vmax:>10.4f}")
print(f"\n{'='*50}")
print(f"SUMMARY ({NUM_FRAMES} frames)")
print(f"{'='*50}")
print(f"  Mean Vpp:  {np.mean(vpps):.4f} V")
print(f"  Std Dev:   {np.std(vpps):.4f} V")
print(f"  Min Vpp:   {min(vpps):.4f} V")
print(f"  Max Vpp:   {max(vpps):.4f} V")
