import boto3
from flask import Flask, request
import requests

app = Flask(__name__)


# CloudWatch 클라이언트 (us-east-2 리전으로 설정)
cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-2')

@app.route('/status', methods=['POST'])
def receive_send_status():
    try:
        data = request.get_json()
        print("[proxy] 수신된 상태 데이터:", data)

        device = data.get("device") or data.get("device_name")
        status = data.get("status")

        if not device or status is None:
            return "Missing 'device' or 'status' field", 400

        # ✅ CloudWatch로 전송
        cloudwatch_client.put_metric_data(
            Namespace='SensorHealth',
            MetricData=[
                {
                    'MetricName': f"{device}_health",
                    'Value': 1 if status == "on" else 0,
                    'Unit': 'Count'
                }
            ]
        )
        print(f"[CloudWatch] {device}_health: {'1' if status == 'on' else '0'} 전송 완료")

        return "OK", 200

    except Exception as e:
        print("[X] 상태 처리 중 예외 발생:", e)
        return "Internal Server Error", 500

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001, debug=True)

