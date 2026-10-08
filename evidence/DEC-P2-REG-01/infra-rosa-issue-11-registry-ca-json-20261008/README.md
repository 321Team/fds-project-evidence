# DEC-P2-REG-01 — ROSA HCP registry 추가 CA 제출 JSON 후보 (2026-10-08 KST)

- 대상 이슈: [321Team/infra-rosa#11](https://github.com/321Team/infra-rosa/issues/11) (원티켓 [DEC-P2-REG-01 — fds-project-baseline#42](https://github.com/321Team/fds-project-baseline/issues/42) Sub-task 3/4, D22 출력 4 "CA/trust" 입력, 테스트 전략 추적 TS08)
- 근거 댓글: [리뷰 반영 — 출력 4 고정](https://github.com/321Team/infra-rosa/issues/11#issuecomment-6056861867) · 리뷰 요청: [요청 4 심층 리뷰 §완결 전에 고칠 부분 1](https://github.com/321Team/infra-rosa/issues/11#issuecomment-6056068014)
- 이 폴더는 **생성 전 입력 후보**다. ROSA 생성, CA 적용, cold-pull, D22 Final, 생성 GO를 의미하지 않는다.

## 파일

| 파일 | 내용 | SHA256 |
|---|---|---|
| `rosa-hcp-registry-additional-trusted-ca.json` | 제출 JSON 후보. 4114 B, key 2개 | `4d86507ecd81789e376669940f68b2dbb27f5989e6fd4315238c9f61a2401da4` |
| `make_registry_ca_json.py` | 생성 스크립트 (아래 규칙) | `8d55707cbcd0c1fddad1418fc86d06ffc1269a546738ecfebe74b6bd45f8c7e1` |
| `generation-log.txt` | 생성 시각·호스트·도구 버전·소스·명령·RC·출력 | `SHA256SUMS` 참조 |

## 수집 정보

| 필드 | 값 |
|---|---|
| ENV | 로컬 PC 오프라인 생성 (ROSA·AWS·OCM·Harbor 접속 없음) |
| 생성 시각 | 2026-10-08T18:30:49+09:00 (`generation-log.txt`) |
| 실행 호스트 / 도구 | Windows PC (Git Bash) / Python 3.14.6 / git 2.54.0.windows.1 |
| 소스 | `321Team/fds-project-evidence@9472f17f13dd6828b6895a47552dcdb9778fb25d:evidence/P1-MON-01/pf-run2-canary-20261006T0725Z/worker03/canary-20261006/fds-root-ca.crt` |
| 소스 blob / SHA256 | `0cfb3414d71c4501621e6c4aa6f72b29d317f355` / `20ddfa5e92c346aaf46fc30179fbc0b069e256effd2615a9f4308a8fe719053f` (2004 B) |
| 명령 | `git show <commit>:<소스> > root-9472f17.crt` → `python -I make_registry_ca_json.py root-9472f17.crt rosa-hcp-registry-additional-trusted-ca.json 10.1.93.54 harbor.fds.internal` |
| RC | 0 (key 순서를 바꾼 재생성도 RC 0, 같은 SHA) |

Root PEM 자체는 위 소스 경로에 이미 있으므로 이 폴더에 복사하지 않았다(`.gitignore` `*.pem`).

## 생성 규칙 (재현 방법)
- JSON 형태: `{"<registry host>": "<PEM>"}` ([ROSA HCP image configuration](https://docs.redhat.com/en/documentation/red_hat_openshift_service_on_aws/4/html/images/image-configuration-hcp))
- 정규화 규칙:
  - key 정렬
  - `separators=(",", ":")`
  - `ensure_ascii=True`
  - PEM 값은 소스 파일과 바이트가 같아야 함 (LF, 마지막 줄바꿈 포함)
  - 파일 끝에 줄바꿈 없음
- 스크립트 내부 검사(assert):
  - CERTIFICATE 블록이 정확히 1개
  - `PRIVATE KEY` 문자열 없음
  - 다시 파싱했을 때 key 집합과 모든 값이 입력과 같음
- 같은 소스와 같은 key 집합이면 key 입력 순서와 무관하게 같은 바이트가 나온다(`generation-log.txt`의 두 번째 실행).

## key 선택 근거

| key | 근거 |
|---|---|
| `10.1.93.54` | P0 기본은 IP endpoint([fds-project-baseline#40](https://github.com/321Team/fds-project-baseline/issues/40)). 1차 manifest도 이미지를 IP로 참조한다 |
| `harbor.fds.internal` | leaf CN/SAN. D23에서 FQDN을 채택해도 key를 추가할 필요가 없다. 생성 후 registry 값을 바꾸면 전체 machine pool 노드가 교체되기 때문이다 |

- 두 이름 모두 leaf SAN(`DNS:harbor.fds.internal`, `DNS:harbor01`, `IP Address:10.1.93.54`)에 있다. 근거: [`../infra-rosa-issue-9-harbor-leaf-tls-20261004T153703/`](../infra-rosa-issue-9-harbor-leaf-tls-20261004T153703/README.md).
- Lead 리뷰의 오프라인 검증(cryptography 50.0.1)에서 FQDN과 IP 모두 PASS했다.
- 이 map은 신뢰할 CA를 지정할 뿐이다. 네트워크 허용 범위(firewall/allowlist)를 넓히지 않는다.

## 판정 범위

| 항목 | 판정 | 비고 |
|---|---|---|
| JSON 형식·key·값 무결성 | PASS (로컬 assert, RC 0, 결정적 재생성) | CLI도 값이 문자열인지만 검사한다 |
| PEM CERTIFICATE-only · `CA:TRUE` | PASS (10-08 #11 ③ 검토) | `pathlen:0`, 2031-09-14까지 유효 |
| HCP가 IP key를 실제 pull trust에 적용하는지 | **미확인** | infra-rosa#4 cold-pull에서 확인. 실패하면 manifest를 FQDN으로 바꾼다(재생성 불필요) |
| ROSA 생성·CA 적용·cold-pull | **NOT RUN** | 사용할 `rosa` CLI·rhcs(≥ 1.6.5) 버전은 생성 실행 기록에 고정 |
| D22 Final | NOT ISSUED | Decision Lead 소관 |

## 민감정보
공개 Root 인증서, 호스트명, IP, 해시, 도구 버전만 들어 있다. private key, token, Robot secret, Pull Secret은 없다.
