# SFTP 수신 검토 및 적용 키트 전송 옵션 수정 v1.0

검토일: 2026-09-08 · [운영 이슈 #10](https://github.com/321Team/infra-ansible/issues/10)

**6대 직접 SFTP 다운로드와 원본 무결성 검토 PASS. 적용 키트가 SSH 전용 `-T`를 SFTP 공통 옵션에도 넣는 결함을 확인하여 수정했다. 수정한 Ansible 전송 경로의 실제 서버 검증은 대기다.**

## 수신 원본과 독립 대조

| 항목 | 확인 결과 |
|---|---|
| 원본 | FDS_SFTP_Followup_Result.tar.gz · 8,039 bytes |
| SHA-256 | `6570cbdaf29d7c321d9d249949d068730fd154896fe5c440af3e0e271c6425df` |
| 외부·내부 무결성 | sidecar 일치, 내부 25/25, 원본 파일 26개 |
| 서버 기록 시각 | 2026-09-08 20:30:07–20:30:13 KST |
| 실행 코드 기준 | infra-ansible main `3a02dc8934adb1f80df48ec6763689c401a1e8d6` |
| 운영 엔진 | ansible-core 2.16.19, Python 3.12.13 |
| 직접 SFTP | 6/6 rc=0, 공개키 인증·SFTP subsystem 수락·종료 rc=0 |
| 파일 대조 | 각 `/etc/os-release` 491 bytes, 다운로드/SSH 관측 Hash 일치 |
| 상태 보존 | 12개 전후 snapshot 일치, 6대 키 상태가 PR4 적용 최종 원본과도 일치 |

Hash뿐 아니라 report의 정확한 6대 집합, 노드별 원본 stdout와 parsed JSON, 실제 SFTP 로그, 다운로드 파일을 대조했다. 키 Hash·uid/gid·0600·mtime를 이전 적용 최종 기록과 교차 확인했다. 컨트롤러 소스와 known_hosts 보존은 수집기의 보고 및 성공 경로로 확인했다. 이번 검토는 사용자 서버에서 생성한 첨부 원본의 검토이며 Codex가 실 서버에서 실행한 시험이 아니다.

6대 모두 키 Hash `b7923e8c646b7a7dd2ccba1ac48ddf02d264780db9100317644dcf87216cc834`, OS 파일 Hash `e1e2155608de5325128e091b3fd8e8f11212d62aa19f78294f7e399e135f4c68`이다. 실제 공개키 인증 성공을 확인했으며, 이 결과가 sshd 전체의 PasswordAuthentication 비활성화를 증명하는 것은 아니다. 수집된 기본 sshd 판독에서는 passwordauthentication yes가 기록됐다. 기존 적용의 범위는 지정 키 제한이며 전역 인증 설정 변경은 포함하지 않는다.

## 확인된 키트 결함

v1.2의 `apply-approved-main.py`는 직접 SSH에 쓸 `ssh_args`에 `-T`를 넣은 다음 그 전체 목록을 `ansible_ssh_common_args`에 전달한다. 이 변수는 SSH뿐 아니라 SFTP/SCP에도 전달된다. SFTP는 `-T`를 지원하지 않는다. [Ansible 공식 옵션 구분](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/ssh_connection.html), [OpenSSH SFTP 옵션](https://man.openbsd.org/sftp)

로컬에서 목적지 없이 `/usr/bin/sftp -T`를 실행해 다음 오류를 재현했다. 네트워크 접속이나 서버 변경은 수행하지 않았다.

```text
unknown option -- T
```

따라서 경고를 유발하는 **키트의 옵션 전달 결함은 확인**됐다. 이전 적용 로그는 SFTP 상세 stderr와 실제 성공한 fallback을 보존하지 않아 과거 36건의 개별 전송 경로를 모두 복원한 것은 아니다. 직접 다운로드 성공만으로 과거 경고 소실을 선언하지 않는다.

`selected_connection_config.stdout`가 비어 있고 선택한 환경 변수가 없다는 것은 해당 수집 항목에 override가 출력되지 않았다는 뜻이다. 별도로 실행 시 `-e`로 생성했던 v1.2 공통 옵션이 없었다는 뜻이 아니다.

## 수정 내용과 영향

| 대상 | 수정 |
|---|---|
| 적용 키트 v1.3 | 공통 옵션에서 `-T` 제거, `ansible_ssh_extra_args='-T'`로 분리 |
| 직접 SSH 검사 | 기존처럼 `-T` 유지 |
| 승인 main의 28개 소스 | v1.2와 바이트 동일 |
| SSH 키·known_hosts·Git 인증 로직 | 이번 수정 대상 아님 |
| 기존 6대 적용 결과 | PASS 유지, 전체 apply 재실행 불필요 |

v1.3 적용 흐름 모의 회귀 8/8과 별도 전송 검증기 9/9을 통과했다. 원래 28개 소스의 구문·엔진 호환성 결과는 소스가 동일한 기존 검증 이력으로 유지한다. 이번 로컬 시험을 실 서버 전송 성공으로 표시하지 않는다.

## 다음 서버 확인 — Ansible SFTP 전송만 검증

`verify-ansible-sftp.py`와 `SFTP_VERIFY_SHA256SUMS`를 ansible01의 server01_ansible 홈에 넣는다. 이번에 사용한 `collect-sftp-followup.py`도 같은 위치에 유지한다. 체크섬은 두 Python 파일을 모두 검증한다.

```bash
(
  set -euo pipefail
  cd ~
  sha256sum --check SFTP_VERIFY_SHA256SUMS
  python3 verify-ansible-sftp.py
)
```

- 시스템 Ansible 2.16.19, 승인 main/28개 소스, 기존 키·known_hosts를 검사한다. git pull·PAT·sudo 실행은 필요 없다.
- 컨트롤러에서 `sftp -T` 오류를 목적지 없이 확인한 뒤, 수정된 옵션으로 Worker01부터 6대에 `ansible.builtin.ping`만 실행한다.
- 이 검증 호출에서만 전송 방식을 SFTP로 한정하고 pipelining을 끈다. 다른 방식으로 우회 성공하는 것을 방지하며, 설정 파일에는 저장하지 않는다.
- 임시 Ansible 모듈의 업로드·실행·정리가 발생한다. SSH 키·DNS·서비스 설정·엔진은 변경하지 않는다.
- 실제 로그의 SFTP 실행·put, 정확한 노드의 pong/changed=false, rc=0, 경고 없음, 전후 상태 보존을 함께 요구한다. 첫 실패 시 다음 노드를 실행하지 않는다.
- 검증 결과 `ARCHIVE`와 `SIDECAR`를 첨부한다. `FDS_Ansible_SFTP_Verify_Result.tar.gz`와 sidecar가 출력된다. 전체 apply 키트 v1.3은 이 확인을 위해 재실행하지 않는다.

## 기록과 잔여 절차

증적은 전용 저장소의 새 수신 회차에 원본 바이트로 편입하고, 원래 압축 파일·sidecar는 기존 첨부로 별도 보존한다. 기존 FUP-01/02 보완 Commit과 원본을 보존한다. 운영 이슈에는 직접 SFTP 성공, 키트 결함 확인·수정, 수정 후 Ansible 실 서버 검증 대기를 구분해 반영한다.

운영 증적의 사람 독립 검토, 증적 PR의 전체 편입·병합, Ansible 2.21.3 운영 전환과 Bootstrap은 별도 상태다. 이번 자료를 다른 티켓의 승인이나 엔진 전환으로 확대하지 않는다.
