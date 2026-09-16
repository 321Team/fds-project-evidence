# cicd-runner01 Actions Runner prepare v1 — 실패 수신 및 v1.1 수정

이 디렉터리는 사용자가 제출한 원본과 분석·로컬 수정 검증을 보존한다. 실제 실패 증적과 수정본 검증을 혼동하지 않는다.

| 구분 | 결과 |
|---|---|
| 제출 원본 SHA256 | `fe7e908018bc38f192154a429673150ba5e4c07cbdf73b322f651c9c3820bdaa` / 3,779bytes |
| 기록 시간 | 2026-09-16 14:26:51 UTC / 23:26:51 KST |
| 무결성 | 외부 checksum, nested archive checksum, 두 SHA256SUMS 및 전체 일반 파일 coverage 일치 |
| 계정 검사 | UID1001/GID1002, home0700, password locked, 자격증명 경로 부재 PASS |
| sudo 검사 | 정확한 비sudo denial 확인(rc0) |
| 실패 | `podman info --format=json` rc1 |
| 단계 | Runner/proxy NOT_CREATED, 등록 시도 false, 이미지 build/Actions 미착수 |
| 정리 | workspace REMOVED |
| 직접 원인 | 원본 stderr가 v1 수집 경로에서 누락·삭제되어 미확정 |
| 수정본 검증 | v1.1 LOCAL UNIT/MOCK 37 PASS, Python AST8/bash -n PASS |
| 수정본 실서버 prepare | NOT_RUN — 재실행 증적 필요 |

v1.1은 로그인 홈에서 이어받던 작업 디렉터리를 전용 계정 홈/run directory로 명시하고, 기존 r3의 local/systemd Podman 옵션을 사용한다. 이는 코드에서 확인한 차이를 바로잡은 것이며 이번 rc1의 직접 원인이 CWD 또는 설정이었다고 확정한 것은 아니다. stdout/stderr를 분리하고 고정된 prepare 로그를 각64KiB까지 보존한다. 토큰 사용 단계 원문은 제외한다.

- 코드 [infra-ansible PR19](https://github.com/321Team/infra-ansible/pull/19), 수정 HEAD `5fd76293da7bbcdb238cc8edeb8206e47283e395`
- [고정 HEAD 실행 안내](https://github.com/321Team/infra-ansible/blob/5fd76293da7bbcdb238cc8edeb8206e47283e395/tools/ansible-runner/README.md)
- v1.1 manifest SHA256 `ecff16d871d7b08cd9aa72e580e54830b61d438ec9dcbbf3847bbac2f690ff46`
- 배포 `FDS_Ansible_Actions_Runner_v1_1.zip` SHA256 `aefcc2cf5be904a3cdde0b769e5bed3650e593b3123aee71f0f0ec3234efc65a`

다음 실행은 cicd-runner01 기존 로그인에서 수정본 검증 후 `sudo bash run.sh prepare`다. 성공/실패 모두 기존 로그인 홈에 새 archive와 checksum을 생성한다. 실제 Podman 및 SELinux/UDS 통신, 등록/해제, 독립 활성화 리뷰, 정상/고의 결함 Actions, merge/운영 적용을 이번 로컬 검증으로 완료 처리하지 않는다. Issue5 AC는 열린 상태를 유지한다.
