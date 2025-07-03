import pymysql
import os
from datetime import datetime
import traceback



def lambda_handler(event, context):
    # 1. 알람 이름 및 상태 추출
    alarm_name = event['detail']['alarmName']
    print(f"[DEBUG] alarm_name 원본: {alarm_name}")

    device_name = alarm_name.replace('_alarm', '')
    print(f"[DEBUG] device_name 최종: {device_name}")

    state = event['detail']['state']['value']
    timestamp = event['detail']['state']['timestamp']

    try:
        # 1. 알람 이름 및 상태 추출
        alarm_name = event['detail']['alarmName']                                     # 예: washer_alarm
        device_name = alarm_name.replace('_alarm', '').replace('_alram', '')
        device_name = device_name.capitalize()                                        # 예: washer
        state = event['detail']['state']['value']
        timestamp = event['detail']['state']['timestamp']

        # 2. 상태 파싱
        is_abnormal = 1 if state == 'OK' else 0  # OK → 정상(1), ALARM → 비정상(0)
        line = '1'  # 고정값

        # 3. DB 연결
        conn = pymysql.connect(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            db=os.environ['RDS_DB'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        # 4. INSERT 실행
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO device_status (device_name, line, is_abnormal, timestamp)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (device_name, line, is_abnormal, datetime.utcnow()))

        conn.commit()
        conn.close()

        print(f"[✅] 기록 완료: {device_name}, 상태: {state}")
        return {'statusCode': 200, 'body': '기록 성공'}

    except Exception as e:
        print(f"[❌] 에러 발생: {str(e)}")
        traceback.print_exc()
        return {'statusCode': 500, 'body': f'에러: {str(e)}'}
