# AC05 두 실패 유형 — 실행 전 준비안

상태: **PROPOSED / NEW RUNTIME NOT AUTHORIZED BY THIS DOCUMENT**. 이 문서는 AC 변경·회차 GO·실행 명령이 아니다. 기존 1회 Unit-negative 승인은 이미 사용됐으며 이번 두 회차에 전용하지 않는다. 증적 편입 승인과 이 시험 코드·입력의 독립 검토, 실제 회차 승인은 별도다.

## 목적과 권장 순서

과거 스캐너 rc1 및 취약점 rc10은 원본으로 확인됐다. 남은 AC05의 “각 실패 후 배포 이미지 유지”를 입증하려면 **현재 검토된 실패 처리 경로를 통과하는 서로 다른 두 회차**와 회차별 전후 관측이 필요하다. 과거 워크플로 재실행이나 기존 PASS 결과의 문구 변경은 사용하지 않는다.

1. 최신 P1 코드 기준에서 전용 `main` / 수동 실행 진입점과 표준 실패 전파 경로의 연결을 구현·검증한다. fixture/Trivy binary hash·입력·새 출력 경로·제한 시간을 코드 PR에서 고정한다. 실패 분류가 서로 섞이거나 준비 실패를 기대 결과로 인정하지 않는 시험을 포함한다.
2. 두 회차 모두 `cicd-runner01` 정상 Runner 계정과 별도 rootless store/cache/output을 사용한다. 승인된 관리 조회 경로에서 앱 Deployment 2개와 해당 Pod의 UID·generation·spec image·실제 imageID·ready·restart count를 수집한다. Runner에 새 Kubernetes/Harbor credential을 공급하지 않는다.
3. 최신 HEAD·리뷰·입력·동시 실행·앱 상태를 확인하고, 아래 두 회차를 **순차** 실행한다. 각 1회 실행안과 시간·중단 기준은 도구와 입력이 준비된 후 구체화해 회차 승인을 받는다. 작업창 확보만으로 승인됐다고 처리하지 않는다.
4. 전후 관측과 원본 receipt/로그/rc/Run/Attempt/Job/SHA를 함께 봉인하고 증적 PR로 제출한다. 독립 검토 후 담당자가 AC05 수용 여부를 판정한다.

## 회차 A — 실제 취약점 차단

- 검토한 고정 이미지/OCI fixture를 실제 Trivy로 검사한다. 기존 source·image hash, scanner identity, input 형식과 fixture가 앱 전달 경로를 대표하는 범위를 코드 PR에 명시한다. 단순 파일시스템 도구 시험으로 앱 이미지 AC를 대체하지 않는다.
- 격리 경로에 새 DB를 수신하고 freshness·metadata·hash를 검사한다. 옛 회차 DB를 현재 fresh DB로 간주하지 않는다.
- 기존 HIGH/CRITICAL 차단 정책을 유지한다. 기대 결과는 실제 findings와 scanner rc10, 이미지 스캔 BLOCK 및 상위 실패 전파, Push/Deploy 미호출, 전후 배포 이미지 동일이다.
- 새 DB에서 예상 취약점이 사라지거나 스캔 오류가 발생하면 `NOT_CONFIRMED`다. 임의 findings 생성, rc 강제 변경, ignore/unfixed 우회로 기대 결과를 만들지 않는다.

## 회차 B — 실제 스캐너 실행 오류

- 다른 격리 출력/캐시로 실제 Trivy의 오류를 발생시킨다. 후보는 **전용 빈 DB + `--skip-db-update`**이며, 운영 DB를 삭제하거나 네트워크/서비스를 끊지 않는다.
- 현재 `scan_pair`는 먼저 DB를 준비한다. 그래서 단순 사전검증 거절이나 잘못된 archive의 입력 검사 실패를 `SCANNER_EXECUTION_ERROR`로 제출하면 안 된다. 전용 시험 진입점이 실제 Trivy를 호출하고 현재 오류 전파 경로를 타는 설계를 코드 PR에서 확인한다. 정상 DB 준비를 생략한 시험 경계도 명시한다.
- 정상/오류 로그는 제한된 비민감 인자로만 남기며, 실제 scanner nonzero와 원인을 보존한다. mock, 강제 `return 1`, 과거 receipt 복사는 실제 오류 증거가 아니다.
- 기대 결과는 scanner 오류의 명시적 실패, GitHub 실패, Push/Deploy 미호출, 전후 배포 이미지 동일이다. 상위 timeout·인증 오류·준비 실패는 별도 `NOT_CONFIRMED`로 남긴다.

## 공통 중단·회수·완료 조건

- 실행 직전과 직후 각 회차의 관측을 따로 수집한다. 사전 관측 실패, 이미지 drift, 다른 관련 작업 진입, 승인 HEAD/입력 불일치가 있으면 착수하지 않는다. 한 회차 실패 원인 미확인 상태에서 다음 회차를 시작하지 않는다.
- 시험 코드에는 Push/Deploy 호출 경로와 해당 credential 공급이 없어야 한다. downstream Job이 없는 구조라면 `skipped`라고 표시하지 않고 실제 미호출 경계를 설명한다. 이 구조가 AC05 목적을 충족하는지는 담당자가 코드 PR에서 검토한다.
- timeout이나 예상 외 변경이 발생하면 해당 회차를 중단하고 원본·프로세스·자원 상태를 보존한다. 공유 store/DB/운영 자원을 광범위 삭제하지 않는다. 자기 실행이 만든 자원만 경로·UID·PID/CID를 대조해 회수한다. 앱 복구가 필요하다면 승인된 복구 절차와 담당자에게 인계하며 자동 변경하지 않는다.
- 성공 판정은 도구의 기대 실패 판정과 별도로 **두 유형 모두 실제 실패 전파 + 배포 이미지 유지 증적**이 있어야 한다. 실패 회차를 GitHub SUCCESS로 바꾸지 않는다. 이 문서만으로 Runtime, AC05, P1-CICD-01, Phase 1을 완료 처리하지 않는다.
