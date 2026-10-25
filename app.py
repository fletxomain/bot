from flask import Flask, request, Response
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib
import json
import time
import base64
import os
import random

app = Flask(__name__)

# ==========================================
# CONFIGURATION
# ==========================================
# Uses Render environment variable, defaults to FVM-HACKER98 if not set
PASSPHRASE = os.environ.get('FVM_PASSPHRASE', 'FVM-HACKER98')
MAX_TS_DIFF = 30 

KEY = hashlib.sha256(PASSPHRASE.encode('utf-8')).digest()

# Global dictionary to lock the result
PERIOD_LOCK = {}

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

        iv = base64.b64decode(data['iv'])
        ciphertext = base64.b64decode(data['cipher'])
        tag = base64.b64decode(data['tag'])
        combined = ciphertext + tag

        aesgcm = AESGCM(KEY)
        try:
            plaintext_bytes = aesgcm.decrypt(iv, combined, None)
            plaintext = plaintext_bytes.decode('utf-8')
        except Exception:
            return send_error("Decryption failed. Passphrase mismatch?")

        payload = json.loads(plaintext)
        if payload.get('action') != "LOAD":
            return send_error("Invalid action")
        
        if abs(time.time() - int(payload.get('ts', 0))) > MAX_TS_DIFF:
            return send_error("Request expired")

        lock_json = json.dumps(PERIOD_LOCK)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>CRAVAULT</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
:root {{ --g1: #00ff88; --g2: #00b347; --g3: #004d1a; --gold: #ffd700; --cyan: #00f0ff; --bg: #010a04; }}
* {{ margin:0; padding:0; box-sizing:border-box; user-select:none; -webkit-tap-highlight-color:transparent; }}
body {{ width:210px; background:transparent!important; font-family:'Rajdhani',sans-serif; color:#fff; overflow:hidden; }}

@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes popIn {{ 0% {{ transform:scale(0); }} 80% {{ transform:scale(1.1); }} 100% {{ transform:scale(1); }} }}
@keyframes barPulse {{ 0%,100% {{ height:4px; opacity:.3; }} 50% {{ height:100%; opacity:1; }} }}
@keyframes flash {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.6; }} }}
@keyframes gridMove {{ 0% {{ background-position: 0 0; }} 100% {{ background-position: 16px 16px; }} }}

.panel {{ position:relative; background:linear-gradient(160deg, rgba(5,30,15,0.95), rgba(1,10,5,0.98)); border-radius:12px; border:1px solid var(--gold); box-shadow:0 0 20px rgba(0,255,136,0.2); padding:8px; overflow:hidden; }}
.panel::before {{ content:''; position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px); background-size:16px 16px; animation:gridMove 10s linear infinite; pointer-events:none; z-index:0; }}

.header {{ display:flex; justify-content:space-between; font-family:'Orbitron'; font-size:10px; font-weight:900; color:var(--gold); border-bottom:1px solid rgba(255,215,0,0.3); padding-bottom:4px; margin-bottom:6px; position:relative; z-index:1; }}
.period {{ text-align:center; font-family:'Share Tech Mono'; font-size:8px; color:var(--cyan); margin-bottom:6px; position:relative; z-index:1; }}
.screen {{ background:rgba(0,0,0,0.6); border:1px solid rgba(255,255,255,0.1); border-radius:8px; min-height:125px; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:6px; position:relative; z-index:1; }}

.view {{ display:none; flex-direction:column; align-items:center; width:100%; justify-content:center; height:100%; }}
.view.active {{ display:flex; animation:popIn 0.4s ease-out; }}

.input-box {{ background:rgba(0,0,0,0.8); border:1px solid var(--gold); color:#fff; font-family:'Orbitron'; font-size:16px; text-align:center; width:80px; padding:6px; border-radius:6px; outline:none; letter-spacing:2px; }}
.input-box::placeholder {{ color:rgba(255,255,255,0.3); }}

.scan-circle {{ width:36px; height:36px; border-radius:50%; border:2px solid transparent; border-top-color:var(--gold); border-bottom-color:var(--g1); animation:spin 1s linear infinite; margin-bottom:6px; }}
.bars {{ display:flex; gap:2px; height:10px; margin-top:4px; align-items:flex-end; }}
.bar {{ width:3px; background:var(--gold); animation:barPulse 0.8s infinite; border-radius:2px 2px 0 0; }}
.bar:nth-child(2) {{ animation-delay:0.1s; }} .bar:nth-child(3) {{ animation-delay:0.2s; }} .bar:nth-child(4) {{ animation-delay:0.3s; }}

.balls {{ display:flex; gap:8px; margin-bottom:6px; }}
.ball {{ width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:'Orbitron'; font-size:16px; font-weight:900; border:1.5px solid #fff; box-shadow:0 0 12px rgba(0,0,0,0.8); animation:popIn 0.5s; }}
.ball.green {{ background:radial-gradient(circle at 30% 30%, #b9f6ca, #00c853); }}
.ball.red {{ background:radial-gradient(circle at 30% 30%, #ff8a80, #d50000); }}
.ball.violet {{ background:radial-gradient(circle at 30% 30%, #ea80fc, #aa00ff); }}

.size-tag {{ font-family:'Orbitron'; font-size:10px; font-weight:900; color:var(--gold); border:1.5px solid var(--gold); padding:2px 12px; border-radius:6px; margin-top:4px; animation:flash 2s infinite; box-shadow:0 0 10px rgba(255,215,0,0.2); }}

.btn {{ width:100%; padding:9px; margin-top:8px; border-radius:6px; border:none; font-family:'Orbitron'; font-size:9px; font-weight:900; color:#fff; background:linear-gradient(180deg, #00b347, #004d1a); border:1px solid var(--gold); cursor:pointer; position:relative; z-index:1; transition:all 0.2s; }}
.btn:active {{ transform:scale(0.96); }}
</style>
</head>
<body>
<div class="panel">
  <div class="header"><span>CRAVAULT</span><span>2-LEVEL</span></div>
  <div class="period">PERIOD: <span id="dispPeriod">---</span></div>
  <div class="screen">
    
    <!-- STATE 1: INPUT -->
    <div class="view active" id="v-input">
      <div style="font-size:9px; font-weight:bold; margin-bottom:5px; font-family:'Orbitron';">ENTER PERIOD</div>
      <input type="number" id="inp" class="input-box" placeholder="000" maxlength="3" oninput="if(this.value.length>3)this.value=this.value.slice(0,3)">
    </div>

    <!-- STATE 2: SCANNING -->
    <div class="view" id="v-scan">
      <div class="scan-circle"></div>
      <div class="bars"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>
      <div style="font-size:8px; margin-top:4px; font-weight:bold; font-family:'Orbitron';">DECODING</div>
    </div>

    <!-- STATE 3: RESULT -->
    <div class="view" id="v-res">
      <div style="font-size:8px; color:var(--cyan); margin-bottom:4px; font-family:'Share Tech Mono';">LOCKED: <span id="resP">---</span></div>
      <div class="balls">
        <div class="ball" id="b1">0</div>
        <div class="ball" id="b2">0</div>
      </div>
      <div class="size-tag" id="resS">BIG</div>
    </div>

  </div>
  <button class="btn" id="btnEx" onclick="run()">EXECUTE</button>
</div>

<script>
  var LOCKS = {lock_json};
  
  function run() {{
    var p = document.getElementById('inp').value.trim();
    if(p.length !== 3 || isNaN(p)) return alert("Please enter a 3-digit period (e.g. 123)");

    document.getElementById('v-input').classList.remove('active');
    document.getElementById('v-scan').classList.add('active');
    document.getElementById('dispPeriod').innerText = p;
    
    var btn = document.getElementById('btnEx');
    btn.innerText = 'SCANNING...';
    btn.style.pointerEvents = 'none';

    setTimeout(function(){{
      if(!LOCKS[p]) {{
        var s = Math.random() > 0.5 ? 'BIG' : 'SMALL';
        var pool = s === 'BIG' ? [5,6,7,8,9] : [0,1,2,3,4];
        
        var n1 = pool.splice(Math.floor(Math.random()*pool.length), 1)[0];
        var n2 = pool[Math.floor(Math.random()*pool.length)];
        
        var c1 = (n1===0||n1===5)?'violet':(s==='BIG'?'green':'red');
        var c2 = (n2===0||n2===5)?'violet':(s==='BIG'?'green':'red');
        
        LOCKS[p] = {{ s:s, n1:n1, n2:n2, c1:c1, c2:c2 }};
      }}
      
      var r = LOCKS[p];
      
      document.getElementById('v-scan').classList.remove('active');
      document.getElementById('v-res').classList.add('active');
      
      document.getElementById('resP').innerText = p;
      
      var b1 = document.getElementById('b1');
      var b2 = document.getElementById('b2');
      
      b1.innerText = r.n1;
      b2.innerText = r.n2;
      b1.className = 'ball ' + r.c1;
      b2.className = 'ball ' + r.c2;
      
      document.getElementById('resS').innerText = r.s;
      
      btn.innerText = 'LOCKED';
      btn.style.background = '#333';
    }}, 2500);
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
