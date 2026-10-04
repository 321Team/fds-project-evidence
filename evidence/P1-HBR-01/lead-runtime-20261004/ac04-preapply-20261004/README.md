# AC-04 적용 전 정적 검증·읽기 전용 사전 점검 — 2026-10-04 KST

수행: 이하영 / ansible01 `server01_ansible` / `~/p1-ans-01`. 대상 코드: infra-ansible PR #63 정확한 HEAD `f222f1f15c52c74c1800ce1b4040a21e439e19ed`(작성자 이권욱, 코드 Approve 이하영, CI success). 변경 없음(`changed=0`). 파일은 서버 결과 파일을 텍스트로 옮겨 **서버에서 계산한 해시와 바이트 동일**을 확인했다.

| 파일 | 내용 | 서버 SHA256 |
|---|---|---|
| `ac04-static-20261004T174627.txt` | runbook §4: HEAD 일치, 플레이북 5개 `--syntax-check` rc=0, contract `PASS`, 테스트 11/11 ok, `TESTS_RC=0` (17:46:27 KST) | `ba2ef71cd2b3475e1694e0ed74670e650efe727534a15ec5544993b64142d9c4` |
| `ac04-precheck-20261004T174413.txt` | runbook §5: `p1-hbr-01-ac04-precheck.yml` 전체 출력, `PRECHECK_PASS_RUNTIME_NOT_CHANGED`, `ok=47 changed=0 failed=0`, nft 1.1.5, guard `ABSENT`, generic 443 `PRESENT` (17:44:13 KST) | `54bb5ffc1439278166c740c4b5c020d834644612ef8d6ffdbad93105e7049df5` |

한계: 이 결과는 **Runtime 적용 전** 상태 확인이며 AC-04 PASS도 적용 승인도 아니다. 사전 점검은 17:44 시점의 상태이고 적용 직전 재실행이 필요하다. `~/p1-ans-01`에는 이 작업과 무관한 추적되지 않는 `ICR_*` 파일들이 있었으나 코드 변경은 없었다. 최초 정적 검증 실행(ansible01 17:4x)은 화면으로만 확인했고 이 파일은 두 번째 실행(저장본)이다.
