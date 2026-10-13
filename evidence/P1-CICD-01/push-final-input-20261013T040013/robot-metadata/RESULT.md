# robot$push 권한·만료 현재 조회

기준: **2026-10-13 03:49:19 KST**, harbor01. 사용자 명령 조회 가능 여부 질의에 따라 기존 관리 경로로 실제 읽기 조회했다.

| 항목 | 실제 관측 |
|---|---|
| 사용자 지정 대상 | `robot$push` |
| 저장 계정 | ID `3`, name `push`, project_id `0`(system 유형) |
| 활성 | disabled=false, visible=true |
| 만료 | **2026-10-18 17:16:55 KST**, epoch1792311415, 관측 시 expired=false |
| 발급 기간 | 30일 |
| 연결 정책 전체 | `/project/2` = `fds`, resource `repository`, action `pull` 및 `push` 두 행 |
| 정책 효과 | 원본 effect 빈 문자열. v2.13.1 `Policy.GetEffect()`의 기본값 allow로 해석 |

따라서 현재 권한·enabled·만료의 미관측 상태는 해소됐다. 앞선 PR208 e4d934b 및 실행 범위 초안의 관련 미확인은 그 작성 시점 이력이며, 새 관측이 보완한다. 봉인된 이전 파일은 수정하지 않았다. 사용자/Harbor Lead에게 같은 값을 다시 회신받는 절차는 불필요하다.

## 방법과 근거

- 기존 `fds-ansible01 → svc_ansible@harbor01 → sudo` 경로 사용. 운영 hostname·product UUID·현재 DB 컨테이너 exact ID와 healthy 상태를 확인했다.
- 기존 DB OS UID999의 psql로 `registry`에 접속하여 단일 **REPEATABLE READ / READ ONLY** 트랜잭션에서 선택 필드만 SELECT했다. statement timeout5초·lock timeout1초·프로세스 timeout12초. 읽기 종료는 ROLLBACK으로 처리했다.
- robot의 secret/salt, 비밀번호, token 값은 SELECT하지 않았다. 새 credential 발급·GitHub Secret 읽기·변경·파일 배치·서비스 재시작은 없다.
- SQL과 수집기 원본, 실행 인수·시각·rc·출력 해시 및 비민감 관측 JSON은 [receipt.json](receipt.json) / [수집기](robot_metadata_read.py)에 보존했다. 기존 SSH 보조 경로는 `deliverables/p1-preapply-resume-20261012/run_harbor_read_probe.py`다.
- SSH/SQL rc0, stderr 빈 값. DB 컨테이너 ID·image·PID·started·restart_count·status/health는 전후 동일했다.
- SELECT/접속에 따른 감사·프로세스 흔적은 생길 수 있으며, 읽기 전용을 시스템 흔적0으로 표현하지 않는다.

공식 스키마: [Robot v2.13.1](https://github.com/goharbor/harbor/blob/v2.13.1/src/pkg/robot/model/model.go), [Robot 권한 연결](https://github.com/goharbor/harbor/blob/v2.13.1/src/controller/robot/controller.go), [RBAC 저장 모델](https://github.com/goharbor/harbor/blob/v2.13.1/src/pkg/rbac/model/model.go), [빈 effect의 allow 처리](https://github.com/goharbor/harbor/blob/v2.13.1/src/pkg/permission/types/types.go).
API로도 [GET /robots 및 /robots/{id}](https://github.com/goharbor/harbor/blob/v2.13.1/api/v2.0/swagger.yaml) 조회 가능하나 Robot 목록/읽기 권한은 Pull/Push 권한과 별개다. 이번에는 비밀번호를 새로 요청할 필요 없는 기존 관리 DB 읽기 경로를 사용했다.

## 남는 범위

- 이 조회는 저장된 계정 설정과 정책 확인이다. GitHub에 등록된 비밀값이 해당 계정의 현재 secret과 일치하는지, 실제 Skopeo 인증/전송이 성공하는지는 확인하지 않았다.
- 실제 Push 유효창·최종 입력/해시·독립 입력 검토·회차 후 Secret 처리 범위는 별도이며, 이번 읽기를 Push 승인으로 확대하지 않는다.
- 새 Push/fresh Scan/Deploy/AC 판정/Phase2 작업 없음. 이 결과만을 위한 새 코드 리뷰·별도 PR를 만들지 않는다.
