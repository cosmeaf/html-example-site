from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False

# Endpoint base para o ping de teste do GitHub
@app.route('/webhook/', methods=['POST'])
def webhook_base():
    event = request.headers.get('X-GitHub-Event', '')
    if event == 'ping':
        print("Ping genérico recebido sem token.")
        return jsonify({'pong': True, 'note': 'Webhook base test passed'}), 200
    return jsonify({'error': 'Token obrigatório'}), 400

# Endpoint real para receber eventos por token
@app.route('/webhook/<string:token>', methods=['POST'])
def webhook_event(token):
    event = request.headers.get('X-GitHub-Event', '')
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify({'error': 'Payload ausente ou inválido'}), 400

    if event == 'ping':
        print(f"Ping recebido do GitHub para token: {token}")
        return jsonify({'pong': True, 'token': token}), 200

    print(f"[{datetime.now()}] Evento recebido: {event} - Token: {token}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    save_log(token, event, payload)
    return jsonify({'status': 'ok', 'token': token, 'event': event}), 200

def save_log(token, event, data):
    os.makedirs('logs', exist_ok=True)
    filename = os.path.join('logs', f'{token}.log')
    with open(filename, 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] EVENTO: {event}\n")
        log.write(json.dumps(data, indent=2, ensure_ascii=False))
        log.write("\n" + "-" * 60 + "\n")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Servidor Flask ativo em http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
