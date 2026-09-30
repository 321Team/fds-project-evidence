# P1-HBR-01 — Harbor AC Runtime 검증 원본 (2026-09-30)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 같은 PR의 [`received-20260928T150921Z`](../received-20260928T150921Z/README.md)(read-only 사전 수집)에 이어, 이번엔 `infra-harbor-trivy/scripts/verify/` 검증 스크립트를 실제 서버(cicd-runner01, k8s-worker01/02/03, mgmt-gw01)에서 실행한 결과를 편입한다.

| 항목 | 값 |
|---|---|
| 원본 | `p1-hbr01-ac-verify-20260930T040033Z.tar.gz` |
| SHA-256 | 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 도구 | [infra-harbor-trivy `scripts/verify/`](https://github.com/321Team/infra-harbor-trivy/tree/main/scripts/verify) — `tls-negative-test.sh`, `worker-pull-pod-start-test.sh`(로컬 2건 수정, 아래 참고), 신규 작성 `runner-push-test.sh`(IF-09용, 이 저장소 밖 별도 파일) |
| 실행 | cicd-runner01, k8s-worker01/02/03, mgmt-gw01. 2026-09-30 KST |
| 수집·제공 | 이하영(P1-HBR-01 Lead). 스크립트 로컬 수정·패키징은 Claude Code(CLAUDE_ASSISTED). 실제 명령 실행은 이하영이 직접 수행 |

## 수신 검증

- tar.gz 내부 `SHA256SUMS`(6개 파일 대상) 재계산 일치
- 비밀정보 검색: `grep -inE "password|secret|-----BEGIN|BEARER|Authorization:"` 전체 파일 대상 0건

## 내용물 요약 (원본 보존 — 판정 아님)

| 파일 | 대응 AC | 내용 |
|---|---|---|
| `tls-negative-test.sh` 실행 로그 | Harbor Service/Health·Certificate Chain | cicd-runner01에서 실행. 정상 CA로 `/api/v2.0/health` 성공(전 컴포넌트 healthy) + 잘못된 CA로는 curl Exit Code 60(인증서 검증 실패)로 정확히 거부 확인 |
| `runner-push-run.log` | IF-09 Runner Push/Pull Positive/Negative | cicd-runner01, Robot 계정 `robot$push`로 로그인+push 성공(Positive), 잘못된 credential로는 로그인 거부(Negative) |
| `worker0{1,2,3}-pull-run.log` | IF-10 Worker Pull/Pod Start/Push DENY, AC-05 일부(Digest Traceability) | 워커 3대 각각: Robot 계정 `robot$worker`로 crictl pull 성공, Push는 인증 성공 후 `action: push` 권한 거부로 정확히 차단, Pod 생성→Ready, Harbor manifest digest와 Pod imageID digest 완전 일치 확인, cleanup까지 정상 |
| `mgmt-gw01-source-ip-allowlist-evidence.txt` | 실제 Source IP/Host Firewall Allowlist | mgmt-gw01 firewalld policy(`mgmt-to-physical`, target=DROP) 원문 발췌: harbor01(`10.1.93.54`):443은 Runner(`10.250.10.20`)에만 명시적으로 허용, ansible01(`10.250.10.10`)은 SSH/ICMP만 허용(443 없음). 실제 접속 테스트로도 ansible01→harbor01:443은 timeout(Negative), Runner→harbor01:443은 정상(Positive) 확인됨 |

## `worker-pull-pod-start-test.sh`에 적용한 로컬 수정 2건 (미리뷰, 투명성 목적 기록)

원본 스크립트를 실행 중 발견한 문제를 그 자리에서 고쳐서 worker01/02/03에 적용했다. **이 수정은 infra-harbor-trivy 저장소 PR 리뷰를 거치지 않았다** — 정식 반영 여부는 그 저장소 담당자가 별도로 판단해야 한다.

1. **Push DENY 체크가 이미 존재하는 태그를 재사용**: 원본은 pull에 쓴 것과 같은 태그로 push를 시도해, 내용이 이미 서버에 있으면 실제 쓰기 권한 검사 없이 "성공"으로 끝나버렸다(최초 실행에서 실제로 이렇게 오탐 발생 — 재현·기록함). 수정: push 직전 `worker-push-denytest-<REVIEW_RUN_ID>`라는 새 고유 태그로 재태깅 후 그 태그로 push하도록 변경(`worker-push-deny-test.sh`가 이미 쓰던 것과 동일한 패턴).
2. **Push 거부 판정 문구가 `docker` 전용**: 원본은 `denied: requested access`(Docker 문구)만 인식했는데, 이 환경은 `docker` 대신 `nerdctl`을 쓰고 있어 실제 거부 시 다른 문구(`unauthorized to access repository ..., action: push`)가 나온다. 원본 그대로였다면 정당한 권한 거부도 FAIL로 오판정됐을 것(최초 실행에서 실제로 이렇게 됨 — 재현·기록함). 수정: 두 문구 중 하나라도 매치하면 PASS로 인정하도록 판정 정규식 확장.

## 배경과 한계

- **Robot 계정 정합성 미확인**: IF-09에 실제로 쓴 계정은 `robot$push`("Python3 베이스 이미지 등록용")이다. Harbor UI의 `robot$worker` 계정 설명에는 "Runner(fds-ci)"라는 문구가 있었으나, baseline(`D19`/`D-SEC-01` 등)에는 이 문구의 근거를 찾지 못했고, 실제 CI 워크플로우(`infra-cicd` 저장소, cicd-runner01의 `actions-runner/_work` 하위)에도 Harbor push 로직 자체가 없었다(별도 위치이거나 미구현으로 추정). **어떤 Robot 계정이 실제 운영 CI가 쓰는 계정인지는 이 편입으로 확정되지 않는다.**
- **AC-05(Digest·Scan·Credential fingerprint)는 부분만 확보**: `digest-traceability-check.sh`로 Harbor manifest ↔ Pod imageID 구간(3대 전부)만 확인했다. CI Scan Digest(P1-CICD-01 #16 담당) 연결은 이 편입 범위 밖이며, 4/4 전체 trace로 표시하지 않는다.
- **`crictl`/`nerdctl`이 워커 3대에 원래 설치돼 있지 않았음**: 이번 실행을 위해 GitHub 공개 릴리스에서 받아 `/usr/bin/`에 설치했다(`sudo`의 `secure_path`에 `/usr/local/bin`이 없어 처음엔 `/usr/local/bin` 설치가 무시됨 — `/usr/bin`으로 재설치). 이 설치 자체는 되돌리지 않았다.
- **Source IP/Firewall 항목은 별도 Positive/Negative 전용 스크립트가 아니라, 기존 firewalld 정책 조회 + 우연히 관측된 접속 성공/실패 결과를 근거로 삼았다.** 정식 절차라면 승인된 별도 절차로 재확인이 필요할 수 있다.
- 이 실행에도 [`received-20260928T150921Z`](../received-20260928T150921Z/README.md)와 같은 `svc_ansible` 프로비저닝(계정 신설, `NOPASSWD: ALL`, key 미제한)이 전제로 깔려 있으며, 그 잔여 하드닝 상태는 여전히 미해소다.

이 편입은 원본 보존이다. P1-HBR-01의 최종 AC 판정, Gate, 티켓 상태는 Lead/Review Owner가 baseline #13에서 별도로 한다.
