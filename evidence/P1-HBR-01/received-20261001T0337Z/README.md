# P1-HBR-01 — blackbox-exporter Harbor push·Trivy, node-exporter Trivy, monitoring pull secret 교체 (2026-10-01 12:22~12:48 KST)

MON Lead(이재환)가 k8s-control01(`server02`)에서 실행했다. HBR Lead(이하영) 승인 근거:
- Harbor push·조회·스캔: 2026-10-01 회의 구두 승인(`robot$push`로 push). 서면 [5923320268](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5923320268)은 조회·스캔 허용, TLS 검증 유지, 자격증명 미기록 조건이다.
- monitoring pull secret 교체: [5923863983](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5923863983) B안 승인.

결과 보고: [#13 5924275301](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5924275301)(push·스캔), [#13 5924371172](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5924371172)(B안 완료).

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/bb-push-20261001T122248/` | `~/bb-push-20261001T122248/` 중 13개 | `bb-push-small-20261001.tar.xz` 5,420 B, SHA-256 `fb2f23c0…bcae058` | base64로 받아 복원, 서버 `sha256sum`과 일치 |
| `control01/p1-mon-pullsecret-20261001T124445/` | `~/p1-mon-pullsecret-20261001T124445/`(30개) | `p1-mon-pullsecret-20261001.tar.xz` 3,988 B, SHA-256 `65a389ce…01fae7a4` | 같음. 서버 `SHA256SUMS` 30줄 모두 OK |

개별 파일은 archive를 그대로 푼 것이다. archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다. 폴더 이름의 수신 시각(03:37Z)은 첫 묶음 기준이다.

## 1. blackbox-exporter push·Trivy, node-exporter Trivy (`bb-push-20261001T122248/`)

control01은 인터넷이 없고, control01에서 바깥으로 파일을 옮기는 경로(scp)가 없어 base64 붙여넣기로 받을 수 있는 작은 파일만 골라 묶었다. 그래서 서버 폴더의 아래 두 파일은 편입하지 않았고 해시만 기록한다(`SHA256SUMS-push`에 줄이 남아 있다).

| 편입하지 않은 파일 | SHA-256 | 위치 |
|---|---|---|
| `blackbox-exporter-065fc18.tar`(이미지, 37,659,648 B) | `8dbf198db7290e91557b954558d7fcd4853081ac8543a3f5b897e472e9fb98b6` | ansible01 `~/bb-build-20261001T112637/`, control01 같은 폴더 |
| `build-evidence-065fc18.tar.gz`(빌드 근거 묶음, 약 107 KB) | `1d22280d0d54d3d9c593c2e7b95906c679a59811ed7cdf934d07c6b75124f78e` | 같음 |

| 단계 | 근거 파일 | 결과 |
|---|---|---|
| 빌드 출처 | `build-evidence-065fc18.tar.gz.sha256` | [infra-monitoring#30](https://github.com/321Team/infra-monitoring/pull/30) 병합본 `build.sh`로 ansible01에서 빌드(11:26 KST) |
| load | `loaded-id.txt` | image ID `f99053f665c55ce925cb27b076f6097ee92bf337aaddedd30042d7cee32696cd`(빌드 결과와 같음) |
| push | `push.log`, `pushed.digest`, `pushed-at.txt` | 12:23:34 KST, `robot$push`, TLS 검증(`--cert-dir`, Root PEM SHA-256 `20ddfa5e…053f`), **`10.1.93.54/fds/blackbox-exporter@sha256:5969ff6a10da39cbcae4c7aa411eae6c9d2236ccc5725436b1c38b9cf7173c35`** (태그 `0.28.0-master.065fc18-candidate-20261001`) |
| manifest | `manifest-bb.json` | 파일 SHA-256 = push digest, `config.digest` = `f99053f6…` → load ID와 일치 |
| Trivy | `art-blackbox-exporter-5969ff6a10da.json`, `vuln-blackbox-exporter.json` | v0.62.1, 12:27:39~12:27:52 KST, **Critical 0 / High 0**, Medium 2(`golang.org/x/crypto` v0.55.0 → 0.56.0), Unknown 1 |
| Trivy | `art-node-exporter-56566542aacd.json`, `vuln-node-exporter.json` | `fds/node-exporter@sha256:56566542aacd5be06add01d3456cd6279e2f7ddb4b24237fc8cdfbc3cc5f699f`(push 2026-09-22 15:25 KST), 12:28:34~12:28:38 KST, **Critical 0 / High 9**(stdlib v1.26.5 8건, x/crypto v0.54.0 1건), Medium 2, Unknown 1 |
| 참고 | `art-prometheus-2c28708bb561.json` | 9/30 17:55 KST 스캔 결과(High·Critical 없음, Unknown 1) 재조회 |

- artifact·스캔 API는 `robot$push`로 403이라 **Harbor `admin`으로 스캔 요청(`POST …/scan`, HTTP 202)과 조회**를 했다. 서면 조건 밖이고 회의 구두 승인이다. 자격증명은 `read -s`로 입력해 `curl -K -`로 넘겼고 파일·명령줄에 남기지 않았다.
- `SHA256SUMS-push`는 서버에서 push 직후(12:25) 만든 것이라 스캔 JSON(12:27 이후)은 들어 있지 않다. 이 폴더 전체는 이 수집회차의 `SHA256SUMS`가 확인한다.

## 2. monitoring pull secret 교체 (`p1-mon-pullsecret-20261001T124445/`)

**운영 변경:** `monitoring-api/harbor-pull-secret`, `monitoring-node/harbor-pull-secret`의 계정을 Harbor `admin` → `robot$worker`(pull-only)로 바꿨다. `fds-app/harbor-pull-secret`을 같은 이름으로 복사(`get -o json` → metadata를 이름·namespace만 남김 → `kubectl replace`)했고 비밀번호를 손으로 입력하지 않았다. 매니페스트·Deployment·DaemonSet 변경 없음, 실행 중 파드 재시작 없음.

Secret 값은 어떤 파일에도 없다. 계정 확인은 username만 출력했고(`users*.txt`), 같은지 비교는 SAME/DIFF만 남겼다(`compare.txt`).

| 단계 | 근거 파일 | 결과 |
|---|---|---|
| 사전 | `secrets.txt`, `usage.txt`, `users.txt` | dockerconfigjson Secret은 3개(fds-app·monitoring-api·monitoring-node), 사용처는 Deployment 4개·DaemonSet 1개의 `imagePullSecrets`, ServiceAccount에는 없음. monitoring 두 개가 `admin` |
| 백업 | `backup.txt` | 클러스터 안 `harbor-pull-secret-bak-admin-20261001`로 복사(파일 백업 없음), rc=0 ×2 |
| 교체 | `replace.txt`, `compare.txt`, `users-after.txt` | replace rc=0 ×2, 두 namespace 모두 `fds-app`과 같음, 백업과는 다름, username `robot$worker` |
| 시험 Pull | `pod-api.yaml`, `pod-node.yaml`, `pod-node2.yaml`, `create*.txt`, `wait*.txt`, `result*.txt`, `ns-labels.txt` | `imagePullPolicy: Always`, digest 지정, restricted 조건. monitoring-api prometheus `2c28708b…` 2.197s 새로 받음 / monitoring-node node-exporter `56566542…` 32ms(노드에 있던 이미지) / monitoring-node blackbox `5969ff6a…` 335ms 새로 받음 — 모두 Succeeded·exit 0 |
| 영향 | `pods-before.txt`, `pods-after.txt`, `pods-final.txt`, `pods-*diff.txt` | 실행 중 파드 이름·노드·restartCount·startTime 변화 없음(diff rc=0 ×2) |
| 정리 | `cleanup.txt` | 시험 파드 3개·백업 Secret 2개 삭제, 잔여 없음 |
| 잔여 | `cluster-pullsecret-users.txt`, `admin-left.txt` | 클러스터 전체 dockerconfigjson Secret 3개 모두 `robot$worker`, `admin` 0건 |
| 시각 | `t-*.txt` | 12:46:06 교체 시작 → 12:47:26 시험 → 12:48:41 정리 → 12:48:42 끝 |

## 판정 범위

- 이 증적이 보여 주는 것: blackbox `5969ff6a…`가 #30 빌드 결과(config `f99053f6…`)와 같은 이미지로 Harbor에 들어갔고 Trivy Critical·High가 0이다. node-exporter `56566542…`는 High 9건이다. 이 클러스터의 monitoring pull secret에 `admin`이 남아 있지 않다.
- 승인·확정은 하지 않는다: blackbox 승인 digest 확정과 node-exporter 처리는 HBR Lead 대조 대상이다(#13).
- 범위 밖: edge01 k3s pull secret(`robot$fds-ci`, A안), 클러스터 밖 `admin` 사용처(스크립트·Ansible 변수·로그인 파일), Harbor `admin` 비밀번호 회전(C안), 빌드 근거 묶음·이미지 tar 원본 편입.

AI 사용: CLAUDE_ASSISTED (명령 준비, 수신 대조·문서화, 실행은 담당자 본인)
