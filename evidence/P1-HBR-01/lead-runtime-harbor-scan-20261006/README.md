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

## 상세 화면 캡처 (추가)
아티팩트 상세 화면(브라우저 화면 축소 후 캡처)이다. 위쪽(digest 제목)이 잘린 캡처가 있어, 화면 안의 내용으로 대상을 식별한 항목은 표에 그 사실을 적었다.

| 파일 | 내용 | SHA-256 |
|---|---|---|
| `screenshots/harbor-ui-fds-fds-engine-detail-top-20261006.png` | `fds-engine` `sha256:d77b8095…` 상세 위쪽: **태그 전체 `delivery-716a8ef98f76492786e73a340db35883`**(CI 인계와 일치), 푸시·풀 26.10.6 AM 12:19, amd64, 생성 10/5/26 11:11 PM | `eb74257e2dd3d9d23eec63506434c7e2b79ad6f3b593d1e97647baf9db266081` |
| `screenshots/harbor-ui-fds-fds-engine-detail-zoomout-20261006.png` | 같은 화면 축소: `org.opencontainers.image.created 2026-10-05T14:11:13Z`, base.name `localhost/fds-apko-runtime:cicd-offline-33b9…` | `44b9dd01832263b86e05c545a72673432281293731cff39fc437aa162437abcf` |
| `screenshots/harbor-ui-fds-fds-engine-detail-history-20261006.png` | "추가사항" 중 "기록 생성"(빌드 이력) 탭이 열린 화면(취약점 탭 아님) | `393dd1bc0215934f75a70cc7d158f369ee657235ce543a373ceb44acd5a85ee2` |
| `screenshots/harbor-ui-fds-fds-engine-detail-vulns-20261006.png` | `fds-engine` **취약점 탭**: "인식 가능한 취약점이 감지되지 않았습니다.", 0 아이템, 표 아래 `Trivy@v0.62.1로 보고 됨`(작은 글씨로 읽음) | `0c2075ae47ff4b8e0657bcfe5f824a47530e5d0364efc93317011918cb50e74d` |
| `screenshots/harbor-ui-fds-transaction-api-detail-vulns-20261006.png` | **위쪽 잘림.** 화면 내용(앱 포트 8000/9091, 생성 `2026-10-05T14:10:57Z`, apko 베이스)으로 `transaction-api`로 식별. 취약점 탭: 같은 문구, 0 아이템, `Trivy@v0.62.1로 보고 됨` | `39715632fbcbc8a9e11125d8e2f5750150557f932bd355335485e63085551076` |
| `screenshots/harbor-ui-fds-test-detail-vulns-20261006.png` | **위쪽 잘림.** 화면 내용(알파인 3.20.10, 생성 4/17/26, base.name `scratch`)으로 `fds/test`로 식별. 취약점 탭: 같은 문구, 0 아이템, `Trivy@v0.62.1로 보고 됨` | `d7de80c9356e9459abd8956513457a48596ec7e67dd86e5625d4b8f247ee92e3` |

"스캐너 `Trivy v0.62.1`"은 표 하단의 작은 글씨를 읽은 값이며 세 화면에서 같게 읽혔다. 화면에 DB 갱신 정보는 보이지 않는다.

## digest 전체 확인 (추가)
Harbor 아티팩트 목록의 복사 아이콘으로 복사한 이미지 주소를 실행자가 텍스트로 제공했다(`observations/harbor-ui-copied-pull-commands-20261006.txt`, SHA-256 `6cc166708fb3a6bac730b52061b0e8d5bb34c2824301fb0626ceffbfbe22ba4e`). 원본 파일이 아니라 실행자 제공 텍스트이며 어느 줄의 아이콘을 눌렀는지는 실행자 보고이다. 값은 아래와 같이 다른 기록과 대조했다.

| 이미지 | 전체 digest | 대조 |
|---|---|---|
| `fds/test` | `sha256:7a3b263c938493c827d8295e64f23d9386ffcbea75516ea03a6b65196636bfc6` | 앞서 병합된 AC-03 시험 로그(`k8s-worker01-node.log` 등)의 승인 digest와 완전 일치 |
| `fds/transaction-api` | `sha256:fa18dc36db8de35fb29ae9f5ec7bea7b7a6a0d0cd293649a79ed0d4dbb093b50` | infra-cicd `f8f802c1…` `PUSH_HANDOFF.json`의 `transaction-api` manifest digest와 완전 일치 |
| `fds/fds-engine` | `sha256:d77b80954fec5c408fb0bb91995d5faf3155ef2b74c76bc4f7e95cf319249e5b` | 같은 인계 파일의 `fds-engine` manifest digest와 완전 일치 |

세 값 모두 `sha256:` 포함 71자이다.

## 한계 (숨기지 않음)
1. **스캔 요청 횟수는 실행자 보고이다:** 실행자(이하영)는 `SCAN VULNERABILITY`를 아티팩트당 **1회** 눌렀다고 보고했다(계획과 같음). 이 횟수를 뒷받침하는 화면·로그 증거는 없고 실행자 진술이다. `fds-engine` 화면에는 `a previous scan process is Running` 경고가 표시되었다(Harbor가 이미 실행 중인 스캔이 있는 상태에서 새 요청을 받았을 때 나오는 문구로 보이며, 이 경고가 요청이 2회 이상이었음을 뜻하는지는 확인하지 못했다). 최종 결과 화면은 `취약점 없음`이다.
2. **digest 전체 확인의 근거:** digest 전체는 위 "digest 전체 확인" 절의 실행자 제공 텍스트와 다른 기록(CI 인계·AC-03 로그)의 대조로 확인했다. 화면 캡처 자체에는 앞 8자리만 있고 `transaction-api`·`fds/test` 상세 캡처는 위쪽(digest·태그)이 잘려 있어, 캡처와 digest의 연결은 화면 내용(포트·베이스 이미지·생성 시각)과 실행자 보고에 근거한다. 같은 digest의 Harbor 표시와 스캔 결과가 같은 대상임을 독립적으로 입증한 것은 아니다.
3. **스캔 시각 미표시·스캐너 DB 미확인:** 스캔 완료 시각과 DB 갱신 정보는 화면에 표시되지 않았다. 캡처에도 날짜·시각이 보이지 않아 정확한 스캔 시각은 알 수 없고, 시작 기록 게시(`fds/test` 18:21, 새 앱 18:45 KST)와 캡처 수신(같은 날 18:3x~19:xx) 사이의 일로만 위치를 추정한다. 스캐너 이름·버전은 작은 글씨로 읽은 `Trivy@v0.62.1`이다.
4. **API 조회 시도(403):** 같은 날 18:12 cp1에서 `robot$worker`로 세 저장소의 아티팩트 API를 호출했으나 모두 HTTP 403(forbidden)이었다. 응답 파일(cp1 `~/harbor-scan-read-20261006T181114/`, 각 56바이트 에러 JSON 3개)은 **이 PR에 포함하지 못했다**(미수신).
5. **전사·화면 증거의 성격:** 모든 파일은 실행자 화면 캡처이며 서버 원본 로그가 아니다. Harbor의 스캔 보고서 원본(취약점 목록)은 보존하지 않았다.
6. 이 관측은 해당 시점의 Harbor 표시이며 CI fresh Scan의 대체나 새 앱 이미지의 배포·Pod digest 일치를 뜻하지 않는다.
