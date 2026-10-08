# P1-HBR-01 — Docker 자동기동 실패의 daemon 원본 보완

CODEX_ASSISTED · 2026-10-08 KST. 책임: [baseline#13](https://github.com/321Team/fds-project-baseline/issues/13), [infra-ansible#62](https://github.com/321Team/infra-ansible/issues/62). 수집 GWONUK, 기존 ansible01→harbor01/svc_ansible sudo 읽기 경로. 서비스/계정/설정·컨테이너 상태 변경, 재시험 및 복구 명령 실행 없음.

## 원본과 직접 원인

기존 [evidence145](https://github.com/321Team/fds-project-evidence/pull/145) HEAD `b3334d36f0f76b7a1f9803e2ad285a09ceabbf98`에는 자동기동 FAIL과 복구 B 성공, syslog 의존 가설이 있다. 이번에는 Docker daemon의 **2026-10-07 23:12:00~23:14:00 KST** 기존 journal을 고정 오류 패턴·200행 상한으로 읽었다. rc0, JSON9개이며 수집 명령/시각/원 stdout/stderr를 보존했다. 신규 실패를 발생시킨 것이 아니다.

**확인:** 23:12:33.927~33.936의 9개 컨테이너 모두 `failed to initialize logging driver: dial tcp [::1]:1514: connect: connection refused`로 시작에 실패했다. ID9개는 145의 시험 전 원본에 있는 harbor-db/redis/registry/registryctl/harbor-core/harbor-portal/harbor-jobservice/trivy-adapter/nginx와 정확히 일치한다. CORRELATION.json은 고정 참조 파일 hash와 개별 ID 대응을 담는다.

**현재 설정 관측(과거 시점과 구분):** 같은 ID의 9개 앱은 syslog `tcp://localhost:1514`; harbor-log는 json-file과 HostIp127.0.0.1/HostPort1514. 현재 ss는 IPv4 127.0.0.1:1514만 LISTEN, getent ahosts localhost는 ::1과127.0.0.1을 반환한다. 해당 선택 필드만 조회했으며 Docker Env/전체 LogConfig/Secret은 수집하지 않았다.

따라서 **직접 실패는 로그 드라이버의 IPv6 loopback 연결 거부로 확인**됐다. 다만 journal의 마지막 연결 주소만으로 당시 IPv4 재시도 유무·harbor-log 준비 시점·이름 해석의 단독 인과까지 확정할 수 없다. “IPv4 주소만 바꾸면 해결” 또는 “기동 순서만 바꾸면 해결”은 아직 입증되지 않았다. 현재 listener 관측은 과거 T0 listener 관측을 대신하지 않는다.

## 권장 수정안의 범위 — 미적용

HBR source owner가 **주소 일치와 로깅 준비 완료 후 앱 기동을 함께 보장하는 최소 변경**을 준비하는 방향을 권고한다. 127.0.0.1:1514 명시 후보는 현재 loopback publish와 일치하지만, 주소 변경만으로 Docker daemon 재시작 시 준비 순서 문제가 해소됐다고 보지 않는다. Compose 실행 순서만 바꾸고 daemon 자체의 자동 재시작 경로가 보장된다고 가정하지 않는다.

다음 구현 전 고정할 사항:
- 실제 관리 중인 Compose/Harbor 생성 원본 및 생성 절차, 각 logging endpoint와 컨테이너 재생성 필요 여부 확인.
- daemon 재시작/호스트 재부팅의 범위를 분리하고, logging 준비 실패 시 무기한 대기·자동 반복 기동 대신 제한시간 STOP과 운영 통보를 정의.
- 기존 image/digest/volume/port/guard를 유지하는 변경 diff와 복귀 source를 확보. 기존 컨테이너/데이터 삭제로 해결하지 않음.
- 새 승인 창에서만 재현·수정 후 검증: 10개 상태/443/TLS, 로그 수신, guard·allow/deny, 동일 데이터/설정 유지 및 실패 경로/수동 복구. 이번 관측을 재시험 GO로 사용하지 않음.

AC-04 방화벽 인수와 자동기동 가용성 위험을 분리할지에 대한 [6040273141](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6040273141)의 판단 요청은 남는다. 이 원인 보완으로 자동기동 FAIL·원 verifier FAIL을 PASS로 바꾸거나 위험을 수용하지 않는다. 수동 복구 B 원본은 기존145를 재사용한다.

## 무결성과 한계

원본 journal은 SSH stdout으로 수신한 바이트이며 수신 SHA256 manifest를 제공한다. 서버 측 별도 봉인 또는 독립 검토는 아직 없다. 필터 밖 전체 daemon/컨테이너 로그, 당시 완전한 listener 시계열은 수집하지 않았다. 145의 기존 파일/누락/전사 한계는 수정하지 않았다.

단계: EXISTING_JOURNAL_CAPTURE=COMPLETE / DIRECT_FAILURE_IDENTIFIED / FULL_ROOT_CAUSE=PARTIAL / RUNTIME_FIX=NOT_RUN / INDEPENDENT_REVIEW=PENDING.
