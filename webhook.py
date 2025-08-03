import os
import hmac
import hashlib
import json
from datetime import datetime, timezone
from flask import Flask, request, abort, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
GITHUB_SECRET = os.getenv("GITHUB_SECRET", "undefined-secret")
LOG_FILE = 'webhook.log'

def log_event(event_type, status, message):
    now = datetime.now(timezone.utc).isoformat()
    log_line = f"[{now} - {event_type.upper()} - {status.upper()}] {message}"
    print(log_line)
    with open(LOG_FILE, 'a') as f:
        f.write(log_line + "\n")

def verify_signature(data, signature_header):
    if not signature_header:
        return False
    mac = hmac.new(GITHUB_SECRET.encode(), msg=data, digestmod=hashlib.sha1)
    expected = f"sha1={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature_header)

@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

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
        log_event(event, '200', f"Push recebido em: {datetime.now(timezone.utc)} - Repo: {json_data['repository']['full_name']}")
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        log_event(event, '500', f"Erro ao processar JSON: {e}")
        abort(500)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
