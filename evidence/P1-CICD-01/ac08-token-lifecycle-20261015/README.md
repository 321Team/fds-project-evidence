# P1-CICD-01 AC08 단기 토큰 만료·재발급 실제 관측

2026-10-15 KST / CODEX_ASSISTED / 실행·Lead 작업 지원: 이권욱 / 증적 독립 검토: 요청 예정.

## 판정

**RUNTIME 관측 PASS / 증적 REVIEW·MERGE 및 Lead AC08 인수 대기.**
동일 SA·동일 Deployment의 고정 GET에서 유효 토큰 HTTP 200 → 만료 토큰 HTTP 401 → 새 토큰 HTTP 200을 확인했다.
TokenRequest 명령은 정확히 2회이며 자동 반복은 없었다. 유효기간은 각각 900초다.
이는 고정 진단 경로의 관측이며 전체 Delivery, 실제 배포·롤백, 다른 API/권한의 전수 시험 결과가 아니다.

책임: [infra-cicd #11](https://github.com/321Team/infra-cicd/issues/11),
[baseline #16](https://github.com/321Team/fds-project-baseline/issues/16).

## 실행·승인 연결

- 코드 [PR83](https://github.com/321Team/infra-cicd/pull/83), 검토 HEAD `4043d975fdcd72aa38e2dca5e57e00ebc7ecbd70`.
- 이하영 [독립 코드 APPROVED](https://github.com/321Team/infra-cicd/pull/83#pullrequestreview-5526395946), 검토 대상 SHA 일치.
- 실제 실행 source는 병합 commit `c373f1d7a8e6e84548180839098c34e9a1262eef`. broker와 8개 module을 해당 commit에서 추출하고 검토 HEAD와 바이트를 대조했다.
- PR CI [38583520277](https://github.com/321Team/infra-cicd/actions/runs/38583520277)와 병합 CI [38659948197](https://github.com/321Team/infra-cicd/actions/runs/38659948197)는 SUCCESS. CI는 Runtime 관측과 구분한다.
- bundle SHA256 `f213fcc9addbf802b45308d5a1dc4b73666aac9606d03256e19d02057d6bf12e`.
- 사용자 “착수”의 실행 범위, 두 번 발급 상한, 09:35~10:05 KST 종료 기한, 세 세션의 비중첩 회신과 PMO 상태 조회를 `EXECUTION_AUTHORITY.json`·`COORDINATION_FINAL.json` 등에 보존했다. [실행 전 공지](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6181605773).
- 명령의 시작/종료는 **2026-10-15T09:35:12+09:00 ~ 2026-10-15T09:51:28+09:00**, rc=0. `native-execute.receipt.json`에 공개 argv와 stdout/stderr hash가 있다.
- 중계 ansible01/server01_ansible → 발급 CP1/server02 → 소비 cicd-runner01/server01_cicd-runner. 정상 계정·기존 SSH trust·CA를 사용했다. CP1의 별도 앱·RBAC 전후 수집은 기존 svc_ansible의 읽기 전용 sudo 경로다.
- API `10.1.93.109:6443`, SA `ci-cd/cicd-runner-sa`, UID `8f1ddfef-7bec-4b15-8cb7-c4b1a068a176`. 실제 Kubernetes v1.36.4 및 3호스트 NTP 동기 상태는 `CLOCK_VERSION_CHECK.json`과 해당 원본에 있다.

## HTTP·토큰 관측

세 요청은 모두 `GET /apis/apps/v1/namespaces/fds-app/deployments/transaction-api`다. API IP/CA 검증, 무재시도, proxy/redirect 미사용 조건이다.

| 단계 | HTTP | 소비자 관측 시각(KST) | TLS 응답 Date(KST) |
|---|---:|---|---|
| valid | 200 | 2026-10-15T09:35:14+09:00 | 2026-10-15T09:35:14+09:00 |
| expired | 401 | 2026-10-15T09:51:28+09:00 | 2026-10-15T09:51:28+09:00 |
| recovery | 200 | 2026-10-15T09:51:28+09:00 | 2026-10-15T09:51:28+09:00 |

| 토큰 | 발급(KST) | 만료(KST) | JWT/status 유효기간 |
|---|---|---|---|
| 1 | 2026-10-15T09:35:13+09:00 | 2026-10-15T09:50:13+09:00 | 900초 |
| 2 | 2026-10-15T09:51:28+09:00 | 2026-10-15T10:06:28+09:00 | 900초 |

만료 401의 서버 Date는 첫 JWT 만료보다 **75초 뒤**다. 검토된 Runtime 코드가 응답 본문의 v1/Status·Failure·Unauthorized·code401과 Date를 확인한 뒤 허용 필드만 공개 영수증에 남겼다. 원문 TokenRequest/TokenReview 응답이나 Authorization 값은 증적으로 저장하지 않았다.
두 번째 발급은 첫 401 검증 후에만 수행했다. 두 토큰 모두 fresh TokenReview와 동일 SA UID가 연결되며 두 200 응답의 Deployment UID가 같다.
preflight는 TokenRequest 0회, 실제 회차는 2회다. 이 숫자는 발급 명령 횟수이며 API audit의 모든 발급 이벤트를 전수 조사한 숫자가 아니다.

## 전후 상태와 정리

- 실행 직전/직후 Deployment 2개·Ready Pod 6개의 UID, generation/spec, image/imageID, restart·Ready 등 비교 필드가 일치했다. `app-fresh`·`app-after`를 고정 버전 comparator로 검증했다.
- 관련 Binding 5개·Role 5개와 SA UID가 유지됐다. 변경 여부는 수집한 관련 객체 범위다.
- broker 및 세 endpoint는 cleanup ACK와 정상 종료를 반환했다. 전후 source/staging 폴더 총 8개, 공개 파일 58개의 예상 이름·SHA256·소유자·0700/0600 권한을 확인했다.
- 세 정상 계정의 진단 Python 프로세스 잔존 0, 접근 불가·분류 불가 후보 0. Runner의 별도 Worker/Scan/Podman/Ansible 실행 0, 기존 Listener는 유지됐다.
- 위 공개 source/staging와 로컬 결과·로그를 값 출력 없이 비밀정보 패턴 검사했다. 기대 외 파일 및 패턴 일치 0. 공개 source는 hash 고정 상태로 보존했다.
- `WINDOW_RELEASE.json`의 사후 확인 시각은 2026-10-15T09:51:39+09:00. 논리 토큰 참조는 해제했으며 서버 폐기(revocation)는 수행하지 않았다. 특히 새 토큰의 자연 만료는 위 표의 시각이다. 작업창 해제는 실행·자격증명 참조·프로세스 정리를 확인한 뒤 별도 통보한다.
- 이번 진단은 Actions Runtime/Artifact를 생성하지 않았다. 전체 디스크·audit 로그·swap·물리 메모리 zeroization 또는 다른 회차 Artifact 무잔존을 주장하지 않는다.

## 파일과 재검증

- `raw/`: 실행 호스트가 반환한 공개 JSON/stdout/stderr와 로컬 transport 영수증의 **수신 바이트 그대로**. 소스 고정·권한·비중첩·사전/사후 수집 기록 포함.
- `raw/source/`, `raw/lifecycle-source.json`: 병합본 runtime 코드/bundle 사본. `SOURCE_BINDING.json`으로 Git blob·SHA256·검토 HEAD 바이트 일치를 연결한다.
- `references/`: 병합본 설계/검증 함수·중앙 정책·조회 시점 PR/리뷰/CI·기존 수집 transport. 원본 출처를 각 파일/REFERENCE_BINDING으로 연결한다.
- `verify.py`: 로컬 전용 정합성 검사. HTTP 순서·시각·두 토큰 메타데이터·같은 UID·입력 hash·전후 상태·정리 범위·manifest를 대조한다. 네트워크/발급/실서버 실행을 하지 않는다.
- `SHA256SUMS`: 자기 자신을 제외한 이 수집회차 파일 전체. 저장소 `REGISTRY_SHA256SUMS`에서 이 manifest를 연결한다.

원본 수집 스크립트는 추적 자료이며 리뷰 과정에서 실행하지 않는다. 오프라인 검증은 이 폴더에서 아래 한 줄만 사용한다.

```sh
python -B verify.py
```

신규 `read_cleanup.py` 및 시계 수집은 중앙 정책의 순수 읽기 전용 Pre-check/Post-check 범위로 실행했으며 **코드 독립 REVIEW=NOT PERFORMED (Pre-check)**다. 서버 설정/서비스/권한을 바꾸지 않는다. 검토된 lifecycle Runtime 코드의 독립 승인과 혼동하지 않는다. 증적 전체의 독립 편입 검토는 별도로 요청한다.

## 잔여

독립 증적 검토·병합 → Lead AC08 인수 판정 → 별도 입력/승인/비중첩을 갖춘 AC09 이전 승인 digest 복귀 시험 순서다. 본 회차의 발급 허용은 소진했다.
`DEPLOY=NOT_EXECUTED`, `DELIVERY_GATE=NOT_VERIFIED`, `server_revocation=NOT_PERFORMED`를 유지한다.
