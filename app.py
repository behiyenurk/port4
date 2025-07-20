from flask import Flask, render_template, request, jsonify, Response
import socket
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__, static_folder="static", static_url_path="/static")

cred = credentials.Certificate("firebase_config.json") 
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

    print("Adım 1: IP ve port geldi mi?", ip, port)

    if not ip or not port:
        print("Adım 2: IP veya port eksik")
        return jsonify({"error": "IP ve port gereklidir."}), 400

    port, status = check_port(ip, port)
    print("Adım 3: Port kontrolü tamamlandı")

    status_text = "Açık" if status else "Kapalı"
    data = {
        "ip": ip,
        "port": int(port),
        "status": status_text,
        "timestamp": datetime.utcnow(),
        "scan_type": "single"
    }

    print("Adım 4: Kaydedilecek veri", data)

    try:
        db.collection("scans").add(data)
        print("Adım 5: Firestore kaydı başarılı")
    except Exception as e:
        print("Adım 5: Firestore HATASI:", e)
        return jsonify({"error": f"Kayıt hatası: {e}"}), 500

    print("Adım 6: API yanıtı dönülüyor")
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
        ts = entry.get("timestamp") + timedelta(hours=3)
        history_data.append({
            "ip": entry.get("ip"),
            "port": entry.get("port"),
            "status": entry.get("status"),
            "timestamp_display": ts.strftime('%d-%m-%Y %H:%M'),
            "timestamp_iso": ts.isoformat(),
            "scan_type": entry.get("scan_type", "unknown")
        })
    return Response(json.dumps(history_data, ensure_ascii=False), mimetype='application/json')


@app.route('/history')
def history():
    docs = db.collection("scans").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    history = []
    for doc in docs:
        entry = doc.to_dict()
        ts = entry.get("timestamp") + timedelta(hours=3)  # UTC+3 düzeltmesi

        history.append({
            "ip": entry.get("ip"),
            "port": entry.get("port"),
            "status": entry.get("status"),
            "timestamp_display": ts.strftime('%d-%m-%Y %H:%M'),  # 🟢 Ekranda gözüken
            "timestamp_iso": ts.isoformat(),                     # 🟢 data-date için
            "scan_type": entry.get("scan_type", "unknown")
        })
        print(f"{len(history)} kayıt yüklendi")

    return render_template('history.html', history=history)


if __name__ == '__main__':
    app.run(debug=True)
