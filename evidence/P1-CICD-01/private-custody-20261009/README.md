> **현재 인수 결정(2026-10-09):** [담당자·보존기간 결정](CUSTODY_ASSIGNMENT_20261009.md)을 우선 적용한다. 이하영(K8S), 이재환(APP 공급), 이권욱(CICD 실행·CI 원본)을 지정했고, 보존은 자원 회수기간 종료(현재 계획10/26 KST)까지로 통일했다. 실제 인수 확인은 대기다. 아래 수집 시점의 “인수자·보존기간 미정”은 당시 기록이다.

# Phase 1 비공개 원본 보관 사본 — 2026-10-09

## 판정

기존 원본 묶음 5건을 승인된 공유 경로에 복사하고 수신 크기·SHA256을 확인했다. 추가로 앱 Run37890963668/Attempt1의 기존 manifest에 등재된 **69개 원본(1,632,589,467 bytes)**을 서버에서 읽어 새 전송 archive로 묶고, PC에서 각 payload 해시를 재검증한 뒤 같은 공유 경로에 보관했다. 신규 APP Test/Build/Scan/Push/Deploy 및 Harbor 작업은 수행하지 않았다.

**수신·무결성 확인 완료 / 독립 리뷰 대기 / 인수자·보존 종료 기준 미정**이다. 복사·해시 일치는 시험 재성공이나 전체 AC 인수를 뜻하지 않는다. 관련 이슈는 OPEN 유지한다.

## 추적 자료

| 자료 | 역할 |
|---|---|
| custody-audit.json | 18:13 PC의 기존 5건 점검. 당시 raw 미전송 표기는 아래 후속 수신으로 보완됨 |
| share-transfer-receipt.json | 18:17 기존 5건 공유 복사 결과·파일별 크기/해시·보관 경로 |
| app-raw-export.stdout / EXPORT_RECEIPT.json | 정상 Runner 계정의 원본 69개 해시 검증 결과·목록, 새 archive 생성 기록 |
| raw-expected.json | 증적 PR190의 기존 manifest payloads. 이번 편입 준비에서 병합 정본과 구조·값 일치를 재확인 |
| app-raw-transfer-receipt.json | 18:25 서버→PC→공유 archive 크기/해시 및 69개 payload 재검증 결과 |
| SCOPE.json / *.py | 실행 계정·경로·검증 한계 및 수행에 사용한 로컬 수집/전달 코드 사본 |

전송 archive: `app-raw-37890963668.tar.gz`, **326,294,507 bytes**, SHA256 `3842a78ab7683c8d2faf7adc82e9173cbe2a305652f4bc7aedd458f16abe150d`.
서버·PC·공유 위치는 receipt에 있다. 큰 archive와 실제 raw/OCI/DB/report 바이트는 Git에 넣지 않는다. 검토자는 승인된 공유 경로에서 확인한다. 공유 폴더의 최초 SHA256SUMS.txt·RECEIPT.json은 기존 5건 전용이며, 추가 raw는 APP_RAW_RECEIPT.json·별도 sidecar로 구분한다.

## 권한·보존 및 한계

- 보관 폴더: 사용자 지정 팀 결과물 경로 아래 `P1-GWONUK-originals-20261009T181731`.
- 공유 권한으로 승인 인원만 접근한다는 **사용자 확인**을 근거로 전달했다. 파일시스템 ACL에서 Everyone/Users FullControl이 관측됐으며 SMB ACL 자체를 독립 확인한 것은 아니다. 접근 권한을 변경하지 않았다.
- 원본 5건은 재압축하지 않았다. raw 전송 archive는 기존 원본 바이트 69개와 새 EXPORT_RECEIPT.json을 포함하는 **신규 묶음**이다. 내부 Podman image store 및 manifest 미등재 파일은 제외했다.
- 서버 원본·로컬 원본을 보존했다. 인수자 및 보존 종료 기준 미정, 자동 삭제 없음. 대체 백업 성공·장기 인수 완료로 표시하지 않는다.
- 수집 코드의 실행 전 독립 리뷰는 **NOT_PERFORMED**. 코드 사본은 실행 후 보존했으며 실행 전 Git SHA/서버 스크립트 파일 해시 기록은 없다. 원본 manifest와 수신 바이트 대조 결과를 리뷰된 운영 코드 실행으로 확대하지 않는다.
- K8S 이전 17파일 보관은 서버 fresh backup/restore 시험 완료가 아니며, CI76 증적 보관은 worker02 Runtime GO가 아니다.

관련: [CICD#11](https://github.com/321Team/infra-cicd/issues/11), [Ansible#61](https://github.com/321Team/infra-ansible/issues/61), [증적#182](https://github.com/321Team/fds-project-evidence/pull/182), [#183](https://github.com/321Team/fds-project-evidence/pull/183), [#189](https://github.com/321Team/fds-project-evidence/pull/189), [#190](https://github.com/321Team/fds-project-evidence/pull/190), [#192](https://github.com/321Team/fds-project-evidence/pull/192).
