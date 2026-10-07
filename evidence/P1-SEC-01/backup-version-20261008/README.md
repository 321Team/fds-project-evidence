# AC-05 backup 프로그램 버전 원인 확인 — 2026-10-08 KST

요청: baseline #19 [수집안 요청](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6040429949), [GWONUK 기술 판단](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6040617016). 사용자가 직접 코드 개선 및 가능한 현장 수집을 요청했다.

## 실제 수행 범위

GWONUK/CODEX_ASSISTED가 기존 PC → fds-ansible01(server01_ansible) → control01(svc_ansible, 기존 sudo) 경로로 읽기 전용 수집했다. 기존 SSH 키/known_hosts 검증 유지. 새 root 전용 수집 코드/증적 디렉터리만 생성했다. 운영 설정·정책·서비스·etcd 데이터는 변경하지 않았고 snapshot 내용·Secret·개인키를 읽지 않았다. `etcd --version` 등 6개 버전 명령, 바이너리 SHA/ELF, Pod UID/imageID, PID/starttime를 기록했다.

## 두 회차와 보존

1. `ONi7knWx`: capture rc2. 제공 collector-v1의 Path.resolve(strict=True)가 컨테이너 `/proc/PID/exe` 링크를 호스트 `/usr/local/bin/etcd` 경로로 해석해 실패했다. 이는 운영 etcd 실패가 아니라 수집기 경로 처리 결함이다. 실패 stdout/stderr/rc·manifest 20개를 보존했다.
2. `VRbii4QQ`: 해당 부분만 os.readlink로 수정한 collector-v2로 새 폴더에 수집. capture rc0, 개별 조회 rc 모두 0, 내부 manifest 92개 일치. 이전 실패를 덮어쓰지 않았다. 세 프로그램 모두 host/container에서 **3.6.8**. PID 2713/starttime 1000, Pod UID/imageID 전후 동일. image `registry.k8s.io/etcd:3.6.8-0`, imageID `sha256:397189418d1a00e500c0605ad18d1baf3b541a1004d768448c367e48071622e5`. etcd 파일 SHA=운영 exe SHA.

정확한 시작/종료 UTC와 서버 경로는 RECEIPT.json 및 tar 내부 원문에 있다(KST=UTC+9). tar는 서버 봉인 폴더를 읽은 전송 스트림을 로컬에 그대로 저장했다. tar sidecar는 **수신 바이트의 로컬 SHA**이며 서버에 저장된 tar SHA라고 주장하지 않는다. 서버 원문 파일은 내부 SHA256SUMS와 전부 대조했다.

| 프로그램 | 원문 SHA256 |
|---|---|
| etcd / 운영 exe | b8956dc9f7479b1f15c46d03edae5dd9db508932840f91a9818e67717fcb1850 |
| etcdutl | d22485cae0e4b9cc946442a2b80a86aed898b917c11d0e25586aa0f946f80d87 |
| etcdctl | 57d03ef113681f2474cc2c9ba14d9b3553275997223380e0ab32cc4db877cf02 |

## 코드와 판정 경계

수정 후보 infra-kubernetes `1b5470e8c9902e7561dbe56fa9129bcf45ba7bb3`는 프로그램 3.6.8/위 해시와 evidence#99 snapshot **storageVersion 3.6.0**을 분리한다. collector-v2는 이 commit의 backup-version-capture.sh와 동일한 바이트다. 실행 시점에는 미커밋 후보였으며 **사전 독립 코드 승인된 실행본으로 표시하지 않는다**. 관측 수집과 격리 복원 시험을 구분한다.

LIVE_READONLY_CAPTURE=COMPLETE / FAILED_CAPTURE=PRESERVED / BACKUP_PRECHECK=NOT_RUN / RESTORE_RUNTIME=NOT_RUN / INDEPENDENT_REVIEW=PENDING / AC·Close 변경 없음.
