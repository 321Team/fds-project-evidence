# P1-HBR-01 Harbor AC 검증 — 트러블슈팅 기록 (2026-09-30)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). [`received-20260930T040033Z`](../received-20260930T040033Z/README.md) 원본을 만드는 과정에서 실제로 부딪힌 문제와 해결 방법을 기록한다. **이건 원본 증적이 아니라 작업 서술 문서**이며, 향후 같은 환경에서 유사 작업을 할 때 반복 조사를 줄이기 위한 목적으로 남긴다.

## 1. 워커 노드 SSH 대화형 로그인 불가

`svc_ansible`로 k8s-worker01에 로그인 시도 시 `PTY allocation request failed on channel 0`로 연결 자체가 끊김. 원인: 이 계정의 SSH 키에 `restrict` 옵션(pty 차단 포함)이 적용돼 있음. `harden_svc_ansible_key.yml`(`from="10.250.10.10",restrict`)이 k8s_nodes 그룹에 이미 적용된 결과로 추정.

**해결**: 대화형 로그인 대신, 매번 `ssh host "명령"` 형태의 **비대화형 단발 명령**으로 실행. `heredoc`도 `ssh host bash -s <<'EOF' ... EOF`처럼 stdin으로 스크립트를 통째로 넘기는 방식은 pty 없이도 정상 동작함.

## 2. `crictl`/`nerdctl` 미설치

k8s-worker01/02/03 전부 `crictl`/`nerdctl`이 없었고(containerd/ctr만 존재), `worker-pull-pod-start-test.sh`가 요구하는 필수 도구였다.

**해결**: 워커는 인터넷 접근이 없어(`curl https://github.com` 타임아웃), 인터넷이 되는 ansible01에서 GitHub Releases API로 최신 버전(`cri-tools` v1.37.0, `nerdctl` v2.4.0)을 받아 `scp`로 3대에 배포. 설치 위치는 `/usr/local/bin`이 아니라 **`/usr/bin`**으로 — `sudo`의 `secure_path`(`/sbin:/bin:/usr/sbin:/usr/bin`)에 `/usr/local/bin`이 빠져 있어서, 처음엔 일반 계정으로는 실행되는데 `sudo crictl ...`만 "명령을 찾을 수 없음"으로 실패했다.

## 3. Harbor Robot 계정명의 `$` 문자와 셸 변수 치환 사고

Robot 계정 이름이 `robot$worker`, `robot$push` 형태(Harbor의 로봇 계정 네이밍 규칙)인데, credential을 파일에 `KEY=VALUE` 형식으로 저장한 뒤 원격에서 `source file.env`로 불러오는 과정에서 **`$worker`가 정의되지 않은 셸 변수로 치환되어 빈 문자열이 되고, 결과적으로 계정명이 `robot`로 잘림**. Harbor는 이걸 다른(존재하지 않는) 계정으로 인식해 매번 `401 Unauthorized`를 반환했다.

증상이 "계정/비밀번호가 틀렸다"는 것과 동일해서(로그인 자체가 401), 실제 원인(따옴표 누락)을 찾기까지 여러 차례 credential을 재발급·재입력하며 시간을 소모했다. 최초 발견 계기는 Harbor UI에서 로봇 계정 목록(`robot$fds-ci`, `robot$push`, `robot$worker`)을 직접 보고 계정명에 `$`가 포함된다는 걸 인지한 것.

**해결**: env 파일 생성 시 값을 **작은따옴표로 감싸서 저장**(`printf "KEY='%s'\n" "$VALUE"`). 작은따옴표 안에서는 `source`(bash)가 `$`를 변수 치환 대상으로 보지 않는다.

## 4. Robot Account에 최소권한(Pull-only)이 실제로 적용됐는지 확인하는 첫 시도의 오탐

`worker-pull-pod-start-test.sh`의 내부 Push DENY 체크가 **pull에 쓴 것과 같은 태그**로 push를 시도하도록 짜여 있었다. 그 태그+digest 조합이 이미 Harbor에 존재하는 경우(오늘 Runner가 먼저 push해둔 이미지라 실제로 존재했음), 서버는 "새로 쓸 게 없다"고 판단해 실제 권한(쓰기) 검사 없이 조용히 성공 처리한다(`total: 0.0B` 전송으로 확인). 결과적으로 Pull-only 계정인데도 "Push 성공"으로 보여서, Harbor 권한 설정 자체가 잘못된 줄 알고 UI를 다시 확인하는 데 시간을 썼다.

**해결**: push 직전에 `worker-push-denytest-<REVIEW_RUN_ID>`라는 **매 실행마다 고유한 새 태그**로 재태깅한 뒤 그 태그로 push하도록 로컬 수정. (`worker-push-deny-test.sh`라는 별도 파일은 원래 이렇게 짜여 있었음 — 통합 스크립트인 `worker-pull-pod-start-test.sh`만 이 패턴이 빠져 있었음.)

## 5. Push 거부 판정 문구가 `docker` 전용이라 `nerdctl` 환경에서 오판정

3번 수정 후 실제로 거부(`401`, `unauthorized to access repository ..., action: push`)가 발생했는데도 스크립트가 FAIL로 판정했다. 판정 로직이 Docker CLI의 문구(`denied: requested access`)만 정규식으로 찾고 있었는데, 이 환경은 `nerdctl`을 쓰고 있어 문구가 달랐다.

**해결**: 판정 정규식에 `unauthorized to access repository.*action: push` 패턴 추가.

## 6. Source IP 방화벽 규칙 확인 경로

harbor01 자체의 firewalld에는 Source 제한이 없어서(누구나 443 접근 가능해 보였음) 처음엔 "allowlist 미구현"으로 오해했다. 실제로는 상위 게이트웨이(`mgmt-gw01`, 물리 서버01)의 firewalld policy(`mgmt-to-physical`, 기본 target=DROP)가 관리망→물리망 트래픽을 포트/호스트별로 개별 허용하는 구조였고, `10.250.10.20(Runner) → 10.1.93.54:443`만 명시적으로 허용돼 있었다. `10.250.10.10(ansible01)`은 SSH만 허용돼 있어 443 접속이 항상 타임아웃났다.

**교훈**: 대상 서버 자체의 방화벽만 보지 말고, 네트워크 경로상의 게이트웨이(이 환경에선 `mgmt-gw01`)도 함께 확인해야 한다.

## 참고

이 문서에 적힌 로컬 스크립트 수정(4, 5번)은 `infra-harbor-trivy` 저장소에 정식 PR로 반영되지 않았다. 원본 저장소 담당자가 review 후 병합 여부를 결정해야 한다.
