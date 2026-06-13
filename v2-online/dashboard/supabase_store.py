"""Supabase persistence layer for the SDI Lab Cloud dashboard.

Thin wrapper over the Supabase REST (PostgREST) API using `requests`
and the anon key — no heavy SDK. Every call is wrapped so that if
Supabase is unconfigured, unreachable, or the tables are missing, the
function returns a safe empty value and the dashboard silently falls
back to its in-memory state. It NEVER raises to the caller.

Tables (see schema.sql): sessions, participants, progress.

Env:
    SUPABASE_URL   e.g. https://xxxx.supabase.co
    SUPABASE_KEY   anon key

Xenith Brand Labs
"""

import os
from urllib.parse import quote

import requests

URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
KEY = os.environ.get('SUPABASE_KEY', '')
TIMEOUT = 4  # seconds — keep short so a hang never freezes the UI

# The 10 tracked exercises, in display order. Shared with app + trainer.
EXERCISES = ['Ex 1.1', 'Ex 1.2', 'Ex 2.1', 'Ex 2.2', 'Ex 2.3',
             'Ex 3.1', 'Ex 3.2', 'Cap A', 'Cap B', 'Cap C']

_warned = False


def enabled():
    return bool(URL and KEY)


def _warn_once(msg):
    global _warned
    if not _warned:
        print(f'[supabase] {msg} — falling back to in-memory.')
        _warned = True


def _headers(extra=None):
    h = {'apikey': KEY, 'Authorization': f'Bearer {KEY}',
         'Content-Type': 'application/json'}
    if extra:
        h.update(extra)
    return h


def _rest(method, path, **kw):
    """Single entry point. Returns parsed JSON, [] for empty, or None on
    any failure (never raises)."""
    if not enabled():
        return None
    try:
        r = requests.request(method, f'{URL}/rest/v1/{path}',
                             timeout=TIMEOUT, **kw)
        if r.status_code >= 400:
            _warn_once(f'{method} {path} -> HTTP {r.status_code}')
            return None
        if r.text:
            return r.json()
        return []
    except Exception as e:                       # network, DNS, timeout…
        _warn_once(f'{method} {path} failed: {e}')
        return None


# ----------------------------------------------------------------------
# Sessions
# ----------------------------------------------------------------------
def create_session(college, trainer, join_code):
    rows = _rest('POST', 'sessions',
                 headers=_headers({'Prefer': 'return=representation'}),
                 json={'college_name': college, 'trainer_name': trainer,
                       'join_code': join_code})
    return rows[0] if rows else None


def get_session_by_code(code):
    rows = _rest('GET', f'sessions?join_code=eq.{quote(str(code))}&select=*',
                 headers=_headers())
    return rows[0] if rows else None


def list_sessions():
    return _rest('GET', 'sessions?select=*&order=created_at.desc',
                 headers=_headers()) or []


# ----------------------------------------------------------------------
# Participants
# ----------------------------------------------------------------------
def get_or_create_participant(session_id, name):
    """Reuse an existing (name, session) participant so a browser
    refresh or re-join does not create duplicates."""
    q = f'participants?name=eq.{quote(name)}&select=*'
    q += f'&session_id=eq.{session_id}' if session_id else '&session_id=is.null'
    rows = _rest('GET', q, headers=_headers())
    if rows:
        return rows[0]
    payload = {'name': name}
    if session_id:
        payload['session_id'] = session_id
    rows = _rest('POST', 'participants',
                 headers=_headers({'Prefer': 'return=representation'}),
                 json=payload)
    return rows[0] if rows else None


# ----------------------------------------------------------------------
# Progress
# ----------------------------------------------------------------------
def set_progress(participant_id, exercise_id):
    """Tick: insert, ignoring the row if it already exists (relies on the
    unique(participant_id, exercise_id) constraint)."""
    return _rest('POST', 'progress?on_conflict=participant_id,exercise_id',
                 headers=_headers({'Prefer': 'resolution=ignore-duplicates,'
                                             'return=minimal'}),
                 json={'participant_id': participant_id,
                       'exercise_id': exercise_id}) is not None


def clear_progress(participant_id, exercise_id):
    """Un-tick: delete the row so the table mirrors the checkboxes."""
    return _rest('DELETE',
                 f'progress?participant_id=eq.{participant_id}'
                 f'&exercise_id=eq.{quote(exercise_id)}',
                 headers=_headers({'Prefer': 'return=minimal'})) is not None


def get_progress(participant_id):
    rows = _rest('GET',
                 f'progress?participant_id=eq.{participant_id}'
                 f'&select=exercise_id', headers=_headers())
    return [r['exercise_id'] for r in (rows or [])]


# ----------------------------------------------------------------------
# Trainer board — full cross-session roster with progress
# ----------------------------------------------------------------------
def board():
    """Returns a list of dicts:
    {name, college, done:set(exercise_id), last:str} — for the trainer
    table and CSV export. Empty list if Supabase is unavailable."""
    parts = _rest('GET',
                  'participants?select=id,name,joined_at,session_id',
                  headers=_headers())
    if not parts:
        return []
    sessions = {s['id']: s for s in list_sessions()}
    prog = _rest('GET',
                 'progress?select=participant_id,exercise_id,completed_at',
                 headers=_headers()) or []
    by_pid = {}
    for p in prog:
        by_pid.setdefault(p['participant_id'], []).append(p)
    out = []
    for p in parts:
        plist = by_pid.get(p['id'], [])
        done = {x['exercise_id'] for x in plist}
        stamps = [x['completed_at'] for x in plist if x.get('completed_at')]
        if p.get('joined_at'):
            stamps.append(p['joined_at'])
        last = max(stamps) if stamps else ''
        sess = sessions.get(p.get('session_id') or '', {})
        out.append({'name': p.get('name') or '—',
                    'college': sess.get('college_name') or '—',
                    'done': done,
                    'last': (last.replace('T', ' ')[:16] if last else '—')})
    out.sort(key=lambda r: (r['college'], r['name']))
    return out
