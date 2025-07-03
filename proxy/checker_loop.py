import requests
import boto3
import time
from concurrent.futures import ThreadPoolExecutor

cloudwatch = boto3.client('cloudwatch', region_name='us-east-2')

SENSOR_URLS = {
    'washer':   'http://10.0.10.192:5000/status',
    'capping':  'http://10.0.10.117:5001/status',
    'labeling': 'http://10.0.10.132:5002/status',
    'charger':  'http://10.0.10.254:5003/status'
}

last_seen = {sensor: 0 for sensor in SENSOR_URLS}
CHECK_INTERVAL = 1       # 센서 상태 확인 주기 (초)
OFF_THRESHOLD = 4        # 응답 없을 때 꺼짐으로 판단할 시간 (초)

def report_all_status(metrics):
    # 여러 센서 상태를 한 번에 CloudWatch로 전송
    cloudwatch.put_metric_data(
        Namespace='SensorHealth',
        MetricData=metrics
    )

def check_sensor(sensor, url):
    current_time = time.time()
    try:
        res = requests.get(url, timeout=3)
        data = res.json()
        status = data.get('status')
        value = 1 if status == 'on' else 0
        last_seen[sensor] = current_time
    except:
        # 일정 시간 이상 응답 없으면 꺼짐으로 판단
        if current_time - last_seen[sensor] >= OFF_THRESHOLD:
            value = 0
        else:
            return None  # 너무 빠르게 꺼졌다고 판단하지 않음

    print(f"[CloudWatch] {sensor}: {value}")
    return {
        'MetricName': f"{sensor}_health",
        'Value': value,
        'Unit': 'Count'
    }

while True:
    with ThreadPoolExecutor(max_workers=len(SENSOR_URLS)) as executor:
        futures = {executor.submit(check_sensor, sensor, url): sensor for sensor, url in SENSO>        metric_data = []
        for future in futures:
            result = future.result()
            if result:
                metric_data.append(result)

        if metric_data:
            report_all_status(metric_data)

    time.sleep(CHECK_INTERVAL)


