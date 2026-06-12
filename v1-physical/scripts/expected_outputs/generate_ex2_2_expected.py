"""
Expected Output Generator: Exercise 2.2 — Logic Analyzer SPI Signals
======================================================================
Generates reference 4-channel digital pattern plot (no hardware needed).

Run: python generate_ex2_2_expected.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Define SPI-like patterns (same as exercise script)
clock = np.array([1, 0] * 50)
data_pattern = np.array([0, 0, 1, 1, 0, 1, 0, 1] * 12 + [0] * 4)[:100]
cs = np.array([0] * 8 + [1] * 84 + [0] * 8)[:100]
mosi = np.array([1, 0, 1, 1, 0, 0, 1, 0] * 12 + [0] * 4)[:100]

patterns = {
    'CLK': (clock, '#2B6CB0'),
    'DATA': (data_pattern, '#0D9488'),
    'CS': (cs, '#DD6B20'),
    'MOSI': (mosi, '#553C9A'),
}

fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

for i, (name, (data, color)) in enumerate(patterns.items()):
    axes[i].step(range(len(data)), data, color=color,
                 linewidth=1.0, where='post')
    axes[i].fill_between(range(len(data)), data,
                         alpha=0.15, color=color, step='post')
    axes[i].set_ylabel(name, fontsize=12, fontweight='bold')
    axes[i].set_ylim(-0.2, 1.4)
    axes[i].set_yticks([0, 1])
    axes[i].grid(True, alpha=0.3)

axes[-1].set_xlabel('Sample Number', fontsize=11)
plt.suptitle('Expected Output: Exercise 2.2 — SPI Bus Signals',
             fontsize=13, fontweight='bold', color='#1A365D')
plt.tight_layout()
plt.savefig('ex2_2_expected.png', dpi=150, bbox_inches='tight')
print("✓ Saved: ex2_2_expected.png")

# Console output
print("\n--- Expected Console Output ---")
for pin, (name, _) in enumerate(patterns.items(), 1):
    data = [clock, data_pattern, cs, mosi][pin - 1]
    print(f"Pin {pin} ({name}): {len(data)} samples, divider=5")
print(f"\nCaptured data from 4 pins.")
print("Plot saved: spi_signals.png")
