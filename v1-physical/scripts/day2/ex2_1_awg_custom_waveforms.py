"""
Exercise 2.1: Arbitrary Waveform Generator — Custom Waveforms
==============================================================
Day 2 | 30 minutes | 5-Day SDI Lab Automation FDP (v2.0)

Objective: Create a library of custom waveforms and output them
           sequentially using the AWG.

Setup: Connect Output 1 -> Input 1 for observation,
       or use external oscilloscope to view outputs.

API NOTE (hardware-verified): the AWG call takes sample_rate='Auto'
and lut_data=<Python list normalized to [-1, 1]>. Pass a plain list,
NOT a numpy array.

Verified against: Liquid Instruments Python API v4.x
Reference: https://apis.liquidinstruments.com/api/reference/awg/

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import json
import time
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from moku.instruments import ArbitraryWaveformGenerator

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT

# ============================================================
# CONFIGURATION
# ============================================================
FREQUENCY = 1e3             # 1 kHz output
AMPLITUDE = 1.0             # 1 Vpp
DISPLAY_TIME = 2            # Seconds to hold each waveform
NUM_POINTS = 256            # LUT resolution
OUT_DIR = Path(__file__).parent

# ============================================================
# WAVEFORM LIBRARY — defined mathematically with numpy
# ============================================================
t = np.linspace(0, 1, NUM_POINTS, endpoint=False)

waveforms = {
    'sine': np.sin(2 * np.pi * t),
    'sawtooth': 2 * t - 1,
    'triangle': 2 * np.abs(2 * t - 1) - 1,
    'staircase': np.floor(t * 8) / 4 - 1,
    'half_rect_sine': np.maximum(np.sin(2 * np.pi * t), 0) * 2 - 1,
}

# Normalize all waveforms to [-1, 1] (required LUT range)
for name in waveforms:
    data = waveforms[name]
    max_val = max(abs(data))
    if max_val > 0:
        waveforms[name] = data / max_val

# ============================================================
# PREVIEW PLOT (save before sending to hardware)
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()

for i, (name, data) in enumerate(waveforms.items()):
    axes[i].plot(t, data, color='#0057B8', linewidth=1.5)
    axes[i].set_title(name.replace('_', ' ').title(), fontsize=12)
    axes[i].set_ylim(-1.2, 1.2)
    axes[i].grid(True, alpha=0.3)
    axes[i].set_xlabel('Normalized Time')
    axes[i].set_ylabel('Amplitude')

# Hide unused subplot
if len(waveforms) < len(axes):
    axes[-1].set_visible(False)

plt.suptitle('Custom Waveform Library', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUT_DIR / 'waveform_library.png', dpi=150)
print("Preview saved: waveform_library.png")

# ============================================================
# SAVE LIBRARY TO JSON
# ============================================================
library = {name: list(data) for name, data in waveforms.items()}
with open(OUT_DIR / 'waveform_library.json', 'w') as f:
    json.dump(library, f, indent=2)
print("Library saved: waveform_library.json")

# ============================================================
# OUTPUT TO HARDWARE
# ============================================================
awg = ArbitraryWaveformGenerator(MOKU_IP, force_connect=FORCE_CONNECT)

try:
    for name, data in waveforms.items():
        awg.generate_waveform(
            channel=1,
            sample_rate='Auto',
            lut_data=list(data),    # must be a Python list, not numpy array
            frequency=FREQUENCY,
            amplitude=AMPLITUDE
        )
        print(f"Generating: {name:20s} @ {FREQUENCY/1e3:.0f} kHz, "
              f"{AMPLITUDE} Vpp")
        time.sleep(DISPLAY_TIME)

    print(f"\nAll {len(waveforms)} waveforms output successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    awg.relinquish_ownership()
    print("Connection released.")
