# devices/charger_flask.py
from flask import Flask
import threading, requests, random, time
from datetime import datetime

app = Flask(__name__)

SERVER_URL = ""  # NGINX가 열려있는 주소와 포트

CLIENT_CERT = ""  #인증서 경로
CLIENT_KEY = ""
Intermediate_CA = ""

DEVICE_NAME = "charger"




NORMAL_MIN = 2.0
NORMAL_MAX = 2.1
ABNORMAL_MIN = 2.11
ABNORMAL_MAX = 2.25

STEP = 0.005
SEND_INTERVAL = 1
ERROR_PROBABILITY = 0.01  # 확률 낮춤 (기존보다 에러 덜 발생)

def send_value(val):
    payload = {
        "device": DEVICE_NAME,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "value": round(val, 3)
    }
    print(f"[→] 송신: {payload}")
    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            cert=(CLIENT_CERT, CLIENT_KEY),  # 디바이스 인증서 + 키 (클라이언트 인증)
            verify=ROOT_CA  # 서버 인증서 유효성 검증 (서버 신뢰)
        )
    except:
        print("[X] 전송 실패")

def sensor_loop():
    current = random.uniform(NORMAL_MIN, NORMAL_MAX)
    err_mode = False
    err_count = 0
    target_err_count = 0
    direction = 1
    check_counter = 0
    CHECK_INTERVAL = 5  # 에러 진입 시도는 5초에 한 번만

    while True:
        check_counter += 1
        if not err_mode and check_counter % CHECK_INTERVAL == 0:
            if random.random() < ERROR_PROBABILITY:
                err_mode = True
                target_err_count = random.choices([random.randint(1, 2), 20], weights=[0.6, 0.4])[0]
                err_count = 0
                direction = 1
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

            if random.random() < 0.02:
                send_value(round(random.uniform(NORMAL_MAX + 0.005, NORMAL_MAX + 0.015), 3))
            else:
                send_value(current)

        time.sleep(SEND_INTERVAL)

@app.route('/')
def home():
    return "Charger simulator is running.", 200

if __name__ == '__main__':
    threading.Thread(target=sensor_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)