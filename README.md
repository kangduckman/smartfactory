팀명: PacktoryPulse

프로젝트 기간: 2025.05.21 ~ 2025.07.04

본 레포는 3인이 협업한 결과물이며, 각 기여자는 README 및 CONTRIBUTORS.md에 명시되어 있습니다.

이 레포지토리는 2025년 7월 3일에 GitHub에 업로드되었으며,
실제 개발은 위 기간 동안 완료되었습니다.

🏭 스마트팩토리 시뮬레이션 시스템
병 음료 제조/포장 중소기업의 공장 자동화를 위한 AWS 기반 스마트팩토리 시뮬레이션 시스템입니다.
IoT 센서를 통해 설비 상태를 실시간으로 수집 및 분석하고, 이상 발생 시 자동 경고를 전송하는 시스템을 구현했습니다.

🧱 사용 기술 스택
| 분야            | 기술명                            | 설명                        |
| ------------- | ------------------------------ | ------------------------- |
| **클라우드 인프라**  | EC2, VPC, RDS, Transit Gateway | 애플리케이션 실행, DB 구성, 네트워크 분리 |
| **데이터 전송/처리** | SQS, SNS, EventBridge, Lambda  | 메시지 큐잉, 알림 전달, 이벤트 처리     |
| **모니터링**      | CloudWatch                     | 로그 기록, 경고 설정              |
| **웹 서버**      | Flask, NGINX                   | 센서 서버 및 API 처리            |
| **보안 인증**     | Step-ca, AWS IAM               | mTLS 인증 게이트웨이, 권한 관리      |


아키텍처 구성도

![image](https://github.com/user-attachments/assets/a9f775ed-2262-4e43-a01a-52ddfaf6550c)


팀장 안현수 (https://github.com/skyblue-network)

팀원 이목원 (https://github.com/NE-mok)

팀원 강승민 (https://github.com/kangduckman)

