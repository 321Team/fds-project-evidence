# Harbor 복제본 A2 변경 전 STOP 원본

CODEX_ASSISTED. baseline #13의 기존 NIC 없는 Harbor 작업 사본에서 사용자 server08 콘솔 sudo로 실행한 결과다. 실행 시각은 2026-10-08 15:21:38 KST, 소스는 infra-harbor-trivy #15 승인 HEAD 3a5ee859cecc2997edb12c6399b1f4aea47227fb(실행 SHA256은 ANALYSIS.json)다.

## 판정

**EXECUTED_PRECHECK_STOP / CHANGE_NOT_ATTEMPTED**. `UNEXPECTED_NON_BIND_DATA`로 재생성 전에 중단. 읽기 명령 13개 rc0, 구성 비교는 로그 주소 9개만 변경 PASS, inspect 시점 컨테이너 10개 running/healthy. recreate-apps 명령 없음. Docker restart/VM reboot/restore 미실행. 현재 회차는 종료·봉인하며 같은 RUN을 재실행하지 않는다.

원인은 기존 실행기의 모든 mount가 bind라는 가정이다. 실제 portal/proxy 각3개, registryctl 1개, log 2개에서 local Docker volume 9개가 확인됐다. 볼륨 내용이나 생성 기원은 수집하지 않았으며 이름만으로 이미지가 생성했다고 단정하지 않는다. DB 데이터는 /data/database→/var/lib/postgresql/data bind로 관측됐다.

## 원본과 회수

- guest-receipt: apply-result.json, 선택 inspect·image ID stdout, guest SHA256SUMS와 회수 이력. 변경하지 않은 바이트를 보존했다. receipt private_files의 exported는 해당 시점 반출 여부다.
- 전체 Compose JSON/stderr는 게스트 /root/hbr-address-trial-20261008-1500에 남겼다. 비밀 설정은 반출하지 않는다. 회수기는 Docker/서비스 명령 없이 고정 원본 파일만 읽는 자체 점검 코드이며 독립 코드 리뷰로 표시하지 않는다.
- 호스트에서 모든 guest SHA와 EXPORT_DONE의 manifest SHA를 대조했다. HBR_RESULT remove/disable rc0, fresh VMX 공유0/NIC false를 확인했다.
- snapshot-completion: 15:17:11 KST 오류0 lazy IO 종료와 SnapshotVMXTakeSnapshotComplete 원본 로그. 최초 vmrun 종료 코드는 미확보지만 VMX 완료 로그로 생성 완료를 확인했다. 실제 revert 시험은 미실행이다. 사용자 관리자 화면이 미표시였던 시점의 캡처는 보조 증거이며 원인은 단정하지 않는다.
- stage-receipt: 이전 자동 도우미는 종료되어 기록이 없었고 STAGED 원본 확인 후 15:11:34에 명시적으로 공유를 정리했다. 자동 완료로 소급하지 않는다.

## 수정과 잔여

수정 코드 PR: https://github.com/321Team/infra-harbor-trivy/pull/16 . 실제 layout을 반영한 제한 volume 검증·동일성 보존과 missing-container restore 중단을 추가했다. 수정 소스는 이 회차에서 실행되지 않았다. 로컬 함수 재검증/모의시험과 서버 Runtime을 구분한다.

본 증적 편입은 독립 리뷰 대상이다. 자동기동·로그 수신·운영 적용·AC/Issue/Phase1 Close를 승인하지 않는다. 기존 A1 및 과거 시험 자료를 수정하지 않는다. SHA256은 무결성 증거이며 시험 성공이 아니다.
