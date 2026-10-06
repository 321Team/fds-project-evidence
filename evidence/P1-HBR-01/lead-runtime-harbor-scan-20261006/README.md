# P1-HBR-01 AC-05A — Harbor 스캔 상태 확인·실행 화면 캡처 편입 (2026-10-06)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 실행: 이하영(HBR Lead), cp1 `k8s-control01`의 Firefox로 Harbor UI 접속. 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 AC-05 PASS 선언이 아니다.** Harbor Scanner 관측이며 CI fresh Scan의 대체가 아니고, Manifest·Pod·rollback(05B)은 이 폴더 범위 밖이다.

## 근거
| 항목 | 값 |
|---|---|
| 요청·방향 | [#13 AC-05A 회신 5995691934](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5995691934) 1절: Harbor Scanner 보고서를 조회·보존, 보고서가 없으면 `NOT VERIFIED / REPORT_NOT_AVAILABLE`, 새 scan 실행은 Lead 실행 판단 절차 |
| Lead 판단·시작 기록 | [fds/test 1회, 6013257214](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6013257214) · [새 앱 2개 1회씩, 6013630514](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6013630514) |
| 새 앱 CI 인계 | infra-cicd `f8f802c149f1868b2f14e3050c8cfb529d2dff7a` `handoff/push-review-37322456303/` (`PUSH_HANDOFF.json`: manifest digest, `harbor_scanner: NOT_VERIFIED`) |

## 로그인 계정 (정정)
화면 오른쪽 위에 **`admin`으로 로그인**한 상태가 보인다. 6013257214에 적은 "이하영 개인 계정"은 틀렸으며 6013630514에서 정정했다.

## 무엇을 했나
1. `fds/test`의 `sha256:7a3b263c…`: 화면에서 취약점 열이 "스캔되지 않음"인 것을 캡처 → `SCAN VULNERABILITY` 실행 → 열이 "취약점 없음"으로 바뀐 것을 캡처.
2. 새 앱 `fds/transaction-api`(`sha256:fa18dc36…`, tag `delivery-…`)와 `fds/fds-engine`(`sha256:d77b8095…`, tag `delivery-…`): 동일하게 "스캔되지 않음" 캡처 → 각각 스캔 실행 → "취약점 없음" 캡처.
3. 같은 저장소의 예전 아티팩트(`latest`, `v0.1.0` 등)는 스캔하지 않았고 후속 화면에서도 "스캔되지 않음" 그대로이다.

## 캡처 목록과 해시
| 파일 | 내용 | SHA-256 |
|---|---|---|
| `screenshots/harbor-ui-fds-test-artifacts-20261006.png` | `fds/test` 스캔 전: 취약점 "스캔되지 않음", SBOM No SBOM, 푸시 26.9.30 AM 11:16, 풀 26.10.5 PM 3:56 | `88b065543fda6696f30425d0c467c385d008f278cdf110b409f32661e6310301` |
| `screenshots/harbor-ui-fds-test-after-scan-20261006.png` | `fds/test` 스캔 후: "취약점 없음", 로그인 `admin` 표시 | `aa6402a110a8096a5bc969cb3955db21e4745775aa14b7383dff2dfe2cd28d46` |
| `screenshots/harbor-ui-fds-transaction-api-artifacts-20261006.png` | `transaction-api` 스캔 전: 5개 아티팩트 모두 "스캔되지 않음", `fa18dc36…` 푸시·풀 26.10.6 AM 12:19 | `6ba7b78ef9f4dcc278e2855e847cead6556e2ef53dc65d0a47e98f7ba9022635` |
| `screenshots/harbor-ui-fds-fds-engine-artifacts-20261006.png` | `fds-engine` 스캔 전: 6개 아티팩트 모두 "스캔되지 않음", `d77b8095…` 푸시·풀 26.10.6 AM 12:19 | `7730ef2ede5feb781df7f18656a45488db0a2c69994ec3b5a94b179fb3fbfce0` |
| `screenshots/harbor-ui-fds-transaction-api-after-scan-20261006.png` | `transaction-api` 스캔 후: `fa18dc36…`만 "취약점 없음", 나머지 4개 "스캔되지 않음" | `197d200c4210360a666e96e7d0325f9e59142894390dcdc64ab8df8da4163c5d` |
| `screenshots/harbor-ui-fds-fds-engine-after-scan-20261006.png` | `fds-engine` 스캔 후: `d77b8095…` "취약점 없음", 나머지 "스캔되지 않음". **화면 위에 `a previous scan process is Running` 경고 표시** | `330c52dc9437ec42054375064981071bf593da0290066de2961cbfe41a1147ce` |
| `screenshots/harbor-ui-fds-fds-engine-after-scan-nobanner-20261006.png` | 위와 같은 상태에서 경고가 사라진 화면 | `c4542cc821ee8c2042b61527ddac88d4b7f32e712132b814d705efc1ab579791` |

## 한계 (숨기지 않음)
1. **스캔 요청 횟수 미확인:** 계획은 아티팩트당 1회였다. 실행자는 정확한 횟수를 확인하지 못했고, `fds-engine` 화면에 `a previous scan process is Running` 경고가 표시되었다(Harbor가 이미 실행 중인 스캔이 있는 상태에서 새 요청을 받았을 때 나오는 문구로 보이나, 요청이 몇 번 들어갔는지는 확인하지 못했다). 시작 기록의 "각 1회"를 사실로 확정하지 않는다. 최종 결과 화면은 `취약점 없음`이다.
2. **스캐너 상세 미수집:** 스캔 완료 시각, 스캐너 이름·버전, DB 갱신 정보, 건수 상세, **digest 전체**는 상세 화면 캡처가 없어 확인하지 못했다. 목록 화면의 `취약점 없음` 표시와 digest 앞 8자리(`7a3b263c`, `fa18dc36`, `d77b8095`)만 확인한다. 새 앱의 앞 8자리는 CI 인계의 manifest digest와 같지만 전체 일치는 확인하지 않았다.
3. **캡처 시각:** 화면에 날짜·시각이 보이지 않는다. 정확한 스캔 시각은 알 수 없고, 시작 기록 게시(`fds/test` 18:21, 새 앱 18:45 KST)와 캡처 수신(같은 날 18:3x~18:5x) 사이의 일로만 위치를 추정한다.
4. **API 조회 시도(403):** 같은 날 18:12 cp1에서 `robot$worker`로 세 저장소의 아티팩트 API를 호출했으나 모두 HTTP 403(forbidden)이었다. 응답 파일(cp1 `~/harbor-scan-read-20261006T181114/`, 각 56바이트 에러 JSON 3개)은 **이 PR에 포함하지 못했다**(미수신).
5. **전사·화면 증거의 성격:** 모든 파일은 실행자 화면 캡처이며 서버 원본 로그가 아니다. Harbor의 스캔 보고서 원본(취약점 목록)은 보존하지 않았다.
6. 이 관측은 해당 시점의 Harbor 표시이며 CI fresh Scan의 대체나 새 앱 이미지의 배포·Pod digest 일치를 뜻하지 않는다.
