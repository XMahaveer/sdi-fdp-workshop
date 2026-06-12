"""
Shared configuration — 5-Day SDI Lab Automation FDP (v2.0)
===========================================================
Every workshop script imports its Moku:Go connection settings from
this file. Change MOKU_IP once here instead of editing each script.

Trainer: Mahaveer. Rajendra. Savanur
Head of Engineering & AI Systems
Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

# ============================================================
# CONNECTION
# ============================================================
# IP address of your Moku:Go. Find it with `mokucli list` or on the
# device screen, then update this single line.
MOKU_IP = '192.168.0.101'

# Always use force_connect=True in the workshop context — it avoids
# "device busy" errors when a previous session did not release the device.
FORCE_CONNECT = True

# Moku:Go Multi-Instrument Mode has 2 slots (Moku:Pro/Lab would be 4).
PLATFORM_ID = 2

# ============================================================
# SHARED TEST DEFAULTS
# ============================================================
SETTLE_TIME = 0.3        # Seconds to wait after changing a waveform
                         # before capturing (50 ms minimum; 0.3 s is safe)
DEFAULT_AMPLITUDE = 1.0  # Vpp used by most exercises
DEFAULT_FREQUENCY = 1e3  # Hz used by most exercises

# Frontend defaults for analog inputs
FRONTEND = dict(impedance='1MOhm', coupling='DC', range='10Vpp')
