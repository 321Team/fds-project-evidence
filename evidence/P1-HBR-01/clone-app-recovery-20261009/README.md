# P1-HBR-01 격리 클론 앱 수동 복구 증적 — 2026-10-09

## 판정과 범위

수신 실행 기록 기준 `MANUAL_RECOVERY_HEALTHY_REVIEW_REQUIRED`를 확인했다. 기존에 중지됐던 앱 9개를 정확한 컨테이너 ID로 각각 1회 시작했고, 종료 시점에 logger 포함 10개가 running/healthy였다. 이는 **일회 수동 복구**이며 원 A3 `STOP_RECOVERY_REQUIRED` 판정을 소급 변경하지 않는다. 영구 자동기동, 실제 syslog 저장, AC 인수·티켓 종결은 미검증/미판정이다. 독립 증적 편입 리뷰는 대기다.

대상은 `harbor01-isolated-firstboot-20261008`, UUID `564d9e38-f024-efe2-b68f-137a5047788a`인 격리 클론이다. 운영 VM은 대상이 아니다. 기존 티켓 상태와 완료일을 변경하지 않는다.

## 출처와 시간 (KST)

- 실행 소스: [infra-harbor-trivy PR #26](https://github.com/321Team/infra-harbor-trivy/pull/26), HEAD `07a1f8d4a087657cba9e7a0ba49b7c3a489c02aa`; 이하영(hayeounglee) 코드 승인 14:38:51, 병합 14:45:30. 실행 GO/AC 승인과 구분한다.
- 실행: 사용자 root 권한 콘솔, 14:59:04.279837~15:03:44.111778, 279.832초. 콘솔 종료 코드 `RECOVERY_RC=0`.
- 게스트 원본: `/root/hbr-app-recovery-ik0dm4a1`; 결과 수집 15:14:22.411262, 호스트 검수 15:16:30.
- 전달 번들: `/root/hbr-app-recovery-bundle-20261009-145042`. 준비 단계 원문 archive는 게스트에 보존했으며 호스트 원문 전체 수신으로 주장하지 않는다.
- 사용자 승인 작업창 종료 17:00. 실제 복구는 15:03:44 종료했으며, 실행기 내부 900초 제한을 임의 변경하지 않았다.
- 수신 후 호스트 공유 제거 및 HGFS 비활성화 15:19:28; VMX의 share count=0, HGFS disabled, NIC present=FALSE와 실제 DEACTIVATED 로그를 기록했다. 비활성 슬롯 키는 VMX에 남아 있다.

실행 명령(과거 실행 기록이며 재실행 지시가 아님):

```bash
sudo python3 -I /root/hbr-app-recovery-bundle-20261009-145042/clone-app-recovery.py \
  --bundle /root/hbr-app-recovery-bundle-20261009-145042 \
  --confirm-host-gate a3-evidence-preserved-no-nic-no-hgfs
```

## 수신 검증

| 항목 | 확인 결과 |
|---|---|
| 수신 manifest | 247개 파일 전부 해시 일치; manifest 자체 별도 보존 |
| 명령 기록 | 242개, 모두 rc=0; start 9개, 각 1회 |
| 시작 순서 | postgresql → redis → registry → registryctl → core → portal → jobservice → trivy-adapter → proxy |
| 상태 | 종료 시 10/10 running/healthy; 메타데이터 상태 표본 156개 비교 |
| Docker | unit 표본 12개에서 원 A3와 동일 InvocationID, active/running, guard Requires/After 유지 |
| AC04 | 12개 표본 형태 동일(handle·counter 수치 제외); 실제 패킷 허용/차단 시험 아님 |
| 불변성 | 복구 전후 프로필 동일, ID·이미지·마운트·restart·logging 메타데이터 동일; 앱 데이터 쓰기 불변성을 뜻하지 않음 |
| 원 A3 | result·claim 고정 해시 일치, 복구 전 상태가 원 A3 종료 상태와 동일 |

원본 `received/SHA256SUMS`와 `collector-v2/EXPORT_DONE`을 보존했다. 본 수집회차 `SHA256SUMS`는 수신본과 새 검수 문서를 구분 없이 바이트 무결성 목적으로 덮으며, 서버 원본 생성 시각·시험 PASS·독립 승인 증명이 아니다.

## 수집 중단과 정정

첫 수집기는 실제 실행 과정에서 생성된 `__pycache__`를 예상하지 못해 `UNEXPECTED_WORK_ENTRY`로 중단했다. 실제 수신 메타데이터에서도 이 디렉터리를 확인했다. v2는 symlink가 아닌 해당 파생 디렉터리만 제외하고 원본 해시와 나머지 항목 검사를 유지한다. 알 수 없는 디렉터리와 symlink는 계속 거부한다. v1·v2 소스와 콘솔을 함께 보존했다. 복구 실행기 변경이나 복구 재실행은 없었다. v2는 기존 파일만 읽었고 추가 Docker 조회·시작·재시작·restore를 하지 않았다.

## 누락과 판정 한계

- 게스트 private 파일 486개는 목록·해시 메타데이터로 보고됐다. raw stderr·app error 원문과 private archive는 게스트에 남아 있고 전부 수신하지 않았다. 수신한 파일만 실제 바이트 검증했다.
- `console/`은 사용자 제출 스크린샷이며 게스트 원문 파일과 구분한다. umount 명령이 오류 없이 반환한 것은 콘솔 확인이며 별도 게스트 mount 재조회는 하지 않았다.
- `records/`는 호스트 검수·전달·공유 종료 기록이다. 보존한 검수 스크립트의 경로는 당시 호스트 기준이다.
- container healthy 및 logger TCP accept는 syslog 실제 저장이나 업무 API 기능 인수를 뜻하지 않는다.
- 자동기동·Docker 재시작·VM 재부팅 시험은 이번 복구에서 수행하지 않았다. 현재 VM은 복구 완료 상태로 유지한다.
- 소스 PR의 STATIC/MOCK/CI와 독립 코드 승인은 소스 기록으로 연결된다. 이번 RUNTIME 증적의 독립 REVIEW/MERGE 및 PUBLICATION은 별도 단계다.

## 다음 작업

HBR Lead 이하영에게 원본·해시·실행 범위·판정 대응·누락·민감정보를 포함한 독립 편입 리뷰를 요청한다. 자동기동 영구 대책은 별도 설계·검토·승인·시험 대상으로 남긴다. 이번 증적 편입을 이유로 원 A3 또는 관련 AC를 PASS/Done으로 변경하지 않는다.
