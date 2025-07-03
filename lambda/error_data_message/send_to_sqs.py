import pymysql
import boto3
import json
import os

# SQS 설정
sqs = boto3.client('sqs', region_name='us-east-2')
QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/207567776727/err_logs_sns_q"

# RDS 연결 정보
conn = pymysql.connect(
    host=os.environ['RDS_HOST'],
    user=os.environ['RDS_USER'],
    password=os.environ['RDS_PASSWORD'],
    db=os.environ['RDS_DB'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def lambda_handler(event, context):
    print("[✅] Lambda 실행 시작")

    try:
        connection = pymysql.connect(**rds_config)
        with connection.cursor() as cursor:
            # ❶ 전송할 데이터 선택
            sql = "SELECT * FROM error_logs_sns LIMIT 30"
            cursor.execute(sql)
            rows = cursor.fetchall()

            print(f"[📦] 읽은 행 수: {len(rows)}")

            for row in rows:
                message_body = {
                    "device_name": row["device_name"],
                    "line_name": row["line_name"],
                    "abnormal_count": row["abnormal_count"],
                    "last_abnormal_value": row["last_abnormal_value"]
                }
                print(message_body)

                # ❷ SQS 전송
                response = sqs.send_message(
                    QueueUrl=QUEUE_URL,
                    MessageBody=json.dumps(message_body)
                )
                print(f"[→] SQS 전송 성공: {response['MessageId']}")

                # ❸ 전송된 행 삭제
                delete_sql = "DELETE FROM error_logs_sns WHERE id = %s"
                cursor.execute(delete_sql, (row["id"],))

            connection.commit()

        return {
            "statusCode": 200,
            "body": f"{len(rows)} rows processed and deleted"
        }

    except Exception as e:
        print(f"[❌] 오류 발생: {str(e)}")
        return {
            "statusCode": 500,
            "error": str(e)
        }