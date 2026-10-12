# K8S17 파일 정합화 — 2026-10-13

이권욱 / CODEX_ASSISTED. 사용자 “다음순서 착수” 및 “5대 모두 호출 배제·콘솔 인수 가능” 확인에 따른 기존 승인 파일 배치 정합화다. source b4303f2df512a8791d2421203cf159567d076b2a, 교체17/보존28, control02 제외. 이전 APP 회차는00:57:20 종료, Harbor 최신 상태는 idle/새 변경0이다. 새 Lead 구현 승인을 요구하지 않는다.

순서: 호스트별 fresh9파일·부모/link/ACL/context/프로세스 대조 → 새0700 `/root/p1-k8s17-20261013-r1`에 해당 파일 원본 backup 및 metadata·공급 candidate → backup에서 별도 임시 복원 → hash/uid/gid/mode/ACL/context 대조 → control01 audit-window.py1개 적용·검수 → control03/worker01/worker02/worker03 각4개를 한 대씩 적용·검수. 원본을 읽는 각 단계에서 변경 여부를 재확인한다.

같은 filesystem의 새 임시 후보 파일을 검증 후 `os.replace`로 파일별 치환한다. 4개 집합 전체가 원자적이라고 하지 않는다. 사용자 확인한 호출 배제는 전체 교체·검증·필요 복귀 동안 유지하며 프로세스 순간 조회는 보조 수단이다. 후보 metadata는 root0:0/0750/기본 ACL/system_u:object_r:usr_t:s0. worker01 보존5개 등 나머지28개는 hash·복원 가능한 metadata와 mtime 불변을 확인한다.

이번 범위는 bytes 및 metadata 정합화다. 운영 도구 실행/import·pycache, 정책/기존 생성 YAML·서비스·계정·credential·DNS·앱·노드 상태 변경을 포함하지 않는다. Python 구문은 compile만 한다. 일반 파일이 아니거나 드리프트/부모 쓰기권한/예상 외 xattr/진행 중 호출/백업·복원 검증 실패면 교체0. 적용 중 실패면 해당 호스트의 실제 교체 파일만 확인된 백업으로 복귀하고 더 진행하지 않는다. 복귀 결과는 `RESTORED_WITH_KNOWN_TOOL_DEFECT`이며 사용 보류다.

SSH 결과 불명확 시 자동 apply 재실행을 하지 않는다. 서버 `PREPARED.json`·`APPLY_RESULT.json` 및 현재9파일을 읽어 상태를 먼저 구분한다. 이번 호출만의 exact 임시 파일은 소유·hash 검증 후 정리할 수 있으나 원본 backup·복원 trial·결과는 보존한다. 실패 복귀가 불가능하면 콘솔 인수, 더 넓은 운영 변경으로 우회하지 않는다.

호스트마다 fresh 준비 결과 JSON SHA를 다음 apply 요청에 결속한다. 준비와 적용을 별도 호출하며 control01 성공을 확인하기 전 나머지 적용은 하지 않는다. 요청 한 번의 작업 한도70초·SSH 수신100초이며, 적용 종료 결과를 확인하지 못하면 다음 호스트로 가지 않는다. 이 시간 한도는 강제 종료나 자동 복원 허용을 추가하지 않는다.

검증 완료 후: 목표17해시·metadata, 보존28해시·metadata, 임시 파일 미잔존, host/boot와 서버 백업·복원·변경 영수증 연결. 도구 사용 재개는 정합화된 파일집합 범위만 인계하며 기존 도구/정책 Runtime·AC 인수와 구분한다.
