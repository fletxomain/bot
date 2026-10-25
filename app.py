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
PASSPHRASE = os.environ.get('FVM_PASSPHRASE', 'FVM-HACKER98')
MAX_TS_DIFF = 30 
KEY = hashlib.sha256(PASSPHRASE.encode('utf-8')).digest()

# This dictionary permanently stores the result for a period
PERIOD_LOCK = {}

def send_error(msg, code=400):
    return Response(f"Error: {msg}", status=code, mimetype='text/plain')

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method != 'POST':
        return send_error("POST required")

    try:
        data = request.get_json()
        if not data or 'iv' not in data:
            return send_error("Bad request")

        iv = base64.b64decode(data['iv'])
        ciphertext = base64.b64decode(data['cipher'])
        tag = base64.b64decode(data['tag'])
        
        aesgcm = AESGCM(KEY)
        try:
            plaintext = aesgcm.decrypt(iv, ciphertext + tag, None).decode('utf-8')
        except Exception:
            return send_error("Decryption failed")

        payload = json.loads(plaintext)
        if payload.get('action') != "LOAD":
            return send_error("Invalid action")

        # ==========================================
        # FETCH PERIOD FROM API (With Fallback)
        # ==========================================
        current_period = None
        try:
            api_url = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://www.ar-lottery01.com/',
                'Origin': 'https://www.ar-lottery01.com'
            }
            # Adding a time parameter prevents caching
            api_res = requests.get(f"{api_url}?t={int(time.time()*1000)}", headers=headers, timeout=5).json()
            
            if api_res.get('data') and api_res['data'].get('list'):
                latest_issue = api_res['data']['list'][0]['issueNumber']
                # The current period is usually the latest + 1
                current_period = str(int(latest_issue) + 1)[-3:] 
        except Exception as e:
            print("API Error:", e)
            
        # If API fails, generate a fallback period based on time
        if not current_period:
            current_period = str(int(time.time() / 60) % 1000).zfill(3)

        # ==========================================
        # ONE PERIOD = ONE RESULT
        # ==========================================
        if current_period not in PERIOD_LOCK:
            # Generate new result ONLY if period doesn't exist
            size = "BIG" if random.random() > 0.5 else "SMALL"
            
            if size == "BIG":
                pool = [5, 6, 7, 8, 9]
            else:
                pool = [0, 1, 2, 3, 4]
                
            # Pick 2 unique numbers
            n1, n2 = random.sample(pool, 2)
            
            c1 = 'violet' if n1 in [0,5] else ('green' if size=='BIG' else 'red')
            c2 = 'violet' if n2 in [0,5] else ('green' if size=='BIG' else 'red')
            
            PERIOD_LOCK[current_period] = {
                'size': size,
                'n1': n1,
                'n2': n2,
                'c1': c1,
                'c2': c2
            }
            
        locked_result = PERIOD_LOCK[current_period]

        # ==========================================
        # HTML UI (COMPACT RED NEON + JARVIS ANIMATION)
        # ==========================================
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>CRAVAULT</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
<style>
:root {{ 
    --red: #ff2a2a; --dark-red: #800000; --bg: #0a0101; 
    --gold: #ffd700; --cyan: #00f0ff; 
}}
* {{ margin:0; padding:0; box-sizing:border-box; user-select:none; -webkit-tap-highlight-color:transparent; }}
body {{ width:210px; background:transparent!important; font-family:'Rajdhani',sans-serif; color:#fff; overflow:hidden; display:flex; justify-content:center; }}

/* ANIMATIONS */
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes popIn {{ 0% {{ transform:scale(0); }} 80% {{ transform:scale(1.1); }} 100% {{ transform:scale(1); }} }}
@keyframes barPulse {{ 0%,100% {{ height:4px; opacity:.3; }} 50% {{ height:100%; opacity:1; }} }}
@keyframes flash {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.5; }} }}
@keyframes gridMove {{ 0% {{ background-position: 0 0; }} 100% {{ background-position: 16px 16px; }} }}

/* JARVIS ANIMATION FIXED (Using explicit class and transform) */
@keyframes jarvisExpand {{
    0% {{ opacity: 0; transform: scale(0.6) rotate(-15deg); filter: brightness(3); }}
    50% {{ opacity: 1; transform: scale(1.05) rotate(5deg); filter: brightness(1.5); }}
    100% {{ opacity: 1; transform: scale(1) rotate(0deg); filter: brightness(1); }}
}}

.panel-wrapper {{
    position: relative;
    animation: jarvisExpand 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}}

.jarvis-ring {{
    position: absolute; inset: -4px; border-radius: 14px;
    border: 2px solid transparent; border-top-color: var(--cyan); border-bottom-color: var(--red);
    animation: spin 3s linear infinite; opacity: 0.7; pointer-events: none; z-index: 1;
}}

.panel {{ 
    position:relative; background:linear-gradient(160deg, rgba(20,2,2,0.95), rgba(5,0,0,0.98)); 
    border-radius:12px; border:1px solid var(--red); 
    box-shadow:0 0 25px rgba(255,42,42,0.4), inset 0 0 20px rgba(255,0,0,0.1); 
    padding:8px; overflow:hidden; z-index: 2; width: 100%;
}}
.panel::before {{ 
    content:''; position:absolute; inset:0; 
    background-image:linear-gradient(rgba(255,42,42,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,42,42,.05) 1px,transparent 1px); 
    background-size:16px 16px; animation:gridMove 10s linear infinite; pointer-events:none; z-index:0; 
}}

.header {{ display:flex; justify-content:space-between; font-family:'Orbitron'; font-size:10px; font-weight:900; color:var(--red); border-bottom:1px solid rgba(255,42,42,0.3); padding-bottom:4px; margin-bottom:6px; position:relative; z-index:1; text-shadow: 0 0 5px rgba(255,0,0,0.5); }}
.period-box {{ text-align:center; font-family:'Rajdhani'; font-size:11px; font-weight:700; color:var(--gold); margin-bottom:6px; position:relative; z-index:1; display:flex; justify-content:center; align-items:center; gap:10px; }}
.timer {{ color: var(--cyan); font-family:'Orbitron'; font-size: 12px; text-shadow: 0 0 5px var(--cyan); }}

/* SHORTER SCREEN */
.screen {{ background:rgba(0,0,0,0.7); border:1px solid rgba(255,42,42,0.3); border-radius:8px; min-height:110px; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:6px; position:relative; z-index:1; }}

.view {{ display:none; flex-direction:column; align-items:center; width:100%; justify-content:center; height:100%; }}
.view.active {{ display:flex; animation:popIn 0.4s ease-out; }}

.scan-circle {{ width:36px; height:36px; border-radius:50%; border:2px solid transparent; border-top-color:var(--red); border-bottom-color:var(--gold); animation:spin 1s linear infinite; margin-bottom:4px; }}
.bars {{ display:flex; gap:2px; height:10px; margin-top:2px; align-items:flex-end; }}
.bar {{ width:3px; background:var(--red); animation:barPulse 0.8s infinite; border-radius:2px 2px 0 0; }}
.bar:nth-child(2) {{ animation-delay:0.1s; }} .bar:nth-child(3) {{ animation-delay:0.2s; }} .bar:nth-child(4) {{ animation-delay:0.3s; }}

.balls {{ display:flex; gap:10px; margin-bottom:6px; }}
.ball {{ 
    width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; 
    font-family:'Orbitron'; font-size:16px; font-weight:900; border:1.5px solid #fff; 
    box-shadow:0 0 15px rgba(0,0,0,0.8); animation:popIn 0.5s; 
}}
.ball.green {{ background:radial-gradient(circle at 30% 30%, #00ff88, #004d1a); box-shadow:0 0 12px #00ff88; }}
.ball.red {{ background:radial-gradient(circle at 30% 30%, #ff5e5e, #8a0000); box-shadow:0 0 12px #ff2a2a; }}
.ball.violet {{ background:radial-gradient(circle at 30% 30%, #ea80fc, #4a0072); box-shadow:0 0 12px #aa00ff; }}

.size-tag {{ 
    font-family:'Orbitron'; font-size:11px; font-weight:900; color:var(--gold); 
    border:1.5px solid var(--gold); padding:2px 14px; border-radius:6px; margin-top:4px; 
    animation:flash 2s infinite; box-shadow:0 0 10px rgba(255,215,0,0.3); 
}}

.btn {{ 
    width:100%; padding:8px; margin-top:8px; border-radius:6px; border:none; 
    font-family:'Orbitron'; font-size:9px; font-weight:900; color:#fff; 
    background:linear-gradient(180deg, #d40000, #550000); border:1px solid var(--red); 
    cursor:pointer; position:relative; z-index:1; transition:all 0.2s; box-shadow:0 0 15px rgba(255,42,42,0.3);
}}
.btn:active {{ transform:scale(0.96); }}
</style>
</head>
<body>
<div class="panel-wrapper">
  <div class="jarvis-ring"></div>
  <div class="panel">
    <div class="header"><span>CRAVAULT AI</span><span>PREMIUM</span></div>
    
    <div class="period-box">
      <span>PERIOD: <span id="dispPeriod">{current_period}</span></span>
      <span class="timer" id="timerText">01:00</span>
    </div>
    
    <div class="screen">
      <div class="view active" id="v-scan">
        <div class="scan-circle"></div>
        <div class="bars"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>
        <div style="font-size:9px; margin-top:4px; font-weight:bold; font-family:'Orbitron'; color:var(--red);">DECODING...</div>
      </div>

      <div class="view" id="v-res">
        <div style="font-size:8px; color:var(--cyan); margin-bottom:4px; font-family:'Orbitron';">LOCKED RESULT</div>
        <div class="balls">
          <div class="ball {locked_result['c1']}" id="b1">{locked_result['n1']}</div>
          <div class="ball {locked_result['c2']}" id="b2">{locked_result['n2']}</div>
        </div>
        <div class="size-tag" id="resS">{locked_result['size']}</div>
      </div>
    </div>
    
    <button class="btn" id="btnEx" style="pointer-events:none; background:#333; border:1px solid #555;">SCANNING...</button>
  </div>
</div>

<script>
  // Timer Logic
  function updateTimer() {{
      var now = new Date();
      var seconds = now.getSeconds();
      var remaining = 60 - seconds;
      document.getElementById('timerText').innerText = '00:' + String(remaining).padStart(2, '0');
  }}
  setInterval(updateTimer, 1000);
  updateTimer();

  // Animation sequence
  window.onload = function() {{
      setTimeout(function() {{
          document.getElementById('v-scan').classList.remove('active');
          document.getElementById('v-res').classList.add('active');
          var btn = document.getElementById('btnEx');
          btn.innerText = 'LOCKED';
          btn.style.background = '#333';
      }}, 2000); // 2 seconds decoding
  }};
</script>
</body>
</html>"""
        return Response(html, mimetype='text/html')

    except Exception as e:
        return send_error(f"Server Error: {str(e)}", 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
