from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# RDS 접속 정보 (환경변수로 설정하세요)
#DB_USER = os.getenv('admin')
#DB_PASS = os.getenv('welcome1')
#DB_HOST = os.getenv('iot-db.c5a4e0ooeip0.us-east-2.rds.amazonaws.com')
#DB_NAME = os.getenv('smart_factory')


DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')



app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class DeviceLog(db.Model):                                       # int = Integer
    __tablename__ = 'device_logs'
    device_name = db.Column(db.String(64), nullable=False, primary_key=True)
    line_name   = db.Column(db.String(64), nullable=False)
    value       = db.Column(db.Float, nullable=False)
    status      = db.Column(db.Enum('normal','abnormal'), nullable=False)
    log_time    = db.Column(db.DateTime, nullable=False)

# 디바이스 상태 테이블 모델
# ------------------------
class DeviceStatus(db.Model):
    __tablename__ = 'device_status'
    id           = db.Column(db.Integer, nullable=False, primary_key=True)
    device_name  = db.Column(db.String(64), nullable=False)
    line         = db.Column(db.String(64), nullable=False)
    is_abnormal  = db.Column(db.Boolean, nullable=False)
    timestamp    = db.Column(db.DateTime, nullable=True)

class ErrorLog(db.Model):
    __tablename__ = 'error_logs_dashboard'
    id             = db.Column(db.Integer, nullable=False, primary_key=True)
    device_name    = db.Column(db.String(64), nullable=True)
    line_name      = db.Column(db.String(64), nullable=True)
    abnormal_count = db.Column(db.Integer, nullable=True)
    last_abnormal_value = db.Column(db.Float, nullable=True)
    created_at      = db.Column(db.DateTime, nullable=True)

@app.route('/')
def index():
    return render_template('dashboard1.html')

@app.route('/api/device-data')
def device_data():
    device = request.args.get('device')
    if not device:
        return jsonify({'error': 'device 파라미터가 필요합니다.'}), 400

    # 가장 최근 로그 한 건 조회
    log = (
        DeviceLog.query
        .filter_by(device_name=device)
        .order_by(desc(DeviceLog.log_time))
        .first()
    )

    # 로그가 있고, log_time이 '지금'으로부터 3초 이내라면 값 사용
    if log:
        now = datetime.utcnow()
        if now - log.log_time <= timedelta(seconds=3):
            val = log.value
        else:
            # 새 로그가 없으면 0
            val = 0
    else:
        # 테이블에 아예 로그가 없으면 0
        val = 0
    
    print(f"device: {device}, log_time: {getattr(log, 'log_time', None)}, val: {val}")

    return jsonify({'value': val})


# 디바이스 상태 조회 API
# ------------------------
@app.route('/api/device-status/all')
def all_device_status():
    # 예: ['Washer', 'Charger', 'Capping', 'Labeling']
    device_names = request.args.getlist('deviceNames')    
    recs = (db.session.query(DeviceStatus)
              .filter(DeviceStatus.device_name.in_(device_names))
              .order_by(DeviceStatus.device_name, DeviceStatus.timestamp.desc())
              .all())

    # device_name별로 가장 최신 rec만 뽑기
    latest = {}
    for r in recs:
        if r.device_name not in latest:
            latest[r.device_name] = r.is_abnormal

    # 기본값은 0으로 채워두기
    result = [
      {'device_name': name, 'is_abnormal': latest.get(name, 0)}
      for name in device_names
    ]
    return jsonify(result)


# 에러 로그 실시간 생성 여부 조회 API
# -----------------------------------
@app.route('/api/error-log/all')
def all_error_log_status():
    # DB에 등록된 고유 device_name 목록 추출
    device_names = [row[0] for row in db.session.query(ErrorLog.device_name).distinct()]
    
    latest = {}
    for device in device_names:
        # device_name별로 가장 최신 created_at 로그 한 건 조회
        log = (
            ErrorLog.query
            .filter_by(device_name=device)
            .order_by(desc(ErrorLog.created_at))
            .first()
        )
        # 로그가 있고, 가장 최신 로그의 created_at이 지금으로부터 5초 이내면 True, 아니면 False
        if log and datetime.utcnow() - log.created_at <= timedelta(seconds=5):
            latest[device] = True
        else:
            latest[device] = False

    # 결과 포맷: [{'device_name': 'Washer', 'has_log': True}, …]
    result = [
        {'device_name': name, 'has_log': latest.get(name, False)}
        for name in device_names
    ]
    return jsonify(result)


if __name__ == '__main__':
# 개발용: 0.0.0.0 바인딩, 디버그 모드 켬
    app.run(host='0.0.0.0', port=3000, debug=True)
