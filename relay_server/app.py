from flask import Flask, request, jsonify
from datetime import datetime
import pymysql
import time

app = Flask(__name__)

# ✅ RDS DB 설정
db_config = {}

# ✅ 디바이스 정상 범위
DEVICE_CONFIG = {
    "washer":   {"normal_min": 55,   "normal_max": 65},
    "charger":  {"normal_min": 2.0,  "normal_max": 2.1},
    "capping":  {"normal_min": 0.85, "normal_max": 1.1},
    "labeling": {"normal_min": 0.45, "normal_max": 0.6}
}

# ✅ 디바이스별 라인 이름
DEVICE_LINE_MAP = {
    "washer":   "line_1",
    "charger":  "line_1",
    "capper":   "line_1",
    "labeling": "line_1"
}

# ✅ 로그 저장 함수 + Deadlock 자동 재시도 포함
def insert_device_log(device_name, line_name, value, status, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            conn = pymysql.connect(**db_config, autocommit=True)
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO device_logs (device_name, line_name, value, status, log_time)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    device_name, line_name, value, status, datetime.now()
                ))
            conn.close()
            break  # 성공 시 루프 탈출
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1213:  # Deadlock
                print(f"[DEADLOCK] 재시도 {attempt}/{max_retries}... (0.1s 대기)")
                time.sleep(0.1)
            else:
                print(f"[DB ERROR] OperationalError: {e}")
                break
        except Exception as e:
            print(f"[DB ERROR] 기타 예외: {e}")
            break

# 상태 수신 테스트용
@app.route("/status", methods=["POST"])
def receive_status():
    data = request.get_json()
    print("[app] 수신된 상태 데이터:", data)
    return jsonify({"status": "status received"})

# 기본 페이지
@app.route("/")
def home():
    return "app.py is running", 200

if __name__ == "__main__":
    print("[✓] app.py 서버 실행됨")
    app.run(host="0.0.0.0", port=5000)



