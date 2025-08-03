from flask import Flask, request, send_from_directory
import os
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/webhook/<string:token>/', methods=['POST'])
@app.route('/webhook/<string:token>', methods=['POST'])
def webhook(token):
    payload = request.get_json()
    print(f"\n✅ Webhook recebido com token: {token}")
    print(json.dumps(payload, indent=2))
    return {'status': 'ok', 'token': token}, 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
