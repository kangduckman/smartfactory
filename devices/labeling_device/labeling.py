from flask import Flask
import threading
import requests
import random
import time
from datetime import datetime

app = Flask(__name__)

# 서버 URL 설정
SERVER_URL_1 = "https://10.1.2.232/data"        # 데이터 전송용 (mTLS)

# 인증서 경로
CLIENT_CERT = ""
CLIENT_KEY  = ""
Intermediate_CA= ""

SEND_INTERVAL = 1
CHECK_INTERVAL = 5
ERROR_PROBABILITY = 5

DEVICE_NAME = "labeling"
NORMAL_MIN = 0.45
NORMAL_MAX = 0.6
ABNORMAL_MIN = 0.61
ABNORMAL_MAX = 0.7
STEP = 0.01

def send_value(val):
    payload = {
        "device": DEVICE_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "value": round(val, 3)
    }

    try:
        response = requests.post(
            SERVER_URL_1,
            json=payload,
            cert=(CLIENT_CERT, CLIENT_KEY),
            verify=ROOT_CA,
            timeout=5
        )
        print(f"[→] Sent: {payload} | Response: {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"[SSL ERROR] 인증서 검증 실패: {e}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 요청 실패: {e}")


def sensor_loop():
    current = random.uniform(NORMAL_MIN, NORMAL_MAX)
    err_mode = False
    err_count = 0
    target_err_count = 0
    direction = 1
    check_counter = 0

    while True:
        check_counter += 1

        # 주기적 상태 전송
#        if check_counter % CHECK_INTERVAL == 0:
#            send_status("healthy")

        # 에러 진입 여부 판단
        if not err_mode and check_counter % CHECK_INTERVAL == 0:
            if random.random() < ERROR_PROBABILITY:
                err_mode = True
                err_count = 0
                direction = 1
                target_err_count = random.choices([random.randint(1, 2), 20], weights=[0.6, 0.4])[0]
                print(f"[!] 이상 상태 진입: {target_err_count}회")

        if err_mode:
            current += STEP * direction
            if current > ABNORMAL_MAX:
                direction = -1
                current = ABNORMAL_MAX
            elif current < ABNORMAL_MIN:
                direction = 1
                current = ABNORMAL_MIN
            send_value(current)
            err_count += 1
            if err_count >= target_err_count:
                err_mode = False
                print("[✔] 이상 종료 후 정상 복귀")
                current = NORMAL_MAX

        else:
            current += STEP * direction
            if current > NORMAL_MAX:
                direction = -1
                current = NORMAL_MAX
            elif current < NORMAL_MIN:
                direction = 1
                current = NORMAL_MIN

            # 미세 잡음 포함 여부
            if random.random() < 0.02:
                noise = random.uniform(0.01, 0.03)
                send_value(round(NORMAL_MAX + noise, 3))
            else:
                send_value(current)

        time.sleep(SEND_INTERVAL)

@app.route('/')
def home():
    return f"{DEVICE_NAME} simulator is running.", 200

@app.route('/status', methods=['GET'])
def status():
    return {
        "device": DEVICE_NAME,
        "status": "on"
    }, 200

if __name__ == '__main__':
    threading.Thread(target=sensor_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5002)


