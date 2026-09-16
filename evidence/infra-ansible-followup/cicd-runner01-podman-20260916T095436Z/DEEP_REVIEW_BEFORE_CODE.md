# r2 코드 작성 전 딥리뷰

검토 시점: 2026-09-16. 이번 r2 구현을 작성하기 전에 기존 r1 코드와 제출 증적을 대조했다. 자기 검토이며 독립 승인으로 간주하지 않는다.

## 원본 증적

- 제출 tar.gz SHA256 `5978d07425cf14658b28a906dc7e9452decc65b89c7950ab97828d7ec8798717`, 1,042 bytes. 외부 sidecar 일치. 내부 파일 집합·해시 검증은 수신 기록에 별도 보존한다.
- 실행 `2026-09-16T09:54:36.778554+00:00`~`09:54:37.110126+00:00`, cicd-runner01, ansible-verify UID1001. HOST_RUN_RESULT는 FAIL, container_cleanup는 NOT_CREATED.
- 오류: `FileNotFoundError: [Errno 2] No such file or directory: 'getenforce'`.
- Podman6.1.0 조회: rootless=true, selinuxEnabled=true, cgroupVersion=v2, cgroupManager=systemd, cpus4. SELinux 활성 정보는 Enforcing 조회 성공과 구분한다.
- PR17 `169571801d1b0cee0ba75137380149a48d6b56dd`, PR18 `d5147ebff0febbb8ab2afca28fe64d68301e033c` 최신 HEAD 일치. 이 실패 시점에는 원본 source pack/wheel 검증·이미지 pull·컨테이너·Ansible 실행까지 도달하지 않았다.

## 발견 사항과 구현 결정

| 항목 | 기존 구현과 영향 | r2 결정 |
|---|---|---|
| 호스트 명령 탐색 | execute와 environment()가 PATH를 /usr/local/bin:/usr/bin:/bin으로 제한한 뒤 getenforce를 이름으로 실행. 관리자 setup의 조회는 통과했지만 일반 UID 실행에서는 찾지 못함. 서버의 실제 getenforce 절대경로는 아직 수신되지 않음 | 호스트 PATH에 표준 sbin 경로 포함. 동일 환경에서 podman/getenforce의 절대경로를 선확인하고 기록. Enforcing 검사 유지. 패키지 설치/SELinux 완화로 처리하지 않음 |
| 증적 전달 위치 | seal()이 전용 계정 홈의 새 작업 폴더에만 저장. 사용자가 수동 복사해야 함 | 관리자 launcher가 기존 로그인 계정 홈에 새 전용 증적 폴더를 만들고 선택한 두 파일을 자동 저장. 작업 원문은 전용 계정에 보존 |
| 격리 경계 | 컨테이너에는 kit/work만 마운트. 기존 로그인 계정 홈에는 운영 자격증명이 있을 수 있음 | 홈폴더 요구 때문에 컨테이너에 기존 홈을 마운트하거나 전체 chmod/chown하지 않음. launcher가 정확히 지정한 새 run 경로에서 정규 파일만 수집하고 링크를 거절 |
| 실행과 수집의 식별 | 기존 run은 내부에서 랜덤 경로를 선택 | launcher가 새 단일 run 경로를 지정. stdout의 경로 문자열을 신뢰해 복사하지 않음. --output은 전용 홈 직속의 새 경로만 허용 |
| 재개 범위 | 계정 및 사용자 manager 구성은 이번 실행이 Podman info까지 도달한 경로상 진행됨 | setup/계정/서비스 구성을 반복하지 않음. 설치된 r1 manifest를 검증하고 별도 r2 bundle 생성. 기존 r1/실패 원문 보존 |
| 실패 처리 | account_check 같은 초기 실패는 원본 tar 생성 이전일 수 있음 | launcher는 성공·실패 모두 홈에 로그/반환코드/원본 bundle(있을 때)/해시를 묶음. 원본 FAIL 또는 원본 누락·내보내기 실패를 성공으로 표시하지 않음 |
| 승인·버전 | 기존 PR 소스와 엔진은 고정되어 있으나 보조 실행기는 독립 리뷰 전 | PR 코드·wheel·image build/container entry는 이번 수정에서 변경하지 않음. LOCAL 검증을 실제 서버 PASS/Actions/독립 승인으로 승격하지 않음 |

## 구현 전 확인한 후속 실행 경로

공통 sudo 거절 확인 → 전용 UID/홈/추가 그룹/manager 확인 → 수정된 호스트 환경에서 명령 탐색 → Podman/rootless/cgroup/SELinux Enforcing → 원본 ZIP/소스 검증 → TLS 검증 이미지 pull → image ID 고정/network none build → read-only/non-root/network none/2CPU/4GiB 컨테이너 → 실제 제한13개 → 원본 IPC 사전점검 → 두 엔진 회귀 → 해당 CID만 제거 → 홈 증적 생성.

이 경로의 기존 gate와 정확한 source/case 집합 검사를 유지한다. 원본 scope 밖 Runtime/Runner 활성화는 수행하지 않는다. 이미지/컨테이너를 실행할 수 없는 제작 환경의 한계는 남는다.

## 구현 후 필요한 검증

1. 구 PATH에서 sbin 전용 실행 파일 미발견, 수정된 환경에서 탐색/실행 성공. 도구 누락은 시험 전 실패.
2. 전용 홈 밖·기존·링크 output 거절. 지정한 새 output 경로와 수집 경로 연결.
3. 성공/실패/원본 누락/해시 불일치/링크 증적 각각의 홈 수집 결과와 nonzero 전달. 컨테이너에 기존 홈이 노출되지 않음.
4. r1→r2 새 디렉터리 구성 및 기존 r1·고정 Ansible ZIP·Containerfile/entry 바이트 보존.
5. sudo 회귀8개와 기존 실행기12개 재확인. 모형·로컬 결과와 서버 실제 시험을 구분.

## 이후 적용할 사용자 지침

추가 설계 검토: root launcher는 전용 UID 소유의 설치 디렉터리에서 Python helper를 root로 실행하지 않는다. 계정 점검/설치/수집 helper는 기존 로그인 사용자가 검증한 패치에서 실행하고, 설치된 실행기는 runuser를 통해 전용 UID로만 실행한다. 설치 실패도 홈 증적에 포함한다.

- 전달용 증적 파일은 기존 로그인 계정의 홈폴더 아래 새 디렉터리에 생성한다. 원본을 보존하며 동일 파일 덮어쓰기를 피한다.
- 코드 작성 전에 기존 구현·실제 증적·수정 영향·실패 및 재개 경로를 딥리뷰하고 그 결과를 남긴다.
