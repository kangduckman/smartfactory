import json
import urllib.request
from datetime import datetime, timedelta

def lambda_handler(event, context):
    try:
        # ✅ Records 키가 없으면 조용히 return (로그도 출력 안 함)
        if 'Records' not in event or 'Sns' not in event['Records'][0]:
            return {
                'statusCode': 200,
                'body': '이벤트 무시됨 (Records 없음)'
            }

        sns_record = event['Records'][0]['Sns']
        message_str = sns_record.get('Message', '{}')
        message_json = json.loads(message_str)

        alarm_name = message_json.get('AlarmName', '알 수 없음')
        timestamp = message_json.get('StateChangeTime', '시간 없음')
        state = message_json.get('NewStateValue', 'UNKNOWN')

        # 센서 이름 추출
        sensor_key = alarm_name.replace('_alram', '').strip()  # 오타 그대로 유지

        # 센서 이모지 & 이미지 매핑
        sensor_info = {
            'washer':   {"name": "Washer", "emoji": "🧼", "image": "https://i.imgur.com/n9D5M1h.png"},
            'capping':  {"name": "Capping", "emoji": "🔩", "image": "https://i.imgur.com/92qgWEC.png"},
            'labeling': {"name": "Labeling", "emoji": "🏷️", "image": "https://i.imgur.com/UM2RpYt.png"},
            'charger':  {"name": "Charger", "emoji": "🔌", "image": "https://i.imgur.com/4kYTqM7.png"}
        }

        sensor = sensor_info.get(sensor_key, {"name": sensor_key, "emoji": "❓", "image": None})

        # 시간 변환 (UTC → KST)
        try:
            dt_utc = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
            dt_kst = dt_utc + timedelta(hours=9)
            timestamp_kst = dt_kst.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            timestamp_kst = timestamp

        # 상태별 메시지 구성
        if state == 'ALARM':
            slack_text = f"{sensor['emoji']} *[{sensor['name']}] OFF*\n시간: `{timestamp_kst}`"
        elif state == 'OK':
            slack_text = f"{sensor['emoji']} *[{sensor['name']}] ON*\n시간: `{timestamp_kst}`"
        else:
            slack_text = f"⚠ *[{sensor['name']}] 알 수 없는 상태 ({state})*\n시간: `{timestamp_kst}`"

        if not slack_text.strip():
            slack_text = "⚠ 센서 상태 메시지를 생성할 수 없습니다."

        # Slack 메시지 payload
        slack_payload = {
            "attachments": [
                {
                    "color": "#ff4d4d" if state == "ALARM" else "#36a64f",
                    "title": slack_text,
                    "thumb_url": sensor["image"] or "",
                    "footer": "Pack'tory Pulse",
                    "ts": int(__import__("time").time())
                }
            ]
        }

    except Exception as e:
        slack_payload = {
            "attachments": [
                {
                    "color": "#cc0000",
                    "title": f"⚠ Lambda 내부 오류 발생: {e}",
                    "footer": "Pack'tory Pulse"
                }
            ]
        }

    # Slack Webhook 전송
    webhook_url = ""
    data = json.dumps(slack_payload).encode('utf-8')
    req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as res:
            print(f"✅ Slack 응답 코드: {res.status}")
    except Exception as e:
        print(f"❌ Slack 전송 실패: {e}")

    return {
        'statusCode': 200,
        'body': 'Slack 메시지 전송 완료'
    }
