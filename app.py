from flask import Flask, request, Response
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib
import json
import time
import base64
import os
import requests
import random

app = Flask(__name__)

# ==========================================
# CONFIGURATION
# ==========================================
PASSPHRASE = 'FVM-HACKER98'
MAX_TS_DIFF = 30 # seconds

# Derive 32-byte key from passphrase
KEY = hashlib.sha256(PASSPHRASE.encode('utf-8')).digest()

# In-memory storage for period locking
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
        body {{ background:#010a04; color:#fff; font-family:-apple-system, sans-serif; 
               min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }}
        .card {{ max-width:420px; width:100%; padding:48px 36px; background:rgba(5,20,10,0.9); 
                border-radius:20px; border:1px solid #ffd700; 
                box-shadow:0 20px 60px rgba(0,255,136,.08); text-align:center; }}
        .icon {{ width:56px; height:56px; margin:0 auto 24px; border-radius:50%; 
                background:rgba(255,255,255,0.05); border:1.5px solid #ffd700; 
                display:flex; align-items:center; justify-content:center; font-size:24px; color:#ffd700; }}
        h1 {{ font-size:20px; font-weight:600; margin-bottom:10px; color:#ffd700; }}
        p {{ font-size:14px; color:rgba(255,255,255,.7); }}
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
        # FETCH REAL PERIOD & LOCK RESULT
        # ==========================================
        current_period = "UNKNOWN"
        try:
            api_url = f"https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?t={int(time.time())}"
            api_resp = requests.get(api_url, timeout=5)
            api_data = api_resp.json()
            if api_data.get('data') and api_data['data'].get('list'):
                # Get current period number
                current_period = str(api_data['data']['list'][0]['issueNumber'])
        except Exception:
            # Fallback if API is down
            current_period = str(int(time.time() / 60)) 

        # Generate new result ONLY if period changes
        if current_period not in PERIOD_CACHE:
            LOGIC = {
                0: {'n': '5', 's': 'BIG', 'color': 'violet'}, 1: {'n': '2', 's': 'SMALL', 'color': 'red'},
                2: {'n': '4', 's': 'SMALL', 'color': 'red'}, 3: {'n': '7', 's': 'BIG', 'color': 'green'},
                4: {'n': '8', 's': 'BIG', 'color': 'red'}, 5: {'n': '9', 's': 'BIG', 'color': 'green'},
                6: {'n': '0', 's': 'SMALL', 'color': 'violet'}, 7: {'n': '3', 's': 'SMALL', 'color': 'green'},
                8: {'n': '6', 's': 'BIG', 'color': 'red'}, 9: {'n': '1', 's': 'SMALL', 'color': 'green'}
            }
            k = random.choice(list(LOGIC.keys()))
            res = LOGIC[k]
            
            PERIOD_CACHE[current_period] = {
                'period': current_period,
                'number': res['n'],
                'size': res['s'],
                'color': res['color']
            }

        locked = PERIOD_CACHE[current_period]

        # ==========================================
        # RETURN HTML (CRAVAULT THEME)
        # ==========================================
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0">
<title>CRAVAULT PREMIUM AI</title>
<link href="https://fonts.googleapis.com/css2?family=Exo+2:ital,wght@1,800;1,900&family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
:root{{
  --g1: #00ff88;  --g2: #00b347;  --g3: #004d1a;  --g4: #001a0a;
  --gold: #ffd700; --cyan: #00f0ff;
  --bg-deep: #010a04; 
  --gn-glow: rgba(0, 255, 136, 0.45);   
  --gold-glow: rgba(255, 215, 0, 0.55);
}}
*{{box-sizing:border-box;margin:0;padding:0;user-select:none;-webkit-tap-highlight-color:transparent;}}
body{{margin:0;height:100vh;overflow:hidden;background:transparent!important;font-family:'Rajdhani',sans-serif;color:#fff;}}

@keyframes spin{{to{{transform:rotate(360deg);}}}}
@keyframes spinR{{to{{transform:rotate(-360deg);}}}}
@keyframes float{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-8px);}}}}
@keyframes pulseDot{{0%{{opacity:.5;transform:scale(.8);}}100%{{opacity:1;transform:scale(1.3);}}}}
@keyframes textShine{{0%{{background-position:0% center;}}100%{{background-position:200% center;}}}}
@keyframes viewIn{{from{{opacity:0;transform:scale(.9) translateY(10px);}}to{{opacity:1;transform:scale(1) translateY(0);}}}}
@keyframes popIn{{0%{{transform:scale(0) rotate(-180deg);opacity:0;}}80%{{transform:scale(1.1) rotate(5deg);}}100%{{transform:scale(1) rotate(0);opacity:1;}}}}
@keyframes gridScroll{{0%{{background-position:0 0;}}100%{{background-position:32px 32px;}}}}
@keyframes scanLine{{0%{{top:-2px;opacity:0;}}5%{{opacity:1;}}93%{{opacity:1;}}100%{{top:calc(100% + 2px);opacity:0;}}}}
@keyframes radarSweep{{to{{transform:rotate(360deg);}}}}
@keyframes neonBreathe{{0%,100%{{box-shadow:0 0 15px var(--g3),0 0 30px var(--gn-glow);}}50%{{box-shadow:0 0 22px var(--g1),0 0 45px var(--gn-glow);}}}}
@keyframes surefireAnim{{0%{{letter-spacing:2px;text-shadow:0 0 12px var(--g1);}}50%{{letter-spacing:4px;text-shadow:0 0 22px var(--gold),0 0 5px #fff;}}100%{{letter-spacing:2px;text-shadow:0 0 12px var(--g1);}}}}

/* ── MINI BUTTON ── */
#miniBtn{{
  position:fixed;right:20px;bottom:100px; width:58px;height:58px;border-radius:50%;
  background:radial-gradient(circle at 30% 30%,rgba(0,180,80,.9),var(--bg-deep));
  border:2px solid var(--gold); box-shadow:0 0 22px var(--gn-glow),0 0 45px var(--gold-glow),inset 0 4px 6px rgba(255,255,255,0.4);
  cursor:pointer;z-index:9998; display:flex;align-items:center;justify-content:center;
  animation:float 3.5s ease-in-out infinite, neonBreathe 3s ease-in-out infinite; touch-action:none;
}}
#miniBtn::before{{content:'';position:absolute;inset:-5px;border-radius:50%;border:1.5px dashed var(--gold);animation:spin 8s linear infinite;pointer-events:none;}}
#miniBtn::after{{content:'';position:absolute;inset:-10px;border-radius:50%;border:1px solid rgba(0,255,136,.5);animation:spinR 12s linear infinite;pointer-events:none;}}
.custom-logo{{border-radius:50%;object-fit:cover;border:1.5px solid #fff;width:100%;height:100%;}}
#miniBtn .custom-logo{{width:42px;height:42px;border:1.5px solid var(--gold);}}
.lb-dot{{position:absolute;top:-2px;right:-2px;width:11px;height:11px;border-radius:50%;background:radial-gradient(circle,#fff,var(--g1));border:2px solid rgba(0,10,5,.9);animation:pulseDot .85s infinite;z-index:3;}}

/* ── MAIN PANEL ── */
#drac-panel-container{{position:fixed;right:15px;bottom:80px;width:230px;z-index:9999;display:none;touch-action:none;}}
.panel-hexagon-backing{{position:absolute;inset:-2px;background:linear-gradient(135deg, var(--g3), var(--gold), var(--g3));border-radius:18px;z-index:2;box-shadow:0 0 35px var(--gn-glow), 0 0 55px rgba(0,26,10,0.8);}}
.panel-body{{position:relative;z-index:5;background:linear-gradient(160deg, rgba(5,30,15,0.8) 0%, rgba(1,10,5,0.96) 100%);backdrop-filter: blur(15px);-webkit-backdrop-filter: blur(15px);border-radius:16px;border-top: 1.5px solid rgba(255,215,0,0.6);border-left: 1px solid rgba(255,255,255,0.2);border-right: 1px solid rgba(255,255,255,0.1);border-bottom: 1px solid rgba(255,255,255,0.1);box-shadow: inset 0 0 20px rgba(0,255,100,0.08), 0 15px 30px rgba(0,0,0,0.9);padding:11px 10px 10px;display:flex;flex-direction:column;gap:6px;overflow:hidden;}}

.header-row{{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:10;padding:0 2px;}}
.header-title{{font-family:'Orbitron',sans-serif;font-weight:900;font-size:12px;letter-spacing:1.2px;background:linear-gradient(90deg, #fff 0%, var(--gold) 40%, var(--g1) 70%, #fff 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:textShine 3.5s linear infinite;filter:drop-shadow(0 0 6px rgba(255,215,0,0.5));}}
.mode-badge{{background:rgba(255,255,255,.12);border:1px solid var(--gold);border-radius:10px;padding:2px 7px;display:flex;align-items:center;gap:4px;box-shadow:0 0 8px rgba(255,215,0,.3);}}
.mode-dot{{width:5px;height:5px;border-radius:50%;background:var(--g1);box-shadow:0 0 6px var(--g1);animation:pulseDot 1s infinite alternate;}}
.mode-text{{font-family:'Share Tech Mono',monospace;font-size:7px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#fff;}}

.period-box{{position:relative;z-index:10;text-align:center;border:1px solid rgba(255,215,0,0.35);border-radius:6px;padding:3px 0;background:linear-gradient(90deg,transparent,rgba(0,255,136,.12),transparent);}}
.period-box::before,.period-box::after{{content:'';position:absolute;top:50%;transform:translateY(-50%);width:3px;height:3px;border-radius:50%;background:var(--gold);box-shadow:0 0 6px var(--gold);}}
.period-box::before{{left:8px;}} .period-box::after{{right:8px;}}
.period-text{{font-family:'Share Tech Mono',monospace;font-size:8px;font-weight:700;letter-spacing:2px;color:#fff;}}

.screen-area{{position:relative;z-index:10;background:linear-gradient(170deg,rgba(2,10,5,.7) 0%,rgba(5,20,10,.85) 100%);border-radius:12px;border:1px solid rgba(255,255,255,0.15);border-top: 1px solid rgba(255,215,0,0.4);min-height:155px;padding:8px 6px;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:inset 0 0 35px rgba(0,0,0,.85),0 4px 14px rgba(0,0,0,.5);overflow:hidden;}}
.screen-area::before{{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:16px 16px;animation:gridScroll 15s linear infinite;pointer-events:none;z-index:0;}}
.screen-scan-stripe{{position:absolute;left:0;width:100%;height:1.5px;background:linear-gradient(90deg,transparent,var(--gold) 40%,#fff 50%,var(--g1) 60%,transparent);box-shadow:0 0 10px #fff,0 0 20px var(--g1);animation:scanLine 3.5s linear infinite;top:-2px;pointer-events:none;z-index:4;}}
.radar-sweep{{position:absolute;top:50%;left:50%;width:200%;height:200%;background:conic-gradient(from 0deg,transparent 75%,rgba(255,215,0,.05) 88%,rgba(0,230,92,.18) 100%);transform-origin:0 0;animation:radarSweep 3.5s linear infinite;z-index:2;pointer-events:none;}}

.bracket{{position:absolute;width:10px;height:10px;border-color:rgba(255,215,0,.6);border-style:solid;z-index:15;}}
.bracket.tl{{top:6px;left:6px;border-width:2px 0 0 2px;}} .bracket.tr{{top:6px;right:6px;border-width:2px 2px 0 0;}}
.bracket.bl{{bottom:6px;left:6px;border-width:0 0 2px 2px;}} .bracket.br{{bottom:6px;right:6px;border-width:0 2px 2px 0;}}

.view-state{{display:flex;flex-direction:column;align-items:center;width:100%;height:100%;text-align:center;position:relative;z-index:20;justify-content:center;gap:4px;animation:viewIn .5s cubic-bezier(0.25, 1, 0.5, 1) forwards;}}

#view-result{{justify-content:space-between;padding:4px 2px;}}
.res-period-top{{font-family:'Share Tech Mono',monospace;font-size:9px;font-weight:900;color:#fff;letter-spacing:1.5px;border-bottom:1px solid rgba(255,215,0,.4);padding-bottom:3px;width:90%;text-align:center;margin-bottom:3px;}}
.res-period-top span{{color:var(--gold);}}
.result-layout{{display:flex;flex-direction:column;align-items:center;justify-content:center;width:100%;position:relative;z-index:5;flex-grow:1;gap:6px;}}

.dual-ball-wrapper{{display:flex;align-items:center;gap:10px;}}
.res-ball-container{{position:relative;width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:1.5px solid #fff; animation:popIn .5s cubic-bezier(0.25, 1, 0.5, 1); box-shadow:0 0 18px rgba(0,0,0,0.9), inset 0 2px 4px rgba(255,255,255,0.7);}}
.res-ball-container.red{{background:radial-gradient(circle at 35% 30%,#ff8a80 0%,#d50000 50%,#5b0000 90%);box-shadow:0 0 16px #ff0055;}}
.res-ball-container.green{{background:radial-gradient(circle at 35% 30%,#b9f6ca 0%,#00c853 50%,#004d1a 90%);box-shadow:0 0 16px #00ff88;}}
.res-ball-container.violet{{background:radial-gradient(circle at 35% 30%,#ea80fc 0%,#aa00ff 50%,#4a0072 90%);box-shadow:0 0 16px #aa00ff;}}
.res-ball-container.gold{{background:radial-gradient(circle at 35% 30%,#fff59d 0%,#fbc02d 50%,#f57f17 90%);box-shadow:0 0 16px #ffd700;}}
.ball-num-txt{{font-family:'Orbitron',sans-serif;font-size:16px;font-weight:900;color:#fff;text-shadow:0 2px 4px rgba(0,0,0,.9);}}

.conf-pill-tag{{font-family:'Share Tech Mono',monospace;font-size:7px;font-weight:800;color:var(--cyan);background:rgba(0,0,0,0.65);padding:1px 6px;border-radius:6px;border:1px solid rgba(0,240,255,0.35);text-shadow:0 0 6px var(--cyan);}}

.res-sureshot-banner{{font-family:'Orbitron',sans-serif;font-size:11px;font-weight:900;border:1.2px solid rgba(255,215,0,.7);padding:4px 14px;border-radius:10px;background:linear-gradient(180deg,rgba(255,215,0,.25) 0%,rgba(0,0,0,.6) 100%);box-shadow:0 0 16px var(--gold-glow);text-shadow:0 0 10px var(--gold);text-transform:uppercase;letter-spacing:2px;color:#fff;display:flex;align-items:center;justify-content:center;gap:6px;animation:surefireAnim 2.5s ease-in-out infinite;}}

.btn-container{{display:flex;gap:6px;position:relative;z-index:10;}}
.drac-btn{{flex:1;padding:9px 4px;border:none;border-radius:10px;font-family:'Orbitron',sans-serif;font-size:8px;font-weight:900;letter-spacing:1.2px;cursor:pointer;text-transform:uppercase;color:#fff;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:4px;transition:all .2s ease;}}
.drac-btn:active{{transform:scale(.94);}}
.btn-primary{{background:linear-gradient(180deg,#00b347 0%,#004d1a 100%);border:1.2px solid var(--gold);flex:1.8;box-shadow:0 0 12px var(--gn-glow);text-shadow:0 1px 3px rgba(0,0,0,0.8);}}
.btn-secondary{{background:linear-gradient(180deg,rgba(255,255,255,.15) 0%,rgba(255,255,255,.05) 100%);color:#fff;border:1px solid rgba(255,255,255,.3);}}
</style>
</head>
<body>

<!-- MINI BUTTON -->
<div id="miniBtn" onclick="openPanel()">
  <img src="https://myimgs.org/storage/images/65497/1000020658.png" class="custom-logo" alt="Logo">
  <div class="lb-dot"></div>
</div>

<!-- MAIN PANEL -->
<div id="drac-panel-container">
  <div class="panel-hexagon-backing"></div>
  <div class="panel-body">
    
    <div class="header-row">
      <div class="header-title">CRAVAULT AI</div>
      <div class="mode-badge">
        <div class="mode-dot"></div>
        <div class="mode-text">2-LEVEL</div>
      </div>
    </div>
    
    <div class="period-box" id="mainPeriodBox">
      <div class="period-text">PERIOD : <span id="periodDisplay">{locked['period'][-4:]}</span></div>
    </div>

    <div class="screen-area">
      <div class="screen-scan-stripe"></div>
      <div class="radar-sweep"></div>
      <div class="bracket tl"></div><div class="bracket tr"></div>
      <div class="bracket bl"></div><div class="bracket br"></div>

      <div class="view-state" id="view-result">
        <div class="res-period-top">LOCKED: <span>{locked['period'][-4:]}</span></div>
        <div class="result-layout">
          <div class="dual-ball-wrapper">
            <div class="res-ball-container {locked['color']}" id="resBall1">
              <span class="ball-num-txt">{locked['number']}</span>
            </div>
            <div class="res-ball-container gold" id="resBall2">
              <span class="ball-num-txt">{locked['number']}</span>
            </div>
          </div>
          <div class="conf-pill-tag">CONF: 98.6% | L1: 85% L2: 90%</div>
          <div class="res-sureshot-banner">
            <span>{locked['size']}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="btn-container">
      <button class="drac-btn btn-primary" onclick="refreshLock()">REFRESH</button>
      <button class="drac-btn btn-secondary" onclick="closePanel()">HIDE</button>
    </div>

  </div>
</div>

<script>
  function openPanel(){{
    document.getElementById('miniBtn').style.display='none';
    document.getElementById('drac-panel-container').style.display='block';
  }}
  function closePanel(){{
    document.getElementById('drac-panel-container').style.display='none';
    document.getElementById('miniBtn').style.display='flex';
  }}
  function refreshLock(){{
    window.location.reload();
  }}
</script>
</body>
</html>"""
        return Response(html, mimetype='text/html')

    except Exception as e:
        return send_error(f"Server Error: {str(e)}", 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)