# Export 수정 정상 Actions 착수 증적

PR22 / source `31895081e30e27481e7c17407047c9454e3b247a` / Run35195838409 / Attempt1 / Job105118736321.
이 디렉터리는 실행 준비·시작 키트 검증의 STATIC/LOCAL/MOCK 기록이다. 실제 CI 결과와 서버 Runtime은 아직 인수하지 않았다.

- `TEST_SOURCE_BINDING.json`: parent PR17의69개 blob/mode 보존 및 추가2파일 연결.
- `ENTRY_REVIEW.md`, `workflow.yml`: 변경 전 범위·보호 조건과 실제 게시 Workflow 원문.
- `LIVE_SNAPSHOT.json`: 제작 시점 GET 원문. 현재 상태는 서버 시작 직전에 다시 조회한다.
- `FDS_Ansible_Export_Fix_Start_v1_0/`: ZIP에 포함된 텍스트 코드·안내·검증 원문 사본.
- `PACKAGE_VERIFICATION.json`: 완성 ZIP/sidecar/안내서 파일명·SHA256, 기존 payload3개 동일성, 로컬 시험 결과.
- `test_start_kit.py`: 사본 코드 및 저장된 API snapshot 대상 재현 시험. 실제 token/Podman 호출은 하지 않는다.
- `PUBLICATION_SHA256SUMS`: 이 디렉터리의 자기 자신을 제외한 전체 선별 파일 집합과 hash.

바이너리 payload와 배포 SHA256SUMS는 별도로 제공한 완성 ZIP에 있다. 이 Git 선별 사본에서 서버 wrapper를 실행하지 않는다.
서버에는 `FDS_Ansible_Export_Fix_Start_v1_0.zip`과 sidecar를 전달하고 ZIP 내부 README 순서로 실행한다.
readiness는 현재 PREPARED/image의 읽기 점검이며 전체 계정·자원·SELinux·IPC·격리 검사는 기존 launcher가 다시 수행한다.
새 wrapper 보호 시험9개, preflight 거부35개 subcase, readiness binding 거부12개 subcase,
Workflow 원문 비교/조건모형19개/변이6개, Bash4개 및 잘못된 로그인3개 거부를 확인했다.
이 숫자들을 합산해 실제 CI 시험 개수로 표시하지 않는다.

과거 Start v1.1의 PR20 admin 고정값을 새 시험에 사용하지 않는다. Runner v1.3/Admin1.1.1/Input Guard1.0 payload는 동일 bytes다.
독립 승인·병합·Issue5 AC 종결·운영 Apply·엔진 전환은 이번 착수로 완료되지 않는다.
