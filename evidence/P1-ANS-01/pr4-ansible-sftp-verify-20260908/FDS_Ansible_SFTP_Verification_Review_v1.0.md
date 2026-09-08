# Ansible SFTP 수정 후 실 서버 검증 수신 검토 v1.0

검토일: 2026-09-08 · 대상: [infra-ansible 운영 이슈 #10](https://github.com/321Team/infra-ansible/issues/10)

**판정: 수정된 SSH 인자를 사용하는 Ansible SFTP 전송 경로의 기술 검증 PASS. 6대 업로드·모듈 실행·임시 모듈 정리 성공, Ansible 경고 0건. 기존 전체 apply를 재실행할 필요는 없다.**

## 수신 원본

| 항목 | 결과 |
|---|---|
| 사용자 제출 | `FDS_Ansible_SFTP_Verify_Result.tar.gz` + SHA-256 sidecar |
| 원본 크기 | 6,335 bytes |
| SHA-256 | `70c16442626426f0c57ab55d402c53fd62799df9cf44621b4831c1f1627d2e30` |
| 무결성 | 외부 sidecar 일치, 내부 22/22, 일반 파일 23개 |
| 서버 기록 시각 | 2026-09-08 21:25:22–21:25:35 KST (12:25:22–12:25:35 UTC) |
| 원본 상태 | `SFTP_ONLY_ANSIBLE_VERIFIED_REVIEW_REQUIRED` |
| 코드 기준 | `3a02dc8934adb1f80df48ec6763689c401a1e8d6` |
| 실행 엔진 | `/usr/bin/ansible`, ansible-core 2.16.19, Python 3.12.13 |
| 실행 설정 | `/home/server01_ansible/p1-ans-01/ansible.cfg` |

원본 tar의 절대 경로·상위 경로 이탈·링크·중복 멤버 여부를 검사하고 일반 파일만 별도 수신 회차에 복사했다. 내부 체크섬은 체크섬 파일 자체를 제외한 전체 22개를 포함한다. 원래 압축 파일과 sidecar는 사용자 제출본으로 보존하며, Git에는 추출 원본과 원본→Git 매핑을 등록한다.

## 노드별 원본 대조

| 노드 | IP | SFTP put rc | ping | changed | 경고 | 정리 rc | 키 상태 |
|---|---|---:|---|---|---:|---:|---|
| k8s-worker01 | 10.1.93.105 | 0 | pong | false | 0 | 0 | 전후 일치 |
| k8s-worker02 | 10.1.93.107 | 0 | pong | false | 0 | 0 | 전후 일치 |
| k8s-worker03 | 10.1.93.108 | 0 | pong | false | 0 | 0 | 전후 일치 |
| k8s-control01 | 10.1.93.102 | 0 | pong | false | 0 | 0 | 전후 일치 |
| k8s-control02 | 10.1.93.103 | 0 | pong | false | 0 | 0 | 전후 일치 |
| k8s-control03 | 10.1.93.104 | 0 | pong | false | 0 | 0 | 전후 일치 |

대조 근거는 [원본 보고서](results/SFTP_REPORT.json), `results/<노드>_ansible_sftp_ping.json`, `results/<노드>_before.json`, `results/<노드>_after.json`이다. [기계 판독 검토 결과](RECEIPT_REVIEW.json)에 노드별 결과를 기록했다.

- report의 정확한 6대 집합과 순서, 원시 stdout의 실제 hostname·Source `10.250.10.10`·목적지를 확인했다.
- 노드별 상세 로그에서 SFTP 명령 1회와 SSH 명령 5회의 반환값이 모두 0이다. SFTP `put ... AnsiballZ_ping.py`, Python 모듈 실행의 pong, 임시 모듈 디렉터리 정리 명령 rc=0을 각각 확인했다. 단순 최종 PASS 문자열에 의존하지 않았다.
- 6개 Ansible 결과의 stderr는 모두 비어 있고 `[WARNING]`는 0건이다. 정확한 노드의 SUCCESS JSON에 `ping=pong`, `changed=false`가 있으며 failed/unreachable/skipped/warnings/exception이 없다.
- 전후 12개 snapshot의 원시 stdout JSON과 parsed 항목이 일치한다. 노드별 전후 내용, 키 Hash·uid/gid·0600·mtime가 동일하다. 이전 직접 SFTP 수신본의 최종 키 상태와도 6/6 일치한다.
- `changed=false`는 모듈 결과다. 시험 중 임시 모듈 업로드·실행·정리가 발생했다. 원격 파일시스템에 아무 쓰기도 없었다는 뜻으로 사용하지 않는다.

## 이전 결함과 수정 경로 확인

[이전 키트 결함·수정 검토](https://github.com/321Team/fds-project-evidence/blob/61d9d41e318f5d41133dd3f9195f57597a913adf/evidence/P1-ANS-01/pr4-sftp-followup-20260908/FDS_SFTP_Receipt_and_Transport_Fix_Review_v1.0.md)에서 v1.2의 SSH 전용 `-T`가 SFTP 공통 옵션에 전달되는 문제를 확인하고 v1.3에서 분리했다.

이번 서버 원본은 다음을 입증한다.

1. [음성 대조 시험](results/local_invalid_sftp_option.json)의 `sftp -T`는 rc=1, `unknown option -- T`로 거부됐다. 이는 예정된 오류 재현이며 원격 SFTP 시험 실패가 아니다.
2. [실행 변수](results/execution-vars.json)의 `ansible_ssh_common_args`에는 `-T`가 없고 `ansible_ssh_extra_args`에만 있다. 실제 로그에서도 SSH에만 `-T`가 있고 SFTP에는 없다.
3. 해당 호출은 `ansible_ssh_transfer_method=sftp`, `ansible_pipelining=false`, `ansible_become=false`로 수행됐다. 실제 SFTP put의 rc=0과 pong을 확인했으므로 이번 성공을 다른 전송 방식의 우회 성공으로 해석하지 않는다.

따라서 **수정 후 Ansible SFTP-only ping 경로의 경고 미발생·전송 성공을 확인**했다. 과거 전체 apply의 36건 경고에서 실제로 사용된 개별 fallback은 이전 상세 로그 부족으로 여전히 복원하지 못했다. 과거 이력은 보존하며, 그 재구성을 위해 전체 apply를 반복하지 않는다.

## 확인 범위와 남은 절차

승인 main/28개 소스 및 known_hosts 보존은 제공한 검증기의 전후 검사 성공 경로와 원본 `source_and_known_hosts_preserved=true`에 근거한다. 이번 압축에는 개별 Git/source-hash/known_hosts 측정 원본이 없으므로 이를 별도 독립 측정 완료로 확대하지 않는다. 검증기 스크립트 바이트도 이번 서버 압축에 포함되지 않았으며, 배포본과 사용자가 제출한 스크립트 체크섬 성공 콘솔을 연결한다.

이번 실행은 Ansible 2.16.19의 수정된 인자에 대한 제한적 전송 검증이다. v1.3 전체 배포 키트의 재실행이나 2.21.3 운영 전환 검증이 아니다. SSH 키·DNS·서비스 설정·엔진 변경이나 Bootstrap 실행을 수행한 것으로 기록하지 않는다.

- **SFTP 후속 기술 항목: 완료.** 승인 main 코드 추가 수정이나 기존 6대 전체 apply 재실행은 불필요하다. 향후 별도 승인된 재배포에는 공통 옵션 결함이 수정된 키트를 사용한다.
- **운영 이슈 #10: 독립 운영 증적 검토 대기.** 기존 운영 적용 원본과 이번 전송 검증 원본을 재환님 검토 범위에 연결한다. Codex의 기술 검토를 사람의 승인으로 대신하지 않는다.
- **증적 PR #1: Draft·전체 독립 편입 검토 및 최종 병합 대기.** 기존 FUP 보완·과거 승인 기록을 보존한다.
- **엔진 전환 #9와 Bootstrap:** 기존 별도 상태를 유지한다. 이번 수신으로 엔진 전환이나 Bootstrap 해제를 승인하지 않는다.

독립 리뷰 시 확인할 내용은 원본 22개 체크섬, 6개 실제 SFTP put/rc=0/pong/경고 없음, 키 전후 대조, 승인 범위 구분이다. 검토한 증적 Commit과 결과를 운영 이슈 #10에 기록하면 종결 조건을 확인할 수 있다. 추가 서버 진단을 반복하도록 요구하지 않는다.
