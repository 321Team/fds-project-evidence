# K8S17 실제 교체·검수 회차 종료 — 2026-10-13T01:14:36.369273+09:00

**교체17/보존28/5대 실제 정합화 완료, 진행 중 파일 교체·임시 파일0.** 새0700 서버 backup→임시 restore의 bytes/uid/gid/mode/ACL/context 확인 후 control01 1개→나머지4대 각4개 순으로 적용했다. 별도 읽기45경로 목표17/비대상28 대조 통과. worker01 보존5개 user_home_t 유지. 서버 `/root/p1-k8s17-20261013-r1`의 backup/restore-trial/candidate/PREPARED.json/APPLY_RESULT.json은 삭제하지 않고 보존한다.

01:11:20~01:12:29 KST 실제 교체. 최종 API 읽기 Node6 Ready/앱6 Ready/앱별1/1/1/Deployment UID·spec SHA 유지. 운영 도구 호출·정책/서비스/앱/DNS/credential 변경0. 해당 파일집합 정합화 상태는 확인됐으나 도구 Runtime/정책 rollback/AC 인수·독립 승인으로 확대하지 않는다. 이번 교체를 위한 호출 보류는 해제 가능하며 이후 도구 실행은 각 기존 작업 범위대로 판단한다. control02 제외.

## 시작 당시 기록

# K8S17 회차 진행 중 — 2026-10-13 KST

사용자 “다음순서 착수”, 이어 “5대 모두 호출 배제·콘솔 인수 가능” 확인. 이권욱 실행/콘솔 인수, CODEX_ASSISTED. 기존 승인source·교체17/보존28 유지, control02 제외. APP 회차 종료 및 Harbor idle/새변경0을 확인하고 비중첩 경계를 통보했다.

현재 새 서버 백업·임시 복원·후보 metadata 검증부터 진행한다. 최초 실제 교체는 control01 audit-window.py1개이며 성공 확인 뒤 한 호스트씩 확대한다. 이 파일의 종료 기록 전 해당 도구 호출을 보류한다. 정책/서비스/앱/DNS/계정 변경은 이번 범위에 없다. 실제 단계별 source/명령/rc/서버 상태는 수신 receipt를 따른다.
