# Phase 1 이권욱 선행 작업 — D04·Grafana·부팅 보호 읽기

2026-10-15 KST · 작성/실행 이권욱 · CODEX_ASSISTED. 사용자 “권장순서로 착수”에 따라 기존 관리 경로에서 읽기 전용 선행 작업을 수행했다. Phase 2 제외. 소스 독립 REVIEW=NOT PERFORMED (Pre-check); 작성자 구문/범위 확인과 증적 독립 편입 리뷰는 별개다.

## 실제 수행과 출처

- 서버 관측: **07:31:29~07:31:35 KST**, edge01 일반 svc_ansible(uid1003), control01 및 K8S6노드 svc_ansible→sudo root. Windows 기존 SSH 별칭 fds-ansible01→ansible01 server01_ansible→고정 관리키/known_hosts 경로. host key 검증·TLS 검증 유지.
- 성공 수집 9건: edge 설정1, control01 D04 API GET8건을 묶은1, Grafana GET1/파일 stat1, 6노드 systemd 조회6. 각 원격 코드·명령/rc·시각·collector SHA·수신 stdout/stderr SHA는 runtime/에 있다. 원격 파일 설치 없이 stdin Python을 실행했고 결과만 PC에 보존했다.
- 첫 edge sudo 시도는 `sudo: 암호가 필요합니다`, rc1로 수집 전 중단했다. 실패 원본을 보존했다. 이후 권한 변경 없이 일반 계정의 허용된 파일 읽기로 완료했다. 다른 원격 수집은 자동 재시도하지 않았다.
- nginx 전체 dump·Secret 객체/값·kubeconfig 내용·Pod env 값은 반출하지 않았다. Kubernetes 원 응답은 원격 메모리에서 필요한 필드만 투영한 뒤 버렸다. **stdout.json은 수집기의 원본 projection 출력**이며 전체 kubectl 원문이 아니다. commands의 원 응답 해시는 대응 메타데이터이며, 미보관 원문을 재검증했다는 뜻이 아니다.
- 새 HTTP 거래/Pod exec/PF/토큰 발급·회전/설정·정책 변경/reload/재부팅/서비스 재시작 0. 관리 SSH·API GET는 실제 실행했다.

## D04 대조 결과

[증적169](https://github.com/321Team/fds-project-evidence/pull/169)의 원본 tgz2개 해시를 대조하고 경로·설정·control01 post 로그만 바이트 그대로 추출했다(reference/INDEX.json). 과거 PC 거래201·DB1행·metric 증가와 최신 앱 [224](https://github.com/321Team/fds-project-evidence/pull/224)/[228](https://github.com/321Team/fds-project-evidence/pull/228)의 연결을 보완한다.

| 대조 | 실제 결과 | 한계 |
|---|---|---|
| `/etc/nginx/conf.d/fds.conf` | 169 after와 SHA256 `a10a5a684c9f8756bb91d78c94befd103ea97baa1af955c373acaebb35a91799` 동일. Worker .105/.107/.108:30080, HTTP80, metrics404, X-Real-IP 등 동일 | 파일 무결성·설정 대조. 메모리에 로드된 설정 전체 동일성을 직접 증명하지 않음 |
| nginx 상태 | active/running, port80 LISTEN. 서비스 시작 10/11 18:32:58, master1593/worker1594. 기본 `/usr/sbin/nginx` 실행 | 새 Client 응답 관측 없음. 원격 전체 nginx dump·reload 없음 |
| Service/endpoint | `Local`,80→8000:30080, selector app=transaction-api. Worker별 Ready·non-terminating endpoint1개 | Pod UID/IP는169 이후 교체됨. 같은 Pod라고 주장하지 않음 |
| nodeport GNP | .50/32 Allow→다른30080 Deny, order50/worker selector/preDNAT/applyOnForward가169 기록과 동일 | 모든 호스트 정책/경로의 실효 차단 동일성·규칙 귀속까지 증명하지 않음 |
| 앱 이미지 | Pod6 Ready, restart0, API338b8a28/engine8b257adb digest가224/228 기준과 일치 | 기능/부하/장애를 이번에 재실행한 것이 아님 |

**기술 권고:** 기존169+224/228과 이번 현재 경로 입력을 함께 APP Lead 이재환에게 제출해 재사용 범위를 판단한다. D04를 자동 종결하지 않는다. 남은 연결을 인수할 수 없다고 판단할 때만 고유 RUN·명시적 offset·사전DB0/사후201·DB1·metric의 최소 Client 거래1건 후보를 구체화한다. 현재 새 거래 실행은 없다.

## Grafana

control01 admin.conf/super-admin.conf root:root0600 존재를 stat으로 확인했다(내용/해시 수집0). Grafana Deployment 동일 UID·generation16, Ready1/1, grafana-sa, admin-user/admin-password가 grafana-admin-credentials를 참조하고 literal env값은 없다. 사람의 실제 수령·사용 가능성·회수 완료는 이 조회로 알 수 없다. [보관·회수 책임 이권욱 확정](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6139012660)은 유지한다. 필요한 사람 입력은 GRAFANA_HANDOFF.md로 한정했다.

## 부팅 보호

현재6노드 모두 firewalld/nftables disabled·inactive, kubelet/containerd enabled·active다. 선택한 unit 검색 범위에서 별도 fds/calico/guard/iptables service는 추가되지 않았다. unit dependency·시작 monotonic timestamp·파일 해시는 원본에 있다.

- [CP3 기존 재부팅](https://github.com/321Team/fds-project-evidence/tree/43e26384ae422f2017f1e96e6c1bb5fe46d087d4/evidence/P1-K8S-01/cp-reboot-20260927)은 전후 steady-state와 CP02 EARLY 도달 공백을 구분한다. [이하영의 기존 수용](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5855751710)은 그 관측에 대한 결정이다.
- [Worker3 기존 재부팅](https://github.com/321Team/fds-project-evidence/tree/43e26384ae422f2017f1e96e6c1bb5fe46d087d4/evidence/P1-K8S-01/icr39-verification-20260927)은 reboot 전후 매트릭스 동일성을 보여준다. 부팅 전 구간의 연속 차단 관측으로 확대하지 않는다.
- 이번 조회는 모든 부팅 hook·커널 ruleset·Felix enforcement 시각을 조사한 것이 아니다. 현재6노드 전부의 공백 존재/길이 또는 새 위험수용을 확정하지 않는다. 이하영이 현 정책과 기존 결정의 적용 범위를 검토한다. 6대 재부팅·새 방화벽 레이어를 자동 요구하지 않는다.

## 실행·중단·복구

실행 소스는 source/ 및 각 runtime/<회차>/collector.py/bridge.py에 고정돼 있다. Python 표준 라이브러리, 기존 SSH 키/known_hosts, control/노드의 기존 sudo, kubectl15초 timeout이 전제다. 재실행이 필요할 때는 새 회차 label과 현재 대상/권한을 확인하며 기존 결과 폴더를 덮어쓰지 않는다. 호스트/계정 불일치·읽기 실패·출력 초과면 해당 수집을 중단한다. 설정 변경이 없으므로 원복 명령은 없고 기존 서비스·권한을 유지한다. 일괄 재시도·권한 완화는 하지 않는다.

검증: `python -I -B verify.py`를 이 디렉터리에서 실행한다. FILE_INTEGRITY_AND_RECORDED_OBSERVATIONS_PASS는 수신 파일/관측 대조만 뜻한다. 실제 업무 시험·AC 인수·독립 리뷰 PASS가 아니다. O01 수행자·시각은 미확정이고 작성자 검증을 제3자 재현으로 집계하지 않는다.
