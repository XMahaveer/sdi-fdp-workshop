"""
MCC Threshold Detector — Python Host Script
============================================
Day 5 | MCC Session | 5-Day SDI Lab Automation FDP (v2.0)

Drives the threshold-detector custom instrument compiled from
mcc_threshold_detector_skeleton.v (see mcc_experiment_guide.md for the
cloud-compile steps that produce the bitstream).

What this does:
  1. MiM: Custom Instrument (Slot 1) + Waveform Generator (Slot 2)
  2. WG generates a 100 Hz sine test signal -> Output 1
  3. Physical BNC loopback: Output 1 -> Input 1 -> custom instrument
  4. Python sets the detection threshold via Control0
  5. Reads crossings-per-second from Status0 once a second
     (expected: ~100 for a 100 Hz sine crossing a mid-level threshold)

Setup: BNC cable from Output 1 to Input 1.

Trainer: Mahaveer. Rajendra. Savanur — Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import sys
import time
from pathlib import Path

# Class name verified against moku 4.1.2.1: CustomInstrument is the
# canonical class (moku.instruments). The old name CloudCompile was
# deprecated in moku 4.1.1 and now just subclasses CustomInstrument
# with a deprecation warning. (MokuCustomInstrument does not exist.)
from moku.instruments import MultiInstrument, WaveformGenerator
from moku.instruments import CustomInstrument

# Shared workshop settings live one level up in config.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MOKU_IP, FORCE_CONNECT, PLATFORM_ID

# ============================================================
# CONFIGURATION
# ============================================================
# Bitstream produced by the Liquid Instruments cloud build from your
# completed mcc_threshold_detector Verilog (see the experiment guide).
BITSTREAM = 'path/to/your_threshold_detector_bitstream.tar'  # <-- update

SIGNAL_FREQ = 100           # Hz test sine
SIGNAL_AMPLITUDE = 1.0      # Vpp
THRESHOLD = 16384           # 0x4000 = 0.5 x full scale (~0.5 V) in Q1.15
MONITOR_SECONDS = 10        # How long to read Status0

# ============================================================
# MAIN SCRIPT
# ============================================================
m = MultiInstrument(MOKU_IP, platform_id=PLATFORM_ID,
                    force_connect=FORCE_CONNECT)

try:
    # --- Deploy instruments ---
    ci = m.set_instrument(1, CustomInstrument, bitstream=BITSTREAM)
    wg = m.set_instrument(2, WaveformGenerator)

    # --- Routing ---
    # WG (Slot 2) -> physical Output 1 -> BNC loopback -> physical
    # Input 1 -> custom instrument's InputA (Slot 1 In A)
    m.set_connections(connections=[
        dict(source='Slot2OutA', destination='Output1'),
        dict(source='Input1', destination='Slot1InA'),
    ])

    # --- Test signal ---
    wg.generate_waveform(channel=1, type='Sine',
                         amplitude=SIGNAL_AMPLITUDE,
                         frequency=SIGNAL_FREQ)

    # --- Set detection threshold from Python ---
    # Q1.15 scale: 32767 = +1.0 V full scale, 16384 = +0.5 V
    # Register API verified against moku 4.1.2.1:
    # set_control(idx, value) writes ControlN; get_status() reads the
    # Status registers (index [0] = Status0).
    ci.set_control(0, THRESHOLD)
    print(f"Threshold set: {THRESHOLD} "
          f"({THRESHOLD/32767:.2f} x full scale)")
    print(f"Test signal: {SIGNAL_FREQ} Hz sine, {SIGNAL_AMPLITUDE} Vpp")
    print(f"Expected crossings/sec: ~{SIGNAL_FREQ} "
          f"(one rising crossing per cycle)\n")

    # --- Read crossings-per-second from the FPGA ---
    print(f"{'Second':>7} | {'Crossings/sec (Status0)':>24}")
    print("-" * 36)
    for second in range(1, MONITOR_SECONDS + 1):
        time.sleep(1)
        crossings = ci.get_status()[0]   # Status0
        flag = '' if abs(crossings - SIGNAL_FREQ) <= 2 else '  <-- check'
        print(f"{second:>7} | {crossings:>24}{flag}")

    print("\nTry it: change THRESHOLD above the signal peak (e.g. 30000)")
    print("and re-run — crossings should drop to 0.")

except Exception as e:
    print(f"Error: {e}")

finally:
    # CRITICAL: release via MultiInstrument, never via ci or wg
    m.relinquish_ownership()
    print("Connection released.")
