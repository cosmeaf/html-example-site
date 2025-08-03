from flask import Flask, request, send_from_directory, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False  # Aceita URLs com ou sem barra no final

# Serve index.html na raiz do projeto
@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

# Rota do Webhook: aceita qualquer token
@app.route('/webhook/<string:token>', methods=['POST'])
def webhook(token):
    payload = request.get_json()

    # Registro visual no terminal
    print(f"\n✅ [{datetime.now()}] Webhook recebido com token: {token}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # Salvar log em arquivo (opcional)
    save_webhook_log(token, payload)

    return jsonify({'status': 'ok', 'token': token}), 200

# Função para salvar o payload em arquivo (logs separados por token)
def save_webhook_log(token, data):
    os.makedirs('logs', exist_ok=True)
    log_file = os.path.join('logs', f'{token}.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"📦 {datetime.now()} - Webhook recebido:\n")
        f.write(json.dumps(data, indent=2, ensure_ascii=False))
        f.write("\n" + "-" * 60 + "\n")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Servidor Flask iniciado em http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
