// 파일 최상단에 전역 타이머 변수 추가
let errorWarningTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
  initDashboard();
  initStatusWindows();
  setInterval(syncStatusFromData, 1000);
  initErrorWarning();
  setInterval(syncErrorLogs, 1000);
});

function initDashboard() {
  initWasherThermometer();
  initChargerDisplay();
  initCappingBar();
  initLabelingGauge();
}

function initWasherThermometer() {
  const mercuryEl   = document.querySelector('.thermometer-mercury');
  const thermometerEl = document.querySelector('.thermometer');
  const tempValueEl = document.getElementById('washer-temp');

  /**
   * JS에서 newLevelPercent를 받아
   * 1) CSS 변수(--level) 업데이트
   * 2) mercury 높이(mercuryEl.style.height) 업데이트
   * 3) 색상 계산→CSS 변수(--mercury-color) & tempValueEl.style.color 적용
   * 4) 텍스트 갱신
   *
   * @param {number} newLevelPercent 0~100
   */
  function updateWasherThermometer(newLevelPercent) {
    const level = Math.min(Math.max(newLevelPercent, 0), 100);
    // CSS 변수 셋팅
    thermometerEl.style.setProperty('--level', `${level}%`);
    // mercury 높이 직접 조절 (CSS var 의존 없이)
    mercuryEl.style.height = `${level}%`;
    // 색상 로직
    let color;
    if (level === 0) {
      color = 'rgb(0, 0, 0)';
    } else if (level < 55) {
      color = 'rgb(60, 60, 250)';
    } else if (level <= 65) {
      color = 'rgb(60, 250, 60)';
    } else {
      color = 'rgb(250, 60, 60)';
    }

    thermometerEl.style.setProperty('--mercury-color', color);
    tempValueEl.style.color = color;
    // 텍스트 표시
    tempValueEl.textContent = Math.round(level);

    // → 55 미만이거나 65 초과일 때 data-window 테두리 깜빡임
    const dataWin = tempValueEl.closest('.data-window');
    if (level < 55 || level > 65) {
      dataWin.classList.add('blink-alert');
    } else {
      dataWin.classList.remove('blink-alert');
    }
  }

  // 초기값 0으로 세팅
  updateWasherThermometer(0);

  // 1초 뒤부터 fetch로 바로 데이터 연동
  setTimeout(() => {
    // fetch + 업데이트 함수
    const fetchAndUpdate = () => {
      fetch('/api/device-data?device=Washer')
        .then(res  => res.json())
        .then(data => updateWasherThermometer(data.value))
        .catch(err => {
          console.error('Washer API error:', err);;
          // 데이터 없으면 0으로 세팅(OFF 처리)
          updateWasherThermometer(0);
        });
    };

    // 첫 호출
    fetchAndUpdate();
    // 이후 1초마다 반복 호출
    setInterval(fetchAndUpdate, 1000);
  }, 1000);
}


function initChargerDisplay() {
  // Charger 디지털 숫자판 요소 가져오기
  const chargerValueEl = document.getElementById('charger-vibe');

  function updateChargerDisplay(newNumber) {
    let num = parseFloat(newNumber);
    if (isNaN(num)) num = 0;
    num = Math.min(Math.max(num, 0), 99.9);

    chargerValueEl.textContent = num.toFixed(2);

    // 색상 변경
    if (num === 0) {
      chargerValueEl.style.color = 'rgb(250, 250, 250)';
    } else if (num < 2.0) {
      chargerValueEl.style.color = 'rgb(60, 60, 250)';
    } else if (num <= 2.1) {
      chargerValueEl.style.color = 'rgb(60, 250, 60)';
    } else {
      chargerValueEl.style.color = 'rgb(250, 60, 60)';
    }

    // → 2.0 미만이거나 2.1 초과일 때 data-window 테두리 깜빡임
    const dataWin = chargerValueEl.closest('.data-window');
    if (num < 2.0 || num > 2.1) {
      dataWin.classList.add('blink-alert');
    } else {
      dataWin.classList.remove('blink-alert');
    }
  }

  // 초기값
  updateChargerDisplay(0);

  // 1초 후부터 API 호출 시작
  setTimeout(() => {
    const fetchAndUpdate = () => {
      fetch('/api/device-data?device=Charger')
        .then(res => res.json())
        .then(data => updateChargerDisplay(data.value))
        .catch(err => {
          console.error('Charger API error:', err);
          updateChargerDisplay(0);
        });
    };

    fetchAndUpdate();                  // 초기 1회 호출
    setInterval(fetchAndUpdate, 1000); // 이후 1초마다 호출
  }, 1000);
}



function initCappingBar() {
  const barEl = document.getElementById('capping-bar');
  const numberEl = document.getElementById('capping-torque');
  const containerEl = document.querySelector('.capping-container');

  const maxTorque = 2.5; // 실제 최대 토크값에 맞춰 수정

  function animateCappingTorque(torqueValue) {
    let val = parseFloat(torqueValue);
    if (isNaN(val) || val < 0) val = 0;
    if (val > maxTorque) val = maxTorque;

    const containerHeight = parseFloat(getComputedStyle(containerEl).height);
    let targetHeight = (val / maxTorque) * containerHeight;
    targetHeight = Math.min(targetHeight, containerHeight);

    let color;
    if (val === 0) {
      color = 'rgb(0, 0, 0)';
    } else if (val < 0.85) {
      color = 'rgb(60, 60, 250)';
    } else if (val <= 1.1) {
      color = 'rgb(60, 250, 60)';
    } else {
      color = 'rgb(250, 60, 60)';
    }

    // 막대 색상 & 높이 설정
    barEl.style.backgroundColor = color;
    barEl.style.height = targetHeight + 'px';

    // 막대 위 숫자 업데이트 & 색상 변경
    numberEl.textContent = val.toFixed(2);
    numberEl.style.color = color;
    
    // → 0.85 미만이거나 1.1 초과일 때 data-window 테두리 깜빡임
    const dataWin = numberEl.closest('.data-window');
    if (val < 0.85 || val > 1.1) {
      dataWin.classList.add('blink-alert');
    } else {
      dataWin.classList.remove('blink-alert');
    }

    // 일정 시간(0.5초) 후에 막대 낮추기
    setTimeout(() => {
      barEl.style.height = '0px';
      barEl.style.backgroundColor = 'rgb(0, 0, 0)';
      // 숫자도 리셋하고, 색상도 기본(#333)으로 돌리고 싶으면 아래처럼
      numberEl.textContent = '0.00';
      numberEl.style.color = 'rgb(0, 0, 0)';
    }, 500);

    // (선택) 막대가 내려간 뒤 숫자 색상을 기본으로 돌리고 싶으면 아래 주석 해제
    // setTimeout(() => {
    //   numberEl.style.color = '#333';
    // }, 800);
  }

  animateCappingTorque(0);

  // 1초 후부터 API 호출 시작
  setTimeout(() => {
    const fetchAndUpdate = () => {
      fetch('/api/device-data?device=Capping')
        .then(res => res.json())
        .then(data => animateCappingTorque(data.value))
        .catch(err => {
          console.error('Capping API error:', err);
          animateCappingTorque(0);
        });
    };

    fetchAndUpdate();                  // 초기 1회 호출
    setInterval(fetchAndUpdate, 1000); // 이후 1초마다 호출
  }, 1000);
}
    
function initLabelingGauge() {
  const needleEl = document.getElementById('labeling-needle');
  const valueEl = document.getElementById('labeling-speed');

  function updateLabelingGauge(percentValue) {
    let val = parseFloat(percentValue);
    if (isNaN(val) || val < 0) val = 0;
    if (val > 1) val = 1;

    // 바늘 각도 계산: 0m/s→-90°, 1m/s→+90°
    const angle = val * 180 - 90;
    needleEl.style.transform = `rotate(${angle}deg)`;

    // 숫자 텍스트 업데이트
    valueEl.textContent = val.toFixed(2);

    // 값에 따른 색상 결정
    let color;
    if (val === 0) {
      // 0 → 검정
      color = 'rgb(0, 0, 0)';
    } else if (val < 0.45) {
      // 0.45 미만 → 파랑
      color = 'rgb(60, 60, 250)';
    } else if (val <= 0.6) {
      // 0.45 이상 0.6 이하 → 연두
      color = 'rgb(60, 250, 60)';
    } else {
      // 0.6 초과 → 빨강
      color = 'rgb(250, 60, 60)';
    }

    // 숫자와 바늘 색상 적용
    valueEl.style.color = color;

    // → 0.45 미만이거나 0.6 초과일 때 data-window 테두리 깜빡임
    const dataWin = valueEl.closest('.data-window');
    if (val < 0.45 || val > 0.6) {
      dataWin.classList.add('blink-alert');
    } else {
      dataWin.classList.remove('blink-alert');
    }

    // 0.5초 뒤에 바늘과 숫자를 0으로 원위치
    setTimeout(() => {
      // 바늘 회전 리셋 (-90deg → 0 위치)
      needleEl.style.transform = 'rotate(-90deg)';
      // 숫자 리셋 및 색상 기본값으로
      valueEl.textContent = '0.00';
      valueEl.style.color = 'rgb(0, 0, 0)';
    }, 500);
  }

  updateLabelingGauge(0);

  // 1초 후부터 API 호출 시작
  setTimeout(() => {
    const fetchAndUpdate = () => {
      fetch('/api/device-data?device=Labeling')
        .then(res => res.json())
        .then(data => updateLabelingGauge(data.value))
        .catch(err => {
          console.error('Labeling API error:', err);
          updateLabelingGauge(0);
        });
    };

    fetchAndUpdate();                  // 초기 1회 호출
    setInterval(fetchAndUpdate, 1000); // 이후 1초마다 호출
  }, 1000);
}

function initStatusWindows() {
  document.querySelectorAll('.status-window').forEach(win => {
    const statusEl = win.querySelector('.status-text');
    statusEl.textContent = 'OFF';
    statusEl.classList.remove('on');
    win.classList.add('blink-off');
  });
}

function updateStatusText(deviceName, isOn) {
  document.querySelectorAll('.status-window').forEach(win => {
    const name = win.querySelector('.s-device-name').textContent.trim();
    if (name === deviceName) {
      const statusEl = win.querySelector('.status-text');

      if (isOn) {
        // ON 상태
        statusEl.textContent = 'ON';
        statusEl.classList.add('on');
        win.classList.remove('blink-off');
      } else {
        // OFF 상태
        statusEl.textContent = 'OFF';
        statusEl.classList.remove('on');
        win.classList.add('blink-off');
      }
    }
  });
}

const DEVICES = ['Washer', 'Charger', 'Capping', 'Labeling'];

/**
 * RDS에서 모든 디바이스의 is_abnormal 값을 한 번에 가져와 상태창 갱신
 */
function syncStatusFromData() {
  // 쿼리 문자열 생성
  const params = DEVICES.map(d => `deviceNames=${encodeURIComponent(d)}`).join('&');

  fetch(`/api/device-status/all?${params}`)
    .then(res => {
      if (!res.ok) throw new Error('네트워크 응답 에러');
      return res.json();
    })
    .then(dataList => {
      // dataList: [{device_name, is_abnormal}, ...]
      dataList.forEach(({device_name, is_abnormal}) => {
        updateStatusText(device_name, Boolean(is_abnormal));
      });
    })
    .catch(err => {
      console.error('Status API error:', err);
      // 에러 시 모든 디바이스 OFF 처리
      DEVICES.forEach(name => updateStatusText(name, false));
    });
}

// 초기화 함수 등록
function initErrorWarning() {
  // 최초 숨김 처리
  document.getElementById('error-warning-container').style.display = 'none';
}
// API 호출 + 화면 업데이트
function syncErrorLogs() {
  fetch('/api/error-log/all')
    .then(res => {
      if (!res.ok) throw new Error('Error logs API 응답 오류');
      return res.json();
    })
    .then(list => {
      // has_log===true인 device_name만 추출
      const devices = list
        .filter(item => item.has_log)
        .map(item => item.device_name);

      const container = document.getElementById('error-warning-container');
      if (devices.length > 0) {
        // 보여줄 문구 조합
        const namesLine = devices.join(', ');
        container.innerHTML = `
          <div><span class="device-names">${namesLine}</span></div>
          <div class="warning-icon">🚨</div>
          <div class="warning-text">기기 점검 바람!</div>
        `;
        container.style.display = 'flex';
        // 기존 타이머가 있으면 리셋
        if (errorWarningTimeout) {
          clearTimeout(errorWarningTimeout);
        }
        // 10초 뒤에 자동 숨김
        errorWarningTimeout = setTimeout(() => {
          container.style.display = 'none';
          errorWarningTimeout = null;
        }, 10 * 1000);

      } else {
        container.style.display = 'none';
        if (errorWarningTimeout) {
          clearTimeout(errorWarningTimeout);
          errorWarningTimeout = null;
        }
      }
    })
    .catch(err => {
      console.error('syncErrorLogs error:', err);
      // 에러 시 숨김
      document.getElementById('error-warning-container').style.display = 'none';
      if (errorWarningTimeout) {
        clearTimeout(errorWarningTimeout);
        errorWarningTimeout = null;
      }
    });
}
