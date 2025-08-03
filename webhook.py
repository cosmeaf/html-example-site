import os
import hmac
import hashlib
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, abort, jsonify
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
GITHUB_SECRET = os.getenv("GITHUB_SECRET", "undefined-secret")

# Configuração do logger
LOG_FILE = 'webhook.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='[%(asctime)s - %(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)

app = Flask(__name__)


def verify_signature(data, signature_header):
    if not signature_header:
        return False
    mac = hmac.new(GITHUB_SECRET.encode(), msg=data, digestmod=hashlib.sha1)
    expected = f"sha1={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature_header)


@app.route('/webhook', methods=['POST'])
def github_webhook():
    event = request.headers.get('X-GitHub-Event', 'unknown')
    signature = request.headers.get('X-Hub-Signature')
    payload = request.get_data()

    if not verify_signature(payload, signature):
        logging.warning(f"[{event}] Assinatura inválida")
        abort(403)

    try:
        json_data = request.get_json()
        repo = json_data.get('repository', {}).get('full_name', 'unknown')
        logging.info(f"[{event}] Push recebido - Repo: {repo}")
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logging.error(f"[{event}] Erro ao processar JSON: {e}")
        abort(500)


@app.route('/', methods=['GET'])
def index():
    return "Webhook ativo."


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
