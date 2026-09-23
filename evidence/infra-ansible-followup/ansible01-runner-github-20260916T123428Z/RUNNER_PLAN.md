# infra-ansible Runner 구성 검토안

상태: **PROPOSED / 구현·등록·활성화 미실행**. 기존 확정 정책을 변경한 결정문이나 실행 허가가 아니다. 등록 목록을 확인했으므로 다음 작업을 Runner 구성 준비로 구체화한다. 실제 실행 스크립트 작성 전 이 검토안과 변경 범위를 다시 딥리뷰한다.

## 제안 구성

| 항목 | 검토안 | 근거·제약 |
|---|---|---|
| 물리 자원 | 기존 cicd-runner01 VM 재사용 후보 | 이 호스트의 rootless Podman에서 두 엔진 로컬 시험이 통과. 앱 CI와 동시 부하의 여유는 아직 검증되지 않음 |
| 등록 범위 | 321Team/infra-ansible repository 전용 | 현재 조회0대. infra-cicd Runner의 URL 변경·조직 공유 전환을 포함하지 않음 |
| 소유 계정 | ansible-verify UID1001 후보 | 시험용 계정의 기존 sudo 거절·홈 자격증명 점검 근거를 재사용하되, 새 Runner 환경의 격리·자격증명 검증은 별도 |
| 실행 경계 | Job마다 새 rootless Podman 컨테이너 안에 Runner 전체를 배치하는 방식 우선 검토 | 기존 Workflow는 Python을 직접 호출하므로 호스트 서비스 등록만으로 이전 컨테이너 격리를 승계할 수 없음 |
| 수명 | ephemeral Runner1개·Job1개, 동시 Ansible Job1개 | GitHub 등록 해제와 로컬 작업 공간 정리는 별도 구현해야 함 |
| 이름·labels 후보 | ansible-ci-<고유값>; self-hosted/Linux/X64/fds-ci/ansible-isolated | 실제 등록 후 반환 labels에 맞춰 선택값을 고정. 예약 sentinel ansible-ci-unconfigured는 부여하지 않음 |
| 자원 후보 | CPU2·메모리4GiB·pids512 | 앞선 Ansible 컨테이너 예산. Runner 프로세스 추가 부하의 적합성은 신규 검증 대상 |
| 자격증명 | 관리용 gh/PAT는 관리 호스트에 유지; 등록용 단기 입력과 Job 최소권한만 사용 | 토큰 원문을 로그·압축·Git에 저장하지 않음. 운영 SSH/Harbor/배포 자격증명 및 호스트 소켓을 마운트하지 않음 |
| 증적 | Runner 로그·Job 결과를 보존한 뒤 실행용 컨테이너/작업공간 정리, 최종 압축은 기존 로그인 계정 홈 | 성공·실패·취소 경로를 각각 확인. 다른 Runner의 디렉터리나 서비스는 정리 대상이 아님 |

현재 확보된 근거는 호스트 기반 자원·시험 환경의 타당성까지다. 이 표의 새 Runner 전체 실행 방식이 검증됐다고 표시하지 않는다. 기존 컨테이너의 network=none은 GitHub 접속을 필요로 하는 Runner에 그대로 적용할 수 없다. GitHub control-plane/checkout/artifact 통신과 wheel 공급을 기존 승인 경로에 맞춰 검토해야 하며 새 egress 허용을 가정하지 않는다.

GitHub의 repository Runner 등록은 해당 저장소 대상으로 이뤄진다. `--ephemeral`은 Job1개 처리 후 등록을 해제하지만, 로컬 파일 삭제는 운영 측 구현이 필요하다. 근거: [Runner 등록](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners), [ephemeral 수명·통신 조건](https://docs.github.com/en/actions/reference/runners/self-hosted-runners#ephemeral-runners-for-autoscaling).

## 구현 전 확인과 변경 범위

1. Runner 배포 파일/컨테이너의 버전·해시·필수 라이브러리·지원 실행 방식, 승인된 통신 경로를 고정한다. 이전 Python 검증 이미지를 Runner 지원 이미지로 간주하지 않는다.
2. Job이 바꿀 수 없는 외부 제어 경로에서 수명과 정리를 관리한다. Rootless·비root·capability drop·seccomp·SELinux·마운트 범위·자격증명 경계를 검토하고 누락 시 실행을 차단한다.
3. 등록/Job 수행/증적 보존/정리를 구분하는 설치·실행안을 준비한다. 기존 앱 서비스의 중지·재등록, 계정 sudo 추가, SSH 키 복사, 광범위 chmod/chown, daemon 소켓 마운트는 범위에 넣지 않는다.
4. Workflow 활성화 변경은 현재 소스에서 별도 검토한다. Runner 입력 확정 전에 활성화 변수를 켜지 않는다. 이미 통과한 PR17/18 SHA와 활성화 후 실제 검토 SHA를 구분하고, 새 SHA에 필요한 검증을 수행한다.

## 완료 판단

- 새 Ansible 전용 Runner가 해당 repository API에서 관측되고 새 계정·컨테이너와 연결되는 근거.
- 실제 Job 수신과 종료, 정상/실패/취소의 증적 보존 및 정리 확인.
- 정상 commit Actions PASS와 실제 고의 결함 commit Actions FAIL, 각 Run/Attempt/Source·Workflow·Check SHA/artifact 연결.
- PR17/18 코드·PR13 증적·활성화 변경의 독립 검토 및 수동 병합 판단.

동일 조회 반복·불필요한 재검증 대신 위 실행 구성을 다음 변경 대상으로 삼는다. 운영 apply와 엔진 전환은 이 범위에 포함되지 않는다.
