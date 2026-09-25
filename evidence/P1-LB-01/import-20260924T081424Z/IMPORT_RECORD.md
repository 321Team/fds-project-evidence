# P1-LB-01 — infra-lb로 이관됐던 원본 증적의 증적 저장소 편입 기록 (2026-09-24)

판정: **원본 86개를 원래 경로에 바이트 그대로 편입한다. 새 판정이나 인수를 만들지 않는다.** Stage A 잔여 인수 조건(LB-A-01)과 Stage B 판정(PRECHECK_NOT_READY)은 원문 그대로이며 P1-LB-01은 In Progress다.

## 왜 편입하는가

- 두 수집회차는 원래 이 저장소의 PR [#14](https://github.com/321Team/fds-project-evidence/pull/14)(DAD 보완)와 [#15](https://github.com/321Team/fds-project-evidence/pull/15)(Stage B 사전점검)로 제출됐다. 2026-09-17 두 PR을 병합 없이 닫고 infra-lb [PR #2](https://github.com/321Team/infra-lb/pull/2)·[PR #3](https://github.com/321Team/infra-lb/pull/3)로 이관했다.
- 2026-09-23 사용자 결정으로 티켓의 증적 경로를 `fds-project-evidence:evidence/<Record ID>/`로 통일했고, 정책 적용 대상 저장소의 원칙은 "수신된 실행 원본·독립 검토 증적은 fds-project-evidence"다. 이관 뒤 이 저장소에는 이관 사실도 원본도 남아 있지 않았다(2026-09-24 전체 점검에서 발견).

## 편입 대상과 대조

| 수집회차 | 원본 PR HEAD | infra-lb 이관·병합 | 파일 |
|---|---|---|---|
| `evidence/P1-LB-01/stage-a/dad-supplement-20260916T150750Z/` | #14 `f74bda7eac39658c297a4dd5d1c590bd0717bcce` | PR #2, 병합 `134dfbd643b143a6d639bbc33b32b7cee2555f7f` | 34 |
| `evidence/P1-LB-01/stage-b/preflight-20260917T031743Z/` | #15 `c6ed08bdd7d54901dffc709fc9fa0d75e961f68b` | PR #3, HEAD `33914fcd9afaf24b8e1bb372f4dc6f2d201338af` 병합 | 52 |

- 가져온 방법: 이 저장소에 남아 있는 원본 PR HEAD 객체에서 `git checkout <HEAD> -- <경로>`로 가져왔다. 서버 재수집·재압축·내용 수정은 하지 않았다.
- 대조 결과(2026-09-24):
  - 86/86 파일의 Git blob SHA와 mode(100644)가 원본 PR HEAD와 같고, infra-lb main `41b33b138d5e8a1dce3d4b2d9a3d7ed30afd72ed`의 같은 경로와도 같다.
  - DAD `raw/SHA256SUMS`, Stage B `SHA256SUMS`와 `raw/SHA256SUMS`를 각 폴더에서 `sha256sum -c`로 검사해 모두 통과했다.
- 원본 PR의 루트 `README.md`·`REGISTRY_SHA256SUMS` 변경은 가져오지 않았다(당시 상태 문구). 대장은 현재 규칙대로 새로 등록했다.

## 검토 이력 (참고)

- infra-lb PR #2: 이하영 Approve 2회(HEAD `3b8c22b`). 이후 `.gitignore` 범위 축소와 본문 정정을 반영한 HEAD `5074a03`을 Lead 이권욱이 병합했다(PR 본문 기준, 증적 파일 변경은 없다고 기재).
- infra-lb PR #3: 이하영 Approve(HEAD `a519120`)와 base 전환분 재확인 "이상 없음"(HEAD `c7b0601`), Lead 이권욱 병합.
- 이 리뷰는 infra-lb 저장소에서 이뤄진 것이다. [EVIDENCE_POLICY](../../../governance/EVIDENCE_POLICY.md)에 따라 이 편입 PR은 이 저장소에서 별도 독립 검토를 받는다. 이전 승인을 이번 편입 승인으로 옮겨 적지 않는다.
- 당시 리뷰가 확인하지 못한 항목(원본 tar.gz 외부 SHA-256 대조, `collector-used.py`와 배포 v1.0 원본 대조)은 이번에도 확인하지 않았다.

## 이후 관리

- 두 수집회차의 정본 위치는 이 저장소다. infra-lb의 같은 파일은 이관 당시 사본으로 남는다. infra-lb 문서의 경로 안내를 바꿀지는 infra-lb Lead(이권욱)가 판단한다.
- 새 LB 증적은 `evidence/P1-LB-01/` 아래에 편입한다.
