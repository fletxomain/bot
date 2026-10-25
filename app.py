from flask import Flask, request, Response
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib
import json
import time
import base64
import os
import random

app = Flask(__name__)

PASSPHRASE = os.environ.get('FVM_PASSPHRASE', 'FVM-HACKER98')
MAX_TS_DIFF = 30 

KEY = hashlib.sha256(PASSPHRASE.encode('utf-8')).digest()
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

        # UPDATED CSS FOR FLOATING WINDOW FIT
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, maximum-scale=1.0">
<title>CRAVAULT AI</title>
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
body{{margin:0;padding:0;width:220px;background:transparent!important;font-family:'Rajdhani',sans-serif;color:#fff;overflow:hidden;}}

@keyframes spin{{to{{transform:rotate(360deg);}}}}
@keyframes spinR{{to{{transform:rotate(-360deg);}}}}
@keyframes pulseDot{{0%{{opacity:.5;transform:scale(.8);}}100%{{opacity:1;transform:scale(1.3);}}}}
@keyframes textShine{{0%{{background-position:0% center;}}100%{{background-position:200% center;}}}}
@keyframes viewIn{{from{{opacity:0;transform:scale(.9) translateY(10px);}}to{{opacity:1;transform:scale(1) translateY(0);}}}}
@keyframes popIn{{0%{{transform:scale(0) rotate(-180deg);opacity:0;}}80%{{transform:scale(1.2) rotate(10deg);}}100%{{transform:scale(1) rotate(0);opacity:1;}}}}
@keyframes gridScroll{{0%{{background-position:0 0;}}100%{{background-position:32px 32px;}}}}
@keyframes scanLine{{0%{{top:-2px;opacity:0;}}5%{{opacity:1;}}93%{{opacity:1;}}100%{{top:calc(100% + 2px);opacity:0;}}}}
@keyframes radarSweep{{to{{transform:rotate(360deg);}}}}
@keyframes neonBreathe{{0%,100%{{box-shadow:0 0 15px var(--g3),0 0 30px var(--gn-glow);}}50%{{box-shadow:0 0 22px var(--g1),0 0 45px var(--gn-glow);}}}}
@keyframes surefireAnim{{0%{{letter-spacing:2px;text-shadow:0 0 12px var(--g1);}}50%{{letter-spacing:4px;text-shadow:0 0 22px var(--gold),0 0 5px #fff;}}100%{{letter-spacing:2px;text-shadow:0 0 12px var(--g1);}}}}
@keyframes barPulse{{0%,100%{{height:4px;opacity:.3;}}50%{{height:100%;opacity:1;}}}}

/* MAIN PANEL (Fitted for Float) */
#drac-panel-container{{width:220px;margin:0 auto;touch-action:none;}}
.panel-hexagon-backing{{position:absolute;inset:-2px;background:linear-gradient(135deg, var(--g3), var(--gold), var(--g3));border-radius:18px;z-index:2;box-shadow:0 0 35px var(--gn-glow), 0 0 55px rgba(0,26,10,0.8);}}
.panel-body{{position:relative;z-index:5;background:linear-gradient(160deg, rgba(5,30,15,0.8) 0%, rgba(1,10,5,0.96) 100%);backdrop-filter: blur(15px);-webkit-backdrop-filter: blur(15px);border-radius:16px;border-top: 1.5px solid rgba(255,215,0,0.6);border-left: 1px solid rgba(255,255,255,0.2);border-right: 1px solid rgba(255,255,255,0.1);border-bottom: 1px solid rgba(255,255,255,0.1);box-shadow: inset 0 0 20px rgba(0,255,100,0.08), 0 15px 30px rgba(0,0,0,0.9);padding:11px 10px 10px;display:flex;flex-direction:column;gap:6px;overflow:hidden;}}

.header-row{{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:10;padding:0 2px;}}
.header-title{{font-family:'Orbitron',sans-serif;font-weight:900;font-size:11px;letter-spacing:1.2px;background:linear-gradient(90deg, #fff 0%, var(--gold) 40%, var(--g1) 70%, #fff 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:textShine 3.5s linear infinite;filter:drop-shadow(0 0 6px rgba(255,215,0,0.5));}}
.mode-badge{{background:rgba(255,255,255,.12);border:1px solid var(--gold);border-radius:10px;padding:2px 6px;display:flex;align-items:center;gap:4px;box-shadow:0 0 8px rgba(255,215,0,.3);}}
.mode-dot{{width:5px;height:5px;border-radius:50%;background:var(--g1);box-shadow:0 0 6px var(--g1);animation:pulseDot 1s infinite alternate;}}
.mode-text{{font-family:'Share Tech Mono',monospace;font-size:6.5px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#fff;}}

.period-box{{position:relative;z-index:10;text-align:center;border:1px solid rgba(255,215,0,0.35);border-radius:6px;padding:3px 0;background:linear-gradient(90deg,transparent,rgba(0,255,136,.12),transparent);}}
.period-box::before,.period-box::after{{content:'';position:absolute;top:50%;transform:translateY(-50%);width:3px;height:3px;border-radius:50%;background:var(--gold);box-shadow:0 0 6px var(--gold);}}
.period-box::before{{left:8px;}} .period-box::after{{right:8px;}}
.period-text{{font-family:'Share Tech Mono',monospace;font-size:7.5px;font-weight:700;letter-spacing:1.5px;color:#fff;}}

.screen-area{{position:relative;z-index:10;background:linear-gradient(170deg,rgba(2,10,5,.7) 0%,rgba(5,20,10,.85) 100%);border-radius:12px;border:1px solid rgba(255,255,255,0.15);border-top: 1px solid rgba(255,215,0,0.4);min-height:145px;padding:6px 4px;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:inset 0 0 35px rgba(0,0,0,.85),0 4px 14px rgba(0,0,0,.5);overflow:hidden;}}
.screen-area::before{{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:16px 16px;animation:gridScroll 15s linear infinite;pointer-events:none;z-index:0;}}
.screen-scan-stripe{{position:absolute;left:0;width:100%;height:1.5px;background:linear-gradient(90deg,transparent,var(--gold) 40%,#fff 50%,var(--g1) 60%,transparent);box-shadow:0 0 10px #fff,0 0 20px var(--g1);animation:scanLine 3.5s linear infinite;top:-2px;pointer-events:none;z-index:4;}}
.radar-sweep{{position:absolute;top:50%;left:50%;width:200%;height:200%;background:conic-gradient(from 0deg,transparent 75%,rgba(255,215,0,.05) 88%,rgba(0,230,92,.18) 100%);transform-origin:0 0;animation:radarSweep 3.5s linear infinite;z-index:2;pointer-events:none;}}

.bracket{{position:absolute;width:8px;height:8px;border-color:rgba(255,215,0,.6);border-style:solid;z-index:15;}}
.bracket.tl{{top:4px;left:4px;border-width:2px 0 0 2px;}} .bracket.tr{{top:4px;right:4px;border-width:2px 2px 0 0;}}
.bracket.bl{{bottom:4px;left:4px;border-width:0 0 2px 2px;}} .bracket.br{{bottom:4px;right:4px;border-width:0 2px 2px 0;}}

.view-state{{display:none;flex-direction:column;align-items:center;width:100%;height:100%;text-align:center;position:relative;z-index:20;justify-content:center;gap:4px;}}
.view-state.active{{display:flex;animation:viewIn .5s cubic-bezier(0.25, 1, 0.5, 1) forwards;}}

.input-box{{
  background: rgba(0,0,0,0.6); border: 1px solid var(--gold); color: #fff;
  font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: 900; 
  width: 85px; text-align: center; padding: 6px; border-radius: 8px;
  outline: none; letter-spacing: 2px;
  box-shadow: inset 0 0 10px rgba(255,215,0,0.2);
}}
.input-box::placeholder{{color: rgba(255,255,255,0.3);}}

.scan-visualizer{{position:relative;width:45px;height:45px;display:flex;align-items:center;justify-content:center;margin-bottom:6px;}}
.arc{{position:absolute;border-radius:50%;border:2px solid transparent;}}
.arc-1{{inset:0;border-top-color:var(--gold);border-bottom-color:var(--g1);animation:spin .9s cubic-bezier(.68,-.55,.265,1.55) infinite;}}
.arc-2{{inset:4px;border-left-color:#66ff99;border-right-color:rgba(255,255,255,0.5);animation:spinR 1.4s linear infinite;}}
.arc-3{{inset:-6px;border:1.5px dotted var(--gold);animation:spin 3.5s linear infinite;}}

.scan-bars{{display:flex;align-items:flex-end;gap:2px;height:12px;position:relative;z-index:2;margin-top:4px;}}
.sbar{{width:3.5px;border-radius:3px 3px 0 0;background:linear-gradient(180deg,var(--gold),var(--g2));box-shadow:0 0 6px var(--gold);}}
.sbar:nth-child(1){{animation:barPulse .7s ease-in-out infinite 0s;}}
.sbar:nth-child(2){{animation:barPulse .7s ease-in-out infinite .1s;}}
.sbar:nth-child(3){{animation:barPulse .7s ease-in-out infinite .2s;}}
.sbar:nth-child(4){{animation:barPulse .7s ease-in-out infinite .3s;}}
.sbar:nth-child(5){{animation:barPulse .7s ease-in-out infinite .4s;}}

#view-result{{justify-content:space-between;padding:4px 2px;}}
.res-period-top{{font-family:'Share Tech Mono',monospace;font-size:8px;font-weight:900;color:#fff;letter-spacing:1px;border-bottom:1px solid rgba(255,215,0,.4);padding-bottom:2px;width:90%;text-align:center;margin-bottom:2px;}}
.res-period-top span{{color:var(--gold);}}
.result-layout{{display:flex;flex-direction:column;align-items:center;justify-content:center;width:100%;position:relative;z-index:5;flex-grow:1;gap:4px;}}

.dual-ball-wrapper{{display:flex;align-items:center;gap:8px;}}
.res-ball-container{{position:relative;width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:1.5px solid #fff; animation:popIn .6s cubic-bezier(0.25, 1, 0.5, 1) both; box-shadow:0 0 18px rgba(0,0,0,0.9), inset 0 2px 4px rgba(255,255,255,0.7);}}
.res-ball-container:nth-child(1) {{ animation-delay: 0.2s; }}
.res-ball-container:nth-child(2) {{ animation-delay: 0.4s; }}

.res-ball-container.red{{background:radial-gradient(circle at 35% 30%,#ff8a80 0%,#d50000 50%,#5b0000 90%);box-shadow:0 0 16px #ff0055;}}
.res-ball-container.green{{background:radial-gradient(circle at 35% 30%,#b9f6ca 0%,#00c853 50%,#004d1a 90%);box-shadow:0 0 16px #00ff88;}}
.res-ball-container.violet{{background:radial-gradient(circle at 35% 30%,#ea80fc 0%,#aa00ff 50%,#4a0072 90%);box-shadow:0 0 16px #aa00ff;}}
.res-ball-container.gold{{background:radial-gradient(circle at 35% 30%,#fff59d 0%,#fbc02d 50%,#f57f17 90%);box-shadow:0 0 16px #ffd700;}}
.ball-num-txt{{font-family:'Orbitron',sans-serif;font-size:15px;font-weight:900;color:#fff;text-shadow:0 2px 4px rgba(0,0,0,.9);}}

.conf-pill-tag{{font-family:'Share Tech Mono',monospace;font-size:6.5px;font-weight:800;color:var(--cyan);background:rgba(0,0,0,0.65);padding:1px 4px;border-radius:6px;border:1px solid rgba(0,240,255,0.35);text-shadow:0 0 6px var(--cyan);}}

.res-sureshot-banner{{font-family:'Orbitron',sans-serif;font-size:10px;font-weight:900;border:1.2px solid rgba(255,215,0,.7);padding:3px 12px;border-radius:8px;background:linear-gradient(180deg,rgba(255,215,0,.25) 0%,rgba(0,0,0,.6) 100%);box-shadow:0 0 16px var(--gold-glow);text-shadow:0 0 10px var(--gold);text-transform:uppercase;letter-spacing:1.5px;color:#fff;display:flex;align-items:center;justify-content:center;gap:4px;animation:surefireAnim 2.5s ease-in-out infinite;}}

.btn-container{{display:flex;gap:6px;position:relative;z-index:10;}}
.drac-btn{{flex:1;padding:8px 4px;border:none;border-radius:8px;font-family:'Orbitron',sans-serif;font-size:7.5px;font-weight:900;letter-spacing:1px;cursor:pointer;text-transform:uppercase;color:#fff;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:4px;transition:all .2s ease;}}
.drac-btn:active{{transform:scale(.94);}}
.btn-primary{{background:linear-gradient(180deg,#00b347 0%,#004d1a 100%);border:1.2px solid var(--gold);flex:1.8;box-shadow:0 0 12px var(--gn-glow);text-shadow:0 1px 3px rgba(0,0,0,0.8);}}
.btn-secondary{{background:linear-gradient(180deg,rgba(255,255,255,.15) 0%,rgba(255,255,255,.05) 100%);color:#fff;border:1px solid rgba(255,255,255,.3);}}
</style>
</head>
<body>

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
      <div class="period-text">PERIOD : <span id="periodDisplay">---</span></div>
    </div>

    <div class="screen-area">
      <div class="screen-scan-stripe"></div>
      <div class="radar-sweep"></div>
      <div class="bracket tl"></div><div class="bracket tr"></div>
      <div class="bracket bl"></div><div class="bracket br"></div>

      <!-- STATE 1: INPUT READY -->
      <div class="view-state active" id="view-ready">
        <div class="header-title" style="font-size:11px; margin-bottom:5px;">ENTER PERIOD</div>
        <input type="number" id="userPeriodInput" class="input-box" placeholder="3-DIGIT" maxlength="3" oninput="limitInput(this)">
      </div>

      <!-- STATE 2: SCANNING -->
      <div class="view-state" id="view-scan">
        <div class="scan-visualizer">
          <div class="arc arc-3"></div>
          <div class="arc arc-1"></div>
          <div class="arc arc-2"></div>
          <img src="https://myimgs.org/storage/images/65497/1000020658.png" class="custom-logo" alt="Logo" style="width:24px;height:24px;z-index:5; border-radius: 50%;">
        </div>
        <div class="scan-bars">
          <div class="sbar"></div><div class="sbar"></div><div class="sbar"></div>
          <div class="sbar"></div><div class="sbar"></div>
        </div>
        <div class="header-title" style="font-size:9px;margin-top:4px;" id="scanText">DECODING</div>
      </div>

      <!-- STATE 3: RESULT -->
      <div class="view-state" id="view-result">
        <div class="res-period-top">LOCKED: <span id="resPeriodDisplay">---</span></div>
        <div class="result-layout">
          <div class="dual-ball-wrapper">
            <div class="res-ball-container" id="resBallColor1">
              <span class="ball-num-txt" id="resNum1">0</span>
            </div>
            <div class="res-ball-container" id="resBallColor2">
              <span class="ball-num-txt" id="resNum2">0</span>
            </div>
          </div>
          <div class="conf-pill-tag">CONF: 98.6% | L1: 85% L2: 90%</div>
          <div class="res-sureshot-banner">
            <span id="resSize">BIG</span>
          </div>
        </div>
      </div>
    </div>

    <div class="btn-container">
      <button class="drac-btn btn-primary" id="btnExecute" onclick="executeLogic()">EXECUTE</button>
      <button class="drac-btn btn-secondary" onclick="closePanel()">MINIMIZE</button>
    </div>

  </div>
</div>

<script>
  var PERIOD_LOCK = {lock_json};

  function limitInput(el) {{
    if (el.value.length > 3) el.value = el.value.slice(0, 3);
  }}

  function closePanel(){{
    // Send message to Android to hide linear3 and show gameimage
    if(window.Android) {{
        window.Android.closePanel();
    }}
  }}

  function executeLogic(){{
    var period = document.getElementById('userPeriodInput').value.trim();
    
    if(period.length !== 3 || isNaN(period)){{
        alert("Please enter a valid 3-digit period number (e.g., 123).");
        return;
    }}

    document.getElementById('view-ready').classList.remove('active');
    document.getElementById('view-scan').classList.add('active');
    document.getElementById('periodDisplay').innerText = period;

    var btn = document.getElementById('btnExecute');
    btn.innerText = 'SCANNING...';
    btn.style.pointerEvents = 'none';

    setTimeout(function(){{
        if (!PERIOD_LOCK[period]) {{
            var size = Math.random() > 0.5 ? 'BIG' : 'SMALL';
            var num1, num2;
            
            if (size === 'BIG') {{
                var pool = [5, 6, 7, 8, 9];
                num1 = pool.splice(Math.floor(Math.random() * pool.length), 1)[0];
                num2 = pool[Math.floor(Math.random() * pool.length)];
            }} else {{
                var pool = [0, 1, 2, 3, 4];
                num1 = pool.splice(Math.floor(Math.random() * pool.length), 1)[0];
                num2 = pool[Math.floor(Math.random() * pool.length)];
            }}

            var color1 = (num1 == 0 || num1 == 5) ? 'violet' : (size === 'BIG' ? 'green' : 'red');
            var color2 = (num2 == 0 || num2 == 5) ? 'violet' : (size === 'BIG' ? 'green' : 'red');

            PERIOD_LOCK[period] = {{
                size: size,
                n1: num1,
                n2: num2,
                color1: color1,
                color2: color2
            }};
        }}

        var result = PERIOD_LOCK[period];

        document.getElementById('view-scan').classList.remove('active');
        document.getElementById('view-result').classList.add('active');
        
        document.getElementById('resPeriodDisplay').innerText = period;
        document.getElementById('resNum1').innerText = result.n1;
        document.getElementById('resNum2').innerText = result.n2;
        document.getElementById('resSize').innerText = result.size;
        
        document.getElementById('resBallColor1').className = 'res-ball-container ' + result.color1;
        document.getElementById('resBallColor2').className = 'res-ball-container ' + result.color2;

        btn.innerText = 'LOCKED';
        btn.style.background = '#333';
    }}, 2800);
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
