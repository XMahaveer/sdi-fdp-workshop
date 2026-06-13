"""SDI FDP Live Workshop Dashboard — V2 online delivery (all models).

One Plotly Dash app serving trainer + participants during a remote
workshop, designed to run beside Google Meet (companion mode: trainer
screen-shares it and/or participants open the tunnel URL; a Join-Meet
button links the call).

Modes (MOKUDASH_MODE):
  sim    — signals come from the mokusim simulator   (Model A)
  live   — signals come from a REAL Moku:Go on MOKU_IP (Models B/C);
           the same code path works because mokusim is API-compatible.

Roles:
  participant — default: open the URL, enter your name
  trainer     — open  /?role=trainer&key=<TRAINER_KEY>   (default key:
                'spruha') to control presets, advance the device queue,
                and push code snippets.

Run:
  cd v2-online/dashboard
  python app.py                       # http://localhost:8050
  cloudflared tunnel --url http://localhost:8050   # share the URL

Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import importlib.util
import os
import threading
import time
from pathlib import Path

import numpy as np
import dash
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objects as go

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
MODE = os.environ.get('MOKUDASH_MODE', 'sim').lower()        # sim | live
MOKU_IP = os.environ.get('MOKU_IP', '192.168.0.101')
MEET_URL = os.environ.get('MEET_URL', 'https://meet.google.com/new')
TRAINER_KEY = os.environ.get('TRAINER_KEY', 'spruha')
PORT = int(os.environ.get('PORT', '8050'))

BLUE, ORANGE, NAVY = '#0057B8', '#FF6B35', '#0B2E59'
TEAL, RED, PAGE, CARD = '#028090', '#C0392B', '#F0F4F8', '#FFFFFF'
INK, MUTED = '#1A202C', '#5A6B7B'

EXERCISES = ['Ex 1.1', 'Ex 1.2', 'Ex 2.1', 'Ex 2.2', 'Ex 2.3',
             'Ex 3.1', 'Ex 3.2', 'Cap A', 'Cap B', 'Cap C']

PRESETS = {
    'ex1_1':  dict(label='Ex 1.1 — 1 kHz sine, 0.5 Vpp',
                   type='Sine', amplitude=0.5, frequency=1e3,
                   timebase=5e-3),
    'square': dict(label='Square 5 kHz, duty 30%',
                   type='Square', amplitude=2.0, frequency=5e3, duty=30,
                   timebase=1e-3),
    'ramp':   dict(label='Ramp 2 kHz, symmetry 50%',
                   type='Ramp', amplitude=1.0, frequency=2e3, symmetry=50,
                   timebase=2e-3),
    'am':     dict(label='AM — 100 kHz carrier, 1 kHz msg, 50%',
                   type='Sine', amplitude=1.0, frequency=100e3,
                   modulation=('Amplitude', 1e3, 50), timebase=2.5e-3),
    'cap_c':  dict(label='Capstone C — 1 MHz oscillator',
                   type='Sine', amplitude=1.0, frequency=1e6,
                   timebase=5e-6),
}

# ----------------------------------------------------------------------
# Instrument backend (mokusim or real moku — identical API)
# ----------------------------------------------------------------------
def _load_backend():
    if MODE == 'live':
        import moku.instruments as mi        # the real package
        return mi, f'LIVE — real Moku:Go @ {MOKU_IP}'
    sim_path = (Path(__file__).resolve().parents[1] / 'simulator'
                / 'moku' / 'instruments.py')
    spec = importlib.util.spec_from_file_location('mokusim_inst', sim_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, 'SIM — mokusim (no hardware)'


BACKEND, MODE_BADGE = _load_backend()
_osc = None
_osc_lock = threading.Lock()


def _scope():
    """One shared (simulated or real) oscilloscope for the dashboard."""
    global _osc
    if _osc is None:
        _osc = BACKEND.Oscilloscope(MOKU_IP, force_connect=True)
    return _osc


def capture(preset_key):
    """Configure per preset and grab one frame. Returns (t, y)."""
    p = PRESETS.get(preset_key, PRESETS['ex1_1'])
    with _osc_lock:
        osc = _scope()
        kw = {}
        if p.get('duty') is not None:
            kw['duty'] = p['duty']
        if p.get('symmetry') is not None:
            kw['symmetry'] = p['symmetry']
        osc.generate_waveform(1, p['type'], amplitude=p['amplitude'],
                              frequency=p['frequency'], **kw)
        if p.get('modulation'):
            mtype, mfreq, depth = p['modulation']
            osc.set_modulation(channel=1, type=mtype, source='Internal',
                               frequency=mfreq, depth=depth)
        tb = p['timebase']
        osc.set_timebase(-tb, tb)
        data = osc.get_data()
    return np.array(data['time']), np.array(data['ch1'])


# ----------------------------------------------------------------------
# Shared workshop state (in-memory; one trainer machine per cohort)
# ----------------------------------------------------------------------
STATE = {
    'progress': {},          # name -> set of exercise labels
    'queue': [],             # device rotation (Model B/C)
    'holder': None,          # who has the Moku right now
    'snippet': '# trainer has not pushed a snippet yet',
    'preset': 'ex1_1',
}
LOCK = threading.Lock()


# ----------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------
def card(title, children, accent=BLUE):
    return html.Div([
        html.Div(title, style={
            'background': accent, 'color': 'white', 'fontWeight': '700',
            'padding': '8px 14px', 'fontSize': '15px'}),
        html.Div(children, style={'padding': '12px 14px'}),
    ], style={'background': CARD, 'marginBottom': '14px',
              'boxShadow': '0 2px 6px rgba(26,32,44,.18)'})


def fig_layout(fig, title, xtitle, ytitle):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=NAVY)),
        margin=dict(l=50, r=15, t=34, b=36), height=260,
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Calibri, sans-serif', color=INK),
        xaxis=dict(title=xtitle, gridcolor='#E3EDF9'),
        yaxis=dict(title=ytitle, gridcolor='#E3EDF9'))
    return fig


app = dash.Dash(__name__, title='SDI FDP Live Dashboard')
server = app.server   # for cloud hosts (gunicorn) later

# Google Meet Add-on surface (side panel + main stage). Optional —
# the dashboard works standalone (companion mode) without it.
try:
    import meet_addon
    meet_addon.register(server)
except Exception as _e:        # never let the add-on layer break the app
    print(f'[dashboard] Meet add-on routes not registered: {_e}')

app.layout = html.Div([
    dcc.Location(id='url'),
    dcc.Store(id='me', storage_type='local'),
    dcc.Interval(id='tick-fast', interval=1500),
    dcc.Interval(id='tick-slow', interval=2500),

    # header
    html.Div([
        html.Div([
            html.Span('5-Day SDI Lab Automation FDP', style={
                'fontWeight': '800', 'fontSize': '20px'}),
            html.Span('  •  Live Workshop Dashboard (V2)', style={
                'fontSize': '15px', 'opacity': .85}),
        ]),
        html.Div([
            html.Span(MODE_BADGE, id='mode-badge', style={
                'background': TEAL if MODE != 'live' else RED,
                'padding': '4px 12px', 'borderRadius': '12px',
                'fontWeight': '700', 'fontSize': '12px',
                'whiteSpace': 'nowrap'}),
            html.A('▶ Join Google Meet', href=MEET_URL, target='_blank',
                   style={'background': ORANGE, 'color': 'white',
                          'padding': '8px 16px', 'fontWeight': '700',
                          'textDecoration': 'none', 'borderRadius': '4px',
                          'whiteSpace': 'nowrap'}),
        ], style={'display': 'flex', 'alignItems': 'center',
                  'gap': '14px', 'flexWrap': 'wrap',
                  'justifyContent': 'flex-end'}),
    ], style={'background': NAVY, 'color': 'white', 'display': 'flex',
              'justifyContent': 'space-between', 'alignItems': 'center',
              'flexWrap': 'wrap', 'gap': '10px',
              'padding': '12px 22px'}),

    # body: two columns
    html.Div([
        # left — live signal
        html.Div([
            card('Live Signal — what the trainer sees', [
                dcc.Dropdown(id='preset',
                             options=[{'label': v['label'], 'value': k}
                                      for k, v in PRESETS.items()],
                             value='ex1_1', clearable=False,
                             style={'marginBottom': '8px'}),
                dcc.Graph(id='scope-fig', config={'displayModeBar': False}),
                dcc.Graph(id='fft-fig', config={'displayModeBar': False}),
            ]),
            card('Code Push — trainer → everyone', [
                dcc.Textarea(id='snippet-in', style={
                    'width': '100%', 'height': '70px',
                    'fontFamily': 'Consolas, monospace',
                    'fontSize': '12px'},
                    placeholder='trainer: paste a snippet, then Push'),
                html.Button('Push to all', id='snippet-btn', n_clicks=0,
                            style={'marginTop': '6px'}),
                html.Pre(id='snippet-out', style={
                    'background': '#1E1E1E', 'color': '#CE9178',
                    'padding': '10px', 'fontSize': '12px',
                    'whiteSpace': 'pre-wrap', 'marginTop': '8px'}),
            ], accent=TEAL),
        ], style={'flex': '1.2', 'marginRight': '14px'}),

        # right — people & device
        html.Div([
            card('You', [
                dcc.Input(id='name-in', placeholder='your name',
                          style={'marginRight': '8px'}),
                html.Button('Join roster', id='name-btn', n_clicks=0),
                html.Div(id='me-label', style={
                    'marginTop': '6px', 'color': MUTED,
                    'fontSize': '13px'}),
                html.Div(id='role-label', style={
                    'color': ORANGE, 'fontWeight': '700',
                    'fontSize': '13px'}),
            ]),
            card('My Exercise Progress', [
                dcc.Checklist(id='my-progress', options=[
                    {'label': ' ' + e, 'value': e} for e in EXERCISES],
                    inline=True,
                    inputStyle={'marginLeft': '10px'}),
            ], accent=TEAL),
            card('Cohort Progress', [
                html.Div(id='roster-table'),
            ]),
            card('Moku:Go Rotation (Models B/C)', [
                html.Div(id='holder-line', style={
                    'fontWeight': '700', 'marginBottom': '6px'}),
                html.Button('Join queue', id='queue-join', n_clicks=0,
                            style={'marginRight': '8px'}),
                html.Button('Leave queue', id='queue-leave', n_clicks=0,
                            style={'marginRight': '8px'}),
                html.Button('Trainer: next →', id='queue-next',
                            n_clicks=0,
                            style={'background': ORANGE, 'color': 'white',
                                   'fontWeight': '700'}),
                html.Div(id='queue-list', style={
                    'marginTop': '8px', 'fontSize': '13px',
                    'color': MUTED}),
            ], accent=ORANGE),
        ], id='right-col', style={'flex': '1'}),
    ], style={'display': 'flex', 'padding': '16px 22px'}),

    html.Div('Spruha Build-in Solutions  |  Powered by Moku:Go — '
             'Liquid Instruments  •  v2.0',
             style={'background': BLUE, 'color': 'white',
                    'textAlign': 'center', 'padding': '7px',
                    'fontSize': '12px'}),
], style={'background': PAGE, 'fontFamily': 'Calibri, sans-serif',
          'minHeight': '100vh'})


# ----------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------
def _is_trainer(search):
    from urllib.parse import parse_qs
    q = parse_qs((search or '').lstrip('?'))
    return (q.get('role', [''])[0] == 'trainer'
            and q.get('key', [''])[0] == TRAINER_KEY)


@app.callback(Output('role-label', 'children'), Input('url', 'search'))
def show_role(search):
    return 'ROLE: TRAINER' if _is_trainer(search) else ''


@app.callback(Output('right-col', 'style'), Input('url', 'search'))
def signal_only_view(search):
    """Main-stage embed (?view=signal) shows just the live signal —
    hide the people/device column so the waveform fills the stage."""
    from urllib.parse import parse_qs
    q = parse_qs((search or '').lstrip('?'))
    if q.get('view', [''])[0] == 'signal':
        return {'display': 'none'}
    return {'flex': '1'}


@app.callback(Output('me', 'data'), Output('me-label', 'children'),
              Input('name-btn', 'n_clicks'), State('name-in', 'value'),
              State('me', 'data'), prevent_initial_call=False)
def join_roster(n, name, me):
    if n and name:
        me = name.strip()[:24]
        with LOCK:
            STATE['progress'].setdefault(me, set())
    label = f'signed in as: {me}' if me else 'not signed in yet'
    return me, label


@app.callback(Output('scope-fig', 'figure'), Output('fft-fig', 'figure'),
              Input('tick-fast', 'n_intervals'), Input('preset', 'value'),
              State('url', 'search'))
def update_scope(_, preset, search):
    if _is_trainer(search) and preset:
        with LOCK:
            STATE['preset'] = preset
    with LOCK:
        active = STATE['preset']
    try:
        t, y = capture(active)
    except Exception as e:
        f = go.Figure()
        f.add_annotation(text=f'signal source error: {e}',
                         showarrow=False)
        return fig_layout(f, 'Signal', '', ''), fig_layout(
            go.Figure(), 'Spectrum', '', '')
    fig = go.Figure(go.Scatter(x=t * 1e3, y=y, mode='lines',
                               line=dict(color=BLUE, width=1.5)))
    fig_layout(fig, f'Time domain — {PRESETS[active]["label"]}',
               'Time (ms)', 'Voltage (V)')
    n = len(y)
    mag = 2.0 / n * np.abs(np.fft.rfft(y * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, t[1] - t[0])
    fft = go.Figure(go.Scatter(x=freqs / 1e3, y=20 * np.log10(
        np.maximum(mag, 1e-9)), mode='lines',
        line=dict(color=TEAL, width=1.2)))
    fig_layout(fft, 'Spectrum (FFT of the frame above)',
               'Frequency (kHz)', 'Magnitude (dBV)')
    return fig, fft


@app.callback(Output('snippet-out', 'children'),
              Input('snippet-btn', 'n_clicks'),
              Input('tick-slow', 'n_intervals'),
              State('snippet-in', 'value'), State('url', 'search'))
def snippet(n, _, value, search):
    trig = dash.callback_context.triggered_id
    if trig == 'snippet-btn' and value and _is_trainer(search):
        with LOCK:
            STATE['snippet'] = value
    with LOCK:
        return STATE['snippet']


@app.callback(Output('roster-table', 'children'),
              Input('tick-slow', 'n_intervals'),
              Input('my-progress', 'value'), State('me', 'data'))
def progress(_, my_done, me):
    if me:
        with LOCK:
            STATE['progress'][me] = set(my_done or [])
    with LOCK:
        snapshot = {k: set(v) for k, v in STATE['progress'].items()}
    if not snapshot:
        return html.Div('nobody on the roster yet', style={'color': MUTED})
    head = html.Tr([html.Th('Name', style={'textAlign': 'left'})] +
                   [html.Th(e.split()[-1], style={'padding': '0 4px'})
                    for e in EXERCISES])
    rows = []
    for name in sorted(snapshot):
        cells = [html.Td(name, style={'fontWeight': '600'})]
        for e in EXERCISES:
            done = e in snapshot[name]
            cells.append(html.Td('✓' if done else '·', style={
                'textAlign': 'center',
                'color': TEAL if done else '#C5D2E0',
                'fontWeight': '700'}))
        rows.append(html.Tr(cells))
    return html.Table([head] + rows, style={'fontSize': '13px',
                                            'width': '100%'})


@app.callback(Output('holder-line', 'children'),
              Output('queue-list', 'children'),
              Input('queue-join', 'n_clicks'),
              Input('queue-leave', 'n_clicks'),
              Input('queue-next', 'n_clicks'),
              Input('tick-slow', 'n_intervals'),
              State('me', 'data'), State('url', 'search'))
def queue(_j, _l, _n, _t, me, search):
    trig = dash.callback_context.triggered_id
    with LOCK:
        if trig == 'queue-join' and me and me not in STATE['queue'] \
                and STATE['holder'] != me:
            STATE['queue'].append(me)
        elif trig == 'queue-leave' and me in STATE['queue']:
            STATE['queue'].remove(me)
        elif trig == 'queue-next' and _is_trainer(search):
            STATE['holder'] = (STATE['queue'].pop(0)
                               if STATE['queue'] else None)
        holder = STATE['holder']
        q = list(STATE['queue'])
    line = (f'Device with: {holder}' if holder
            else 'Device with: trainer (nobody checked out)')
    qtxt = ('Queue: ' + ' → '.join(q)) if q else 'Queue: empty'
    return line, qtxt


if __name__ == '__main__':
    print(f'[dashboard] mode={MODE_BADGE}  trainer key={TRAINER_KEY!r}')
    print(f'[dashboard] participants:  http://localhost:{PORT}')
    print(f'[dashboard] trainer:       http://localhost:{PORT}/'
          f'?role=trainer&key={TRAINER_KEY}')
    print('[dashboard] share publicly: '
          f'cloudflared tunnel --url http://localhost:{PORT}')
    app.run(host='0.0.0.0', port=PORT, debug=False)
