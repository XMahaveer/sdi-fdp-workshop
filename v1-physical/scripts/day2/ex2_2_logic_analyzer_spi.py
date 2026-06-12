"""
Exercise 2.2: Logic Analyzer — Digital Pattern Generation (HARDWARE VERIFIED)
=============================================================================
Day 2 | 30 minutes | 5-Day SDI Lab Automation FDP (v2.0)

Objective: Generate SPI-like digital patterns on 4 pins and capture
           them back with the Logic Analyzer.

API FIXES APPLIED (March 2026 — hardware-verified on Moku:Go):
  - set_pattern_generator: channel=1 (PG channel), NOT pin number
  - All pins go in ONE patterns list (list of dicts)
  - set_pin_mode uses 'PG1' NOT 'Pattern'

Verified against: moku v4.1.2, MokuOS 4.1.2 (build 12726)

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
from moku.instruments import LogicAnalyzer

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT

# ============================================================
# CONFIGURATION
# ============================================================
DIVIDER = 5
OUT_DIR = Path(__file__).parent

# ============================================================
# DEFINE SPI-LIKE DIGITAL PATTERNS
# ============================================================
clock = [1, 0] * 50
data_pattern = [0, 0, 1, 1, 0, 1, 0, 1] * 12 + [0] * 4
cs = [0] * 8 + [1] * 84 + [0] * 8
mosi = [1, 0, 1, 1, 0, 0, 1, 0] * 12 + [0] * 4

pin_config = {
    1: ('CLK',  clock[:100]),
    2: ('DATA', data_pattern[:100]),
    3: ('CS',   cs[:100]),
    4: ('MOSI', mosi[:100]),
}

# ============================================================
# MAIN SCRIPT
# ============================================================
la = LogicAnalyzer(MOKU_IP, force_connect=FORCE_CONNECT)

try:
    # All pins are configured in ONE call to Pattern Generator channel 1.
    patterns_list = []
    for pin, (name, pattern) in pin_config.items():
        patterns_list.append({"pin": pin, "pattern": pattern})
        print(f"Pin {pin} ({name}): {len(pattern)} samples")

    la.set_pattern_generator(
        channel=1,
        patterns=patterns_list,
        divider=DIVIDER
    )
    print(f"Pattern Generator 1 configured with {len(patterns_list)} pins, divider={DIVIDER}")

    # Pin mode 'PG1' routes Pattern Generator 1 to each pin.
    for pin in pin_config:
        la.set_pin_mode(pin, 'PG1')

    time.sleep(1)

    data = la.get_data(include_pins=[1, 2, 3, 4])
    print("\nCaptured data from 4 pins.")

    colors = ['#0057B8', '#0D9488', '#FF6B35', '#553C9A']
    fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

    for i, (pin, (name, _)) in enumerate(pin_config.items()):
        pin_data = data[f'pin{pin}']
        axes[i].plot(pin_data, color=colors[i], linewidth=1.0)
        axes[i].fill_between(range(len(pin_data)), pin_data, alpha=0.2, color=colors[i])
        axes[i].set_ylabel(name, fontsize=12, fontweight='bold')
        axes[i].set_ylim(-0.2, 1.4)
        axes[i].set_yticks([0, 1])
        axes[i].grid(True, alpha=0.3)

    axes[-1].set_xlabel('Sample Number', fontsize=11)
    plt.suptitle('SPI Bus Signals — Logic Analyzer Capture', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'spi_signals.png', dpi=150)
    print("Plot saved: spi_signals.png")

except Exception as e:
    print(f"Error: {e}")

finally:
    la.relinquish_ownership()
    print("Connection released.")
