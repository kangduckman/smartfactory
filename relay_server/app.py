from flask import Flask, request, jsonify
from datetime import datetime
import pymysql

app = Flask(__name__)
# DB 설정
db_config = {
    "host": "your-rds-endpoint.amazonaws.com",
    "user": "admin",
    "password": "your_password",
    "database": "smart_factory",
    "charset": "utf8mb4",
    "autocommit": True
}

# 디바이스 정상 범위 기준
DEVICE_CONFIG = {
    "washer":   {"normal_min": 55,   "normal_max": 65},
    "charger":  {"normal_min": 2.0,  "normal_max": 2.1},
    "capper":   {"normal_min": 0.85, "normal_max": 1.1},
    "labeling": {"normal_min": 0.45, "normal_max": 0.6}
}

# 디바이스별 라인 이름 정의
DEVICE_LINE_MAP = {
    "washer":   "line_1",
    "charger":  "line_1",
    "capper":   "line_1",
    "labeling": "line_1"
}

# 로그 저장 함수
def insert_device_log(device_name, line_name, value, status):
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO device_logs (device_name, line_name, value, status)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (device_name, line_name, value, status))
    finally:
        conn.close()

# 데이터 수신 엔드포인트
@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    device = data.get("device")
    value = data.get("value")

    if not device or value is None:
        return jsonify({"error": "missing device or value"}), 400

    config = DEVICE_CONFIG.get(device)
    if not config:
        return jsonify({"error": "unknown device"}), 400

    line_name = DEVICE_LINE_MAP.get(device, "line_1")
    is_normal = config["normal_min"] <= value <= config["normal_max"]
    status = "normal" if is_normal else "abnormal"

    print(f"[📦] {device}({line_name}): 수신값={value}, 상태={status}")
    insert_device_log(device, line_name, value, status)

    return jsonify({"status": "saved"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
from datetime import datetime
import pymysql

app = Flask(__name__)

db_config = {
    "host": "your-rds-endpoint.amazonaws.com",
    "user": "admin",
    "password": "your_password",
    "database": "smart_factory",
    "charset": "utf8mb4",
    "autocommit": True
}

DEVICE_CONFIG = {
    "washer":   {"normal_min": 55,   "normal_max": 65},
    "charger":  {"normal_min": 2.0,  "normal_max": 2.1},
    "capper":   {"normal_min": 0.85, "normal_max": 1.1},
    "labeling": {"normal_min": 0.45, "normal_max": 0.6}
}

DEVICE_LINE_MAP = {
    "washer":   "line_1",
    "charger":  "line_1",
    "capper":   "line_1",
    "labeling": "line_1"
}

def insert_device_log(device_name, line_name, value, status):
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO device_logs (device_name, line_name, value, status)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (device_name, line_name, value, status))
    finally:
        conn.close()

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    device = data.get("device")
    value = data.get("value")

    if not device or value is None:
        return jsonify({"error": "missing device or value"}), 400

    config = DEVICE_CONFIG.get(device)
    if not config:
        return jsonify({"error": "unknown device"}), 400

    line_name = DEVICE_LINE_MAP.get(device, "line_1")
    is_normal = config["normal_min"] <= value <= config["normal_max"]
    status = "normal" if is_normal else "abnormal"

    insert_device_log(device, line_name, value, status)
    return jsonify({"status": "saved"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

