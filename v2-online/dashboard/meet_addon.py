"""Google Meet Add-on wrapper for the live workshop dashboard.

Registers three Flask routes on the existing Dash server so the
dashboard can render INSIDE Google Meet (side panel + main stage) via
the Meet Add-ons Web SDK — the "dashboard inside Meet" showpiece. The
same app still works as a normal web page (companion mode); these
routes only add the Meet-embedded surface.

Routes (served by the Dash app's Flask server):
    /addon/sidepanel   narrow panel: roster, queue, code-push, plus a
                       "Show live signal on main stage" button
    /addon/mainstage   wide panel: the live signal + FFT, next to the
                       Meet video tiles
    /addon/manifest    the add-on config values to paste into the GCP
                       Workspace Marketplace SDK (JSON)

Free-tier: the Meet Add-ons SDK and an unlisted add-on in a free Google
Cloud project cost nothing; only PUBLIC distribution needs Marketplace
review, which a private FDP does not require.

Configuration (env vars, all optional with safe defaults):
    PUBLIC_URL            HTTPS origin the add-on is reachable at
                          (the Cloudflare tunnel URL or cloud host).
                          REQUIRED for the main-stage hand-off to work
                          inside Meet; defaults to the request origin.
    GCP_PROJECT_NUMBER    your Google Cloud project NUMBER (not id).
    MEET_ADDON_SDK_VERSION  pinned Meet Add-ons Web SDK version.

Spruha Build-in Solutions | Powered by Moku:Go — Liquid Instruments
"""

import os
from flask import Response, request

# NOTE: verify the current Meet Add-ons Web SDK version against
# https://developers.google.com/workspace/meet/add-ons/guides/overview
# before a live deployment — pin it here so the manifest matches.
SDK_VERSION = os.environ.get('MEET_ADDON_SDK_VERSION', '0.9.0')
SDK_SRC = (f'https://www.gstatic.com/meetjs/addons/{SDK_VERSION}/'
           'meet.addons.js')
PROJECT_NUMBER = os.environ.get('GCP_PROJECT_NUMBER', 'YOUR_GCP_PROJECT_NUMBER')

NAVY, ORANGE, TEAL = '#0B2E59', '#FF6B35', '#028090'


def _origin():
    """Absolute HTTPS origin this add-on is served from."""
    return (os.environ.get('PUBLIC_URL')
            or request.url_root.rstrip('/'))


_BOOT = """
<script src="{sdk}"></script>
<script>
  // Meet Add-ons SDK boot. Degrades gracefully to a standalone page
  // when not opened inside Google Meet (window.meet is undefined).
  const PROJECT = "{project}";
  const ORIGIN  = "{origin}";
  async function boot() {{
    const banner = document.getElementById('meet-banner');
    if (!window.meet || !window.meet.addon) {{
      banner.textContent = 'Standalone view — open via the Meet '
        + 'add-on to dock this inside the call.';
      return;
    }}
    try {{
      const session = await window.meet.addon.createAddonSession(
        {{ cloudProjectNumber: PROJECT }});
      window._session = session;
      if (document.body.dataset.surface === 'sidepanel') {{
        const client = await session.createSidePanelClient();
        window._panel = client;
        banner.textContent = 'Connected to Meet — side panel active.';
        const btn = document.getElementById('to-stage');
        if (btn) btn.onclick = async () => {{
          await client.startActivity(
            {{ mainStageUrl: ORIGIN + '/addon/mainstage' }});
        }};
      }} else {{
        await session.createMainStageClient();
        banner.textContent = 'Connected to Meet — main stage active.';
      }}
    }} catch (e) {{
      banner.textContent = 'Meet add-on init error: ' + e;
    }}
  }}
  window.addEventListener('load', boot);
</script>
"""


def _page(surface, title, body, embed_qs=''):
    origin = _origin()
    boot = _BOOT.format(sdk=SDK_SRC, project=PROJECT_NUMBER, origin=origin)
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SDI Lab Cloud — {title} | Xenith Brand Labs</title>
<style>
  html,body{{margin:0;height:100%;font-family:Calibri,Segoe UI,sans-serif;
    background:#F0F4F8;color:#1A202C}}
  .bar{{background:{NAVY};color:#fff;padding:8px 14px;font-weight:700;
    font-size:14px;display:flex;justify-content:space-between;
    align-items:center}}
  .badge{{background:{TEAL};color:#fff;border-radius:10px;
    padding:2px 10px;font-size:11px;font-weight:700}}
  #meet-banner{{background:#E3EDF9;color:#0B2E59;font-size:12px;
    padding:5px 14px}}
  iframe{{border:0;width:100%;height:calc(100% - 78px)}}
  button{{background:{ORANGE};color:#fff;border:0;border-radius:4px;
    padding:7px 12px;font-weight:700;cursor:pointer}}
</style></head>
<body data-surface="{surface}">
  <div class="bar">
    <span>SDI Lab Cloud — {title} | Xenith Brand Labs</span>
    {body}
  </div>
  <div id="meet-banner">loading Meet add-on…</div>
  <iframe src="{origin}/{embed_qs}" title="dashboard"></iframe>
  {boot}
</body></html>"""


def register(server):
    """Attach the Meet Add-on routes to the Dash Flask server."""

    @server.route('/addon/sidepanel')
    def addon_sidepanel():
        body = ('<button id="to-stage">Show live signal on main stage'
                '</button>')
        # side panel embeds the full dashboard (roster/queue/snippet
        # are usable in the narrow column)
        return Response(_page('sidepanel', 'Trainer Panel', body),
                        mimetype='text/html')

    @server.route('/addon/mainstage')
    def addon_mainstage():
        body = '<span class="badge">LIVE SIGNAL</span>'
        # main stage embeds the dashboard focused on the signal view
        return Response(_page('mainstage', 'Live Signal', body,
                              embed_qs='?view=signal'),
                        mimetype='text/html')

    @server.route('/addon/manifest')
    def addon_manifest():
        origin = _origin()
        import json
        manifest = {
            '_comment': 'Paste these values into the Google Workspace '
                        'Marketplace SDK → Meet Add-on config (free, '
                        'unlisted). Replace cloudProjectNumber with your '
                        'GCP project NUMBER.',
            'cloudProjectNumber': PROJECT_NUMBER,
            'sdkVersion': SDK_VERSION,
            'meetAddOn': {
                'supportsCollaboration': True,
                'sidePanelUri': f'{origin}/addon/sidepanel',
                'mainStageUri': f'{origin}/addon/mainstage',
                'addOnOrigins': [origin],
            },
            'oauthScopes': [
                'https://www.googleapis.com/auth/meetings.space.created',
            ],
        }
        return Response(json.dumps(manifest, indent=2),
                        mimetype='application/json')

    return server
