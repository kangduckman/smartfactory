import json
import boto3
from datetime import datetime

sns_client = boto3.client("sns")
SNS_TOPIC_ARN = ""


def lambda_handler(event, context):
    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
        except json.JSONDecodeError:
            body = record["body"]

        print(body, 'body###')

        print(f"[📩] 수신된 메시지: {body}")

        # SNS에 JSON 형식으로 보낼 메시지 구성
        sns_payload = {
            "line": body.get("line_name"),
            "device": body.get("device_name"),
            "value": body.get("last_abnormal_value"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        print(sns_payload, 'payload###')

        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(sns_payload),  # ✅ JSON 문자열로 전송!
            Subject="[스마트팩토리 경고]"
        )

        print(f"[✅] SNS 전송 결과: {response}")

    return {
        "statusCode": 200,
        "body": json.dumps("메시지 처리 완료")
    }
