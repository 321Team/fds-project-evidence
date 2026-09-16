# cicd-runner01 Podman 실패 수신 및 r2 보완 — 2026-09-16

실제 서버 원본은 **FAIL**이다. 09:54:36 UTC 실행에서 ansible-verify UID1001이 Podman6.1.0 rootless/SELinux 활성/cgroup v2/systemd 조회를 마친 뒤 `FileNotFoundError: getenforce`로 중단됐다. container_cleanup=NOT_CREATED이며 이미지 pull/build·컨테이너·Ansible 시험에 도달하지 않았다.

원본 tar.gz 1,042 bytes, SHA256 `5978d07425cf14658b28a906dc7e9452decc65b89c7950ab97828d7ec8798717`. 외부 sidecar·내부 해시·정확한 파일 집합 일치. 원본 tar/sidecar 및 내부 파일은 그대로 보존했다. 이전 preflight·CI 실패 증적은 변경하지 않았다.

기존 보조 실행기의 호스트 PATH가 sbin을 제외했다. 코드 작성 전 DEEP_REVIEW_BEFORE_CODE.md를 작성한 뒤 PATH 및 홈 증적 전달을 수정했다. 표준 sbin 포함 및 실제 명령 절대경로 기록, Enforcing 검사 유지. 전용 계정에서 실행하고 원본과 launcher 로그를 기존 sudo 로그인 계정의 새 홈 하위 폴더에 자동 보존한다. 초기 점검/설치 실패도 홈 증적을 생성한다. root helper는 사용자에게 전달한 패치에서만 실행하고 전용 UID 소유 설치 코드/PR 코드는 root로 실행하지 않는다.

전달 패치: FDS_Ansible_Podman_PathHomeFix_r2.zip, 37,221 bytes, SHA256 `ea90ec45e587fdde60eb33a006f27357dd59ca59b59f21b708fdb9ee158a3ab9`. 설치된 r1을 검증하여 별도 r2 디렉터리를 구성한다. 계정/서비스 설정을 반복하지 않는다. 원본 Ansible ZIP·Containerfile/container-entry.py 바이트 유지. 패치 안에 전체 보조 코드·딥리뷰·입력 원본·회귀 코드/로그가 포함된다.

로컬 STATIC/UNIT/MODEL 32개(8+12+12) PASS, Python AST/Bash 구문 PASS, 최종 ZIP 왕복·manifest 검증 PASS. 홈 생성의 성공/원본FAIL/nonzero/누락/초기중단 5모형과 링크/해시/경로/소유권 거절을 확인했다. 이는 실제 Podman/Ansible 실행 결과가 아니다. 최종 포장 점검의 첫 시도는 검사기가 만든 __pycache__ 추가 파일을 정상 거절했고, 전달 명령과 동일한 -B 조건에서 다시 검증했다.

PR17 `169571801d1b0cee0ba75137380149a48d6b56dd`, PR18 `d5147ebff0febbb8ab2afca28fe64d68301e033c` 유지. 실제 r2 서버 재개·두 엔진 전체 검증·GitHub Actions는 NOT RUN. 운영 apply/엔진 전환 없음. 독립 승인·merge·AC 완료로 처리하지 않는다.

사용자 후속 지침: **전달 증적은 기존 로그인 계정 홈에 생성**, **코드 작성 전 딥리뷰 수행**. 다음 입력은 r2 종료 시 HOME_EVIDENCE에 표시되는 tar.gz와 .sha256이다.
