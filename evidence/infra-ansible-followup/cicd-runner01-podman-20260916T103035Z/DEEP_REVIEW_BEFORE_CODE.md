# r3 코드 작성 전 딥리뷰 — 2026-09-16

아래 검토를 기록한 뒤 r3 구현을 시작한다. 작성자의 자기 검토이며 독립 승인으로 간주하지 않는다.

## 실제 수신 증적

- 업로드 이름 `ansible-podman-evidence.tar(1).gz`, 7,932 bytes, SHA256 `146ec68d70bc744230a1561df01abe62139ca76fd8924d1cbbf19cf40597059c`.
- sidecar의 정식 파일명은 `ansible-podman-evidence.tar.gz`이며 다운로드 중 `(1)`이 붙은 이름과 구분했다. 실제 바이트 해시 일치. 외부/내부 두 단계 archive의 manifest 해시·정확한 파일 집합 및 내부 archive sidecar도 검증했다.
- 실행 10:30:35~10:31:00 UTC, cicd-runner01, ansible-verify UID1001. 기존 로그인 사용자 UID1000 홈에 최종 증적 생성 성공. HOME/HOST 모두 FAIL, host_rc1.
- sudo 명시적 거절 및 계정 점검 통과, r2 설치 완료. getenforce 실제 위치 `/usr/sbin/getenforce`. 이미지 pull rc0, build rc0, 컨테이너 rc2/ExitCode2/OOMKilled=false, 정확한 CID 제거 rc0/REMOVED.
- 직접 오류는 container.log의 `/usr/local/bin/python3: can't open file '/usr/local/lib/fds-container-entry.py': [Errno 13] Permission denied`.
- HOST_RUN_RESULT의 CONTAINER_RESULT.json 미발견은 시작 스크립트 미실행의 후속 증상이다. 격리13개 점검 및 Ansible은 시작하지 않았다. 이미지 build 성공을 검증 성공으로 승격하지 않는다.
- 제출 Containerfile SHA `c71e4f5a8f6247ee92313601b3ad07ad51b9067ded996a744f48e09d8e600be5`, entry SHA `9a408e69cc54fa016f59212bf73cebe486033d38fa16beda3a101ff0dd659293`는 로컬 r2와 일치.
- PR17 `169571801d1b0cee0ba75137380149a48d6b56dd`, PR18 `d5147ebff0febbb8ab2afca28fe64d68301e033c` 현재 HEAD 재확인. Draft/미병합 유지.

## 결함과 수정 결정

| 항목 | 근거와 영향 | 수정 및 검증 |
|---|---|---|
| 시작 파일 읽기 권한 | r2 installer가 모든 설치 파일을0600으로 설정한다. Containerfile은 COPY 후 권한을 명시하지 않고 USER1000으로 전환한다. COPY는 파일 권한을 보존하며 기본 소유자는0:0이다. 따라서 root 소유0600 Python 파일을 UID1000이 읽지 못하는 코드 경로가 실제 오류와 일치한다. 서버의 해당 파일 stat/AVC 로그는 수신되지 않았으므로 별도 SELinux 원인 유무를 확정하지 않는다. | 호스트 설치파일0600은 유지한다. 이미지 안에서만 entry 한 파일의 소유자0:0/권한0444를 명시. rootless·SELinux·UID1000·cap-drop·read-only 경계 유지. 로컬에서 root 소유0600→UID1000 읽기 실패와0444→성공을 실제 프로세스로 재현한다. |
| 빌드 검증 누락 | 기존 build는 Python/git 버전만 root 단계에서 검사하고 COPY 이후 실행 사용자가 entry를 읽는지 확인하지 않았다. rc0 이미지에도 시작 실패가 남음. | USER1000:1000 이후 같은 entry를 --self-test로 호출. 실제 파일 읽기·모듈 import·소유자/모드·UID/GID를 검사하고, 불일치 시 이미지 build를 nonzero로 종료. 이 검사는 Ansible/호스트/서비스에 접근하지 않으며 전체 Runtime 검증과 구분. |
| 원인 진단 가림 | result_ok의 인자를 구성하면서 결과 JSON을 먼저 읽는다. rc2인 상황에서도 FileNotFoundError가 최초 container 오류를 대표하는 결과가 됨. | rc/ExitCode/OOM 및 예상 결과 존재 여부를 먼저 기록. 실패 시 제한된 container.log 마지막 부분과 경로를 HOST_RUN_RESULT/별도 진단 JSON에 보존. 필요한 결과의 누락도 명시적으로 FAIL. 정상 결과에 대한 기존 SHA/45case/격리 집합 검사는 유지. |

## 이후 경로와 범위 점검

1. 기존 호출자 홈의 새 증적 디렉터리 → 전용 계정 및 sudo 명시적 거절 → r2 정확한 manifest 검증 → 별도 r3 설치. 기존 r2/원본 보존, 계정·systemd 설정 반복 없음.
2. 호스트 도구 탐색/SELinux Enforcing/cgroup 점검 → 원본 고정 Ansible ZIP·source/wheel 검증 → 공개 이미지 pull 및 immutable image ID → network none build → 새 UID1000 entry self-test.
3. 기존과 동일한 network none/read-only/2CPU/4GiB/PID512/private namespaces/SELinux/seccomp/키 없는 컨테이너 실행 → 기존 격리13개 점검 → 원본 IPC preflight → 두 엔진 시험.
4. source/expectation/원본 rc 검증 → 해당 CID만 정리 → 기존 로그인 홈 자동 수집. 원본 FAIL/nonzero/누락/정리 또는 수집 실패는 계속 FAIL.

권한은 이미지의 시작 스크립트 한 파일에만 바꾼다. 전용 홈을 다른 계정에 개방하거나 호스트 전체 chmod/chown, SELinux permissive/disable, root 컨테이너 전환으로 해결하지 않는다. 컨테이너 /kit와 /work 소유자는 keep-id 매핑으로 현재1000에 대응하므로 이 입력만으로 해당 경로의 권한 완화는 필요하지 않다. cgroup/proc/network 실제 점검은 미실행 상태이므로 다음 실행 증적이 필요하다.

코드 수정 전 공식 문서 확인: [Podman build](https://docs.podman.io/en/latest/markdown/podman-build.1.html), [Dockerfile COPY/USER 규칙](https://docs.docker.com/reference/dockerfile/). 파일 COPY 권한 보존·기본 소유자와 USER가 후속 RUN/ENTRYPOINT 사용자에 적용되는 규칙을 검토했다.

## 완료 조건과 한계

CLI 변경 영향 추가 검토: --self-test 옵션을 명시적으로 파싱하므로 이미지 CMD를 빈 배열로 선언해 base의 기본 인자가 검증기 옵션으로 전달될 여지를 제거한다. 관측된 원인과 별개로 이번 옵션 추가에 수반한 입력 계약 명시다.

- 로컬 실제 UID 변경 프로세스로0600 실패/0444 성공/잘못된 소유자·UID 거절. self-test에서 Ansible 및 실제 컨테이너 격리 점검을 실행하지 않는지 확인.
- 제출 rc2/log를 fixture로 재사용하여 최초 오류 보존, 결과 누락·OOM·exit 불일치 FAIL, 정상 결과 기존 엄격한 판정 유지.
- 기존 계정/홈 수집/소스 무결성 및 설치 보존 회귀. 원본24MB Ansible ZIP과 PR17/18 소스는 수정하지 않는다.
- 제작 환경에 Podman/Docker가 없으므로 실제 이미지 빌드·컨테이너·두 엔진 시험은 NOT RUN. 로컬 재현은 일반 Linux 파일 접근 검증이며 서버 SELinux/namespace 성공 증거가 아니다. 서버의 추가 AVC 유무를 검사했다고 주장하지 않는다.
- 사용자 지침: 코드 작성 전 딥리뷰, 전달용 증적은 기존 로그인 계정 홈. 그대로 유지한다.

## 구현 후 확인한 제작 환경 한계

계획한 실제 UID1000 재현은 제작 환경의 UID/GID map이 `0 0 1`로 제한되어 EPERM/EINVAL로 차단됐다. 최초 실패 로그를 보존하고 실제 UID 시험2개는 ENVIRONMENT_BLOCKED로 구분한다. 자기 점검 모형은 추가하되 실제 권한 재현 성공으로 표시하지 않는다. 서버 이미지 build의 USER1000 self-test는 그대로 필수 조건이다.
