from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False  # aceita / ou sem / no final da URL

@app.route('/webhook/<string:token>', methods=['POST'])
def webhook(token):
    payload = request.get_json()

    print(f"\n✅ [{datetime.now()}] Webhook recebido com token: {token}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    save_webhook_log(token, payload)

    return jsonify({'status': 'ok', 'token': token}), 200

def save_webhook_log(token, data):
    os.makedirs('logs', exist_ok=True)
    path = os.path.join('logs', f'{token}.log')
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f"📦 {datetime.now()} - Webhook recebido:\n")
        f.write(json.dumps(data, indent=2, ensure_ascii=False))
        f.write("\n" + "-" * 60 + "\n")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Servidor Flask escutando em http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
