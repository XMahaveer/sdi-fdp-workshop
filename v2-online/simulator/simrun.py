"""Run any V1 workshop script against the mokusim simulator.

Usage:
    python simrun.py <path-to-script> [script args]

Example:
    cd v2-online/simulator
    python simrun.py ../../v1-physical/scripts/day1/ex1_1_oscilloscope_logging.py

The simulator directory is prepended to sys.path so `import moku`
resolves to the simulated package instead of the real one. The script
itself runs UNMODIFIED — the same file works on real hardware.

Optional environment:
    MOKUSIM_DUT=rc:2500   simulate an RC low-pass (fc=2.5 kHz) in the
                          Output 1 -> Input 1 loopback path, so sweep
                          exercises find a real cutoff.
"""

import os
import runpy
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(2)

# Headless plotting before any matplotlib import inside the target
os.environ.setdefault('MPLBACKEND', 'Agg')

SIM_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SIM_DIR))

target = Path(sys.argv[1]).resolve()
if not target.exists():
    print(f'simrun: script not found: {target}')
    sys.exit(2)

sys.argv = [str(target)] + sys.argv[2:]
runpy.run_path(str(target), run_name='__main__')
