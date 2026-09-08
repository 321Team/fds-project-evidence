# FUP-01 Rollback 상태 원본 수신 검토 v1.0

- 수신 ID: FUP01-ANSIBLE01-20260908T115139Z
- 수집 보고서 시각: 2026-09-08 20:51:39 KST
- 수신 검토 시각: 2026-09-08 20:55:33 KST
- 검토 범위: 사용자가 제출한 원본 패키지와 sidecar. 운영 서버 직접 접속·변경·rollback 재시험 없음.
- 결과: **Rollback 상태자료 5/5 수신 검증 완료 / Refinalization 원본 미수신**

## 1. 무결성과 편입 범위

| 검사 | 결과 |
|---|---|
| 원본 패키지 | FDS_FUP01_02_Remediation_Receipt_v1.0.tar.gz / 1,326 bytes |
| 외부 SHA-256 | f96da70280d8b049c4b7cb23162bc2ecb66b15ae3a362b7954a73351ac42713b / sidecar 일치 |
| 내부 매니페스트 | 수집 보고서 1개 + 상태파일 5개 = 6/6 일치 |
| 매니페스트 자체 | 자기 해시 제외. 원본 바이트는 보존하고 루트 REGISTRY_SHA256SUMS로 별도 추적 |
| 경로·유형 | 7개 멤버 모두 일반 파일, 경로 이탈·중복·심볼릭/하드 링크 없음 |
| 비밀정보 | 7개 텍스트의 알려진 Private Key·Token·AWS Key·Bearer·Password 패턴 없음 |
| FUP-02 파일 | 이번 패키지에 없음. 직전 보완·독립 검토 대기 상태 유지 |

JSON 5개와 수집 메타데이터 2개는 바이트 그대로 새 수신 경로에 복사했다. 원본 JSON의 마지막 줄바꿈도 추가하지 않았다. 외부 sidecar는 그대로 보존하며 원본 tar.gz는 재압축하거나 Git/Release에 중복 업로드하지 않는다.

- [원본 패키지 보관 참조](SOURCE_PACKAGE.json)
- [원본 멤버 → Git 경로·SHA-256](SOURCE_FILE_MAP.json)
- [기계 판독 검증 결과](RECEIPT_VERIFICATION.json)
- [수집기 원본 보고서](COLLECTION_REPORT.json)
- [수신된 원본 내부 매니페스트](COLLECTION_SHA256SUMS)

내부 매니페스트는 원래 tar.gz의 review-input 디렉터리를 기준으로 한다. 이 수신 디렉터리에서 그대로 실행하는 명령이 아니다. 저장소 배치 경로 검증은 SOURCE_FILE_MAP.json 및 저장소 루트 REGISTRY_SHA256SUMS를 사용한다.

## 2. 변경 노드별 보존 상태

| 노드 | JSON 내부 보존 시각(KST, 2026-09-04) | 바이트 | CR·호스트 식별자 / SHA-256 대조 |
|---|---|---:|---|
| k8s-control02 | 17:15:31 | 279 | MATCH |
| k8s-control03 | 17:15:42 | 279 | MATCH |
| k8s-worker01 | 17:26:56 | 277 | MATCH |
| k8s-worker02 | 17:27:08 | 277 | MATCH |
| k8s-worker03 | 17:27:18 | 277 | MATCH |

5개 파일 모두 change_id=CR-P1-ANS-01-01, 해당 inventory_hostname, connection=fds-<호스트>, interface=ens160으로 식별된다.

보존 내용은 ipv4_dns=8.8.8.8, 빈 search, ipv4_ignore_auto_dns=yes다. 이는 기존 apply 로그에 기록된 **변경 전 resolver 상태**와 부합한다. 현재 DNS가 8.8.8.8이라는 의미도, 실제 rollback이 수행됐다는 의미도 아니다. 현재 Runtime 상태는 이번 수신의 검증 범위가 아니다.

원본 경로: 각 노드의 /var/lib/fds-change/CR-P1-ANS-01-01/original-resolver.json

## 3. 보관·권한 증명의 한계

수집 보고서는 5대 모두 uid=0, gid=0, mode=0600 및 source_unchanged=true를 기록한다. 이번 검토에서는 이 메타데이터와 파일 해시·크기를 대조했다.

다만 수집기 v1.0은 원격 stat-before/stat-after 원시 결과를 패키지에 포함하지 않는다. 따라서 권한·읽기 전후 불변성은 **수집기 보고 기반**으로 표시하며, 독립적으로 서버에서 재측정한 결과라고 주장하지 않는다. 원본 tar 멤버의 uid/gid=1000/1000은 제출용 패키지 소유자이고 원격 원본의 root:root 권한과 구분한다. Git의 파일 모드도 서버 권한 복구 증거로 사용하지 않는다.

captured_at은 JSON 내부 기록이며 별도의 서명된 시각 증명은 아니다. 수집기 실행본 자체도 첨부되지 않아 보고서의 버전 표시만으로 실행 코드까지 독립 인증하지 않는다. 이 한계 때문에 이미 수령한 파일을 수정하거나 resolver rollback을 재실행하지 않는다.

## 4. FUP-01 잔여 항목

| 항목 | 판정 | 다음 조치 |
|---|---|---|
| RCV-CR-02 Rollback 상태자료 5대 | 원본 수신·해시 검증 완료 | 독립 편입 검토에서 보관 메타데이터의 보고 기반 범위 확인 |
| RCV-CR-01 Refinalization 원본 | 미수신 | 당시 파일 또는 고정된 원본 참조 확인 |
| FUP-01 전체 | ROLLBACK_RECEIPT_VERIFIED_REFINALIZATION_PENDING | Refinalization 수령 전 완료 처리 금지 |

기대 Refinalization SHA-256:

db7da7eae13c1b07e6b073003a23229e76f3a86f6903a66ac9a2cf522f84395d

수집 보고서는 MISSING / matches=0으로 기록했고, 수신한 7개 멤버에서도 일치하는 바이트가 없었다. 이것은 수집 대상 범위에서 미발견·이번 패키지에서 미수신이라는 뜻이며, 서버 전체 또는 다른 보관소에 파일이 없다고 단정하지 않는다.

다음 제출은 Refinalization 원본 또는 당시 보관 경로·고정 참조로 한정한다. 이미 검증된 5개 노드 파일을 다시 수집할 필요는 없다. finalize 재실행이나 문서 재작성으로 신규 바이트를 만들고 과거 원본이라고 표시하지 않는다. 원본이 실제로 유실됐다면 유실 사실과 당시 해시 기록을 보존한 별도 예외 판단이 필요하며 본 검토가 그 예외를 승인한 것은 아니다.

## 5. 승인과 변경 통제

- 기존 CR의 Done·종결일 2026-09-07과 원 승인·병합 이력 유지
- 이번 작업은 증적 수신·추적 갱신이며 구현 완료 재판정이나 새 기준선 발행이 아님
- 기존 FUP-02 보완 상태 유지. 이번 파일로 과거 서버 배포 검증을 새로 주장하지 않음
- 증적 PR #1은 Draft 유지. 현재 추가 Commit의 독립 편입 검토 및 사용자 최종 병합 승인 별도
- 운영 서버 명령, DNS 설정 변경, rollback 실행, Bootstrap 해제, Tag·Release 발행 없음

