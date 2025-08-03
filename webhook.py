from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False

@app.route('/webhook/', methods=['POST'])
def webhook_ping_root():
    event = request.headers.get('X-GitHub-Event', '')
    if event == 'ping':
        print("Ping genérico recebido (sem token)")
        return jsonify({'pong': True, 'note': 'Webhook base test passed'}), 200
    return jsonify({'error': 'Token obrigatório'}), 400

@app.route('/webhook/<string:token>', methods=['POST'])
def webhook(token):
    event = request.headers.get('X-GitHub-Event', '')
    payload = request.get_json()

    if event == 'ping':
        print(f"Ping recebido do GitHub para token: {token}")
        return jsonify({'pong': True, 'token': token}), 200

    print(f"[{datetime.now()}] Webhook recebido com token: {token}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    save_webhook_log(token, payload)
    return jsonify({'status': 'ok', 'token': token}), 200

def save_webhook_log(token, data):
    os.makedirs('logs', exist_ok=True)
    path = os.path.join('logs', f'{token}.log')
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] Webhook recebido:\n")
        f.write(json.dumps(data, indent=2, ensure_ascii=False))
        f.write("\n" + "-" * 60 + "\n")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Servidor Flask escutando em http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
