import os
import time
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Base de données temporaire pour stocker les annonces trouvées
LATEST_ITEMS = []
SEEN_IDS = set()

# Recherche Leboncoin (Category 3: Véhicules/Motos - Mots clés: motocross quad)
LBC_API_URL = "https://api.leboncoin.fr/api/adfinder/v1/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# Interface Application Mobile (PWA)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>LBC Moto & Quad</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 16px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 12px; }
        .header h1 { font-size: 1.2rem; margin: 0; color: #38bdf8; }
        .status { background: #22c55e; color: #000; font-weight: bold; font-size: 0.75rem; padding: 4px 8px; border-radius: 12px; }
        .card { background: #1e293b; border-radius: 12px; padding: 12px; margin-bottom: 16px; display: flex; gap: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        .card img { width: 90px; height: 90px; border-radius: 8px; object-fit: cover; background: #334155; }
        .card-details { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .title { font-weight: 600; font-size: 0.95rem; margin: 0 0 4px 0; color: #f1f5f9; }
        .price { color: #4ade80; font-weight: 700; font-size: 1.1rem; }
        .location { font-size: 0.8rem; color: #94a3b8; }
        .btn { background: #f97316; color: white; text-decoration: none; text-align: center; padding: 8px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; margin-top: 6px; display: block; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏍️ Scanner Moto & Quad</h1>
        <span class="status">● 24/7 Actif</span>
    </div>
    <div id="feed">
        <p style="text-align: center; color: #64748b;">Recherche de nouvelles pépites en cours...</p>
    </div>

    <script>
        async function fetchItems() {
            try {
                const res = await fetch('/api/items');
                const items = await res.json();
                if(items.length > 0) {
                    const feed = document.getElementById('feed');
                    feed.innerHTML = items.map(item => `
                        <div class="card">
                            <img src="${item.photo}" alt="moto">
                            <div class="card-details">
                                <p class="title">${item.title}</p>
                                <span class="price">${item.price}</span>
                                <span class="location">📍 ${item.location}</span>
                                <a href="${item.url}" target="_blank" class="btn">⚡ Voir sur Leboncoin</a>
                            </div>
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