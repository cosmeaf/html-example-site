from flask import Flask, request, jsonify, send_from_directory
import hmac, hashlib, json, os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

# Secret configurado no GitHub
GITHUB_SECRET = os.getenv('GITHUB_SECRET')

def verify_signature(data, signature):
    mac = hmac.new(bytes(GITHUB_SECRET, 'utf-8'), msg=data, digestmod=hashlib.sha1)
    expected = f'sha1={mac.hexdigest()}'
    return hmac.compare_digest(expected, signature)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/webhook/', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event', '')
    signature = request.headers.get('X-Hub-Signature', '')
    data = request.get_data()

    if not verify_signature(data, signature):
        print("Assinatura HMAC inválida.")
        return jsonify({'error': 'Assinatura inválida'}), 403

    payload = request.get_json()

    if event == 'ping':
        print("Ping recebido")
        return jsonify({'pong': True}), 200

    if event == 'push':
        print(f"Push recebido em: {datetime.now()}")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        os.makedirs("logs", exist_ok=True)
        with open("logs/push.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] PUSH:\n")
            f.write(json.dumps(payload, indent=2, ensure_ascii=False))
            f.write("\n" + "-" * 60 + "\n")

        return jsonify({'status': 'ok'}), 200

    return jsonify({'status': 'ignorado', 'event': event}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Webhook iniciado em http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
