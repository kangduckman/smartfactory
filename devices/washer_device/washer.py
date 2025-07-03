from flask import Flask
import threading
import requests
import random
import time
from datetime import datetime

app = Flask(__name__)

# 서버 URL 설정
SERVER_URL_1 = "https://10.1.2.232/data"  # NGINX가 열려있는 주소와 포트



CLIENT_CERT = ""
CLIENT_KEY = ""
Intermediate_CA = ""


SEND_INTERVAL = 1
CHECK_INTERVAL = 5
ERROR_PROBABILITY = 0.01

DEVICE_NAME = "washer"
NORMAL_MIN = 50
NORMAL_MAX = 80
STEP = 1




def send_value(val):
    payload = {
        "device": DEVICE_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "value": round(val, 3)
    }

    try:
        response = requests.post(
            SERVER_URL,
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



def send_status(val):

    # ② 점프서버로 보낼 헬스체크 데이터
    health_payload = {
        "device_name": DEVICE_NAME,
        "status": "healthy"
    }
    try:
        res2 = requests.post(SERVER_URL_2, json=health_payload, timeout=3)
        print(f"[✔] {SERVER_URL_2} 전송 성공 (status {res2.status_code})")
    except Exception as e:
        print(f"[X] {SERVER_URL_2} 전송 실패: {e}")

def sensor_loop():
    current = random.uniform(NORMAL_MIN, NORMAL_MAX)
    err_mode = False
    err_count = 0
    target_err_count = 0
    direction = 1
    check_counter = 0

    while True:
        check_counter += 1

        #  CHECK_INTERVAL 주기로 상태 전송 (헬스체크)
        if check_counter % CHECK_INTERVAL == 0:
            send_status("healthy")

        # 에러 상태 진입 판단
        if not err_mode and check_counter % CHECK_INTERVAL == 0:
            if random.random() < ERROR_PROBABILITY:
                err_mode = True
                err_count = 0
                direction = 1
                target_err_count = random.choices(
                    [random.randint(1, 2), 20], weights=[0.6, 0.4]
                )[0]
                print(f"[!] 이상 상태 진입: {target_err_count}회")

        if err_mode:
            current += STEP * direction
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

            # 정상값 or 잡음 포함 전송
            if random.random() < 0.02:
                noise = random.uniform(0.005, 0.02)
                send_value(round(NORMAL_MAX + noise, 3))
            else:
                send_value(current)


@app.route('/')
def home():
    return f"{DEVICE_NAME} simulator is running.", 200


# ✅ 센서 상태 확인용 GET 라우트 추가
@app.route('/status', methods=['GET'])
def status():
    return {
        "device": DEVICE_NAME,
        "status": "on"
    }, 200

if __name__ == '__main__':
    threading.Thread(target=sensor_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)



