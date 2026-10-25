import os
import time
from flask import Flask, request, Response, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

# Render sits behind a proxy; only trust one forwarded proxy hop.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CRAVAULT Panel</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:transparent;color:#f4fff8;font:16px system-ui,sans-serif;padding:12px}
.card{max-width:420px;margin:0 auto;padding:18px;border:1px solid #ffd700;border-radius:16px;
background:rgba(2,16,8,.96);box-shadow:0 0 22px rgba(0,255,136,.15)}
h2{margin:0 0 8px;color:#ffd700;font-size:18px}
p{margin:8px 0;color:#d8e8de;line-height:1.45}
.status{display:inline-block;padding:5px 9px;border-radius:8px;border:1px solid #00c96b;color:#8dffc0}
</style>
</head>
<body><main class="card">
<h2>CRAVAULT SERVER</h2>
<div class="status">Server response OK</div>
<p>The server returned this HTML successfully.</p>
<p id="detail">Waiting for an authorized app request.</p>
</main>
<script>
/* The server HTML intentionally does not generate fake predictions or claim guaranteed results. */
</script>
</body></html>"""

def html_response(status=200):
    return Response(HTML_PAGE, status=status, mimetype="text/html")

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.get("/")
def home():
    # Opening the service URL in a browser/WebView returns HTML, not a misleading 400 page.
    return html_response()

@app.post("/api/load")
def load_panel():
    # This route accepts a small JSON request. No shared secret is embedded in the APK.
    # For private/protected use, add real user authentication before returning private content.
    if not request.is_json:
        return jsonify(error="Content-Type must be application/json"), 415

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Invalid JSON body"), 400

    if data.get("action") != "LOAD":
        return jsonify(error="Invalid action"), 400

    try:
        ts = int(data.get("ts", 0))
    except (TypeError, ValueError):
        return jsonify(error="Invalid timestamp"), 400

    if abs(int(time.time()) - ts) > 30:
        return jsonify(error="Request expired; retry with a fresh timestamp"), 400

    return html_response()

@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="Not found"), 404

@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="Request too large"), 413

@app.errorhandler(500)
def server_error(_error):
    return jsonify(error="Internal server error"), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
