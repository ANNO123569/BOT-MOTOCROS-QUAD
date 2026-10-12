import os
import time
import threading
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

LATEST_ITEMS = []

def fetch_leboncoin():
    global LATEST_ITEMS
    url = "https://api.leboncoin.fr/api/adfinder/v1/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Api-Key": "ba0c2dad58b3ec"
    }
    params = {
        "category": "3",
        "text": "motocross quad",
        "regions": "all",
        "limit": 30
    }
    
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ads = data.get("ads", [])
                items = []
                for ad in ads:
                    images = ad.get("images", {}).get("urls", [])
                    photo = images[0] if images else ""
                    
                    price_val = ad.get('price', [0])
                    price_str = f"{price_val[0]} €" if isinstance(price_val, list) and price_val else "Prix N/C"
                    
                    item = {
                        "title": ad.get("subject", "Sans titre"),
                        "price": price_str,
                        "location": f"{ad.get('location', {}).get('city', '')}",
                        "url": ad.get("url", "#")
                    }
                    items.append(item)
                if items:
                    LATEST_ITEMS = items
        except Exception as e:
            print(f"Erreur : {e}")
        
        time.sleep(60)

# Lancer la recherche en arrière-plan
threading.Thread(target=fetch_leboncoin, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LBC Moto & Quad</title>
    <style>
        body { font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 16px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 12px; }
        .header h1 { font-size: 1.2rem; margin: 0; color: #38bdf8; }
        .status { background: #22c55e; color: #000; font-weight: bold; font-size: 0.75rem; padding: 4px 8px; border-radius: 12px; }
        .card { background: #1e293b; border-radius: 12px; padding: 14px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .title { font-weight: 600; font-size: 1rem; margin: 0 0 6px 0; color: #f1f5f9; }
        .price { color: #4ade80; font-weight: 700; font-size: 1.1rem; margin-bottom: 4px; }
        .location { font-size: 0.85rem; color: #94a3b8; margin-bottom: 10px; }
        .btn { background: #f97316; color: white; text-decoration: none; text-align: center; padding: 10px; border-radius: 8px; font-weight: 600; display: block; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏍️ Scanner Moto & Quad</h1>
        <span class="status">● 24/7 Actif</span>
    </div>
    <div id="feed">
        <p style="text-align: center; color: #64748b;">Analyse des annonces en cours...</p>
    </div>
    <script>
        async function fetchItems() {
            try {
                const res = await fetch('/api/items');
                const items = await res.json();
                const feed = document.getElementById('feed');
                if(items.length > 0) {
                    feed.innerHTML = items.map(item => `
                        <div class="card">
                            <div class="title">${item.title}</div>
                            <div class="price">${item.price}</div>
                            <div class="location">📍 ${item.location}</div>
                            <a href="${item.url}" target="_blank" class="btn">⚡ Voir l'annonce</a>
                        </div>
                    `).join('');
                }
            } catch(e) { console.error(e); }
        }
        setInterval(fetchItems, 5000);
        fetchItems();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/items')
def get_items():
    return jsonify(LATEST_ITEMS)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
