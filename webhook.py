import os
import hmac
import hashlib
import json
from datetime import datetime, timezone
from flask import Flask, request, abort, jsonify, send_from_directory
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# Obter chave secreta do .env
GITHUB_SECRET = os.getenv("GITHUB_SECRET", "undefined-secret")

# Caminho para o log
LOG_FILE = 'webhook.log'

# Função para log estruturado
def log_event(event_type, status, message):
    now = datetime.now(timezone.utc).isoformat()
    log_line = f"[{now} - {event_type.upper()} - {status.upper()}] {message}"
    print(log_line)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + "\n")

# Verificar assinatura HMAC do GitHub
def verify_signature(data, signature_header):
    if not signature_header:
        return False
    mac = hmac.new(GITHUB_SECRET.encode(), msg=data, digestmod=hashlib.sha1)
    expected = f"sha1={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature_header)

# Servir index.html diretamente da raiz
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

# Evitar erro 404 para favicon
@app.route('/favicon.ico')
def favicon():
    return '', 204

# Endpoint do webhook GitHub
@app.route('/webhook', methods=['POST'])
def github_webhook():
    event = request.headers.get('X-GitHub-Event', 'unknown')
    signature = request.headers.get('X-Hub-Signature')
    payload = request.get_data()

    if not verify_signature(payload, signature):
        log_event(event, '403', 'Assinatura inválida')
        abort(403)

    try:
        json_data = request.get_json()
        repo_name = json_data['repository']['full_name']
        log_event(event, '200', f"Push recebido - Repo: {repo_name}")
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        log_event(event, '500', f"Erro ao processar JSON: {e}")
        abort(500)

# Executar a aplicação
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
