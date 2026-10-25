import os, time, json, base64, hashlib
from flask import Flask, request, Response
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)
MAX_TS_DIFF = 30
PROTECTED_HTML = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>CRAVAULT PREMIUM AI</title>\n<style>\n*{box-sizing:border-box}body{margin:0;background:#010a04;color:white;font-family:Arial,sans-serif}\n.card{margin:18px auto;max-width:650px;padding:22px;border:1px solid #ffd700;border-radius:20px;background:#05140a}\nh1{font-size:22px;color:#ffd700}p{color:#ddd;line-height:1.5}\ninput,button{font-size:16px;padding:10px;border-radius:8px;border:1px solid #ffd700}\ninput{background:#000;color:white;width:120px}button{background:#006b32;color:white}\n</style></head><body><main class="card">\n<h1>CRAVAULT AI</h1><p>Authorized request accepted.</p>\n<label for="period">ENTER PERIOD</label><br><br>\n<input id="period" inputmode="numeric" maxlength="3" placeholder="123">\n<button onclick="run()">EXECUTE</button><p id="result"></p>\n<script>\nfunction run(){\n const p=document.getElementById(\'period\').value.trim();\n if(!/^\\d{3}$/.test(p)){document.getElementById(\'result\').textContent=\'Enter a 3-digit period.\';return;}\n const n=Math.floor(Math.random()*10), m=Math.floor(Math.random()*10);\n document.getElementById(\'result\').textContent=\'Period \'+p+\' — \'+(n>=5?\'BIG\':\'SMALL\')+\' | \'+n+\', \'+m;\n}\n</script></main></body></html>'

def page_error(message, status):
    from html import escape
    body = ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Access Denied</title><style>"
            "body{background:#010a04;color:#fff;font-family:Arial;padding:24px}"
            "main{max-width:520px;margin:12vh auto;padding:28px;border:1px solid #ffd700;"
            "border-radius:18px;background:#05140a}h1{color:#ffd700}</style></head>"
            "<body><main><h1>Access Denied</h1><p>" + escape(message) +
            "</p></main></body></html>")
    r = Response(body, status=status, mimetype="text/html")
    r.headers["Cache-Control"] = "no-store"
    return r

@app.get("/health")
def health():
    return Response('{"status":"ok"}', mimetype="application/json")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method != "POST":
        return page_error("POST required", 405)
    secret = os.environ.get("PASSPHRASE", "").strip()
    if not secret:
        return page_error("Server secret is not configured", 503)
    if not request.is_json:
        return page_error("Invalid request", 400)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not all(k in data for k in ("iv", "cipher", "tag")):
        return page_error("Invalid request", 400)
    try:
        iv = base64.b64decode(data["iv"], validate=True)
        cipher = base64.b64decode(data["cipher"], validate=True)
        tag = base64.b64decode(data["tag"], validate=True)
        if len(iv) != 12 or len(tag) != 16:
            raise ValueError("Invalid lengths")
        key = hashlib.sha256(secret.encode("utf-8")).digest()
        plaintext = AESGCM(key).decrypt(iv, cipher + tag, None)
        payload = json.loads(plaintext.decode("utf-8"))
        if not isinstance(payload, dict) or payload.get("action") != "LOAD":
            return page_error("Access denied", 403)
        if abs(time.time() - int(payload.get("ts", 0))) > MAX_TS_DIFF:
            return page_error("Access denied", 403)
    except Exception:
        return page_error("Access denied", 403)
    r = Response(PROTECTED_HTML, mimetype="text/html")
    r.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["Referrer-Policy"] = "no-referrer"
    return r

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
