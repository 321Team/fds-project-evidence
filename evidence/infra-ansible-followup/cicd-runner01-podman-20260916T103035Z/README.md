# cicd-runner01 r2 실행 실패 수신 및 r3 수정 — 2026-09-16

**실제 r2 서버 실행 FAIL 유지 / 로컬 r3 STATIC·UNIT·MODEL38개 통과 / UID 전환 실제 시험2개 환경 차단 / 서버 r3 NOT RUN.**

19:30:35~19:31:00 KST, ansible-verify UID1001에서 실행했다. sudo 거절 확인·계정 점검·r2 설치·getenforce(/usr/sbin/getenforce)·이미지 pull/build·홈 증적 생성을 확인했다. 컨테이너는 entry Python 파일 읽기 Permission denied로 rc2/ExitCode2/OOMKilled=false. 정확한 CID 제거 rc0/REMOVED. 격리13개 점검·Ansible은 시작하지 않았다. HOST_RUN_RESULT의 CONTAINER_RESULT.json 누락은 그 후속 증상이다.

제출 원본7,932 bytes, SHA256 `146ec68d70bc744230a1561df01abe62139ca76fd8924d1cbbf19cf40597059c`. 업로드 (1) 접미사는 다운로드 이름 변경이며 sidecar의 정식명은 ansible-podman-evidence.tar.gz. 외부/내부 두 archive의 해시·manifest 집합과 내부 sidecar를 검증했다. HOME의 ORIGINAL_HOST_RUN_RESULT와 내부 원본 HOST_RUN_RESULT도 바이트 동일하다. 원본 압축·sidecar 및 선택한 원문 파일을 보존했다.

DEEP_REVIEW_BEFORE_CODE.md를 작성한 뒤 수정했다. 설치기의0600 파일이 COPY되며 기본 소유자0:0과 USER1000이 조합되는 결함을 확인했다. 이미지의 entry 한 파일만0:0/0444로 명시하고 USER1000 이후 --self-test를 필수 build 단계로 추가했다. 새 옵션의 입력을 고정하도록 CMD []도 명시했다. 호스트 설치파일은0600 유지. 최초 오류를 가리던 결과 JSON 선읽기는 rc/ExitCode/OOM 확인과 로그 마지막8KiB 진단 이후로 옮겼다. REVIEWED_CODE_DIFF.patch에 핵심 변경을 연결했다.

로컬 계정8+실행기12+홈 수집12+신규6=38 통과. 신규 실제 UID 변경 시험2개는 제작 환경 uid/gid map 0 0 1로 EPERM/EINVAL 발생. 최초 실패 로그를 지우지 않았고, 이후 환경 차단2개로 명시했다. 모형 성공을 실제 UID1000/Podman 성공으로 승격하지 않는다. actual image build/self-test/container/two-engine 검증은 다음 서버 실행에서 확인해야 한다. Python/Bash 구문·최종 ZIP 바이트/manifest 검증 완료.

전달 패치 FDS_Ansible_Podman_EntryFix_r3.zip,55,695 bytes, SHA256 `ed70f746bb88ef9b4031bd59934f1a050ec718eaa3c0884f8fb6282a4f12101f`. 설치된 정확한 r2를 확인해 새 r3에 적용한다. 기존 r2/실패 원문 유지, 계정·서비스 설정 반복 없음. 로그인 사용자 홈의 새 ansible-evidence-* 폴더에 최종 압축/sidecar를 자동 생성한다.

PR17 `169571801d1b0cee0ba75137380149a48d6b56dd`, PR18 `d5147ebff0febbb8ab2afca28fe64d68301e033c` 유지. 원본 Ansible ZIP/source/wheel·격리 설정 유지. GitHub Actions/운영 apply/엔진 전환 없음. Draft/독립 승인·병합 대기이며 AC 완료로 표시하지 않는다.

참고 규칙: [COPY 권한/소유자 및 USER](https://docs.docker.com/reference/dockerfile/), [Podman build](https://docs.podman.io/en/latest/markdown/podman-build.1.html). 서버 파일 stat/AVC 원문은 수신되지 않았으므로 별도 SELinux 원인 유무를 확인했다고 주장하지 않는다.
