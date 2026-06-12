"""Simulated moku.instruments — V2 Model A.

Drop-in stand-ins for the instrument classes used in the workshop:
Oscilloscope, WaveformGenerator, ArbitraryWaveformGenerator,
LogicAnalyzer, Datalogger, MultiInstrument, CustomInstrument
(+ CloudCompile deprecation shim, mirroring moku 4.1.1+).

Design rules:
- get_data()/get_stream_data() return dicts of PYTHON LISTS, exactly
  like real hardware.
- The hardware-verified teaching rules are ENFORCED with instructive
  errors: plain-dict set_connections, 'Pattern' pin mode, numpy
  lut_data, Input1 trigger inside MiM, per-type waveform params, and
  releasing slot instruments instead of the MultiInstrument.
- Physical model: the workshop's standard BNC loopback
  (Output 1 -> Input 1) is assumed present. Set the environment
  variable MOKUSIM_DUT="rc:<fc_hz>" to insert a simulated RC low-pass
  filter in that path (e.g. MOKUSIM_DUT=rc:2500), so sweep exercises
  find a real cutoff.
"""

import math
import os
import numpy as np


class MokuException(Exception):
    """Simulated counterpart of moku.exceptions.MokuException."""


NOISE_RMS = 0.0005        # ~0.5 mV measurement noise
HD3 = 0.003               # 3rd-harmonic distortion (THD ~0.3%) for realism
FRAME_POINTS = 1024


def _dut_gain(freq):
    """Loopback path gain at `freq` (RC low-pass if MOKUSIM_DUT is set)."""
    spec = os.environ.get('MOKUSIM_DUT', '').strip().lower()
    if spec.startswith('rc:'):
        try:
            fc = float(spec.split(':', 1)[1])
        except ValueError:
            return 1.0
        if fc > 0:
            return 1.0 / math.sqrt(1.0 + (freq / fc) ** 2)
    return 1.0


class _Signal:
    """State of one generated output channel."""

    def __init__(self, type, amplitude, frequency, duty=None,
                 symmetry=None, offset=0.0, lut=None):
        self.type = type
        self.amplitude = float(amplitude)      # Vpp
        self.frequency = float(frequency or 0)
        self.duty = duty
        self.symmetry = symmetry
        self.offset = float(offset)
        self.lut = lut                          # arbitrary waveform list
        self.modulation = None                  # (type, frequency, depth)

    def sample(self, t, gain=1.0):
        """Synthesize samples at times t (numpy array). Returns array."""
        A = self.amplitude / 2.0 * gain
        f = self.frequency
        if self.type == 'DC':
            y = np.full_like(t, A)
        elif self.type == 'Arbitrary' and self.lut is not None:
            frac = (t * f) % 1.0
            idx = (frac * len(self.lut)).astype(int) % len(self.lut)
            y = A * np.asarray(self.lut, dtype=float)[idx] * 2.0
        elif self.type == 'Square':
            duty = (self.duty if self.duty is not None else 50) / 100.0
            y = np.where((t * f) % 1.0 < duty, A, -A)
        elif self.type in ('Ramp',):
            sym = (self.symmetry if self.symmetry is not None else 50) / 100.0
            frac = (t * f) % 1.0
            rise = frac < sym if sym > 0 else np.zeros_like(frac, bool)
            y = np.where(rise,
                         -A + 2 * A * np.divide(frac, sym,
                                                out=np.zeros_like(frac),
                                                where=sym > 0),
                         A - 2 * A * np.divide(frac - sym, (1 - sym),
                                               out=np.zeros_like(frac),
                                               where=(1 - sym) > 0))
        elif self.type == 'Triangle':
            frac = (t * f) % 1.0
            y = A * (4 * np.abs(frac - 0.5) - 1)
        elif self.type == 'Pulse':
            duty = (self.duty if self.duty is not None else 50) / 100.0
            y = np.where((t * f) % 1.0 < duty, A, 0.0)
        else:  # Sine
            ph = 2 * np.pi * f * t
            y = A * np.sin(ph) + HD3 * A * np.sin(3 * ph)
        if self.modulation:
            mtype, mfreq, depth = self.modulation
            if mtype == 'Amplitude':
                y = y * (1 + (depth / 100.0)
                         * np.sin(2 * np.pi * mfreq * t))
        return y + self.offset


def _require(params, type_, required, name):
    missing = [k for k in required if params.get(k) is None]
    if missing:
        raise MokuException(
            f"generate_waveform(type='{type_}') requires "
            f"{', '.join(m + '=' for m in missing)} (API validates "
            f"parameters per waveform type)")


class _BaseInstrument:
    """Connection / ownership plumbing shared by all instruments."""

    def __init__(self, ip=None, force_connect=False, _mim=None, _slot=None,
                 **kwargs):
        self._ip = ip
        self._mim = _mim
        self._slot = _slot
        self._owned = True
        self._signals = {}          # channel -> _Signal
        self._frontends = {}

    # -- shared API ----------------------------------------------------
    def set_frontend(self, channel=1, impedance='1MOhm', coupling='DC',
                     range='10Vpp', **kw):
        self._frontends[channel] = dict(impedance=impedance,
                                        coupling=coupling, range=range)
        return self._frontends[channel]

    def generate_waveform(self, channel=1, type='Sine', amplitude=1.0,
                          frequency=1000, duty=None, symmetry=None,
                          offset=0.0, **kw):
        if type == 'Square':
            _require(dict(duty=duty), type, ['duty'], 'Square')
        if type == 'Ramp':
            _require(dict(symmetry=symmetry), type, ['symmetry'], 'Ramp')
        if type == 'Pulse':
            _require(dict(duty=duty), type, ['duty'], 'Pulse')
        sig = _Signal(type, amplitude, frequency, duty, symmetry, offset)
        self._signals[channel] = sig
        return dict(channel=channel, type=type, amplitude=amplitude,
                    frequency=frequency)

    def set_modulation(self, channel=1, type='Amplitude',
                       source='Internal', frequency=1e3, depth=50, **kw):
        sig = self._signals.get(channel)
        if sig is None:
            raise MokuException('set_modulation: no waveform on channel '
                                f'{channel} — call generate_waveform first')
        sig.modulation = (type, float(frequency), float(depth))
        return dict(channel=channel, type=type, frequency=frequency,
                    depth=depth)

    def summary(self):
        return (f'<simulated {self.__class__.__name__} @ {self._ip} '
                f'(mokusim)>')

    def relinquish_ownership(self):
        if self._mim is not None:
            raise MokuException(
                'In Multi-Instrument Mode, release via '
                'm.relinquish_ownership() on the MultiInstrument object — '
                'never on individual slot instruments (hardware-verified '
                'rule; on real hardware this crashes or locks the device).')
        self._owned = False

    # -- internal ------------------------------------------------------
    def _input_signal(self):
        """The signal arriving at Input/Slot-in A, honoring MiM routing
        or the standalone loopback assumption."""
        if self._mim is not None:
            return self._mim._signal_into_slot(self._slot)
        sig = self._signals.get(1)
        gain = _dut_gain(sig.frequency) if sig else 1.0
        return (sig, gain)


class Oscilloscope(_BaseInstrument):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._t1, self._t2 = -1e-3, 1e-3

    def set_timebase(self, t1, t2):
        if not t2 > t1:
            raise MokuException('set_timebase: t2 must be greater than t1')
        self._t1, self._t2 = float(t1), float(t2)

    def set_trigger(self, type='Edge', source='Input1', level=0, **kw):
        if self._mim is not None and str(source).startswith('Input'):
            raise MokuException(
                f"'{source}' is not a valid trigger source inside "
                'Multi-Instrument Mode — use auto-trigger (do not call '
                'set_trigger). Hardware-verified March 2026.')
        return dict(type=type, source=source, level=level)

    def set_source(self, channel, source):
        return dict(channel=channel, source=source)

    def get_data(self):
        t = np.linspace(self._t1, self._t2, FRAME_POINTS)
        sig, gain = self._input_signal()
        rng = np.random.default_rng()
        ch1 = rng.normal(0, NOISE_RMS, FRAME_POINTS)
        if sig is not None:
            ch1 = ch1 + sig.sample(t, gain)
        ch2 = rng.normal(0, NOISE_RMS, FRAME_POINTS)
        # exactly like hardware: plain Python lists
        return {'time': t.tolist(), 'ch1': ch1.tolist(),
                'ch2': ch2.tolist()}


class WaveformGenerator(_BaseInstrument):
    pass


class ArbitraryWaveformGenerator(_BaseInstrument):
    def generate_waveform(self, channel=1, sample_rate='Auto',
                          lut_data=None, frequency=1000, amplitude=1.0,
                          **kw):
        if lut_data is None:
            raise MokuException('AWG generate_waveform requires lut_data=')
        if isinstance(lut_data, np.ndarray):
            raise MokuException(
                'lut_data must be a plain Python list, not a numpy array '
                '— wrap it with list(...). (#1 AWG mistake, '
                'hardware-verified.)')
        if not isinstance(lut_data, list):
            raise MokuException('lut_data must be a Python list')
        peak = max(abs(v) for v in lut_data) if lut_data else 0
        if peak > 1.0 + 1e-9:
            raise MokuException(
                f'lut_data values must be normalized to [-1, 1] '
                f'(got peak {peak:.3f})')
        sig = _Signal('Arbitrary', amplitude, frequency, lut=list(lut_data))
        self._signals[channel] = sig
        return dict(channel=channel, sample_rate=sample_rate,
                    frequency=frequency, amplitude=amplitude)


class LogicAnalyzer(_BaseInstrument):
    _PIN_MODES = ('PG1', 'PG2', 'I', 'X')

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._patterns = {}     # pin -> list of 0/1
        self._pin_modes = {}

    def set_pattern_generator(self, channel=1, patterns=None, divider=1,
                              **kw):
        if 'pin' in kw or 'pattern' in kw:
            raise MokuException(
                'set_pattern_generator takes channel= (the PG channel, '
                'not a pin) and patterns=[{"pin": n, "pattern": [...]}] '
                '— the old per-pin call is not valid (hardware-verified '
                'March 2026, moku v4.1.2).')
        if not isinstance(patterns, list) or not all(
                isinstance(p, dict) and 'pin' in p and 'pattern' in p
                for p in (patterns or [])):
            raise MokuException(
                'patterns must be a LIST of dicts: '
                '[{"pin": n, "pattern": [0,1,...]}, ...]')
        if channel not in (1, 2):
            raise MokuException('channel must be 1 or 2 (PG1 / PG2)')
        for p in patterns:
            self._patterns[int(p['pin'])] = [int(v) for v in p['pattern']]
        return dict(channel=channel, pins=sorted(self._patterns),
                    divider=divider)

    def set_pin_mode(self, pin, mode):
        if mode == 'Pattern':
            raise MokuException(
                "'Pattern' is not a valid pin mode — use 'PG1' (or "
                "'PG2'/'I'/'X'). Hardware-verified fix, moku v4.1.2.")
        if mode not in self._PIN_MODES:
            raise MokuException(f"pin mode must be one of "
                                f"{self._PIN_MODES}, got '{mode}'")
        self._pin_modes[pin] = mode

    def get_data(self, include_pins=None, **kw):
        include_pins = include_pins or sorted(self._patterns)
        out = {}
        for pin in include_pins:
            pat = self._patterns.get(pin)
            if pat:
                reps = FRAME_POINTS // len(pat) + 1
                out[f'pin{pin}'] = (pat * reps)[:FRAME_POINTS]
            else:
                out[f'pin{pin}'] = [0] * FRAME_POINTS
        return out


class Datalogger(_BaseInstrument):
    _CHUNK = 1024

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._enabled = {1: True, 2: True}
        self._total = 0
        self._pos = 0
        self._rate = 1000.0
        self._streaming = False

    def enable_input(self, channel, enable=True):
        self._enabled[channel] = bool(enable)

    def start_streaming(self, duration=10, sample_rate=1000, **kw):
        self._rate = float(sample_rate)
        self._total = int(float(duration) * self._rate)
        self._pos = 0
        self._streaming = True

    def get_stream_data(self):
        if not self._streaming:
            raise MokuException('start_streaming has not been called')
        if self._pos >= self._total:
            self._streaming = False
            raise MokuException('End of stream')
        n = min(self._CHUNK, self._total - self._pos)
        t = (np.arange(self._pos, self._pos + n)) / self._rate
        sig, gain = self._input_signal()
        rng = np.random.default_rng()
        ch1 = rng.normal(0, NOISE_RMS, n)
        if sig is not None:
            ch1 = ch1 + sig.sample(t, gain)
        self._pos += n
        out = {'time': t.tolist(), 'ch1': ch1.tolist()}
        if self._enabled.get(2, False):
            out['ch2'] = rng.normal(0, NOISE_RMS, n).tolist()
        return out

    def stop_streaming(self):
        self._streaming = False

    def start_logging(self, duration=10, sample_rate=1000, **kw):
        return dict(duration=duration, sample_rate=sample_rate,
                    file='mokusim_log.li')


class CustomInstrument(_BaseInstrument):
    """Simulated MCC slot instrument (threshold detector semantics).

    set_control(0, value): detection threshold, Q1.15 (32767 = +1.0 V).
    get_status(): [crossings_per_second, 0, 0, 0] — crossings equal the
    routed input signal's frequency while its peak exceeds threshold.
    """

    def __init__(self, *a, bitstream=None, **kw):
        super().__init__(*a, **kw)
        self._bitstream = bitstream
        self._controls = {}

    def upload_bitstream(self, name, bs_path=None):
        self._bitstream = name

    def set_control(self, idx, value, strict=True):
        if not 0 <= int(idx) <= 19:
            raise MokuException('Control index must be 0..19')
        self._controls[int(idx)] = int(value)

    def set_controls(self, controls, strict=True):
        for pair in controls:
            self.set_control(pair['id'], pair['value'])

    def get_control(self, idx, strict=True):
        return self._controls.get(int(idx), 0)

    def get_controls(self):
        return [dict(id=k, value=v) for k, v in sorted(
            self._controls.items())]

    def get_status(self):
        sig, gain = self._input_signal()
        threshold_v = self._controls.get(0, 0x2000) / 32767.0
        crossings = 0
        if sig is not None:
            peak_v = sig.amplitude / 2.0 * gain
            if peak_v >= threshold_v * 0.999:   # edge tolerance
                crossings = int(round(sig.frequency))
        return [crossings, 0, 0, 0]


class CloudCompile(CustomInstrument):
    def __init__(self, *a, **kw):
        print('Warning: CloudCompile is deprecated, use CustomInstrument '
              'instead')
        super().__init__(*a, **kw)


class MultiInstrument:
    """Simulated 2-slot MiM (platform_id=2, Moku:Go)."""

    _SOURCES = {'Input1', 'Input2', 'Slot1OutA', 'Slot1OutB',
                'Slot2OutA', 'Slot2OutB'}
    _DESTS = {'Output1', 'Output2', 'Slot1InA', 'Slot1InB',
              'Slot2InA', 'Slot2InB'}

    def __init__(self, ip=None, platform_id=None, force_connect=False,
                 **kw):
        if platform_id != 2:
            raise MokuException('platform_id=2 is required for Moku:Go '
                                '(2-slot MiM)')
        self._ip = ip
        self._slots = {}
        self._connections = []
        self._owned = True

    def set_instrument(self, slot, cls, **kw):
        if slot not in (1, 2):
            raise MokuException('Moku:Go has 2 slots (platform_id=2)')
        inst = cls(self._ip, _mim=self, _slot=slot, **kw)
        self._slots[slot] = inst
        return inst

    def set_connections(self, connections=None, **kw):
        if isinstance(connections, dict):
            raise MokuException(
                'connections must be a LIST of dicts — a plain dict '
                'silently loses duplicate keys. Use: '
                "connections=[dict(source='Slot1OutA', "
                "destination='Output1'), ...] (hardware-verified; the #1 "
                'MiM mistake).')
        if not isinstance(connections, list) or not all(
                isinstance(c, dict) and 'source' in c and 'destination'
                in c for c in (connections or [])):
            raise MokuException(
                "each connection must be dict(source=..., destination=...)")
        for c in connections:
            if c['source'] not in self._SOURCES:
                raise MokuException(
                    f"invalid source '{c['source']}' — valid: "
                    f"{sorted(self._SOURCES)}")
            if c['destination'] not in self._DESTS:
                raise MokuException(
                    f"invalid destination '{c['destination']}' — valid: "
                    f"{sorted(self._DESTS)}")
        self._connections = [dict(c) for c in connections]
        return self._connections

    def set_frontend(self, channel=1, **kw):
        return dict(channel=channel, **kw)

    def set_dio(self, pin=1, direction='Output', **kw):
        return dict(pin=pin, direction=direction)

    def get_connections(self):
        return list(self._connections)

    def relinquish_ownership(self):
        self._owned = False
        for inst in self._slots.values():
            inst._owned = False

    def summary(self):
        return f'<simulated MultiInstrument @ {self._ip} (mokusim)>'

    # -- routing model ---------------------------------------------------
    def _source_signal(self, source):
        """Signal present on a source node (slot outputs only)."""
        if source.startswith('Slot'):
            slot = int(source[4])
            inst = self._slots.get(slot)
            if inst is not None:
                sig = inst._signals.get(1)
                if sig is not None:
                    return sig
        return None

    def _signal_into_slot(self, slot):
        """(signal, gain) arriving at Slot<slot>InA, following routing.
        Input1 is fed by whatever drives Output1, through the physical
        loopback cable (and the optional simulated DUT)."""
        dest = f'Slot{slot}InA'
        for c in self._connections:
            if c['destination'] != dest:
                continue
            src = c['source']
            if src.startswith('Slot'):
                return (self._source_signal(src), 1.0)   # internal: direct
            if src.startswith('Input'):
                # physical input <- Output1 via loopback (+ DUT)
                for c2 in self._connections:
                    if c2['destination'] == 'Output1':
                        sig = self._source_signal(c2['source'])
                        gain = _dut_gain(sig.frequency) if sig else 1.0
                        return (sig, gain)
                return (None, 1.0)
        return (None, 1.0)
