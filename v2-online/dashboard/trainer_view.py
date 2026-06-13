"""Trainer console — /trainer routes on the dashboard Flask server.

Password-gated (env TRAINER_PASSWORD, default 'XBL@2026') live table of
every participant's progress across sessions, with CSV export, 30-second
auto-refresh, and session creation (college name -> 4-digit join code).

Reads/writes through supabase_store; if Supabase is unavailable the page
still renders and explains that persistence is off (in-memory only).

Xenith Brand Labs
"""

import csv
import hashlib
import io
import os
import random

from flask import Response, request, redirect

import supabase_store as store

PASSWORD = os.environ.get('TRAINER_PASSWORD', 'XBL@2026')
COOKIE = 'xbl_trainer'
NAVY, ORANGE, TEAL, BLUE = '#0B2E59', '#FF6B35', '#028090', '#0057B8'
EX = store.EXERCISES


def _token():
    return hashlib.sha256(('xbl-salt::' + PASSWORD).encode()).hexdigest()


def _authed():
    return request.cookies.get(COOKIE) == _token()


def _login_page(error=''):
    msg = (f'<p style="color:#C0392B">{error}</p>') if error else ''
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>SDI Lab Cloud — Trainer Console | Xenith Brand Labs</title>
<style>body{{font-family:Calibri,Segoe UI,sans-serif;background:#F0F4F8;
display:flex;height:100vh;margin:0;align-items:center;justify-content:center}}
.box{{background:#fff;padding:28px 32px;box-shadow:0 2px 10px rgba(0,0,0,.15);
border-top:5px solid {NAVY}}}
h1{{color:{NAVY};font-size:18px;margin:0 0 4px}}
small{{color:#5A6B7B}} input{{padding:8px;width:220px;margin:10px 0;
border:1px solid #ccd}} button{{background:{ORANGE};color:#fff;border:0;
padding:9px 16px;font-weight:700;cursor:pointer}}</style></head>
<body><form class="box" method="post" action="/trainer/login">
<h1>SDI Lab Cloud — Trainer Console</h1>
<small>Xenith Brand Labs</small>{msg}<br>
<input type="password" name="pw" placeholder="trainer password" autofocus><br>
<button type="submit">Enter</button></form></body></html>"""


def _board_page():
    rows = store.board()
    sessions = store.list_sessions()
    persist = ('on' if store.enabled() else
               'OFF — set SUPABASE_URL/SUPABASE_KEY (in-memory only)')

    # sessions + join codes
    sess_html = ''.join(
        f'<tr><td>{s.get("college_name") or "—"}</td>'
        f'<td style="font-weight:700;color:{ORANGE}">{s.get("join_code") or "—"}</td>'
        f'<td>{s.get("trainer_name") or "—"}</td></tr>'
        for s in sessions) or '<tr><td colspan="3">no sessions yet</td></tr>'

    # participant table
    head = ('<th>Name</th><th>College</th>'
            + ''.join(f'<th>{e}</th>' for e in EX)
            + '<th>Score %</th><th>Last Active</th>')
    body = ''
    for r in rows:
        score = round(len(r['done'] & set(EX)) / len(EX) * 100)
        cells = ''.join(
            f'<td style="text-align:center;color:'
            f'{TEAL if e in r["done"] else "#C5D2E0"};font-weight:700">'
            f'{"✓" if e in r["done"] else "·"}</td>' for e in EX)
        body += (f'<tr><td style="font-weight:600">{r["name"]}</td>'
                 f'<td>{r["college"]}</td>{cells}'
                 f'<td style="text-align:center;font-weight:700">{score}%</td>'
                 f'<td style="font-size:12px;color:#5A6B7B">{r["last"]}</td></tr>')
    if not rows:
        body = (f'<tr><td colspan="{len(EX)+4}" style="padding:14px;'
                f'color:#5A6B7B">no participants yet</td></tr>')

    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<title>SDI Lab Cloud — Trainer Console | Xenith Brand Labs</title>
<style>body{{font-family:Calibri,Segoe UI,sans-serif;background:#F0F4F8;
margin:0}} .bar{{background:{NAVY};color:#fff;padding:10px 18px;display:flex;
justify-content:space-between;align-items:center}}
.bar b{{font-size:17px}} .wrap{{padding:16px 18px}}
table{{border-collapse:collapse;background:#fff;width:100%;font-size:13px;
box-shadow:0 1px 4px rgba(0,0,0,.12);margin-bottom:18px}}
th{{background:{NAVY};color:#fff;padding:6px 8px;font-size:12px}}
td{{padding:6px 8px;border-bottom:1px solid #eef}}
.card{{background:#fff;padding:12px 16px;margin-bottom:16px;
box-shadow:0 1px 4px rgba(0,0,0,.12)}} h2{{color:{NAVY};font-size:15px;
margin:0 0 8px}} input{{padding:7px;border:1px solid #ccd;margin-right:6px}}
button,a.btn{{background:{ORANGE};color:#fff;border:0;padding:8px 14px;
font-weight:700;cursor:pointer;text-decoration:none;border-radius:3px}}
a.teal{{background:{TEAL}}} small{{color:#5A6B7B}}</style></head>
<body>
<div class="bar"><b>SDI Lab Cloud — Trainer Console</b>
<span>Xenith Brand Labs &nbsp;·&nbsp; persistence: {persist} &nbsp;·&nbsp;
auto-refresh 30s</span></div>
<div class="wrap">

  <div class="card"><h2>Create a session</h2>
   <form method="post" action="/trainer/session">
     <input name="college" placeholder="college name" required>
     <input name="trainer" placeholder="trainer name (optional)">
     <button type="submit">Create + generate join code</button>
   </form>
   <small>Participants enter the 4-digit join code on the dashboard to
   link to this session.</small>
   <table style="margin-top:10px"><tr><th style="text-align:left">College</th>
   <th>Join code</th><th>Trainer</th></tr>{sess_html}</table>
  </div>

  <div class="card">
   <h2>Cohort progress
     &nbsp; <a class="btn" href="/trainer/export.csv">Export CSV</a>
     &nbsp; <a class="btn teal" href="/trainer">Refresh now</a></h2>
   <table><tr>{head}</tr>{body}</table>
  </div>

</div></body></html>"""


def register(server):
    @server.route('/trainer')
    def trainer_home():
        if not _authed():
            return Response(_login_page(), mimetype='text/html')
        return Response(_board_page(), mimetype='text/html')

    @server.route('/trainer/login', methods=['POST'])
    def trainer_login():
        if request.form.get('pw') == PASSWORD:
            resp = redirect('/trainer')
            resp.set_cookie(COOKIE, _token(), httponly=True,
                            samesite='Lax', max_age=60 * 60 * 12)
            return resp
        return Response(_login_page('Wrong password.'), mimetype='text/html')

    @server.route('/trainer/logout', methods=['POST', 'GET'])
    def trainer_logout():
        resp = redirect('/trainer')
        resp.delete_cookie(COOKIE)
        return resp

    @server.route('/trainer/session', methods=['POST'])
    def trainer_session():
        if not _authed():
            return redirect('/trainer')
        college = (request.form.get('college') or '').strip()[:80]
        trainer = (request.form.get('trainer') or '').strip()[:60]
        if college and store.enabled():
            # 4-digit join code, retry on the unique-constraint clash
            for _ in range(8):
                code = str(random.randint(1000, 9999))
                if store.get_session_by_code(code):
                    continue
                if store.create_session(college, trainer, code):
                    break
        return redirect('/trainer')

    @server.route('/trainer/export.csv')
    def trainer_export():
        if not _authed():
            return redirect('/trainer')
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['Name', 'College'] + EX + ['Score %', 'Last Active'])
        for r in store.board():
            score = round(len(r['done'] & set(EX)) / len(EX) * 100)
            w.writerow([r['name'], r['college']]
                       + ['1' if e in r['done'] else '0' for e in EX]
                       + [score, r['last']])
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition':
                                 'attachment; filename=sdi_lab_cloud_progress.csv'})

    return server
