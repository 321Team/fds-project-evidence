# P1-SEC-01 — Edge Cutover RUN 20261008T1730 원본 (C1 rc4 → rollback, 판정 결함 확인)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 2026-10-08 16:15~19:30 KST 창에서 실행했다가 C1에서 멈추고 원복한 회차의 원본이다. **C1 완료가 아니며, rollback도 스크립트 결과는 rc4이다.** 이어진 성공 회차는 [`../edge-cutover-20261008T1800/`](../edge-cutover-20261008T1800/README.md)에 있다.

## 출처
| 항목 | 값 |
|---|---|
| 승인 | [6054208925](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6054208925)(A3 GO·Cutover 조건부 GO), 착수 시각 변경 [6054554864](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6054554864) |
| A3 사전 확인 | [6054358460](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6054358460)(콘솔 전사). 시험 파일은 이 폴더에 넣지 않았다 |
| 코드 | [infra-kubernetes#75](https://github.com/321Team/infra-kubernetes/pull/75) 병합 `c112e4131822be2bbf82d7014beaf954c758d90d`. `edge01-cutover.sh` `0405cf0499fc085a3fe6b170dff082a1fc0dd8588dee7a9d2ba8b6ec5a461250`, 나머지 3개는 1800 회차와 같은 SHA |
| 결과 보고 | [#19 6055218019](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6055218019) |

## 파일
| 파일 | 내용 | SHA-256 |
|---|---|---|
| `edge01-edge-cutover-20261008T1730.tgz` | edge01 `~/edge-cutover-20261008T1730/`(check·apply·rollback 로그, `upstream-file.*`, `manual-rollback-verify-rbman163702.txt`, `smoke-rbman163702.json`) + `/var/tmp/edge-cutover-capture-20261008T1730/{check,apply,rollback}/` | `a5f611a2c2ebee7953dbcce1c596747c1db4c1e2771cb937ad98566e69a1fd50` |
| `control01-edge-cutover-20261008T1730.tgz` | control01 pre `161522` | `552b0e15adf977de62d91d982afc040fbcd2513024627b205cc387e9e2d14b41` |
| `ansible01-edge-rx-20261008T1730.tgz` | Worker report check/apply, C0 인계 수신본, judge check 출력, Worker 3대 캡처 원본 tgz·목록 | `b00e4c3b4450c90b6d88b2b640214bf510f9daae71aa196ffdd970dd646b0ca7` |

- sidecar 출처와 비밀정보 검색 결과는 1800 README와 같다(일치 0건).

## 진행·관측 (원본 보존 — 판정 아님)
| 단계 | KST | 관측 |
|---|---|---|
| C0 | 16:15~16:29 | pre COLLECTED, edge check rc0 `tag=check162518`, judge `scope=all METHOD_READY` rc0 |
| C1 apply | 16:31:31~16:32:10 | 4줄 전환·`nginx -t`·reload(16:31:32, journal `Reloaded`)는 됐으나 반영 판정 7회가 `설정 수정 16:31:32 / worker 시작 16:31:31`로 **rc4 UNCONFIRMED**. 표식·smoke 미발송 |
| rollback | 16:34:31~16:35:10 | 사본 복원(`.50`)·reload(16:34:32) 뒤 같은 판정으로 **rc4** |
| 수동 보완 관측 | 16:37:02 | tag `rbman163702`: upstream `.50`, GET 3/3 200, `/metrics` 404, smoke 201. edge01 rollback 캡처에서 표식 4건이 E-K3S Pod(`10.42.0.198`·`.193`)로 각 1번(`xri=10.1.93.50`). db01 `SIM_cut_202610081730_rbman163702` 1행 false/false. **스크립트 rc는 4 그대로** |

원인: worker 시작 시각을 `ps lstart`(btime 초 단위 버림 + 경과)로 읽어 실제보다 최대 1초 이르게 나왔다(16:34:11 `etimes=159`, `btime 1791248670` → 실제 16:31:32). 같은 RUN 재apply는 `upstream-file.before` 가드로 하지 않았다. 수정은 infra-kubernetes#77(하한 비교 + reload 전 `sleep 1`).

AI 사용: CLAUDE_ASSISTED
