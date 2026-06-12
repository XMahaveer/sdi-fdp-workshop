"""
Expected Output Generator: Exercise 2.1 — AWG Custom Waveforms
================================================================
Generates reference waveform library plot (no hardware needed).

Run: python generate_ex2_1_expected.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NUM_POINTS = 256
t = np.linspace(0, 1, NUM_POINTS, endpoint=False)

waveforms = {
    'Sine': np.sin(2 * np.pi * t),
    'Sawtooth': 2 * t - 1,
    'Triangle': 2 * np.abs(2 * t - 1) - 1,
    'Staircase': np.floor(t * 8) / 4 - 1,
    'Half-Rect Sine': np.maximum(np.sin(2 * np.pi * t), 0) * 2 - 1,
}

# Normalize all to [-1, 1]
for name in waveforms:
    data = waveforms[name]
    max_val = max(abs(data))
    if max_val > 0:
        waveforms[name] = data / max_val

colors = ['#2B6CB0', '#0D9488', '#DD6B20', '#553C9A', '#9B2C2C']

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()

for i, (name, data) in enumerate(waveforms.items()):
    axes[i].plot(t, data, color=colors[i], linewidth=1.5)
    axes[i].set_title(name, fontsize=12, fontweight='bold')
    axes[i].set_ylim(-1.3, 1.3)
    axes[i].grid(True, alpha=0.3)
    axes[i].set_xlabel('Normalized Time')
    axes[i].set_ylabel('Amplitude')

# Hide unused subplot
axes[-1].set_visible(False)

plt.suptitle('Expected Output: Exercise 2.1 — Custom Waveform Library',
             fontsize=13, fontweight='bold', color='#1A365D')
plt.tight_layout()
plt.savefig('ex2_1_expected.png', dpi=150, bbox_inches='tight')
print("✓ Saved: ex2_1_expected.png")

# Console output
print("\n--- Expected Console Output ---")
print("Preview saved: waveform_library.png")
print("Library saved: waveform_library.json")
for name in waveforms:
    print(f"Generating: {name:20s} @ 1 kHz, 1.0 Vpp")
print(f"\nAll {len(waveforms)} waveforms output successfully.")
