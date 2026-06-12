"""mokusim — a moku-API-compatible SIMULATOR (V2 Model A).

This package deliberately shadows the real `moku` package when the
simulator directory is first on sys.path (see ../simrun.py). Every V1
workshop script then runs unmodified, with zero hardware.

It is NOT the Liquid Instruments moku package. On real hardware,
remove the simulator from sys.path and the same scripts run unchanged.

Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

SIMULATED = True
__version__ = '4.1.2.1+sim0.1'

import sys as _sys

if not getattr(_sys, '_mokusim_banner_shown', False):
    print('[mokusim] MOKU SIMULATOR ACTIVE - no hardware required '
          '(v2-online Model A)')
    _sys._mokusim_banner_shown = True
