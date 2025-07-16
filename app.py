from flask import Flask, render_template, request, jsonify, Response
import socket
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__)

cred = credentials.Certificate(r"C:\Users\BEHİYE NUR\OneDrive\Desktop\firebase\firebase_config.json") 
firebase_admin.initialize_app(cred)
db = firestore.client()

def check_port(ip, port):
    try:
        port = int(port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            return port, result == 0
    except:
        return port, False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/singlescan')
def single_scan():
    ip = request.args.get('ip')
    port = request.args.get('port')

    if not ip or not port:
        return jsonify({"error": "IP ve port gereklidir."}), 400

    port, status = check_port(ip, port)
    status_text = "Açık" if status else "Kapalı"

    db.collection("scans").add({
        "ip": ip,
        "port": int(port),
        "status": status_text,
        "timestamp": datetime.utcnow(),
        "scan_type": "single"
    })

    return jsonify({"port": port, "status": status_text})

@app.route('/api/multiscan')
def multi_scan():
    ip = request.args.get('ip')
    try:
        start_port = int(request.args.get('start'))
        end_port = int(request.args.get('end'))
    except:
        return jsonify({"error": "Port numaraları geçerli değil."}), 400

    if start_port > end_port or start_port < 0 or end_port > 65535:
        return jsonify({"error": "Geçersiz port aralığı."}), 400

    results = []
    for port in range(start_port, end_port + 1):
        p, status = check_port(ip, port)
        status_text = "Açık" if status else "Kapalı"
        results.append({"port": p, "status": status_text})

        db.collection("scans").add({
            "ip": ip,
            "port": p,
            "status": status_text,
            "timestamp": datetime.utcnow(),
            "scan_type": "multi"
        })

    return jsonify(results)

@app.route('/api/history')
def api_history():
    docs = db.collection("scans").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    history_data = []
    for doc in docs:
        entry = doc.to_dict()
        # UTC zamanına +3 saat ekle
        ts = entry.get("timestamp") + timedelta(hours=3)
        history_data.append({
            "ip": entry.get("ip"),
            "port": entry.get("port"),
            "status": entry.get("status"),
            "timestamp": ts.strftime('%d-%m-%Y %H.%M'),
            "scan_type": entry.get("scan_type", "unknown")
        })
    return Response(json.dumps(history_data, ensure_ascii=False), mimetype='application/json')


@app.route('/history')
def history():
    docs = db.collection("scans").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    history = []
    for doc in docs:
        entry = doc.to_dict()
        ts = entry.get("timestamp") + timedelta(hours=3)
        history.append({
            "ip": entry.get("ip"),
            "port": entry.get("port"),
            "status": entry.get("status"),
            "timestamp": ts.strftime('%d-%m-%Y %H.%M'),
            "scan_type": entry.get("scan_type", "unknown")
        })
    return render_template('history.html', history=history)
if __name__ == '__main__':
    app.run(debug=True)
