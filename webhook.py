from flask import Flask, request, jsonify
import os, json
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False

@app.route('/webhook/<string:token>', methods=['POST'])
def webhook(token):
    event = request.headers.get('X-GitHub-Event', 'unknown')
    payload = request.get_json(silent=True)

    if not payload:
        print("Payload inválido ou ausente")
        return jsonify({'error': 'Invalid JSON'}), 400

    print(f"[{datetime.now()}] Evento: {event} | Token: {token}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # Salvar log
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{token}.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] EVENTO: {event}\n")
        f.write(json.dumps(payload, indent=2, ensure_ascii=False))
        f.write("\n" + "-" * 60 + "\n")

    return jsonify({'status': 'ok', 'token': token, 'event': event}), 200

@app.route('/webhook/', methods=['POST'])
def webhook_ping():
    event = request.headers.get('X-GitHub-Event', '')
    if event == 'ping':
        print("Ping recebido sem token")
        return jsonify({'pong': True}), 200
    return jsonify({'error': 'Token obrigatório'}), 403

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Webhook Flask rodando na porta {port}")
    app.run(host='0.0.0.0', port=port)