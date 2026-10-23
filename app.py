from flask import Flask, request, Response
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib
import json
import time
import base64
import os
import requests

app = Flask(__name__)

# ==========================================
# CONFIGURATION
# ==========================================
PASSPHRASE = 'FVM-HACKER98'
MAX_TS_DIFF = 30 # seconds

# Derive 32-byte key from passphrase
KEY = hashlib.sha256(PASSPHRASE.encode('utf-8')).digest()

# In-memory storage for period locking
# Format: { "period_number": { "number": "7", "size": "BIG", "color": "GREEN" } }
PERIOD_CACHE = {}

def send_error(msg, code=400):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Access Denied</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background:#FCFBF4; color:#1E2022; font-family:-apple-system, sans-serif; 
               min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }}
        .card {{ max-width:420px; width:100%; padding:48px 36px; background:#FFFFF0; 
                border-radius:20px; border:1px solid rgba(63,78,79,.12); 
                box-shadow:0 20px 60px rgba(30,32,34,.08); text-align:center; }}
        .icon {{ width:56px; height:56px; margin:0 auto 24px; border-radius:50%; 
                background:#FCFBF4; border:1.5px solid rgba(63,78,79,.15); 
                display:flex; align-items:center; justify-content:center; font-size:24px; color:#3F4E4F; }}
        h1 {{ font-size:20px; font-weight:600; margin-bottom:10px; color:#1E2022; }}
        p {{ font-size:14px; color:rgba(30,32,34,.55); }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✕</div>
        <h1>Access Denied</h1>
        <p>{msg}</p>
    </div>
</body>
</html>"""
    return Response(html, status=code, mimetype='text/html')

@app.route('/', methods=['GET', 'POST'])
def main():
    # 1. Force POST
    if request.method != 'POST':
        return send_error("POST required")

    try:
        data = request.get_json()
        if not data or 'iv' not in data or 'cipher' not in data or 'tag' not in data:
            return send_error("Bad encrypted request")

        # Decode base64
        iv = base64.b64decode(data['iv'])
        ciphertext = base64.b64decode(data['cipher'])
        tag = base64.b64decode(data['tag'])

        # Reconstruct combined ciphertext + tag for AESGCM
        combined = ciphertext + tag

        # Decrypt
        aesgcm = AESGCM(KEY)
        try:
            plaintext_bytes = aesgcm.decrypt(iv, combined, None)
            plaintext = plaintext_bytes.decode('utf-8')
        except Exception:
            return send_error("Decryption failed. Passphrase mismatch?")

        # Parse decrypted JSON
        payload = json.loads(plaintext)
        if payload.get('action') != "LOAD":
            return send_error("Invalid action")
        
        if abs(time.time() - int(payload.get('ts', 0))) > MAX_TS_DIFF:
            return send_error("Request expired")

        # ==========================================
        # FETCH PERIOD & LOCK RESULT LOGIC
        # ==========================================
        current_period = "UNKNOWN"
        try:
            api_resp = requests.post(
                "https://api.bdg88zf.com/api/webapi/GetGameIssue",
                json={
                    "typeId": 1, "language": 0,
                    "random": "40079dcba93a48769c6ee9d4d4fae23f",
                    "signature": "D12108C4F57C549D82B23A91E0FA20AE",
                    "timestamp": 1727792520
                },
                timeout=5
            )
            api_data = api_resp.json()
            if api_data.get('code') == 0 and api_data.get('data'):
                current_period = str(api_data['data'].get('issueNumber', 'UNKNOWN'))
        except Exception:
            pass # If API fails, use UNKNOWN

        # If period is new or not in cache, generate a new result
        if current_period not in PERIOD_CACHE:
            LOGIC = {
                0: {'n': '5', 's': 'BIG'}, 1: {'n': '2', 's': 'SMALL'},
                2: {'n': '4', 's': 'SMALL'}, 3: {'n': '7', 's': 'BIG'},
                4: {'n': '8', 's': 'BIG'}, 5: {'n': '9', 's': 'BIG'},
                6: {'n': '0', 's': 'SMALL'}, 7: {'n': '3', 's': 'SMALL'},
                8: {'n': '6', 's': 'BIG'}, 9: {'n': '1', 's': 'SMALL'}
            }
            import random
            k = random.choice(list(LOGIC.keys()))
            res = LOGIC[k]
            
            PERIOD_CACHE[current_period] = {
                'period': current_period,
                'number': res['n'],
                'size': res['s'],
                'color': 'GREEN' if res['s'] == 'BIG' else 'RED'
            }

        locked_result = PERIOD_CACHE[current_period]

        # ==========================================
        # RETURN HTML
        # ==========================================
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"/>
<title>𝑪𝑹𝑨𝑽𝑨𝑼𝑳𝑻 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑨𝑰 ™</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet"/>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; -webkit-font-smoothing:antialiased; }}
:root {{
  --bg:#FCFBF4; --surface:#FFFFF0; --ink:#1E2022; --accent:#3F4E4F;
  --muted:rgba(30,32,34,.48); --line:rgba(63,78,79,.14);
  --green:#3F4E4F; --red:#B85C4A;
}}
body {{
  background:var(--bg); color:var(--ink); font-family:'Inter', system-ui, sans-serif;
  min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px;
  position:relative; overflow:hidden;
}}
body::before {{
  content:''; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.025;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}}
body::after {{
  content:''; position:fixed; top:-20%; left:50%; transform:translateX(-50%);
  width:120%; height:60%; z-index:0; pointer-events:none;
  background:radial-gradient(ellipse at 50% 0%, rgba(63,78,79,.04), transparent 70%);
}}
.card {{
  position:relative; z-index:10; width:100%; max-width:380px;
  background:var(--surface); border-radius:24px; border:1px solid var(--line);
  box-shadow:0 30px 80px rgba(30,32,34,.07), 0 8px 24px rgba(30,32,34,.04), inset 0 1px 0 rgba(255,255,255,.6);
  padding:40px 32px 32px; overflow:hidden;
}}
.card::before {{
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg, transparent, var(--accent), transparent); opacity:.35;
}}
.brand {{ text-align:center; margin-bottom:32px; }}
.brand-mark {{
  width:52px; height:52px; margin:0 auto 18px; border-radius:16px;
  background:var(--surface); border:1.5px solid var(--line);
  display:flex; align-items:center; justify-content:center; position:relative;
}}
.brand-mark::after {{ content:''; position:absolute; inset:5px; border-radius:11px; border:1px solid var(--line); opacity:.5; }}
.brand-mark span {{ font-family:'Playfair Display', serif; font-size:24px; font-weight:700; color:var(--accent); position:relative; z-index:1; }}
.brand-name {{ font-family:'Playfair Display', serif; font-size:16px; font-weight:600; letter-spacing:.5px; color:var(--ink); line-height:1.4; }}
.brand-name .tm {{ font-family:'Inter', sans-serif; font-size:9px; font-weight:500; vertical-align:super; color:var(--muted); }}
.brand-sub {{ font-size:10px; font-weight:500; letter-spacing:2.5px; text-transform:uppercase; color:var(--muted); margin-top:8px; }}
.status-row {{
  display:flex; align-items:center; justify-content:space-between; padding:10px 14px;
  background:var(--bg); border:1px solid var(--line); border-radius:10px;
  margin-bottom:28px; font-size:10px; font-weight:500; letter-spacing:.6px; color:var(--muted);
}}
.status-left {{ display:flex; align-items:center; gap:7px; }}
.dot {{ width:6px; height:6px; border-radius:50%; background:var(--accent); animation:pulseDot 2s infinite; }}
@keyframes pulseDot {{ 0%{{box-shadow:0 0 0 0 rgba(63,78,79,.35);}} 70%{{box-shadow:0 0 0 6px rgba(63,78,79,0);}} 100%{{box-shadow:0 0 0 0 rgba(63,78,79,0);}} }}
.status-online {{ color:var(--accent); font-weight:600; }}
.clock {{ font-family:monospace; font-size:10px; opacity:.55; }}
.prediction {{
  background:var(--bg); border:1px solid var(--line); border-radius:16px;
  padding:24px 20px 20px; margin-bottom:24px; text-align:center; position:relative;
}}
.prediction::before {{ content:''; position:absolute; top:0; left:20%; right:20%; height:1.5px; background:linear-gradient(90deg, transparent, var(--accent), transparent); opacity:.5; }}
.period-label {{ font-size:9.5px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--muted); margin-bottom:4px; }}
.period-value {{ font-family:'Playfair Display', serif; font-size:22px; font-weight:600; color:var(--ink); letter-spacing:1px; margin-bottom:22px; }}
.number-stage {{ display:flex; align-items:center; justify-content:center; gap:16px; margin-bottom:20px; }}
.num-arrow {{ font-size:12px; color:var(--accent); opacity:.4; letter-spacing:-1px; }}
.num-main {{
  width:92px; height:92px; border-radius:50%; background:var(--surface); border:2px solid var(--accent);
  display:flex; align-items:center; justify-content:center;
  box-shadow:0 8px 28px rgba(63,78,79,.12), inset 0 2px 6px rgba(255,255,255,.6);
  transition:transform .3s cubic-bezier(.34,1.56,.64,1);
}}
.num-main::after {{ content:''; position:absolute; inset:6px; border-radius:50%; border:1px solid var(--line); }}
.num-main span {{ font-family:'Playfair Display', serif; font-size:40px; font-weight:700; color:var(--accent); line-height:1; }}
.num-main.pop {{ animation:numPop .45s cubic-bezier(.34,1.56,.64,1); }}
@keyframes numPop {{ 0%{{transform:scale(1);}} 50%{{transform:scale(1.08);}} 100%{{transform:scale(1);}} }}
.result-row {{ display:flex; justify-content:center; gap:10px; }}
.pill {{
  display:flex; align-items:center; gap:6px; padding:7px 16px;
  border-radius:20px; font-size:11px; font-weight:600; letter-spacing:1px;
  text-transform:uppercase; border:1px solid var(--line); background:var(--surface);
  transition:all .3s ease;
}}
.pill .pdot {{ width:6px; height:6px; border-radius:50%; background:currentColor; }}
.pill.big {{ color:var(--green); border-color:rgba(63,78,79,.3); }}
.pill.small {{ color:var(--red); border-color:rgba(184,92,74,.3); }}
.btn-row {{ display:flex; gap:12px; }}
.btn {{
  flex:1; padding:14px 0; border-radius:12px; font-family:'Inter', sans-serif;
  font-size:12px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase;
  border:none; cursor:pointer; transition:transform .15s ease, box-shadow .25s ease, background .25s ease;
}}
.btn:active {{ transform:scale(.97); }}
.btn-primary {{ background:var(--accent); color:var(--surface); box-shadow:0 8px 24px rgba(63,78,79,.25); }}
.btn-primary:hover {{ background:#354143; box-shadow:0 12px 32px rgba(63,78,79,.35); }}
.btn-secondary {{ background:var(--surface); color:var(--accent); border:1.5px solid var(--line); }}
.btn-secondary:hover {{ background:var(--bg); border-color:rgba(63,78,79,.3); }}
.footer {{
  text-align:center; margin-top:28px; padding-top:20px; border-top:1px solid var(--line);
  font-size:9px; font-weight:500; letter-spacing:1.8px; text-transform:uppercase; color:var(--muted);
}}
.footer strong {{ color:var(--accent); font-weight:600; }}
</style>
</head>
<body>
<div class="card">
  <div class="brand">
    <div class="brand-mark"><span>C</span></div>
    <div class="brand-name">𝑪𝑹𝑨𝑽𝑨𝑼𝑳𝑻 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑨𝑰<span class="tm">™</span></div>
    <div class="brand-sub">Intelligence Engine</div>
  </div>
  <div class="status-row">
    <div class="status-left"><span class="dot"></span><span>Secure Link</span></div>
    <div>Status <span class="status-online">Online</span></div>
    <div class="clock" id="clock">--:--:--</div>
  </div>
  <div class="prediction">
    <div class="period-label">Current Period</div>
    <div class="period-value" id="periodVal">{locked_result['period'][-5:]}</div>
    <div class="number-stage">
      <span class="num-arrow">‹‹</span>
      <div class="num-main pop"><span>{locked_result['number']}</span></div>
      <span class="num-arrow">››</span>
    </div>
    <div class="result-row">
      <div class="pill {'big' if locked_result['size']=='BIG' else 'small'}">
        <span class="pdot"></span><span>{locked_result['size']}</span>
      </div>
      <div class="pill {'big' if locked_result['size']=='BIG' else 'small'}">
        <span class="pdot"></span><span>{locked_result['color']}</span>
      </div>
    </div>
  </div>
  <div class="footer">2026 <strong>𝑪𝑹𝑨𝑽𝑨𝑼𝑳𝑻 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑨𝑰 ™</strong> · All Rights Reserved</div>
</div>
<script>
  function tick() {{
    var n = new Date();
    document.getElementById('clock').textContent = 
      String(n.getHours()).padStart(2,'0') + ':' + 
      String(n.getMinutes()).padStart(2,'0') + ':' + 
      String(n.getSeconds()).padStart(2,'0');
  }}
  setInterval(tick, 1000); tick();
</script>
</body>
</html>"""
        return Response(html, mimetype='text/html')

    except Exception as e:
        return send_error(f"Server Error: {str(e)}", 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)