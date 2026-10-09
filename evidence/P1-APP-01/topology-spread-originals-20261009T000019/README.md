# P1-APP-01 잔여 원본14개 수신 — 2026-10-09 00:00 KST

CODEX_ASSISTED · 수집 이권욱 / 원 실행 APP Lead 이재환. [#15 원문 보충 기록](https://github.com/321Team/fds-project-baseline/issues/15#issuecomment-6033218381)의 서버 전용14개를 새 시험 없이 회수했다.

## 결과와 출처

- 서버 `k8s-control01` / `10.1.93.102`, 원 경로 `/home/server02/p65-apply-20261007/`.
- 전달 경로: Windows → 기존 `fds-ansible01`(server01_ansible) → 기존 키의 `svc_ansible` SSH + `sudo -n python3 -`. 접속 신뢰나 권한을 새로 만들지 않았다.
- 서버 읽기 시각 **2026-10-09T00:00:20.301241~00:00:20.306866+09:00**, outer rc0. [사용자 확인 단독 창](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6062332401) 안이다.
- dry-run 전체 JSON4개와 MON Pod JSON10개 **14/14 수신**. 서버에서 읽은 bytes 및 로컬 수신 bytes 모두 기존 #136 `SHA256SUMS.all` 항목과 일치한다.
- 기준 manifest SHA256: `021b958282704ac79e3a6421fad316c5782ce2ab826fbb9d1d33c8fb871b0a98`. `SOURCE_SHA256SUMS.all.txt`는 [기존 편입본](../topology-spread-apply-20261007T0540Z/control01/p65-apply-20261007/SHA256SUMS.all)의 바이트 사본이다. 새 서버 manifest를 과거 기록으로 만들지 않았다.
- [#138의6개](../topology-spread-apply-supplement-20261007T0729Z/README.md)와 이번14개를 합쳐, 당시 미편입20개의 수신 보완이 완료됐다. 편입 리뷰·AC 인수는 별도다.

## 파일과 검증 방법

- `original/`: 수신한 원본14개. 바이트 수정·줄바꿈 정규화 없음.
- `receipt.stdout.json`: 서버가 실제 반환한 메타데이터·base64 원문 전체. 각 파일을 디코딩하면 `original/`과 같다.
- `metadata.json`: 위 stdout에서 base64 본문만 제외한 파생 인덱스. 서버 경로·크기·권한·UID/GID·mtime 및 expected/actual SHA256을 보존한다.
- `invocation.json`, `receipt.stderr`, `collector.py`: 명령·시각·rc·실행 코드 SHA와 실제 stdin 수집 코드. `receipt-driver.py`는 Windows 실행자의 코드 사본이다.
- `SHA256SUMS`: 이 수신회차의 현재 파일 무결성. 과거 manifest와 별개다.

리뷰어는 각 원본 SHA256을 `metadata.json`과 `SOURCE_SHA256SUMS.all.txt`의 해당 상대 경로에 대조하고, stdout base64 디코딩 값도 같은지 확인할 수 있다. 원 manifest에는 이번 범위 밖 파일도 있으므로 이 폴더에서 원 manifest 전체를 실행해 빠진 파일을 새 실패로 해석하지 않는다.

## 제한

이 결과는 **기존 파일 수신·무결성 보완**이다. 새 dry-run·배포·MON 재시험·Pod exec·서비스 변경은 없다. fds-engine MON60.9647초 절차 이탈, 당시 fds-engine Service EndpointSlice 미수집, HA·현재 배치 인수 등은 변경하지 않는다.

수집 코드는 독립 리뷰 미수행이며 이미 승인된 계정으로 제한된 파일14개만 읽고 stdout으로 반환하는 순수 수집기로 사용했다. 시간창/호스트/regular file·크기·읽기 중 변경·기존 해시 확인을 수행했다. 자체 검증은 독립 증적 리뷰가 아니다.

개인키·GitHub token·JWT·credential URI 패턴 및 JSON의 민감 env literal 검색에서 검출0. 패턴 기반 점검의 한계를 유지하며 원본에 비밀값을 덧붙이지 않았다.

RUNTIME_NEW_TEST=NOT_RUN / ORIGINAL_RECEIPT=14_OF_14 / HISTORICAL_MANIFEST_MATCH=14_OF_14 / REVIEW=REQUESTED_SEPARATELY / AC=UNCHANGED.
