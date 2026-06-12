"""V2 acceptance test: every V1 script must run hardware-free.

Runs each Day 1-4 exercise/capstone (and the Day 5 MCC host) through
the simulator in a subprocess, checks exit codes, success markers in
stdout, and expected artifacts on disk. Also verifies that the
simulator ENFORCES the hardware-verified teaching rules by asserting
that known-wrong API calls raise instructive errors.

Usage:  python run_all_v1.py
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SIM = Path(__file__).resolve().parent
SCRIPTS = (SIM / '../../v1-physical/scripts').resolve()

# script, env extras, stdin, success marker in stdout, artifacts produced
CASES = [
    ('day1/ex1_1_oscilloscope_logging.py', {}, '',
     'Connection released', ['day1/oscilloscope_summary.png',
                             'day1/frame_10.csv']),
    ('day1/ex1_2_waveform_generator_sweep.py', {}, '',
     'EFFICIENCY REPORT', ['day1/wg_sweep_log.csv']),
    ('day2/ex2_1_awg_custom_waveforms.py', {}, '',
     'waveforms output successfully', ['day2/waveform_library.png',
                                       'day2/waveform_library.json']),
    ('day2/ex2_2_logic_analyzer_spi.py', {}, '',
     'Plot saved: spi_signals.png', ['day2/spi_signals.png']),
    ('day2/ex2_3_mim_frequency_sweep.py', {'MOKUSIM_DUT': 'rc:2500'}, '',
     '-3dB cutoff frequency', ['day2/mim_sweep_bode.png',
                               'day2/mim_sweep_data.csv']),
    ('day3/ex3_1_datalogger_streaming.py', {}, '',
     'Stream complete!', ['day3/stream_data.csv']),
    ('day3/ex3_2_fft_snr_thd.py', {}, '',
     'SIGNAL QUALITY REPORT', ['day3/fft_snr_thd_analysis.png']),
    ('day4/capstone_option_a_component_characterizer.py',
     {'MOKUSIM_DUT': 'rc:2500'}, '', 'Done in', []),
    ('day4/capstone_option_b_signal_monitor.py', {}, '',
     'Monitoring window complete', []),
    ('day4/capstone_option_c_production_tester.py', {}, '\n\n\n',
     'BATCH COMPLETE: 3/3 units passed', []),
]


def run_case(rel, env_extra, stdin, marker, artifacts):
    script = SCRIPTS / rel
    env = dict(os.environ, MPLBACKEND='Agg',
               PYTHONPATH=str(SIM), PYTHONIOENCODING='utf-8',
               **env_extra)
    r = subprocess.run([sys.executable, str(script)], env=env,
                       input=stdin, capture_output=True, text=True,
                       timeout=300)
    problems = []
    if r.returncode != 0:
        problems.append(f'exit {r.returncode}: {r.stderr.strip()[-400:]}')
    if marker and marker not in r.stdout:
        problems.append(f'missing marker {marker!r}')
    if '[mokusim]' not in r.stdout:
        problems.append('simulator banner missing — ran on REAL moku?!')
    for art in artifacts:
        if not (SCRIPTS / art).exists():
            problems.append(f'artifact missing: {art}')
    return problems, r.stdout


def teaching_rules():
    """Known-wrong calls must raise instructive errors."""
    sys.path.insert(0, str(SIM))
    import importlib
    import moku.instruments as mi
    importlib.reload(mi)
    import numpy as np
    checks = []

    def expect(label, fn, needle):
        try:
            fn()
            checks.append((label, 'FAIL — no error raised'))
        except Exception as e:
            ok = needle.lower() in str(e).lower()
            checks.append((label, 'ok' if ok
                           else f'FAIL — wrong message: {e}'))

    m = mi.MultiInstrument('10.0.0.1', platform_id=2, force_connect=True)
    expect('plain-dict set_connections rejected',
           lambda: m.set_connections(connections={'Slot1OutA': 'Slot2InA'}),
           'list of dicts')
    osc = m.set_instrument(2, mi.Oscilloscope)
    expect("MiM trigger source='Input1' rejected",
           lambda: osc.set_trigger(type='Edge', source='Input1', level=0),
           'not a valid trigger source')
    expect('slot-instrument release rejected',
           lambda: osc.relinquish_ownership(),
           'm.relinquish_ownership')
    la = mi.LogicAnalyzer('10.0.0.1', force_connect=True)
    expect("pin mode 'Pattern' rejected",
           lambda: la.set_pin_mode(1, 'Pattern'),
           "'PG1'")
    expect('old per-pin pattern call rejected',
           lambda: la.set_pattern_generator(pin=1, pattern=[1, 0]),
           'patterns=')
    awg = mi.ArbitraryWaveformGenerator('10.0.0.1', force_connect=True)
    expect('numpy lut_data rejected',
           lambda: awg.generate_waveform(channel=1, sample_rate='Auto',
                                         lut_data=np.zeros(8),
                                         frequency=1e3, amplitude=1.0),
           'list')
    wg = mi.WaveformGenerator('10.0.0.1', force_connect=True)
    expect('Square without duty rejected',
           lambda: wg.generate_waveform(channel=1, type='Square',
                                        amplitude=1.0, frequency=1e3),
           'duty')
    return checks


def main():
    print('=' * 64)
    print('V2 ACCEPTANCE: all V1 scripts on the mokusim simulator')
    print('=' * 64)
    failures = 0
    for rel, env_extra, stdin, marker, artifacts in CASES:
        problems, _ = run_case(rel, env_extra, stdin, marker, artifacts)
        status = 'PASS' if not problems else 'FAIL'
        if problems:
            failures += 1
        extra = ('  [' + '; '.join(problems) + ']') if problems else ''
        print(f'{status}  {rel}{extra}')

    print('-' * 64)
    print('Teaching-rule enforcement:')
    for label, result in teaching_rules():
        print(f'  {result:4s} {label}' if result == 'ok'
              else f'  {result}  <- {label}')
        if result != 'ok':
            failures += 1
    print('-' * 64)
    print('RESULT:', 'ALL PASS' if failures == 0 else f'{failures} FAILURES')
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
