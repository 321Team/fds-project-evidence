# FDS SSH 검사 수정·서버 복구·Ansible 호환성 검토 v1.17

검토일: 2026-09-08  
검토 대상: `321Team/infra-ansible` PR #4, Commit `5a2c3786f6af9f107200654aa12c92c3b09700f0`

**판정: 현재 SSH·프로필명·Management 반환 경로·DNS 복구 PASS. 두 Ansible 버전의 전체 6대 읽기 전용 검증 PASS_READONLY_SCOPE.** 기존 Control01·02의 TCP 22 장애는 이번 실행 시점에 해소됐다. 수정 수집기의 실제 서버 before 재실행 원본을 수신해 두 노드 각각 PRE_REBOOT_STATE_PASS, 21/21 검사를 확인했다. 활성 UUID·자동 연결 정책·DNS를 포함한 정상 before 기준을 확보했다. 추가 control01 after 수신으로 실제 부팅 ID 변경 및 재부팅 후 21/21 상태 유지가 확인됐다. control01의 재부팅 후 ansible01 신규 SSH도 사용자 콘솔 출력으로 확인해 로컬 유지·원격 접속을 포함한 control01 검증을 PASS로 완료했다. control02의 after 원본과 재부팅 후 ansible01 신규 SSH 콘솔도 확인했다. 두 노드 각각 다른 boot ID의 로컬 21/21 및 신규 SSH 호스트명 일치로 정의한 재부팅 후 유지·원격 접속 검증을 PASS로 완료했다.

**현재 리뷰 담당: 재환님(`supreme33-kr`) / 재검토 v2 / 최종 판정 PENDING / 사람 확인 PENDING / GitHub COMMENTED 1건 / Open·미병합.** 리뷰 HEAD는 현재 코드와 일치한다. 전체 5개 파일의 정적 검토 범위와 CLAUDE_ASSISTED가 명시됐지만 서버 증적은 리뷰어 세션에서 NOT VERIFIED다. 이권욱 최종 병합 승인은 별도이며 현재 상태는 19절을 따른다. 이하 과거의 병합 권고·리뷰 0건·대기 표시는 해당 기록 당시 상태로 보존한다.

이 문서는 사용자 제출 콘솔 및 수신 원본을 검토한 결과다. 검토 환경에서 현장 서버에 직접 접속하거나 같은 시험을 독립적으로 재실행한 결과는 아니다.


**리뷰 현황 갱신:** 동일 Review ID의 본문이 재검토 v2로 수정됐다. 앞선 rc=1·출력 수집 설명 보정을 수용했고, 최종 판정과 사람 확인을 명시적으로 PENDING으로 남겼다. [v2 확인 답변](https://github.com/321Team/infra-ansible/pull/4#issuecomment-5580680097)과 PR 본문·체크리스트를 갱신했다. 새로 지적된 두 번째 검사의 hardening --check 생략은 두 버전 각각 6대 skipped 로그와 일치하며, 별도 readonly_ssh는 각각 6대 ok다. 기존 수신 로그를 다시 읽은 결과이며 새로운 서버 시험은 아니다. 원본 인계 묶음은 그대로 보존하고 최신 문서를 별도로 배포한다.

## 1. 수신 및 소스 무결성

| 항목 | 확인 결과 |
|---|---|
| 수신 파일 | FDS_SSH_Main_Verification_Result.tar.gz + SHA-256 sidecar |
| TAR SHA-256 | `d764cb22c0f83b401a3fe889b0c8ed32ff07fc6b72615e122e7946b91698a7dc` |
| TAR 크기 / 내부 파일 | 22,182 bytes / 일반 파일 43개, 디렉터리 5개 |
| 첨부 sidecar | 일치 |
| SOURCE_MANIFEST.json | 배포본과 바이트 일치 |
| INPUT_SHA256SUMS | 배포 SHA256SUMS와 바이트 일치, 배포 입력 42개 체크섬 일치 |
| 소스 28개 | 배포 파일 SHA-256·Git blob SHA 일치, 현재 PR Commit tree와 28/28 일치 |
| base main | `4f9bdb7c08704eebb3d1b294751e51b0721b6af4` |
| 실행 시작 | 2026-09-08 10:25:44 KST — 보고서 첫 단계 시각 |
| wrapper_exit_code.txt | 0 |
| VERIFICATION_REPORT.json | PASS_READONLY_SCOPE, 14/14 단계 PASS |

TAR 경로·중복 이름·파일 유형·전체 크기를 검사하고 별도 폴더에서 읽었다. 첨부 원본은 수정하지 않았다. 서버에서 받은 manifest·체크섬 기록과 배포본의 일치는 확인했지만, 이것만으로 서버 실행의 독립 증명을 주장하지 않는다.

## 2. 이전 장애와 현재 복구 확인

| 항목 | k8s-control01 | k8s-control02 |
|---|---|---|
| 사용자 콘솔 SSH 명령 목적지 | 10.1.93.102 | 10.1.93.103 |
| SSH hostnamectl 출력 | k8s-control01 | k8s-control02 |
| 두 버전 OS precheck 호스트명 | k8s-control01 | k8s-control02 |
| DNS verify가 조회한 활성 프로필명 | fds-k8s-control01 | fds-k8s-control02 |
| 반환 경로의 대상 | 10.250.10.10 | 10.250.10.10 |
| 반환 경로 gateway / dev | 10.1.93.58 / ens160 | 10.1.93.58 / ens160 |
| 반환 경로 source IPv4 | 10.1.93.102 | 10.1.93.103 |
| 저장 DNS 및 resolver 검사 | 10.1.93.52, 10.1.93.53 / PASS | 동일 |
| search / ignore-auto-dns | fds.internal / yes | 동일 |
| 현재 DNS drift | false | false |

사용자가 제시한 SSH 명령은 기존 관리 키와 known_hosts를 사용하고 호스트 키 검증을 유지한다. 수신 키트의 실제 6대 SSH 검사도 publickey 인증, StrictHostKeyChecking=yes 및 연결 재사용 비활성화 조건으로 실행됐고 각 노드의 sudo root·키 검사가 통과했다.

IP 반환은 사용자 확인으로 접수한다. 기존 원인 장비의 소유자·포트·DHCP/정적 배정·Proxy ARP 조치 내역 및 현재 무충돌 상태의 독립 ARP 증적은 이 묶음에 없다. 통신 복구 PASS와 원인 조치 이력 수신 상태는 별개다.

앞선 Ansible 키트는 활성 프로필 이름을 확인했으며, 이번 followup before 수신본으로 아래 UUID와 자동 연결 정책을 직접 확인했다.

| 항목 | k8s-control01 | k8s-control02 |
|---|---|---|
| 활성 UUID | 2403bbcc-41f3-4439-81f7-4a3b6a3f582e | 8914aee6-bdb7-4d97-a0ae-0640143ff9c5 |
| K8s 프로필 autoconnect | yes | yes |
| 남아 있는 기본 ens160 프로필 autoconnect | no | no |
| 다른 등록 프로필 | lo; 이전 VPN·DNS UUID는 현재 목록에 없음 | lo |

현재 등록 상태에 대한 판정이며 삭제·변경 행위자와 실행 시각을 입증하지는 않는다.

## 3. 두 버전의 실제 실행 결과

대상 6대: k8s-control01·02·03, k8s-worker01·02·03.

| 단계 | 2.16.19 | 2.21.3 |
|---|---|---|
| 버전 확인 | PASS | PASS |
| 원본 SSH 조건식 회귀 | 14/14 PASS | 14/14 PASS |
| 원본 localhost 태스크 회귀 | 14/14 PASS | 14/14 PASS |
| 신규 SSH·sudo·관리 키·제한 키·파일 불변 | 6/6 PASS | 6/6 PASS |
| hardening --check | 6/6 PASS | 6/6 PASS |
| main OS precheck | 6/6 PASS | 6/6 PASS |
| main DNS verify | 6/6 PASS | 6/6 PASS |
| 단계 합계 | 7/7 PASS | 7/7 PASS |

원본 로그의 PLAY RECAP을 다시 해석해 VERIFICATION_REPORT.json과 일치하는지 대조했다. 원격 단계 8개 × 노드 6개 = 48개 recap 모두 changed/unreachable/failed/rescued/ignored=0이다.

| 원격 단계 | 각 노드 recap — 두 버전 공통 |
|---|---|
| readonly SSH | ok=13, changed=0, skipped=0 |
| hardening check | ok=3, changed=0, skipped=1 |
| OS precheck | ok=15, changed=0, skipped=0 |
| DNS verify | ok=32, changed=0, skipped=5 |

각 버전에서 SSH_READONLY_PASS 6건을 확인했다. 모든 노드의 managed_key_count=1, restricted_key_count=1, effective_user=root, authorized_keys_unchanged=true다. authorized_keys의 검증 전후 불변은 전용 assertion 결과에 근거하며 모든 시스템 파일의 불변을 주장하는 것은 아니다.

OS precheck에서 CentOS 10, 기대 hostname, SELinux Enforcing, swap 비활성, chronyd active, NTP 동기화, Asia/Seoul, overlay·br_netfilter 및 Management 반환 경로 검사가 통과했다.

DNS verify에서 현재·저장 resolver 기준, 내부 FQDN·짧은 이름, 승인 DNS 2대 직접 질의, 외부 이름 해석, API LB Listener 연결 및 실행 전후 kubelet/containerd 상태 동일 검사가 통과했다. 서비스 상태가 동일하다는 검사는 해당 서비스가 활성화됐거나 Kubernetes 클러스터가 Ready라는 의미가 아니다.

## 4. 예상 실패·생략 해석

- localhost의 fatal 출력 10건과 rescued=10은 의도한 음성 시험의 거부 경로다. 최종 recap은 ok=42, changed=0, failed=0, ignored=0이고 14개 계약 assertion이 통과했다.
- hardening --check에서 마지막 제한 키 검사 태스크가 노드별 1건 생략됐다. 동일한 원본 guard는 별도 readonly SSH 단계에서 실제 실행되어 6대 모두 통과했다.
- DNS verify의 생략 5건/노드는 apply 전용 승인 토큰 검사, 롤백 디렉터리 생성, 원본 보존, DNS 구성 변경, NM 재적용이다. verify에서 구성 적용 경로를 실행하지 않은 결과다.
- hardening check의 changed=0은 이번 현재 상태에서 예상 변경이 없었다는 결과다. 실제 apply·rollback 또는 최초 적용 후 멱등성 시험 완료로 확대하지 않는다. [Ansible check mode 공식 설명](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)

## 5. 2.21.3 호환성 판정과 후속 정리

**확인된 범위에서 2.21.3 실행 호환성 PASS다.** 이 판정은 수정된 검토 Commit의 조건식 회귀, 원본 localhost 태스크, 실제 SSH·sudo·키 검사, hardening check, 기존 main의 OS precheck·DNS verify에 한정한다. main의 모든 구성 변경 경로, DNS apply·rollback, P1-LB 전체 시험 및 PR #3 변경까지 시험한 것은 아니다.

2.21.3의 OS precheck·DNS verify 로그에는 INJECT_FACTS_AS_VARS 폐기 예고 경고가 있다. 모든 해당 단계는 rc=0 및 6대 PASS다. 따라서 이번 2.21.3 실행 차단 결함으로 판정하지 않는다.

후속 유지보수로 아래 참조를 ansible_facts 경로로 정리하는 것을 권고한다. 지금은 증적 검토만 수행했으며 이 코드 수정은 포함하지 않았다. [Ansible facts 공식 설명](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)

| 현재 참조 | 후속 정리 방향 |
|---|---|
| ansible_hostname | ansible_facts['hostname'] |
| ansible_distribution | ansible_facts['distribution'] |
| ansible_distribution_major_version | ansible_facts['distribution_major_version'] |
| ansible_default_ipv4 | ansible_facts['default_ipv4'] |

수신 로그가 안내한 제거 예정 버전은 2.24이며, 그 버전에 대한 실행 검증이나 별도 릴리스 일정 확인 결과는 아니다. 경고를 숨기는 조치로 해결 처리하지 않는다.

실행기에는 operational_upgrade=NOT_APPROVED_BY_THIS_RUN이 기록됐다. 2.21.3은 이번 실행 폴더의 venv에서 검증했고, 이번 검토로 시스템 Ansible 전환을 수행하거나 승인하지 않았다.

## 6. 남은 증적과 승인

| 항목 | 상태 / 필요한 내용 |
|---|---|
| 현재 두 노드 SSH·반환 경로·프로필명·DNS | PASS — 이번 결과로 확인 완료 |
| 두 버전 6대 읽기 전용 검증 | PASS — 정상 결과 재제출 요구 없음 |
| 현재 활성 UUID·자동 연결 정책 | PASS — 추가 before 수신본으로 확인 |
| 기존 복구 TAR + sidecar | 두 쌍 수신·무결성 PASS; 모두 과거 적용 전 중단, 성공 기록·백업 없음 |
| 수정 수집기의 before 기준 자료 | PASS — control01·02 각각 21/21, 새 정상 baseline 수신 완료 |
| control01 재부팅 후 로컬 유지 | PASS — 실제 다른 boot ID, 정상 before 원본 일치, after 21/21 |
| control01 재부팅 후 원격 SSH | PASS — 사용자 제출 신규 SSH 출력 k8s-control01 일치 |
| control02 재부팅 후 로컬 유지 | PASS — 다른 boot ID, 정상 before 원본 일치, after 21/21 |
| control02 재부팅 후 원격 SSH | PASS — 사용자 제출 신규 SSH 출력 k8s-control02 일치 |
| 주소 반환 조치 원본 | 사용자 확인 접수 / 상세 원인 장비·조치 기록 미수신 |
| 사람 리뷰어의 GitHub 승인 | 재환님(supreme33-kr) 정식 리뷰 요청 등록, 승인 결과 대기 |
| 최종 병합 승인 | 별도 대기 — 이번에는 병합하지 않음 |

해당 로그인 계정 홈에서 선택된 최신 유효 복구 원본은 이제 수신했다. 모두 실패 기록이므로 복구 성공 과정까지 확인한 것으로 기록하지 않는다. 실제 변경 경위는 기존 작업 기록으로 보완하며, 성공 로그 생성을 위해 복구기를 재실행하지 않는다.

현재 정상 연결을 다시 이전 VPN/DHCP 상태로 되돌리지 않는다. 부족한 복구 이력과 지속성 증적은 현재 통신 PASS를 취소하는 사유로 취급하지 않으며 재발 방지 및 복구 작업 종결 자료로 관리한다.

## 7. GitHub 반영

[infra-ansible Draft PR #4](https://github.com/321Team/infra-ansible/pull/4)의 본문에 이번 결과를 반영하고 재조회로 일치를 확인했다.

- 현재 검토 결과: PASS_READONLY_SCOPE 및 두 노드 통신·반환 경로·DNS 복구 확인.
- 기존 2026-09-07 UNREACHABLE·프로필 불일치·ARP 적용 전 중단은 당시 이력으로 구분했다.
- 현재 HEAD: `5a2c3786f6af9f107200654aa12c92c3b09700f0`.
- 상태: Open / Draft / 미병합. 소스 Commit 변경 없음.
- GitHub에는 검토 결과·식별 해시를 기록했다. 수신 TAR 원본 자체를 GitHub에 업로드한 것은 아니다.
- 이 검토는 Stage A 인수·Bootstrap 해제·시스템 버전 전환의 승인으로 확대하지 않는다.

## 8. 이전 기록과 연결

- 2026-09-07 복구 사전 검사: control01·02 각각 저장 K8s 프로필 9/9 PASS, 다른 MAC의 ARP 응답으로 PREFLIGHT_BLOCKED_NO_CHANGE.
- 당시 응답: .102 → F4:F1:9E:23:2D:7C, .103 → F4:F1:9E:23:30:54.
- 당시 복구 TAR 해시: control01 `97f3ed451df7d31142f9dd580ff791a0d6b4c38fd99d9f6e6918e555e7255a25`; control02 `0fbce2bcf2005150549a991f43b160a1d189fd7e6d5cfa6cab7fac5538cc44b9`.
- Windows 대조 v1.1: 제출 8대의 조회 출력에서 대상 IP·응답 MAC 일치 없음. VM 내부와 미제출 장비는 조사 완료로 보지 않았다.
- 2026-09-08 최신 실행: 두 기대 주소의 SSH 성공, 정상 프로필명·반환 경로·DNS 확인, 전체 14/14 단계 PASS.
- v1.5의 상세 복구 계획·과거 증적은 이전 버전으로 보존한다. 그 문서의 미전환·ARP 차단 상태는 2026-09-07 당시 판정이며 이번 현재 상태 판정으로 사용하지 않는다.

## 9. 이전 before 수신과 수집기 오류 수정 이력 — 2026-09-08

이 절은 오류 수정 당시 기록이다. 아래 재수집 요구는 10절의 새 원본 수신으로 완료됐다.

| 대상 | 수집 시각(KST) | 제출 원본 상태 | 원시 DNS를 수정 해석한 검토 |
|---|---|---|---|
| k8s-control01 | 11:27:18 | REVIEW_REQUIRED, 20/21 | 21/21 일치 |
| k8s-control02 | 11:28:16 | REVIEW_REQUIRED, 20/21 | 21/21 일치 |

원본 TAR·sidecar, 내부 STATE_REPORT.json·sidecar 및 중첩 복구 TAR·sidecar가 모두 일치한다. 두 TAR의 각 4개 항목은 중복·비일반 파일 없이 기대 경로와 일치한다. 기존 수집기 SHA도 배포본과 일치한다.

| 원본 | SHA-256 |
|---|---|
| FDS_Control_Followup_k8s-control01_before.tar.gz | `5401d68a8213da7cf2a59b035ced15c8072e48a063b64696decb52a6cf0c6120` |
| FDS_Control_Followup_k8s-control02_before.tar.gz | `0193a39e44c184649ce7aa0ee5cf9287c353a9e62eb24b4ad2225a2a496d7627` |
| 포함된 control01 복구 TAR | `f984dfeafa3293344cfbbaff1b42100e77fe69f8657f68763aaf41412487337a` |
| 포함된 control02 복구 TAR | `ce5ae4cb2066a1f0bc993a166ce65d058b06258f5e209a91c655489bd6e1f877` |

### 오류와 수정 범위

두 서버 모두 `nmcli -t -e no -g IP4.DNS device show ens160`의 rc=0, 원시 stdout은 `10.1.93.52 | 10.1.93.53\n`이다. 기존 words()가 파이프를 항목으로 남겨 `['10.1.93.52', '|', '10.1.93.53']`으로 비교한 것이 원인이다. 저장 DNS와 /etc/resolv.conf의 DNS·search는 기존 검사에서도 정상이다.

전용 runtime DNS 파서로 구분자만 처리하고 각 토큰을 IPv4Address로 검증한다. 순서·개수·중복 검사를 유지하고 오류 토큰을 묵살하지 않는다. 수신 원본과 원본의 REVIEW_REQUIRED는 수정하지 않았다. 21/21은 동일 원시 출력의 검토·재해석 결과이며 수정본의 서버 재실행 결과가 아니다.

수정 회귀 시험 7건 PASS: 두 수신본 재현, 여러 구분 형식, 누락·역순·추가·중복 DNS 거부, 잘못된 주소·오류 토큰 거부, 실패/구버전 baseline 거부, 실제 명령 출력으로 두 노드 before/after 모의 실행 및 원본 보존, 오류 시 결과 묶음 생성. 현장 네트워크 명령은 실행하지 않았다.

### 과거 복구 이력의 실제 내용

- control01 선택 기록: 2026-09-08 10:22:42 KST, PREFLIGHT_BLOCKED_NO_CHANGE, `An expected profile is missing`. 조회 당시에도 기대 K8s UUID가 활성화돼 있으며 이전 VPN·DNS UUID가 목록에 없다. 이 실행에는 변경 명령과 AUTOCONNECT_BACKUP이 없다.
- control02 선택 기록: 2026-09-07 20:13:28 KST, PREFLIGHT_BLOCKED_NO_CHANGE. 당시 .103에 다른 MAC의 ARP 응답이 있어 적용 전 중단했다. 변경 명령과 AUTOCONNECT_BACKUP이 없다.
- 수신된 상태는 그대로 보존한다. 두 현재 노드의 정상 상태는 이번 before 자료와 앞선 14/14 결과로 확인하며, 과거 중단 로그를 성공으로 해석하지 않는다.

### 다음 실행

수정한 `collect-control-recovery-followup.py`와 `CONTROL_FOLLOWUP_SHA256SUMS`를 각 기존 계정 홈에 교체하고 `--phase before`만 다시 실행한다. 새 PRE_REBOOT_STATE_PASS와 BASELINE 경로를 사용한다. 이전 ng1esxrg·r42dw8wy의 실패 보고서는 after 기준으로 사용하지 않는다. 네트워크 재설정과 전체 14개 단계 재검증은 필요하지 않다.

수정 수집기 SHA-256: `cf37a6d6a585123de9006cc680a13f1a5932076c3b967f69f3b4f07b23d3625d`.

새 before 검토 후 점검 시점에 한 노드씩 재부팅하고 같은 수정본의 after 및 ansible01 신규 SSH로 유지 여부를 확인한다. 현재 제출본은 before이므로 재부팅 후 유지 PASS는 아직 부여하지 않는다. 상세 명령은 FDS_Control_Recovery_Followup_Runbook_v1.1.md에 있다.

## 10. 수정 수집기 실제 서버 before 수신 완료 — 2026-09-08

**PRE_REBOOT_STATE_PASS — 두 노드 각각 21/21 PASS.** 이번에는 수정 파서로 이전 원본을 재해석한 결과가 아니라 사용자가 수정본을 현장에서 다시 실행해 제출한 원본 보고서의 판정이다. 검토 환경에서 현장 명령을 독립 실행한 것은 아니다.

| 항목 | k8s-control01 | k8s-control02 |
|---|---|---|
| 수집 시각(KST) | 2026-09-08 11:44:48 | 2026-09-08 11:45:27 |
| 상태 / 검사 | PRE_REBOOT_STATE_PASS / 21/21 | 동일 |
| 기록된 읽기 명령 | 30개, 모두 rc=0 | 동일 |
| 기준 JSON SHA-256 | `c2292626b86aaceaee20bb79838e9c28e7a5bad9a1ce4593641cf05b1edfe7e7` | `7cacec34be8da9713649360d714780b4fc22d3635c2ccfcd67ada8a9e845fb71` |
| 부팅 ID | 7d3b2a48-a645-49ad-9429-d8c18bb5caaa | be231668-eccd-4f15-9956-45a8a4125014 |
| TAR SHA-256 | `964f6fa047b2b6249e0d4f6645f0a352891667d81cbb7969c996f91665ef11de` | `48b03ce7d06ec953f641810c170b2e70a33c5d7f4d371eecf01128c73e1ddced` |
| TAR 크기 | 3,856 bytes | 5,153 bytes |

수집기 SHA-256은 두 보고서 모두 배포 수정본 `cf37a6d6a585123de9006cc680a13f1a5932076c3b967f69f3b4f07b23d3625d`와 일치한다. 바깥 TAR·sidecar, 내부 STATE_REPORT·sidecar, 포함된 복구 TAR·sidecar의 SHA-256을 검증했다. 각 TAR의 내부 일반 파일 4개는 기대 경로와 일치하고 중복·링크가 없다. raw nmcli/ip/hostnamectl 출력과 보고된 프로필·UUID·주소·MAC·경로·runtime DNS를 대조했다. resolver·부팅 ID는 수집 보고서의 직접 읽기 필드에 근거한다. 기록된 변경 명령은 없다.

첨부 파일명에는 `(1)`이 붙었지만 sidecar 안의 원래 파일명은 `FDS_Control_Followup_<host>_before.tar.gz`다. 업로드 이름과 원본 이름을 대응시켜 실제 바이트 해시를 검증했다. 첨부 원본은 수정하지 않았다.

실제 DNS 출력은 여전히 `10.1.93.52 | 10.1.93.53`이며 수정본은 두 주소로 올바르게 해석했다. uptime과 DNS 해석 표현을 제외한 현재 보고 상태는 이전 before 수신 상태와 일치하고, 부팅 ID도 같다. 수집기 오류는 해소됐으며 이 자료만으로 재부팅 후 유지 PASS를 부여하지 않는다.

### 확정한 비교 기준 경로

아래 서버 경로는 사용자가 제출한 실행 콘솔의 BASELINE과 연결한다. 기준 내용은 위 STATE_REPORT 해시로 식별한다.

- control01: `/home/server02/FDS_Control_Followup.rfas2d1m/STATE_REPORT.json`
- control02: `/home/server03/FDS_Control_Followup.0een9osv/STATE_REPORT.json`

해당 JSON과 바로 옆 `.sha256`을 서버에 유지한다. 이전 ng1esxrg·r42dw8wy의 실패 기준은 사용하지 않는다. 현재 기준 수집 이후 설정이 변경되지 않았다면 before 재수집을 반복할 필요가 없다.

### 기존 복구 기록의 해석

포함된 복구 TAR 두 쌍은 이전에 수신한 중단 원본과 바이트가 같다. control01은 기대 프로필 누락 검사에서 중단, control02는 과거 ARP 응답으로 중단한 기록이며 둘 다 AUTOCONNECT_BACKUP이 없다. `RECOVERY_RECEIPT=LATEST_VALID_PAIR_INCLUDED_REVIEW_REQUIRED`는 이 별도 복구 이력의 검토 상태다. 현재 PRE_REBOOT_STATE_PASS를 취소하거나 재수집을 요구하는 의미가 아니다. 실제 변경 경위는 별도 이력 항목으로 유지한다.

### 다음 단계 및 GitHub 상태

control01부터 계획된 점검 시점에 VMware 콘솔을 확보하고 재부팅한다. 같은 수정본과 위 baseline으로 after 수집 후 ansible01의 기존 관리 키·엄격한 호스트 키 검증·연결 재사용 비활성 조건으로 새 SSH를 확인한다. control01 확인이 끝나면 control02에 같은 절차를 적용한다. after TAR·sidecar와 SSH 출력이 최종 유지 확인의 증적이다.

명령은 FDS_Control_Recovery_Followup_Runbook_v1.2.md에 노드별 절대 경로로 제공한다. 기존 14/14 Ansible 검증은 유지한다. 현재 before 정상 수신 완료를 PR #4에 반영하고 재조회로 확인했으며, HEAD `5a2c3786f6af9f107200654aa12c92c3b09700f0`, Draft/Open/미병합 상태를 유지한다.

## 11. control01 재부팅 후 로컬 유지 수신 이력 — 2026-09-08

이 절은 after 원본 수신 당시 상태다. 당시 남았던 신규 SSH는 12절의 콘솔 제출로 확인 완료했다.

**POST_REBOOT_LOCAL_PASS_REMOTE_PENDING.** 실제 다른 부팅 ID에서 기대 로컬 상태 21개가 모두 유지됐다. ansible01의 재부팅 후 신규 SSH 출력이 아직 없어 원격 접속까지 포함한 최종 유지 PASS는 대기로 둔다.

| 항목 | 확인 결과 |
|---|---|
| 수집 시각 | 2026-09-08 11:58:10 KST |
| 대상 | k8s-control01 / phase=after |
| after TAR | FDS_Control_Followup_k8s-control01_after.tar.gz, 4,496 bytes |
| after TAR SHA-256 | `fba378d54059367bf532626d0a6b6f77b1e175544794edc8e2da4fd0e1bc8274` |
| after JSON SHA-256 | `47c7fd09e70696b29c431c9c518515db7920d05582db1419ea11b48ac2aac9f2` |
| 포함된 before JSON SHA-256 | `c2292626b86aaceaee20bb79838e9c28e7a5bad9a1ce4593641cf05b1edfe7e7` — 앞서 수신한 정상 원본과 일치 |
| before boot ID | `7d3b2a48-a645-49ad-9429-d8c18bb5caaa` |
| after boot ID | `bfa5774a-4df9-448e-adb8-e6cf17984a71` |
| 보고 uptime | before 5277.62초 → after 137.22초 |
| 로컬 상태 | 21/21 PASS; 읽기 명령 30개 모두 rc=0 |
| 수집기 SHA-256 | `cf37a6d6a585123de9006cc680a13f1a5932076c3b967f69f3b4f07b23d3625d` — before·after·배포본 일치 |

외부 TAR·sidecar, 내부 after JSON·sidecar, baseline-before JSON·sidecar, recovery-original TAR·sidecar의 무결성을 확인했다. 내부 항목 6개는 모두 기대 경로의 일반 파일이며 중복·링크가 없다. baseline-before 두 파일은 앞서 수신한 control01 정상 before 두 파일과 바이트가 같다. compare_boot 및 evaluate_state를 다시 실행해 같은 호스트·수집기, 정상 before, 이후 시각, 다른 부팅 ID, 현재 21개 상태를 확인했다. 수신 원본은 변경하지 않았다.

raw hostnamectl/nmcli/ip 출력과 보고서의 프로필·UUID·주소·MAC·경로·runtime DNS도 대조했다. 실제 활성 UUID `2403bbcc-41f3-4439-81f7-4a3b6a3f582e`, 주소 `10.1.93.102/24`, 기본 GW `.254`, Management 반환 `.58`, DNS `.52/.53`, search `fds.internal`, K8s autoconnect=yes 및 남아 있는 ens160 프로필 autoconnect=no가 유지됐다. resolver·boot ID는 수집 보고서의 직접 읽기 필드에 근거한다.

before 대비 관찰된 차이는 boot ID·uptime 및 lo 프로필 UUID다. lo는 connection.type=loopback, interface=lo이며 Ethernet 경쟁 프로필이 아니다. 두 Ethernet 프로필의 UUID와 수집 설정 값은 그대로다. lo UUID 변경 원인까지 이 자료로 단정하지 않으며, 이 차이는 정의된 ens160 복구 조건을 위반하지 않는다.

포함된 복구 TAR는 앞서 수신한 PREFLIGHT_BLOCKED_NO_CHANGE 원본과 바이트가 같다. RECOVERY_RECEIPT의 REVIEW_REQUIRED는 해당 별도 이력에 대한 표시이고 이번 로컬 유지 PASS를 취소하지 않는다.

### 즉시 남은 확인

ansible01의 server01_ansible 계정에서 Runbook v1.3 2.3절의 관리 키·StrictHostKeyChecking·연결 재사용 비활성 옵션으로 control01 신규 SSH를 실행하고 hostnamectl 결과를 제출한다. 기대 출력은 k8s-control01이다. 이전 재부팅 전 SSH 성공이나 server02 프롬프트만으로 이 원격 검사를 대신하지 않는다.

control01 로컬 after와 신규 SSH가 모두 정상임을 확인한 뒤 control02의 재부팅·after·신규 SSH를 진행한다. control02 기준은 `/home/server03/FDS_Control_Followup.0een9osv/STATE_REPORT.json`이다. control01의 이번 출력에 나타난 a6zy31pt/STATE_REPORT.json은 after 결과이며 새 before로 사용하지 않는다.

PR #4에 control01 로컬 유지 완료와 원격 SSH·control02 대기를 구분해 반영하고 재조회로 확인했다. 검토 HEAD와 Draft/Open/미병합 상태는 유지했다.

## 12. control01 재부팅 후 신규 SSH 확인·검증 완료 — 2026-09-08

**control01 재부팅 후 로컬 유지 및 원격 접속 검증 PASS.** 앞서 확인한 정상 before·다른 boot ID의 after 21/21과 이번 사용자 제출 신규 SSH 출력을 연결해 판정했다.

출처는 대화에 제출된 `server01_ansible@ansible01` 콘솔 텍스트다. 별도 서버 로그 파일·sidecar·실행 시각·종료 코드가 첨부된 것은 아니다. 검토자가 현장에 독립 접속한 결과로 기록하지 않는다. 제출 순서는 control01 after 원본 검토 및 신규 SSH 요청 이후다.

제출 명령:

```bash
ssh -T \
  -i "$HOME/.ssh/p1_ansible_ed25519" \
  -o BatchMode=yes -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no \
  -o StrictHostKeyChecking=yes \
  -o "UserKnownHostsFile=$HOME/.ssh/known_hosts" \
  -o IdentitiesOnly=yes -o IdentityAgent=none \
  -o ControlMaster=no -o ControlPersist=no -o ControlPath=none \
  -o ConnectTimeout=10 \
  svc_ansible@10.1.93.102 hostnamectl --static
```

제출 출력:

```text
k8s-control01
```

명령은 기존 관리 키·known_hosts를 사용하고 공개키 인증을 지정했다. 비밀번호·키보드 대화형 인증을 끄고 StrictHostKeyChecking=yes, IdentitiesOnly=yes, IdentityAgent=none, ControlMaster/ControlPersist/ControlPath 비활성 조건으로 실행한 것으로 제출됐다. 출력 호스트명이 기대값과 일치한다.

| 연결 증적 | 결과 |
|---|---|
| before 원본 | PRE_REBOOT_STATE_PASS, 21/21, JSON SHA c2292626b86aaceaee20bb79838e9c28e7a5bad9a1ce4593641cf05b1edfe7e7 |
| after 원본 | 다른 boot ID, 21/21; TAR SHA fba378d54059367bf532626d0a6b6f77b1e175544794edc8e2da4fd0e1bc8274 |
| 재부팅 후 신규 SSH | 콘솔 제출본, svc_ansible@10.1.93.102 → k8s-control01 |
| control01 종합 판정 | PASS — 정의한 로컬 유지·신규 SSH 확인 범위 완료 |

수신 after 보고서의 원래 POST_REBOOT_LOCAL_PASS_REMOTE_PENDING 문자열은 변경하지 않는다. 이 원본의 원격 확인 대기 항목을 별도 콘솔 검토 기록으로 완료 처리한 것이다. 과거 복구기의 PREFLIGHT_BLOCKED_NO_CHANGE 기록과 실제 변경 경위 보완 항목도 별도로 유지한다.

다음 노드는 control02다. 정상 baseline `/home/server03/FDS_Control_Followup.0een9osv/STATE_REPORT.json`을 유지하고 Runbook v1.4의 3절에 따라 VMware 콘솔에서 재부팅, server03 계정 after 수집, ansible01 신규 SSH를 진행한다. control01 절차를 반복할 필요는 없다. control02의 after TAR·sidecar와 신규 SSH 출력이 수신되기 전까지 두 노드 전체 유지 검증 완료로 확대하지 않는다.

이번 완료 상태를 PR #4에 반영하고 재조회로 확인했다. 검토 HEAD `5a2c3786f6af9f107200654aa12c92c3b09700f0`, Draft/Open/미병합 상태를 유지했다. 시스템 Ansible 전환·Bootstrap 해제·사람 리뷰 승인으로 확대하지 않는다.

## 13. control02 재부팅 후 로컬 유지 수신 이력 — 2026-09-08

이 절은 after 원본 수신 당시 상태다. 당시 남았던 신규 SSH는 14절의 콘솔 제출로 확인 완료했다.

**POST_REBOOT_LOCAL_PASS_REMOTE_PENDING.** control02의 정상 before 이후 다른 부팅 ID에서 현재 로컬 상태 21개가 모두 유지됐다. control01은 로컬 유지·신규 SSH까지 완료됐고, control02는 ansible01 신규 SSH 출력만 남아 있다.

| 항목 | control02 확인 결과 |
|---|---|
| after 수집 시각 | 2026-09-08 12:10:57 KST |
| after TAR | FDS_Control_Followup_k8s-control02_after.tar.gz, 5,820 bytes |
| after TAR SHA-256 | `3196b74699f073fae22d4a67fffee5b02a26dbb664e05f9c475c044c58f4caf9` |
| after JSON SHA-256 | `ffe953cbe2c06be8c0df31d6674074e8d11e1edf6753626c3590ebfe3d0e5324` |
| 포함된 before JSON SHA-256 | `7cacec34be8da9713649360d714780b4fc22d3635c2ccfcd67ada8a9e845fb71` |
| before boot ID | `be231668-eccd-4f15-9956-45a8a4125014` |
| after boot ID | `84596ca2-4386-4ebc-bfca-5d90643f4eed` |
| 보고 uptime | before 5512.66초 → after 884.12초 |
| 상태 검사 / 읽기 명령 | 21/21 PASS / 30개 모두 rc=0 |
| 수집기 SHA-256 | `cf37a6d6a585123de9006cc680a13f1a5932076c3b967f69f3b4f07b23d3625d` — 배포본·before·after 일치 |

외부 TAR·sidecar, 내부 after JSON·sidecar, baseline-before JSON·sidecar, recovery-original TAR·sidecar가 모두 일치한다. 내부 항목 6개는 기대 경로의 일반 파일이며 중복·링크가 없다. baseline-before 두 파일은 앞서 수신한 0een9osv 정상 before 원본과 바이트가 같다. compare_boot 및 evaluate_state를 재실행해 같은 호스트·수집기, 정상 기준 상태, 이후 수집 시각, 실제 boot ID 변경과 after 21개 상태를 확인했다. 이 검증은 수신 자료 검토이며 현장 서버 독립 재실행이 아니다.

raw hostnamectl/nmcli/ip 출력과 보고된 프로필·UUID·주소·MAC·경로·runtime DNS를 대조했다. 활성 UUID `8914aee6-bdb7-4d97-a0ae-0640143ff9c5`, `10.1.93.103/24`, 기본 GW `.254`, Management 반환 `.58`, DNS `.52/.53`, search `fds.internal`, K8s autoconnect=yes 및 기본 ens160 프로필 autoconnect=no가 유지됐다. resolver·부팅 ID는 수집 보고서의 직접 읽기 필드에 근거한다.

관찰된 차이는 boot ID·uptime 및 lo 프로필 UUID다. lo UUID는 `23b404c1-855a-486e-90de-87b63ab27a45`에서 `70f0e7e6-b04a-4c25-a0ed-9557a94c4d8e`로 바뀌었으며 type=loopback/interface=lo 상태다. Ethernet 두 프로필의 수집 값은 그대로다. lo UUID 변경 원인을 단정하지 않으며 정의된 ens160 복구 기준을 위반하지 않는다.

기존 복구 TAR는 과거 ARP 응답으로 PREFLIGHT_BLOCKED_NO_CHANGE였던 수신 원본과 바이트가 같다. RECOVERY_RECEIPT의 REVIEW_REQUIRED는 별도 복구 이력 표시이며 현재 로컬 유지 PASS를 취소하지 않는다.

### 시각·작업 순서 해석

수집 시각에서 보고 uptime을 단순 차감하면 부팅 시작 추정은 control01 약 11:55:53 KST, control02 약 11:56:14 KST다. 이는 두 노드의 부팅 시점이 가까웠을 가능성을 보여주며, 자료 제출 순서만으로 control01 검증 완료 후 control02를 재부팅하는 순차 절차를 준수했다고 기록하지 않는다. 수집 시각과 uptime의 읽기 시점 차이 및 벽시계 보정 가능성이 있어 정확한 재부팅 명령 시각을 확정한 값은 아니다. 노드별 before 이후 boot ID 변경·현재 로컬 상태 PASS와 작업 순서 입증 범위를 구분한다.

### 남은 확인

ansible01의 server01_ansible 계정에서 Runbook v1.5 3.3절에 따라 기존 관리 키·known_hosts·엄격한 호스트 키 검증·연결 재사용 비활성 조건으로 `svc_ansible@10.1.93.103 hostnamectl --static`을 실행한다. 기대 출력은 `k8s-control02`다. 해당 결과가 수신되기 전까지 control02 원격 확인을 완료하지 않는다. 두 노드의 재부팅·after 수집은 이미 완료됐으며 증적 제출을 위해 반복하지 않는다.

control02 after 출력의 `/home/server03/FDS_Control_Followup.70yk4mgs/STATE_REPORT.json`은 after 결과이며 before 기준 경로를 대체하지 않는다. 이번 로컬 유지 완료와 신규 SSH 대기를 PR #4에 반영하고 재조회로 확인했다. 검토 HEAD·Draft/Open/미병합 상태를 유지했다.

## 14. control02 신규 SSH 수신 및 두 노드 유지 검증 완료 — 2026-09-08

**control01·02의 재부팅 후 로컬 상태 유지·신규 SSH 확인 PASS.** 각 정상 before·after 원본의 무결성, 실제 다른 부팅 ID, after 21/21과 재부팅 후 신규 SSH 콘솔 출력을 연결해 기술 검증을 완료했다. 기존 Ansible 2.16.19/2.21.3 전체 14/14 읽기 전용 검증도 유지한다.

### 이번 control02 SSH 제출 원문

출처: 사용자 대화 콘솔, 실행 프롬프트 `server01_ansible@ansible01`. control02 after 원본 검토 및 신규 SSH 요청 이후 제출됐다. 별도 서버 로그 파일·sidecar·명시적 실행 시각·종료 코드는 제출되지 않았다. 검토자가 서버에 독립 접속한 결과로 기록하지 않는다.

```bash
ssh -T \
  -i "$HOME/.ssh/p1_ansible_ed25519" \
  -o BatchMode=yes -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no \
  -o StrictHostKeyChecking=yes \
  -o "UserKnownHostsFile=$HOME/.ssh/known_hosts" \
  -o IdentitiesOnly=yes -o IdentityAgent=none \
  -o ControlMaster=no -o ControlPersist=no -o ControlPath=none \
  -o ConnectTimeout=10 \
  svc_ansible@10.1.93.103 hostnamectl --static
```

```text
k8s-control02
```

기존 관리 키 및 known_hosts 사용, 공개키 인증 지정, 비밀번호·키보드 대화형 인증 비활성, StrictHostKeyChecking=yes, IdentitiesOnly=yes, IdentityAgent=none, ControlMaster/ControlPersist/ControlPath 비활성 조건을 포함한 제출 명령과 기대 호스트명 일치를 확인했다.

### 완료 판정과 원본 연결

| 항목 | control01 | control02 |
|---|---|---|
| 정상 before 원본 및 after에 포함된 기준 일치 | PASS | PASS |
| before → after 실제 boot ID 변경 | 확인 | 확인 |
| 재부팅 후 로컬 상태 | 21/21 PASS | 21/21 PASS |
| 재부팅 후 ansible01 신규 SSH | k8s-control01 — 콘솔 제출 | k8s-control02 — 콘솔 제출 |
| 유지·원격 접속 기술 검증 | PASS / 완료 | PASS / 완료 |
| after TAR SHA-256 | `fba378d54059367bf532626d0a6b6f77b1e175544794edc8e2da4fd0e1bc8274` | `3196b74699f073fae22d4a67fffee5b02a26dbb664e05f9c475c044c58f4caf9` |

after 원본의 POST_REBOOT_LOCAL_PASS_REMOTE_PENDING 문자열은 변경하지 않았다. 원격 확인 대기는 별도 콘솔 증적 검토로 완료했다. 동일 검증을 끝내기 위한 추가 재부팅·before·after·SSH 재제출은 요구하지 않는다.

### 종결 범위와 별도 남은 항목

- 이번에 완료한 범위: SSH 결함 수정 검토 Commit의 기존 두 버전 실행 검증 및 control01·02 기대 네트워크 상태의 재부팅 후 유지·신규 SSH 확인.
- 실제 프로필 변경·주소 반환 경위는 별도 작업 이력 보완 항목이다. 수신 복구기 원본은 모두 PREFLIGHT_BLOCKED_NO_CHANGE이므로 성공 이력으로 바꾸지 않는다.
- 13절의 부팅 시각 추정상 두 부팅이 가까웠을 가능성을 기록했다. 노드별 기능·상태 유지 PASS가 순차 재부팅 절차 준수의 입증을 포함하지는 않는다.
- PR #4 사람 리뷰 제출은 이번 조회에서 0건이다. 사람 리뷰와 이권욱 최종 병합 승인은 별도이며, PR은 Draft/Open/미병합 상태로 유지했다.
- 시스템 Ansible 2.21.3 전환, 모든 Playbook의 apply·rollback 호환성, Stage A 인수·Bootstrap 해제는 이 검증으로 승인하지 않는다. INJECT_FACTS_AS_VARS 경고 정리는 별도 유지보수 항목이다.

PR #4 본문에 두 노드 기술 검증 완료와 별도 미완료 항목을 반영하고 재조회로 일치 확인했다. HEAD는 `5a2c3786f6af9f107200654aa12c92c3b09700f0`으로 유지했다. 수신 TAR 원본을 GitHub에 새로 업로드한 것은 아니며, 검토 결과와 식별 해시를 반영했다. 완료 상태와 과거 실행 절차는 Runbook v1.6에 연결했다.

## 15. 재환님 리뷰 담당 등록 및 인계 — 2026-09-08

사용자가 하영님 부재에 따라 재환님으로 리뷰 담당을 변경하도록 요청했다. 사용자가 앞서 명시한 GitHub 계정 `supreme33-kr`를 식별 기준으로 사용했고, 현재 infra-ansible 저장소의 Write 권한을 조회해 확인했다. 동일 계정을 PR #4의 requested reviewers에 등록했다.

| 항목 | 결과 |
|---|---|
| 리뷰어 | supreme33-kr / 재환님 |
| 기존 요청 리뷰어 | 최초 조회 시 없음 — 기존 하영님 요청 삭제나 제출 리뷰 무효화는 수행하지 않음 |
| 단계 | Draft → Ready for review |
| 리뷰 요청 상태 | REQUESTED — 사람 승인 완료 아님 |
| 검토 HEAD | 5a2c3786f6af9f107200654aa12c92c3b09700f0, 유지 |
| base main | 4f9bdb7c08704eebb3d1b294751e51b0721b6af4, 유지 |
| PR | Open / 미병합 |
| 최종 병합 승인 | 이권욱 별도 승인 대기 |

GitHub의 정식 리뷰 진행 단계로 전환하고 requested_reviewers의 supreme33-kr 등록을 확인했다. [GitHub 단계 전환 공식 설명](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/changing-the-stage-of-a-pull-request)

PR 본문 상단에 담당·고정 Commit·검토 순서·수신 증적 및 판정 범위를 추가했다. 변경 5개 파일은 playbooks/harden_svc_ansible_key.yml, tests/test-ssh-key-guards.py, tests/ssh-server-readonly.yml, scripts/verify-ssh-main.py, docs/runbooks/SSH-Key-Guard-Verification.md다. 코드·서버 재검증을 새로 수행한 작업은 아니다.

재환님은 단일 OR 조건식의 누락·중복 거부, 기존 키 옵션·교체 동작 보존, 실제 6대 검증과 14/14 결과의 범위, check mode 생략·예상 음성 rescued 해석 및 수신 원본·콘솔 출처 구분을 검토한다. 적합성을 판단한 뒤 해당 HEAD에 Approve 또는 Changes requested를 남긴다. 순차 재부팅 절차 준수와 변경 경위 입증의 한계도 유지한다.

인계 파일: FDS_PR4_Reviewer_Handoff_supreme33-kr_v1.0.md. 완료 실행 절차: FDS_Control_Recovery_Followup_Runbook_v1.7.md. PR 본문에는 검토 결과·식별 해시를 반영했으며, 서버 TAR 원본을 새로 GitHub에 업로드하거나 별도 메시지 채널로 전송한 것은 아니다.

재조회로 리뷰어·Ready 상태·본문 반영·미병합과 HEAD 보존을 확인했다. 이 변경은 infra-ansible PR #4의 리뷰 담당 등록이며, 정본 저장소 접근권한·리드 역할·타 PR 승인 상태 변경으로 확대하지 않는다.

## 16. 재환님 리뷰 초안 수신 및 대응 — 2026-09-08

**원본 증적에 접근할 수 없다는 지적은 타당하다.** 기존 인계는 결과와 해시를 제시했지만 독립 리뷰어가 원본을 대조할 수 있는 전달 경로가 부족했다. 이 사유로 재환님 관점에서 증적을 `NOT VERIFIED`로 둔 판단은 적절하다. 아래 설명과 원본 인계 ZIP으로 보완하며, ZIP 준비만으로 재환님의 수신·검토 완료를 기록하지 않는다.

이번 대조에서 SSH 가드 수정의 추가 차단 결함은 발견하지 못했다. 읽기 전용 경로와 모의시험 변수의 출처를 확인했다. **독립 리뷰는 대기 상태이며, 병합 보류 사유는 증적 확인과 사람의 최종 판단이다.** 코드 리뷰, 수신 원본에 대한 기술 검토, GitHub CI, 사람 승인 상태를 분리한다.

## 지적별 검토

| 첨부 문서 항목 | 판단 | 확인 및 조치 |
|---|---|---|
| §2.1 SSH 가드 단일 OR 수정 | 동의 | `failed_when` 목록의 AND 의미와 선행 `or` 오류를 제거하는 수정. 최초·최종 가드 외의 키 경로·제한 옵션·교체 동작은 유지 |
| §3 원본·해시 독립 대조 불가 | 수용 | 원본 TAR 5개와 sidecar, TAR에서 읽은 로그·보고서, 콘솔 제출 기록, 인덱스·체크섬을 `FDS_PR4_Review_Evidence_v1.0.zip`으로 준비. 재환님 실제 수신·확인은 대기 |
| §3 CI NOT RUN | 동의, 의미 보정 | 해당 HEAD Actions 0건, Check run 0건, Commit status 항목 0건. CI 미실행과 제출된 서버 실행 미실행은 다름. CI PASS로 표시하지 않음 |
| §4 precheck·DNS verify 읽기 전용 미확인 | 작성 측 추가 검토 완료 | 고정 HEAD의 호출 파일과 DNS role 및 실패 복구 분기를 검토. 원격 구성 변경 경로가 verify 단계에서 차단됨을 확인 |
| §4 PR3_REVIEW_* 제거 사유 | 출처 확인 | 이전 PR #3 로컬 모의시험의 `sitecustomize.py` 활성화·사례·추적 변수. PYTHONPATH와 함께 자식 프로세스 환경에서 제거 |
| §4 PR Template 정책 미반영 | 별도 정책 작업 대상 | 이 HEAD tree 28개 파일에는 `.github/pull_request_template.md`, Governance 문서·검증 스크립트 자체가 없음. 기존 템플릿의 일부 필드만 누락된 것으로 단정하지 않음 |
| §5 사람 확인 CONFIRMED | 제출 전 수정 필요 | 본문은 사람 미확인 초안인데 제출용 예문은 CONFIRMED로 미리 채워짐. 실제 확인 전 `PENDING`으로 두고, 재환님 본인이 확인한 뒤 최종 판정과 함께 변경 |

Ansible 조건식 해석은 [공식 실패 조건 문서](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html#defining-failure)와 일치한다.

## 읽기 전용 경로의 근거

고정 HEAD의 전체 28개 파일과 로컬 검토본 Git blob SHA를 대조해 28/28 일치를 확인했다. 이번 검토는 정적 소스 대조와 기존 수신 증적 검토이며 새 서버 실행이 아니다. `changed_when: false` 표기만으로 읽기 전용을 판단하지 않고 실제 명령과 변경 분기 조건을 검토했다.

| 고정 소스 | 검토 내용 |
|---|---|
| [scripts/verify-ssh-main.py](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/scripts/verify-ssh-main.py) | hardening에는 `--check`, DNS에는 extra vars `cr_dns_phase=verify`를 전달. 운영 apply·rollback Playbook은 호출하지 않음 |
| [playbooks/precheck.yml](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/playbooks/precheck.yml) | facts·assert·stat·debug 및 id/getenforce/timedatectl show/systemctl is-active/swapon --show/sysctl -n/ip route get 조회. 구성 변경 명령 없음 |
| [playbooks/cr-p1-ans-01-01-verify.yml](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/playbooks/cr-p1-ans-01-01-verify.yml) | `cr_dns_phase: verify`, dns_resolver role 호출 |
| [roles/dns_resolver/tasks/main.yml](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/roles/dns_resolver/tasks/main.yml) | 상태 디렉터리 생성·원본 저장·nmcli modify/reapply는 apply 조건. 변경 블록 rescue도 해당 블록에 한정. 후속 검증 실패의 복구 쓰기 명령도 각각 apply 조건으로 차단 |
| [roles/dns_resolver/tasks/verify.yml](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/roles/dns_resolver/tasks/verify.yml) | nmcli show·slurp·dig/getent·TCP listener 연결 확인·systemctl show·assert. resolver·서비스 구성 변경 없음 |

읽기 전용은 운영 구성에 대한 의미다. Ansible 임시 모듈 파일, 인증·감사 로그, DNS 질의 및 TCP 접속 등 실행 부수 효과까지 없다는 주장은 하지 않는다. API 6443 listener 응답은 Kubernetes backend 또는 클러스터 Ready 입증이 아니다.

## 모의시험 변수와 SSH 설명

기존 작업 파일 `pr3_review/run_review_checks.py`는 `PR3_REVIEW_MOCK=1`, `PR3_REVIEW_CASE`, `PR3_REVIEW_TRACE`, `PYTHONPATH=<mocks 경로>`를 모의시험 환경에 설정한다. `pr3_review/mocks/sitecustomize.py`는 첫 변수가 1일 때 Ansible ActionBase의 모듈 실행을 fixture 반환으로 대체한다. 이 실제 소스를 확인했다.

PR #4 수집기는 `os.environ.copy()`에서 위 네 변수를 제거하고 subprocess에 전달한다. 배포 wrapper도 같은 변수를 unset한다. 이전 로컬 모의시험의 영향을 실제 검증 자식 프로세스에 물려주지 않기 위한 처리이며, 운영 서버에 해당 변수가 존재했다거나 모의 결과가 실제 증적에 섞였다는 증거는 아니다. 이것은 해당 모의시험 경로에 대한 방어이며 모든 Python 시작 훅·플러그인 오염을 격리하는 일반 보안 경계는 아니다.

첨부 §2.3의 “에이전트 포워딩 차단”은 “인증 에이전트 사용 비활성화”로 고친다. `IdentityAgent=none`은 인증 에이전트 사용을 끄는 옵션이고, 전달 여부의 별도 설정은 `ForwardAgent`다. 이 옵션 하나로 모든 agent forwarding 설정을 검증했다고 기록하지 않는다. [OpenSSH 공식 설정 설명](https://man.openbsd.org/ssh_config#IdentityAgent), [ForwardAgent](https://man.openbsd.org/ssh_config#ForwardAgent).

## 정책 적용과 증적 상태

첨부에서 인용한 `Claude_GitHub_Canonical_and_Repository_Governance_Prompt_v1.2.md` 원문을 확인했다. §3.2·§7은 미실행을 NOT RUN, 미확인을 NOT VERIFIED로 구분한다. §9.2는 Evidence 경로가 없거나 검사할 수 없으면 실패하도록 요구한다. **구현 저장소 안에 원본을 저장하거나 GitHub Actions에서 재실행해야만 인정된다고 한정하지는 않는다.** 합의된 증적 전용 Private 저장소나 검토자가 접근해 무결성을 확인할 수 있는 인계 경로가 필요하다.

해당 문서는 정책 반영 요청이며, 이 HEAD에 그 검증 스크립트가 구현돼 실행됐다는 증거는 없다. 따라서 이번 건은 정책 기준상 증적 접근 보완이 필요한 상태이지, 실제 실행되지 않은 Governance 스크립트의 FAIL 결과를 관측한 것은 아니다. CI·정책 스크립트·템플릿 반영은 별도 변경으로 관리한다.

| 상태 | 현재 기록 |
|---|---|
| 고정 소스 무결성 | GitHub tree 대비 28/28 일치 |
| 제출 서버 결과 | 기존 기술 검토: 두 버전 합계 14/14 PASS_READONLY_SCOPE, 원격 각 단계 전체 6대 포함 |
| 네트워크 복구 후속 | 두 노드 정상 before·변경된 boot ID의 after·각 21/21, 신규 SSH는 사용자 콘솔 제출본 |
| CI | NOT RUN — 이번 확인에서도 실행 기록 0건 |
| 재환님 원본 수신·독립 검증 | PENDING / NOT VERIFIED_BY_REVIEWER |
| 첨부의 성격 | 재환님 계정이 댓글로 제출한 Claude 보조 초안. 문서 전체에서 사람 확인·최종 판정은 아직 확정되지 않음 |
| GitHub 정식 리뷰 | 조회 시 0건. 댓글 제출만으로 APPROVED 또는 정식 Changes requested로 바꾸지 않음 |
| 병합 | Open / Ready for review / 미병합. 재환님 최종 리뷰와 이권욱 병합 승인 대기 |

재환님은 인계 ZIP의 원본을 확인한 범위만 최종 리뷰에 기재하고 `APPROVED` 또는 `HOLD`, `사람 확인: CONFIRMED`를 본인 계정으로 제출하면 된다. 코드만 검토한 경우 서버 결과는 본인 관점의 미검증으로 남긴다. 최종 판단을 미리 채운 제출용 승인 문구는 제공하지 않는다.

## 원본 인계 묶음과 한계

`FDS_PR4_Review_Evidence_v1.0.zip`에는 원본 TAR 5쌍, 내용 열람용 추출본, 검토 인덱스·해시 대장, 본 답변서·기술 검토서·인계서, 제출 리뷰 원문, 모의시험 출처 설명 및 콘솔 출처 기록을 포함한다. ZIP 옆 SHA-256 sidecar와 ZIP 내부 `SHA256SUMS`로 확인할 수 있다. 원본 TAR와 기존 sidecar의 바이트는 그대로 보존한다. 다운로드 중 `(1)`이 붙었던 정상 before 자료는 ZIP 안에서 원래 이름으로 배치하고 원래 업로드 이름을 대장에 기록한다.

현재 원본 ZIP은 사용자에게 전달할 준비본이다. GitHub 원본 업로드·재환님 다운로드·수신 확인 완료로 기록하지 않는다. PR에는 답변과 준비본 식별 정보를 반영한다.

과거 `PREFLIGHT_BLOCKED_NO_CHANGE` 복구 기록은 원본 그대로이며 성공한 복구 스크립트 실행 기록으로 바꾸지 않는다. 실제 프로필 변경·IP 반환 행위자와 시각, 순차 재부팅 절차 준수는 미입증이다. 전체 apply/rollback, 운영 Ansible 버전 전환, PR #3 Gate 0, Stage A 인수 및 Bootstrap 해제는 이번 코드·증적 검토의 승인 대상이 아니다.

## 17. 구두 합의 반영 — 2026-09-08

이권욱님이 이번 대화에서 **“구두로 합의했고 리뷰 갱신”**이라고 확인하여, 재환님 리뷰 내용에 대한 구두 합의 완료를 기록합니다. 기록의 출처는 이권욱님의 전달이며, 재환님 GitHub 계정으로 제출된 리뷰와 구분합니다.

| 항목 | 현재 상태 |
|---|---|
| 대상 HEAD | `5a2c3786f6af9f107200654aa12c92c3b09700f0` |
| 리뷰 담당 | 재환님 `supreme33-kr` / REPOSITORY_ONLY |
| 구두 리뷰 합의 | **완료 — USER_ATTESTED_VERBAL_AGREEMENT** |
| 합의 확인 출처 | 이권욱님의 이번 대화 전달 |
| 재환님 GitHub 정식 리뷰 | 조회 시 0건 / 본인 계정 제출 기록 없음 |
| 기존 코드·서버 검증 | 기존 기술 검토 및 제출 증적 결과 유지 |
| 원본 증적 인계 | 준비된 ZIP과 sidecar 유지. 다운로드·개별 해시 대조 여부는 이번 구두 합의 전달에 구체적으로 명시되지 않음 |
| PR 상태 | Ready for review / Open / 미병합 |
| 최종 병합 승인 | 별도 대기 |

기존 “리뷰 내용 합의 대기”는 위 구두 합의 완료 기록으로 갱신합니다. GitHub의 APPROVED 상태와 첨부 초안의 `사람 확인: CONFIRMED`는 재환님 본인 제출 기록에 따라 관리합니다. 구두 합의의 상세 시각·개별 증적 확인 범위는 전달되지 않았으므로 새로 채우지 않습니다.

정확한 검토 HEAD는 유지했으며 운영 버전 전환, 전체 apply/rollback, PR #3 Gate 0, Stage A 인수·Bootstrap 해제 및 main 병합의 승인 범위로 확대하지 않습니다.

아래 초안 대응과 수신 이력은 **구두 합의 전의 기록**입니다. 현재 구두 합의 상태는 이 절을 따릅니다. 갱신 검토 문서: `FDS_SSH_Key_Guard_Fix_Review_v1.15.md`.

---


## 18. 재환님 정식 리뷰 수신·검토 및 GitHub 반영 — 2026-09-08


작성일: 2026-09-08  
대상: [321Team/infra-ansible PR #4](https://github.com/321Team/infra-ansible/pull/4)  
GitHub 반영: [지적별 답변](https://github.com/321Team/infra-ansible/pull/4#issuecomment-5580440870) 및 PR 본문·인계 체크리스트. 재조회에서 본문·댓글 일치, HEAD 유지, Open·미병합 확인.

**결론: 재환님 정식 리뷰 제출을 확인했으며 핵심 수정의 기술적 타당성에 동의합니다. CI와 재현 절차 보완 의견은 타당하고, 내부 API·stdout 의존은 유지보수 개선 대상으로 정리했습니다. GitHub 리뷰 상태는 COMMENTED입니다.**

## 재환님 제출 리뷰 검토 및 후속 정리 — 2026-09-08

[재환님 정식 리뷰](https://github.com/321Team/infra-ansible/pull/4#pullrequestreview-5138096865)를 현재 코드와 기존 실행 증적에 대조했습니다. 이 답변은 작성 측의 Codex 보조 검토이며 재환님 명의의 승인 리뷰를 대신하지 않습니다.

| 항목 | 확인 결과 |
|---|---|
| 리뷰어 / 시각 | supreme33-kr / 2026-09-08 15:20:30 KST |
| 검토 HEAD | `5a2c3786f6af9f107200654aa12c92c3b09700f0` — 현재 HEAD와 일치 |
| GitHub 리뷰 | **COMMENTED 1건** / APPROVED 0건 / 인라인 리뷰 댓글 0건 |
| 리뷰 본문 판정 | 핵심 SSH 수정 병합 권고, 검증 도구 분리·개선 제안 |
| CI | Actions 0건, check run 0건, commit status 항목 0건 — NOT RUN |
| 기존 서버 증적 | 고정 HEAD의 2.16.19·2.21.3 읽기 전용 검증 14/14 PASS 유지 |
| PR | Open / Ready / 미병합 |

### 지적별 검토

| 항목 | 검토 결과와 권고 |
|---|---|
| SSH 검사 결함 | **동의.** 기존 리스트 조건의 AND 단락으로 키 개수 검사가 우회될 수 있는 결함이며, 수정된 단일 OR 조건은 이를 거부합니다. 기존 조건식·실제 태스크 회귀와 서버 증적이 뒷받침합니다. |
| A. CI 미연동 | **보완 필요.** 서버가 필요 없는 키 검사 회귀를 고정 버전에서 자동 실행할 워크플로가 필요합니다. 이번 검토에서는 미구현이며, 기존 수동 시험이 없었다는 의미는 아닙니다. |
| B. Ansible 내부 API | **유지보수 우려 수용.** 공개 CLI를 통한 실제 태스크 회귀를 중심으로 구성하는 것이 적절합니다. 현재 `regression.yml` 생성도 같은 Python 스크립트에 있으므로 생성 단계를 분리한 뒤 내부 평가기 축소를 검토해야 합니다. 현재 평가 오류는 ERROR·비정상 종료로 처리되며, 조용히 PASS한 사례는 확인되지 않았습니다. |
| C. 외부 실행 준비 파일 | **재현성 보완 필요.** 배포 패키지에만 있는 wrapper·고정 requirements를 저장소에서 관리하거나 접근 가능한 고정 배포 링크·SHA와 준비 절차를 연결해야 합니다. 저장소만으로 완전 재현하기 어려운 점은 맞지만, 이미 수신한 14/14 서버 결과를 무효화하는 근거는 아닙니다. |
| D. stdout 파싱 | **형식 의존성 수용.** 호스트별 구조화 결과와 전체 성공 조건을 함께 검증하는 방향이 적절합니다. 아래 재생 시험에서는 형식 변경·누락 시 REVIEW_REQUIRED로 종료했습니다. 모든 가능한 오판을 배제한 시험은 아닙니다. |
| rc 조건 통일 | 현재 실제 grep의 rc·개수 조합에서는 수정된 두 검사가 한 개의 관리 키를 요구합니다. 표현 일관성 제안으로 분류하며 이번 검토에서 코드를 변경하지 않았습니다. |
| PR 분리 | 핵심 수정과 회귀 방지 시험을 함께 검토하는 것을 권고합니다. 검증 도구 개선은 후속 변경으로 정리할 수 있습니다. 현재 PR은 5개 파일이 한 Commit에 묶여 있으므로 현 상태에서 핵심 파일만 선택 병합할 수 없습니다. 분리하면 새 HEAD에 대한 리뷰가 필요합니다. |

### 설명상 보정

- 기존 **두 번째** 검사는 첫 조건이 `rc != 0`이므로 rc=1에서도 잘못된 `or` 식을 평가해 오류가 납니다. “rc>=2에서만 구문 오류”라는 설명은 첫 번째 검사에 한정됩니다. 기존 두 버전 음성 사례 결과에서 이를 확인했습니다.
- 수정된 OR 식도 단락 평가합니다. 두 하위 식이 매번 실행된다는 뜻이 아니라, **rc 이상 또는 개수 불일치 중 하나면 실패하도록 논리가 복구됐다**는 의미입니다.
- `--tree`는 ad-hoc `ansible` 명령의 옵션이며 현재 수집기가 사용하는 `ansible-playbook`에 그대로 붙일 수 없습니다. `set_stats`도 통계 설정 기능으로, 그 자체가 JSON 파일 출력기는 아닙니다. 구조화하려면 지원하는 callback 또는 별도 결과 직렬화와 수집 절차를 함께 설계해야 합니다. [ansible CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible.html), [ansible-playbook CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-playbook.html), [set_stats](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/set_stats_module.html).
- 버전 결론은 실제 시험한 **2.16.19·2.21.3**에 한정합니다. 향후 버전 호환성이나 운영 버전 전환 승인으로 확대하지 않습니다.

### 추가 확인: 기록 출력 재생 5/5

현재 `verify-ssh-main.py`의 원래 `run()` 함수를 사용하고 subprocess를 대체해 수신된 2.16.19 readonly SSH stdout을 재생했습니다. **실제 SSH·Ansible·서버 시험을 새로 실행한 결과가 아닙니다.**

| 재생 입력 | 관측 판정 |
|---|---|
| 기존 원본 stdout, rc=0 | PASS |
| verdict 표시의 공백 형식 변경 | REVIEW_REQUIRED |
| PLAY RECAP 표식 누락 | REVIEW_REQUIRED |
| 6대 중 한 호스트 recap 누락 | REVIEW_REQUIRED |
| 기존 stdout, rc=1 | REVIEW_REQUIRED |

### 현재 처리와 남은 리뷰

정식 리뷰 **제출 완료**로 PR 인계 기록을 갱신합니다. 핵심 수정의 병합 권고는 확인했으며, 검증 도구 분리 제안이 있어 전체 5개 파일에 대한 무조건 승인을 대신 기록하지 않습니다.

재환님 최종 리뷰에는 현재 5개 파일 전체를 수용하는지, 분리 후 재검토가 필요한지와 함께 APPROVED/HOLD 및 실제 확인한 코드·증적 범위를 명시해 주시면 됩니다. 가이드의 AI 사용 여부와 `사람 확인: CONFIRMED`는 실제 확인 후 본인 계정으로 기록하며, 이번 제출 본문에 없는 값을 작성 측에서 채우지 않습니다. GitHub 승인을 의도한 경우 본인 계정의 Review changes에서 **Approve**로 제출할 수 있습니다.

이번 조치는 리뷰 답변·기록 갱신입니다. CI 추가, 코드 분리·수정, main 병합은 수행하지 않았습니다. 이권욱님의 PR #4 최종 병합 승인은 별도 상태로 유지합니다.

## 기록 갱신 내역

- 기존 PR 본문의 ‘정식 리뷰 0건’을 실제 제출된 COMMENTED 1건으로 갱신했습니다.
- 기존 리뷰와 댓글은 수정하지 않았습니다. 작성 측 답변 댓글을 추가했습니다.
- PR 본문 전체 이력 재전송은 내부 운영 상세정보가 포함됐다는 사유로 자동 승인 검토에서 거절됐습니다. 이후 내부 주소·운영 상세를 제외한 코드·검증·리뷰 요약과 기존 기록 링크로 갱신했고, 정상 반영을 확인했습니다. 현재 미반영으로 남은 리뷰 갱신 작업은 없습니다.
- 상세 수신·복구·구두 합의 이력은 종합 검토 문서 v1.16에 보존했습니다. 원본 증적 ZIP과 TAR 바이트는 변경하지 않았습니다.



<details>
<summary>2026-09-08 본문 요약 전 PR 상세 이력 — 당시 상태 보존본</summary>

이 부록은 정식 리뷰 반영 전의 원문이다. 리뷰 0건·미완료 등의 현재 판단에는 사용하지 않는다. 최신 판정은 문서 상단과 18절을 따른다.

## 구두 리뷰 합의 반영 — 2026-09-08

이권욱님이 이번 대화에서 **“구두로 합의했고 리뷰 갱신”**이라고 확인하여, 재환님 리뷰 내용에 대한 구두 합의 완료를 기록합니다. 기록의 출처는 이권욱님의 전달이며, 재환님 GitHub 계정으로 제출된 리뷰와 구분합니다.

| 항목 | 현재 상태 |
|---|---|
| 대상 HEAD | `5a2c3786f6af9f107200654aa12c92c3b09700f0` |
| 리뷰 담당 | 재환님 `supreme33-kr` / REPOSITORY_ONLY |
| 구두 리뷰 합의 | **완료 — USER_ATTESTED_VERBAL_AGREEMENT** |
| 합의 확인 출처 | 이권욱님의 이번 대화 전달 |
| 재환님 GitHub 정식 리뷰 | 조회 시 0건 / 본인 계정 제출 기록 없음 |
| 기존 코드·서버 검증 | 기존 기술 검토 및 제출 증적 결과 유지 |
| 원본 증적 인계 | 준비된 ZIP과 sidecar 유지. 다운로드·개별 해시 대조 여부는 이번 구두 합의 전달에 구체적으로 명시되지 않음 |
| PR 상태 | Ready for review / Open / 미병합 |
| 최종 병합 승인 | 별도 대기 |

기존 “리뷰 내용 합의 대기”는 위 구두 합의 완료 기록으로 갱신합니다. GitHub의 APPROVED 상태와 첨부 초안의 `사람 확인: CONFIRMED`는 재환님 본인 제출 기록에 따라 관리합니다. 구두 합의의 상세 시각·개별 증적 확인 범위는 전달되지 않았으므로 새로 채우지 않습니다.

정확한 검토 HEAD는 유지했으며 운영 버전 전환, 전체 apply/rollback, PR #3 Gate 0, Stage A 인수·Bootstrap 해제 및 main 병합의 승인 범위로 확대하지 않습니다.

아래 초안 대응과 수신 이력은 **구두 합의 전의 기록**입니다. 현재 구두 합의 상태는 이 절을 따릅니다. 갱신 검토 문서: `FDS_SSH_Key_Guard_Fix_Review_v1.15.md`.

---

## 구두 합의 전 리뷰 초안 대응 — 2026-09-08

재환님이 [댓글로 제출한 PR4_review_infra-ansible.md](https://github.com/321Team/infra-ansible/pull/4#issuecomment-5578861616)를 이번에 수신해 고정 HEAD와 기존 원본에 대조했습니다. 문서는 **CLAUDE_ASSISTED 초안**이며 최종 판정과 사람 확인은 아직 확정되지 않았습니다. 작성 측 대응은 Codex 보조로 정리했습니다.

- 저장소 구분: IMPLEMENTATION_CODE.
- 작성자: GWONUK / 요청 독립 리뷰어: supreme33-kr / 역할 범위: REPOSITORY_ONLY.
- 검토 HEAD: `5a2c3786f6af9f107200654aa12c92c3b09700f0` — 코드 Commit 변경 없음.
- 독립 Reviewer 판정: PENDING / 사람 확인: PENDING. 첨부 제출용 예문의 CONFIRMED를 확정 승인으로 산정하지 않습니다.
- 현재 GitHub 정식 리뷰 0건, 인라인 댓글 0건. Open / Ready for review / 미병합.

### 지적별 답변

| 지적 | 확인 결과 및 대응 |
|---|---|
| 원본 증적을 리뷰어가 대조할 수 없음 | 수용. 기존 결과·해시 인계만으로는 부족했습니다. 원본 TAR 5쌍, 열람용 추출본, 콘솔 출처 기록·인덱스·체크섬을 인계 ZIP으로 준비했습니다. 재환님 수신 및 직접 확인은 대기입니다. |
| CI NOT RUN | 해당 HEAD Actions 0건, Check run 0건, status 항목 0건을 확인했습니다. 기존 수신 서버 결과 14/14 PASS_READONLY_SCOPE와 CI는 별도 상태입니다. CI 미실행을 서버 미실행으로 바꾸지 않습니다. |
| precheck·DNS verify 읽기 전용 미확인 | 고정 HEAD 28개 소스와 검토본 Git blob 28/28 일치. precheck 조회 명령을 확인했고, dns_resolver의 변경·실패 복구 쓰기 명령은 apply 조건에서만 실행됩니다. 수집기는 cr_dns_phase=verify를 전달합니다. |
| PR3_REVIEW_* 제거 사유 | 이전 로컬 PR #3 모의시험의 활성화·사례·추적 변수입니다. pr3_review/run_review_checks.py 및 mocks/sitecustomize.py의 사용을 확인했습니다. PYTHONPATH와 함께 자식 프로세스 환경에서 제거해 해당 모의시험 경로의 상속을 방지합니다. 실제 서버에 변수가 존재했거나 오염됐다는 증거는 아닙니다. |
| 원본 저장 위치 | 인용 정책 v1.2 §9.2는 접근·검사 가능한 Evidence 경로를 요구합니다. 구현 저장소 내부 저장 또는 Actions 재실행만 인정한다고 한정하지 않습니다. 증적 전용 저장소와 구현 저장소 분리 원칙을 유지합니다. |
| PR 템플릿·정책 필드 | 검토 HEAD에는 .github/pull_request_template.md와 Governance 문서·스크립트 자체가 없습니다. 별도 정책 적용 대상으로 남기며, 실제 실행되지 않은 Governance 스크립트 FAIL 결과를 관측한 것으로 쓰지 않습니다. |
| 사람 확인 예문 | 실제 사람 확인 전까지 PENDING. 재환님이 확인 범위와 APPROVED/HOLD를 본인 계정으로 제출한 뒤에만 확정합니다. |

읽기 전용 검토 근거: [precheck](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/playbooks/precheck.yml), [DNS role main](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/roles/dns_resolver/tasks/main.yml), [DNS verify](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/roles/dns_resolver/tasks/verify.yml), [수집기](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/scripts/verify-ssh-main.py).
이는 원격 구성의 읽기 전용 범위이며 임시 파일·인증 로그·DNS 질의·TCP 접속 등 실행 부수 효과까지 없다는 뜻은 아닙니다.

첨부의 IdentityAgent 설명은 “인증 에이전트 사용 비활성화”로 보정합니다. `IdentityAgent=none`과 `ForwardAgent`는 별도 설정이므로 해당 옵션 하나로 모든 agent forwarding을 검증했다고 기록하지 않습니다. [OpenSSH 공식 설명](https://man.openbsd.org/ssh_config#IdentityAgent).

### 인계 준비본

- `FDS_PR4_Review_Evidence_v1.0.zip`: 151,669 bytes, 83개 파일, 내부 SHA256SUMS 82개 일치.
- ZIP SHA-256: `7067291df4b5a26741ba45797fded205099fec9fce5d11c016982f3a5d93b308`.
- 원본 TAR 5개와 sidecar는 바이트 보존. 정상 before/after의 baseline도 바이트 일치.
- 상세 답변서 `FDS_PR4_Review_Response_v1.0.md`, 기술 검토 v1.14, 재환님 인계 v1.1 포함.
- 원본 ZIP은 사용자에게 전달할 준비본이며 **이 PR에 ZIP을 업로드하거나 재환님 수신을 확인한 것은 아닙니다.** 위 이름·해시는 다운로드 링크가 아닙니다.
- 재환님이 원본을 확인한 범위만 최종 리뷰에 기재합니다. 첨부에서 지적한 독립 검증 대기는 ZIP 준비만으로 자동 해소하지 않습니다.

기존 수신 결과의 기술 검토를 유지하며 추가 서버 시험은 실행하지 않았습니다. 실제 변경·주소 반환 경위, 순차 재부팅 절차 준수, 전체 apply/rollback, 운영 버전 전환, PR #3 Gate 0, Stage A 인수·Bootstrap 해제는 별도 범위입니다. 재환님 최종 리뷰 및 이권욱 병합 승인 대기입니다.

---

## 리뷰 담당 및 인계 — 재환님

사용자 요청으로 하영님 부재 기간의 PR #4 리뷰 담당을 재환님(`supreme33-kr`)으로 조정했습니다. 재환님의 이 저장소 Write 권한을 확인했고, PR을 Ready for review로 전환해 정식 리뷰를 요청했습니다. **리뷰 요청 상태이며 기술 승인·최종 병합 승인을 대신하지 않습니다.**

- 검토 대상 HEAD: `5a2c3786f6af9f107200654aa12c92c3b09700f0`.
- 대상 PR: [infra-ansible #4](https://github.com/321Team/infra-ansible/pull/4), base main `4f9bdb7c08704eebb3d1b294751e51b0721b6af4`.
- 리뷰어: `supreme33-kr`; 최종 병합 승인: 이권욱 별도 확인.
- 최초 조회 시 requested reviewers는 비어 있었습니다. 기존 제출 리뷰를 삭제·무효화한 조치가 아닙니다.

### 재환님 검토 순서

1. [Files changed](https://github.com/321Team/infra-ansible/pull/4/files)에서 변경 5개 파일을 검토합니다. 핵심은 SSH 키 검사 `failed_when`의 단일 OR 수정이 누락·중복을 거부하는지, 기존 관리 키 경로·제한 옵션·교체 동작을 유지하는지입니다.
2. 원본 조건식/태스크 회귀, 신규 SSH·sudo·키 개수·파일 불변 검증 및 수집기의 판정 범위를 확인합니다.
3. 아래 증적 기술 검토에서 두 Ansible 버전의 14/14, 각 원격 단계 6대 모두 포함, control01·02 재부팅 후 21/21 및 신규 SSH 확인을 대조합니다.
4. `hardening --check` 생략과 localhost의 예상 음성 사례 rescued=10을 실제 실패로 혼동하지 않고, 전체 apply·rollback 시험으로 확대하지 않았는지 확인합니다.
5. 원본·검토 한계를 확인한 뒤 해당 HEAD에 Approve 또는 Changes requested 리뷰를 남깁니다. 리뷰 중 HEAD가 바뀌면 변경 범위를 다시 확인합니다.

### 완료 증적과 남은 항목

| 구분 | 인계 내용 |
|---|---|
| 두 버전 검증 | 2.16.19 / 2.21.3, 전체 14/14 PASS_READONLY_SCOPE; 소스 manifest 28/28 현재 HEAD 일치 |
| 6대 원격 검증 | 신규 SSH·sudo·키·파일 불변, hardening check, OS precheck, DNS verify 확인 |
| 두 Control 노드 | 정상 before·다른 boot ID의 after·각 21/21·재부팅 후 신규 SSH 완료 |
| SSH 후속 출력 출처 | 두 건 모두 사용자 콘솔 제출 증적; 별도 서버 로그·sidecar로 표현하지 않음 |
| 과거 복구 기록 | PREFLIGHT_BLOCKED_NO_CHANGE 원본 보존; 현재 정상 상태와 변경 경위 입증을 구분 |
| 남은 이력 | 실제 변경·주소 반환 경위 보완; 순차 재부팅 절차 준수는 입증하지 않음 |
| 별도 범위 | INJECT_FACTS_AS_VARS 후속 정리, 시스템 버전 전환, 모든 apply/rollback, Stage A 인수·Bootstrap 해제 |

원본 식별 SHA-256:

- 두 버전 실행 결과 TAR: `d764cb22c0f83b401a3fe889b0c8ed32ff07fc6b72615e122e7946b91698a7dc`.
- control01 after TAR: `fba378d54059367bf532626d0a6b6f77b1e175544794edc8e2da4fd0e1bc8274`.
- control02 after TAR: `3196b74699f073fae22d4a67fffee5b02a26dbb664e05f9c475c044c58f4caf9`.

이 PR 본문에는 검토 결과와 식별 해시가 있으며 수신 TAR 원본을 GitHub에 새로 업로드한 것은 아닙니다. 원본 확인이 필요한 경우 기존 제출 자료와 해시를 대조합니다. 별도 배포 문서: FDS_PR4_Reviewer_Handoff_supreme33-kr_v1.1.md, 검토 문서 v1.14, 완료 Runbook v1.7.

## 변경 이유

main의 SSH 관리 키 검증이 `failed_when` 목록의 두 번째 항목을 `or ...`로 작성해, 키 누락·중복을 놓치거나 조건식 평가 오류를 일으킵니다. 기존 2.16.19와 2.21.3에서 같은 결함을 확인했습니다.

## 변경 내용

- `harden_svc_ansible_key.yml`의 최초·최종 검사를 각각 단일 OR 표현식으로 수정합니다.
- 원본 검사 태스크를 읽는 14개 fixture 회귀 시험과 localhost 태스크 재현을 추가합니다.
- 실제 6대 노드의 신규 SSH 연결·sudo·키 개수·제한 옵션·파일 불변 여부를 확인하는 읽기 전용 검증을 추가합니다.
- 두 버전에서 hardening `--check`, 기존 main의 OS precheck·DNS verify 결과를 수집하고 전체 6대 recap을 확인합니다.

키 경로·`from="10.250.10.10",restrict` 옵션·백업 및 교체 로직은 기존과 같습니다. PR #3 변경은 포함하지 않습니다.

## 검증 — 2026-09-08 최신 수신 결과

### 현재 종결 판정 — control01·02 재부팅 후 유지·신규 SSH 확인 PASS

control02에 대한 ansible01 신규 SSH 콘솔 출력 `k8s-control02`을 추가 수신했습니다. 앞서 완료한 control01 결과와 각 정상 before·after 원본을 연결해 **두 노드의 정의된 재부팅 후 로컬 상태 유지·신규 SSH 확인을 완료**했습니다.

| 항목 | control01 | control02 |
|---|---|---|
| 정상 before 및 after에 포함된 기준 원본 일치 | PASS | PASS |
| 실제 boot ID 변경 | 확인 | 확인 |
| after 로컬 상태 | 21/21 PASS | 21/21 PASS |
| 재부팅 후 ansible01 신규 SSH | k8s-control01 — 콘솔 제출 | k8s-control02 — 콘솔 제출 |
| 유지·원격 접속 기술 검증 | PASS / 완료 | PASS / 완료 |

이번 control02 콘솔은 `server01_ansible@ansible01`에서 기존 `p1_ansible_ed25519` 키로 `svc_ansible@10.1.93.103 hostnamectl --static`을 실행한 내용입니다. publickey 인증 지정, PasswordAuthentication=no, KbdInteractiveAuthentication=no, StrictHostKeyChecking=yes, 기존 known_hosts, IdentitiesOnly=yes, IdentityAgent=none 및 ControlMaster/ControlPersist/ControlPath 비활성 옵션을 포함합니다. 출력은 기대 호스트명과 일치합니다.

SSH 증적은 사용자 대화 콘솔이며 별도 서버 로그 파일·sidecar·명시적 실행 시각·종료 코드가 첨부되거나 검토자가 현장에 독립 접속한 결과로 기록하지 않습니다. control02 after 검토 및 신규 SSH 요청 이후 제출된 결과로 연결했습니다.

after 보고서의 POST_REBOOT_LOCAL_PASS_REMOTE_PENDING 문자열은 보존하고 별도 콘솔 검토로 원격 확인 항목을 완료했습니다. 기존 두 Ansible 버전 14/14 읽기 전용 검증도 유지합니다. 이번 검증을 끝내기 위한 재부팅·before·after·SSH 반복 제출은 필요하지 않습니다.

남은 별도 항목은 실제 변경·주소 반환 경위 보완과 사람 리뷰·최종 병합 승인입니다. 현재 PR은 Ready for review/Open/미병합이며 재환님에게 리뷰를 요청했습니다. 사람 리뷰 결과와 최종 병합 승인은 대기입니다. 순차 재부팅 절차의 준수 여부는 아래 시각 해석 한계와 별도로 관리하며, 노드별 기술 PASS로 이를 함께 입증하지 않습니다. 시스템 Ansible 전환·모든 apply/rollback 경로·Stage A 인수·Bootstrap 해제로 확대하지 않습니다.

완료 검토 문서 v1.12와 Runbook v1.6을 대화에서 배포합니다. **아래는 단계별 수신 이력이며 당시의 재수집·신규 SSH 대기 표시는 이 종결 판정과 구분합니다.**



**증적 기술 검토: PASS_READONLY_SCOPE. Control01·02의 기대 IP를 통한 SSH 접속, 현재 K8s 프로필·Management 반환 경로·DNS 복구 및 두 Ansible 버전의 전체 6대 읽기 전용 검증을 확인했습니다.**

- 검토 대상: `5a2c3786f6af9f107200654aa12c92c3b09700f0` — 현재 PR HEAD와 일치.
- 수신 결과: `FDS_SSH_Main_Verification_Result.tar.gz` / SHA-256 `d764cb22c0f83b401a3fe889b0c8ed32ff07fc6b72615e122e7946b91698a7dc`, 첨부 sidecar 일치.
- 내부 파일 43개 확인. SOURCE_MANIFEST·INPUT_SHA256SUMS가 배포본과 바이트 일치하며 체크섬 42개 및 manifest 소스 28개의 Git blob SHA를 현재 PR tree와 대조했습니다.
- 실행 시작: 2026-09-08 10:25:44 KST. wrapper 종료 코드 0, 전체 14/14 단계 PASS.
- 이는 수신 로그 검토이며 이 환경에서 현장 서버를 독립적으로 재실행한 결과는 아닙니다. 결과 원본은 대화 첨부로 수신했으며, 이 본문에는 검토 결과와 식별 해시를 기록합니다.

| 검증 항목 | 2.16.19 | 2.21.3 |
|---|---|---|
| 엔진 버전 | PASS | PASS |
| 원본 조건식 회귀 | 14/14 PASS | 14/14 PASS |
| localhost 원본 태스크 회귀 | 14/14 PASS | 14/14 PASS |
| 신규 SSH·sudo·키·파일 불변 | 6/6 PASS | 6/6 PASS |
| hardening --check | 6/6 PASS, changed=0 | 6/6 PASS, changed=0 |
| OS precheck | 6/6 PASS, changed=0 | 6/6 PASS, changed=0 |
| DNS verify | 6/6 PASS, changed=0 | 6/6 PASS, changed=0 |

전체 원격 recap은 각 단계에서 6대를 모두 포함하며 changed/unreachable/failed/rescued/ignored=0입니다. 각 버전의 SSH_READONLY_PASS는 6건이며 관리 키 1개·제한 키 1개, sudo root 및 authorized_keys 검증 전후 불변이 확인됐습니다.

localhost recap의 rescued=10은 예상한 음성 사례의 거부 검증입니다. hardening check의 마지막 키 검사 1건/노드 생략은 check mode 동작이며, 해당 검사는 별도 readonly SSH 단계에서 실제 실행되어 통과했습니다. DNS verify의 생략 5건/노드는 구성 적용·롤백 준비 등 apply 전용 태스크입니다. 실제 구성 적용이나 apply 후 멱등성 시험으로 확대 해석하지 않습니다.

### 현재 복구 확인

| 노드 | 접속 IP·확인 호스트명 | 활성 프로필명 | 실제 Management 반환 경로 |
|---|---|---|---|
| control01 | 10.1.93.102 / k8s-control01 | fds-k8s-control01 | 10.250.10.10 via 10.1.93.58 dev ens160 src 10.1.93.102 |
| control02 | 10.1.93.103 / k8s-control02 | fds-k8s-control02 | 10.250.10.10 via 10.1.93.58 dev ens160 src 10.1.93.103 |

두 노드 모두 DNS 10.1.93.52·10.1.93.53, search fds.internal, ignore-auto-dns=yes 및 resolver 검사가 통과했습니다. 6대의 내부 FQDN·짧은 이름·외부 이름 확인, 승인 DNS 2대 직접 질의와 API LB Listener 연결도 통과했습니다. 이는 Kubernetes Backend/클러스터 Ready 판정이나 Bootstrap 해제를 뜻하지 않습니다.

사용자는 IP 반환 확인 후 재검증 결과를 제출했습니다. 기존 TCP 22 장애는 이번 실행 시점에 해소된 것으로 판단합니다. 추가 followup before 수신본에서 활성 UUID와 현재 자동 연결 정책까지 정상임을 확인했습니다. 포함된 과거 복구 TAR 두 쌍은 모두 적용 전 중단 기록이며 백업이 없어 복구 적용 성공 이력으로 판정하지 않습니다. 주소 반환·실제 변경 경위와 재부팅 후 유지 증적은 별도입니다.

### 호환성 관찰 사항

2.21.3의 OS precheck·DNS verify에는 `INJECT_FACTS_AS_VARS` 폐기 예고 경고가 있습니다. 실행은 통과했고 이번 2.21.3 범위의 차단 결함으로 판정하지 않습니다. 후속 정리는 `ansible_hostname`, `ansible_distribution`, `ansible_default_ipv4` 등의 참조를 `ansible_facts` 경로로 전환하는 것입니다. 제거 예정 버전 2.24는 수신 로그의 안내이며 그 버전에서 별도 시험한 결과는 아닙니다. [Ansible facts 공식 설명](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)

이번 호환성 PASS는 수정된 검토 Commit의 실행한 검증 범위에 한정합니다. 시스템 Ansible 버전 전환, 모든 Playbook의 apply·rollback 호환성, PR #3 변경의 적합성을 함께 승인하지 않습니다.

### control02 재부팅 후 로컬 유지 확인 완료 — 2026-09-08

**control02 after 원본은 POST_REBOOT_LOCAL_PASS_REMOTE_PENDING, 로컬 21/21 PASS입니다.** 해당 원본 수신 이후 신규 관리 키 SSH 콘솔도 확인해 현재 두 노드의 로컬 유지·신규 SSH 검증을 완료했습니다.

| 항목 | control02 수신 결과 |
|---|---|
| after 수집 시각(KST) | 2026-09-08 12:10:57 |
| before boot ID | be231668-eccd-4f15-9956-45a8a4125014 |
| after boot ID | 84596ca2-4386-4ebc-bfca-5d90643f4eed |
| 상태 검사 / 읽기 명령 | 21/21 PASS / 30개 모두 rc=0 |
| after TAR SHA-256 | `3196b74699f073fae22d4a67fffee5b02a26dbb664e05f9c475c044c58f4caf9` |
| after JSON SHA-256 | `ffe953cbe2c06be8c0df31d6674074e8d11e1edf6753626c3590ebfe3d0e5324` |
| 포함된 before JSON SHA-256 | `7cacec34be8da9713649360d714780b4fc22d3635c2ccfcd67ada8a9e845fb71` |

TAR·sidecar, 내부 after·before JSON 쌍 및 복구 TAR 쌍의 무결성을 확인했습니다. 내부 일반 파일 6개는 기대 경로와 일치하며, baseline-before 두 파일은 앞서 수신한 0een9osv 정상 기준과 바이트가 같습니다. 배포본·before·after 수집기 SHA 일치, 같은 호스트·정상 기준, 이후 시각과 다른 boot ID를 재검증했습니다.

raw 명령 출력과 활성 UUID·주소·MAC·경로·runtime DNS를 대조했습니다. 기대 Ethernet 프로필 및 자동 연결 정책, IP·GW·Management 반환 경로·DNS·search가 유지됐습니다. 차이는 boot ID·uptime 및 lo 프로필 UUID이며, Ethernet 두 프로필의 수집 값은 같습니다. lo는 type=loopback/interface=lo로 ens160 경쟁 프로필이 아닙니다. 해당 UUID 변경 원인은 단정하지 않습니다.

포함된 과거 복구 TAR는 기존 ARP 적용 전 중단 원본과 바이트가 같습니다. RECOVERY_RECEIPT의 REVIEW_REQUIRED는 별도 이력 표시이며 이번 로컬 유지 PASS를 취소하지 않습니다.

수집 시각에서 uptime을 단순 차감한 부팅 시작 추정은 control01 약 11:55:53, control02 약 11:56:14 KST입니다. 수집 시점 차이와 벽시계 보정 가능성이 있어 정확한 명령 시각으로 확정하지 않습니다. 자료 제출 순서만으로 control01 검증 완료 후 control02를 재부팅하는 순차 절차를 준수했다고 기록하지 않으며, 노드별 상태 유지 PASS와 구분합니다.

**해당 단계 완료:** control02 신규 관리 키 SSH 콘솔의 `k8s-control02` 일치를 확인했습니다. 최신 완료 기록은 위 종결 판정과 Runbook v1.6·검토 문서 v1.12를 따릅니다.

### control01 재부팅 후 로컬 유지 확인 완료 — 2026-09-08

**control01 재부팅 후 로컬 유지·원격 접속 확인 PASS.** 정상 before, 실제 다른 부팅 ID의 after 21/21에 이어 ansible01의 신규 관리 키 SSH 출력 `k8s-control01`을 사용자 콘솔 제출본으로 확인했습니다. after 원본의 POST_REBOOT_LOCAL_PASS_REMOTE_PENDING 문자열은 보존하고 원격 확인 항목을 이 별도 검토로 완료합니다. control02도 최신 after 원본에서 로컬 유지 PASS를 확인했으며 신규 SSH만 대기입니다.

| 항목 | control01 수신 결과 |
|---|---|
| after 실행 시각(KST) | 2026-09-08 11:58:10 |
| before boot ID | 7d3b2a48-a645-49ad-9429-d8c18bb5caaa |
| after boot ID | bfa5774a-4df9-448e-adb8-e6cf17984a71 |
| 상태 검사 | 21/21 PASS, 기록된 읽기 명령 30개 모두 rc=0 |
| after TAR SHA-256 | `fba378d54059367bf532626d0a6b6f77b1e175544794edc8e2da4fd0e1bc8274` |
| after JSON SHA-256 | `47c7fd09e70696b29c431c9c518515db7920d05582db1419ea11b48ac2aac9f2` |
| 포함된 before JSON SHA-256 | `c2292626b86aaceaee20bb79838e9c28e7a5bad9a1ce4593641cf05b1edfe7e7` |

TAR·sidecar, 내부 after·before JSON 쌍 및 복구 TAR 쌍의 무결성을 확인했습니다. 내부 일반 파일 6개는 기대 경로와 일치하며, 포함된 before JSON·sidecar는 앞서 수신한 rfas2d1m 정상 기준과 바이트가 같습니다. 배포본·before·after 수집기 SHA도 같고, 기준 이후 시각과 실제 boot ID 변경을 재검증했습니다.

raw 명령 출력과 보고서의 활성 UUID·주소·MAC·경로·runtime DNS를 대조했습니다. 기대 Ethernet 프로필 및 자동 연결 정책, IP·GW·Management 반환 경로·DNS·search가 유지됐습니다. 관찰된 차이는 boot ID·uptime 및 lo 프로필 UUID입니다. lo는 loopback이며 ens160 경쟁 Ethernet 프로필에 해당하지 않습니다. 해당 UUID 변경 원인까지 단정하지 않습니다.

포함된 과거 복구 TAR는 기존 적용 전 중단 원본과 바이트가 같습니다. RECOVERY_RECEIPT의 REVIEW_REQUIRED는 별도 복구 이력의 상태이며 이번 로컬 유지 PASS를 취소하지 않습니다.

### control01 신규 SSH 콘솔 수신 및 다음 단계

사용자가 `server01_ansible@ansible01`에서 기존 `p1_ansible_ed25519` 키로 `svc_ansible@10.1.93.102 hostnamectl --static`을 실행한 콘솔을 제출했고, 출력은 `k8s-control01`입니다. 명령은 publickey 인증, PasswordAuthentication=no, KbdInteractiveAuthentication=no, StrictHostKeyChecking=yes, 기존 known_hosts, IdentitiesOnly=yes, IdentityAgent=none 및 ControlMaster/ControlPersist/ControlPath 비활성 옵션을 포함합니다.

이번 SSH 증적은 대화의 콘솔 제출본입니다. 별도 서버 파일·sidecar·실행 시각·종료 코드가 첨부되거나 검토자가 현장에 독립 접속한 결과로 기록하지 않습니다. after 원본 검토와 신규 SSH 요청 이후 제출된 결과로 연결했습니다.

**control01의 정의된 재부팅 후 유지 검증은 완료했습니다.** 다음은 control02의 VMware 콘솔 재부팅, 기존 정상 baseline `/home/server03/FDS_Control_Followup.0een9osv/STATE_REPORT.json`을 이용한 after 수집, ansible01 신규 SSH입니다. control01 절차는 반복하지 않습니다. Runbook v1.4와 검토 문서 v1.10을 대화에서 배포합니다.

### 수정 수집기 실제 서버 before 원본 수신 완료 — 2026-09-08

**두 노드 모두 PRE_REBOOT_STATE_PASS, 21/21 PASS입니다.** 수정본을 실제 서버에서 재실행한 새 원본을 수신했으며, 이전 원본의 오프라인 재해석 결과와 구분합니다. 검토 환경에서 현장 명령을 독립 실행한 것은 아닙니다.

| 항목 | control01 | control02 |
|---|---|---|
| 수집 시각(KST) | 2026-09-08 11:44:48 | 2026-09-08 11:45:27 |
| 보고 상태 / 재평가 | PRE_REBOOT_STATE_PASS / 21/21 | 동일 |
| 기록된 읽기 명령 | 30개, 모두 rc=0 | 동일 |
| 새 baseline 디렉터리 | /home/server02/FDS_Control_Followup.rfas2d1m | /home/server03/FDS_Control_Followup.0een9osv |

각 디렉터리의 `STATE_REPORT.json`과 인접 `.sha256`을 재부팅 후 비교 기준으로 사용합니다. 경로는 사용자가 제출한 실행 콘솔과 연결하며 내용은 아래 해시로 식별합니다.

- control01 TAR SHA-256: `964f6fa047b2b6249e0d4f6645f0a352891667d81cbb7969c996f91665ef11de`.
- control02 TAR SHA-256: `48b03ce7d06ec953f641810c170b2e70a33c5d7f4d371eecf01128c73e1ddced`.
- control01 기준 JSON SHA-256: `c2292626b86aaceaee20bb79838e9c28e7a5bad9a1ce4593641cf05b1edfe7e7`.
- control02 기준 JSON SHA-256: `7cacec34be8da9713649360d714780b4fc22d3635c2ccfcd67ada8a9e845fb71`.
- 두 보고서의 수집기 SHA는 배포 수정본 `cf37a6d6a585123de9006cc680a13f1a5932076c3b967f69f3b4f07b23d3625d`와 일치합니다.

업로드 파일명에 붙은 `(1)`을 원래 sidecar 파일명과 대응해 실제 바이트 SHA-256을 확인했습니다. TAR·sidecar, 내부 상태 JSON·sidecar 및 포함된 복구 TAR·sidecar가 모두 일치하며, 각 묶음은 기대한 일반 파일 4개를 포함합니다. raw 명령 출력과 보고된 프로필·UUID·주소·MAC·경로·runtime DNS를 대조했습니다. resolver와 부팅 ID는 수집 보고서의 직접 읽기 필드에 근거합니다.

runtime DNS의 원시 출력은 이전과 같은 파이프 구분 형식이며 새 수집기가 두 주소로 올바르게 해석했습니다. uptime과 DNS 해석 표현을 제외한 상태는 이전 before와 일치하고 부팅 ID도 같습니다. 따라서 **정상 before 기준 확보는 완료, 재부팅 후 유지 확인은 아직 미검증**입니다.

포함된 복구 TAR 두 쌍은 앞서 수신한 적용 전 중단 원본과 바이트가 같습니다. `RECOVERY_RECEIPT=LATEST_VALID_PAIR_INCLUDED_REVIEW_REQUIRED`는 이 별도 이력의 검토 상태이며 현재 PRE_REBOOT_STATE_PASS를 취소하지 않습니다. 성공 이력을 만들기 위한 복구기 재적용은 요구하지 않습니다.

다음 단계는 점검 시점에 control01부터 한 노드씩 재부팅하고, 같은 수정본의 `--phase after --baseline ...` 및 ansible01 신규 SSH로 유지 여부를 확인하는 것입니다. control01 확인 후 control02를 진행합니다. 노드별 명령은 대화에서 배포하는 Runbook v1.2에 확정 경로로 제공합니다. before 이후 설정이 바뀌지 않았다면 before 재수집이나 기존 14/14 전체 Ansible 검증 반복은 필요하지 않습니다.

### 이전 before 수신·수집기 오류 수정 이력 — 2026-09-08

아래는 첫 수신본과 수정 당시 검토입니다. 당시의 before 재수집 항목은 위 새 원본 수신으로 완료했습니다.

**두 노드의 서버 DNS는 정상입니다. 기존 수집기가 nmcli의 파이프 구분자를 주소 항목으로 처리해 runtime_dns에서 거짓 실패를 냈습니다.** 수신 원본의 REVIEW_REQUIRED는 그대로 보존하고, 원시 출력의 수정 해석 결과를 별도 기록합니다.

| 항목 | control01 | control02 |
|---|---|---|
| before 수집 시각(KST) | 2026-09-08 11:27:18 | 2026-09-08 11:28:16 |
| 원본 검사 | 20/21, runtime_dns 실패 | 동일 |
| 실제 runtime DNS 출력 | `10.1.93.52 \| 10.1.93.53` | 동일 |
| 수정 파서로 수신 출력 재해석 | 21/21 일치 | 21/21 일치 |
| 활성 UUID | 2403bbcc-41f3-4439-81f7-4a3b6a3f582e | 8914aee6-bdb7-4d97-a0ae-0640143ff9c5 |
| K8s / 남아 있는 ens160 자동 연결 | yes / no | yes / no |

control01의 이전 VPN·DNS UUID는 현재 등록 목록에 없으며 두 노드의 lo 프로필은 정상적으로 제외됩니다. 현재 상태를 확인한 결과이며 변경·삭제 행위자와 시각을 입증하지는 않습니다. 저장 DNS·resolver DNS·search, 주소·MAC·반환 경로는 원본 검사에서도 통과했습니다.

수신 TAR·sidecar, 내부 STATE_REPORT·sidecar, 포함된 복구 TAR·sidecar 무결성을 모두 확인했습니다.
- `FDS_Control_Followup_k8s-control01_before.tar.gz`: SHA-256 `5401d68a8213da7cf2a59b035ced15c8072e48a063b64696decb52a6cf0c6120`.
- `FDS_Control_Followup_k8s-control02_before.tar.gz`: SHA-256 `0193a39e44c184649ce7aa0ee5cf9287c353a9e62eb24b4ad2225a2a496d7627`.

선택된 복구 원본의 실제 상태:
- control01: 2026-09-08 10:22:42 KST, `PREFLIGHT_BLOCKED_NO_CHANGE`, `An expected profile is missing`. 당시에도 기대 K8s UUID는 이미 활성입니다. 원본 SHA-256 `f984dfeafa3293344cfbbaff1b42100e77fe69f8657f68763aaf41412487337a`.
- control02: 2026-09-07 20:13:28 KST, `PREFLIGHT_BLOCKED_NO_CHANGE`, .103 ARP 응답으로 적용 전 중단. 원본 SHA-256 `ce5ae4cb2066a1f0bc993a166ce65d058b06258f5e209a91c655489bd6e1f877`.
- 두 원본 모두 AUTOCONNECT_BACKUP과 변경 명령이 없습니다. 원본 수신은 완료했지만 복구 성공 이력으로 바꾸지 않습니다. 성공 로그 생성을 위해 정상 연결에 복구기를 재적용하지 않습니다.

수집기 수정 및 검증:
- `collect-control-recovery-followup.py`의 runtime DNS 전용 파서는 파이프·쉼표·공백을 처리하고 모든 항목을 IPv4 주소로 검증합니다. DNS 순서·개수 검사를 유지합니다.
- 수정 SHA-256: `cf37a6d6a585123de9006cc680a13f1a5932076c3b967f69f3b4f07b23d3625d`. 이전 SHA `1b9422a9b19946b47890162b2c00e25927a300c7a470b5898fb4e537a9990634`는 실패 수신본의 식별 정보로 보존합니다.
- 수정 회귀 시험 7건 PASS: 수신한 두 노드 출력 재현, DNS 구분 형식, 누락·역순·추가·중복 거부, 잘못된 토큰 거부, 실패/구버전 baseline 거부, 두 노드 before/after 모의 실행·동일 boot ID 거부·복구 원본/기준 바이트 보존, 오류 시 결과 묶음 생성.
- 모의 시험은 수신 명령 출력을 재생한 결과이며 수정본의 현장 실행 PASS가 아닙니다. 원본 상태를 재해석한 21/21과 현장 재실행 결과를 구분합니다.
- 대화에서 수정 수집기·CONTROL_FOLLOWUP_SHA256SUMS와 Runbook v1.1을 배포합니다. 이번 검증 Commit의 소스는 변경하지 않습니다.
- 수정본의 `--phase before` 재수집은 위 최신 수신으로 완료했습니다. 이전 ng1esxrg·r42dw8wy의 실패 기준은 사용하지 않고 새 rfas2d1m·0een9osv의 정상 기준을 사용합니다.
- 이후 계획된 점검 시 한 노드씩 재부팅하고 같은 수정본의 after·ansible01 신규 SSH로 유지 여부를 확인합니다. 수집기는 구성 변경·복구 적용·재부팅을 실행하지 않습니다. 이미 통과한 두 버전 14/14 검증은 유지합니다.

## 2026-09-07 진단 이력

아래는 장애 당시 기록입니다. 당시의 UNREACHABLE·잘못된 활성 프로필·ARP 적용 전 중단은 현재 상태 판정이 아니며, 최신 결과는 위 2026-09-08 검토를 따릅니다. 변경 전 조건식은 두 엔진에서 각각 4 PASS / 5 FAIL / 5 ERROR였고 수정 후 14/14 PASS로 바뀌었습니다.

### 2026-09-07 서버 실행 증적 수신

수신 파일: `FDS_SSH_Main_Verification_Result.tar.gz` 및 SHA-256 sidecar.
확인한 SHA-256: `52d8bf7a4fc172fa6f7602e1d64e85d5d011af9847e1e3c3d7110873c0492d28`.
수신 SOURCE_MANIFEST.json과 INPUT_SHA256SUMS는 배포 검증 패키지의 대응 파일과 바이트가 일치합니다.
이는 수신 파일의 무결성과 제출 manifest 일치 확인이며, 서버 실행 내용을 독립적으로 재실행한 증명은 아닙니다.

| 대상 | 2.16.19 | 2.21.3 |
|---|---|---|
| k8s-control01 | TCP 22 시간 초과 | TCP 22 시간 초과 |
| k8s-control02 | TCP 22 시간 초과 | TCP 22 시간 초과 |
| k8s-control03·worker01/02/03 | Facts 수집 성공, 전체 6대 누락 조건에서 중단 | 동일 |
| localhost 수정 태스크 회귀 | 14/14 PASS | 14/14 PASS |

### 2026-09-07 추가 연결 진단 수신

진단 묶음 `FDS_SSH_Connectivity_ansible01.tar.gz`의 SHA-256은 `b388934b6e42bb7a00c6c1108d4251589294c1f3ac54034b585bb8788bc115f9`이며 첨부 sidecar와 일치합니다. 진단기 SHA도 배포본과 일치합니다. `server02.txt`와 `server03.txt`는 사용자가 제출한 VM 콘솔 텍스트로 검토했습니다.

| 항목 | 기대 상태 | 제출된 현재 상태 |
|---|---|---|
| control01 ens160 IPv4 | 10.1.93.102/24 | 10.1.93.51/24 |
| control02 ens160 IPv4 | 10.1.93.103/24 | 10.1.93.125/24 |
| 두 노드 → 10.250.10.10 반환 경로 | via 10.1.93.58 | via 10.1.93.254 |
| 두 노드 sshd | 실행·TCP 22 리스너 | active, 0.0.0.0:22 및 [::]:22 |
| 두 노드 firewalld 활성 public zone | SSH 허용 상태 확인 | services에 ssh 포함 |
| ansible01 → control03(.104) | 비교 대상 연결 | ping 2/2 및 TCP 22 연결 성공 |

**확인된 구성 불일치는 노드 IP와 Management 반환 경로입니다.** 예상 .102/.103 주소는 제출된 두 노드 NIC에 설정돼 있지 않습니다. 반환 경로도 기존 precheck의 `via 10.1.93.58` 조건과 다릅니다. 이는 전체 경로 정상이나 모든 방화벽 계층의 무결성을 입증한 결과는 아닙니다.

### NetworkManager 프로필 추가 진단

사용자 제출 `server02_2.txt`·`server03_2.txt`에서 다음을 확인했습니다.

| 노드 | 현재 활성 프로필 | 확인된 주소/DNS 원인 | 비활성 K8s 프로필 |
|---|---|---|---|
| control01 | fds-vpn-gw01, UUID af066fb9-77e9-47f7-b86f-baa30ef1a210 | manual .51/24, DNS 8.8.8.8 | fds-k8s-control01, UUID 2403bbcc-41f3-4439-81f7-4a3b6a3f582e |
| control02 | ens160, UUID 620ccca8-1f64-3e53-b75f-b4a3b48f7319 | DHCP server .254에서 .125 할당, DNS 168.126.63.1 및 8.8.8.8 | fds-k8s-control02, UUID 8914aee6-bdb7-4d97-a0ae-0640143ff9c5 |

이는 두 노드에서 기대한 K8s 프로필이 활성화되지 않은 상태를 입증합니다. control01은 DHCP로 .51을 받은 경우가 아닙니다. control02의 DHCP 할당은 DHCP4 옵션으로 확인됐습니다. 이 프로필들이 활성화된 계기·행위자와 K8s 프로필의 이전 활성화 실패 여부는 아직 확인되지 않았습니다.

control01의 VPN·DNS·K8s 프로필은 autoconnect=yes, priority=100으로 같은 NIC에 연결돼 있습니다. control02는 K8s=100, DHCP=-999이므로 우선순위만으로 현재 DHCP 활성화 원인을 단정할 수 없습니다. NetworkManager의 autoconnect는 이미 활성인 프로필을 자동으로 교체하지 않습니다. [공식 동작 설명](https://networkmanager.dev/docs/api/latest/settings-connection.html)

앞선 콘솔 텍스트에는 두 K8s 프로필의 IPv4 상세 부분이 빠져 있었으며, 이번 복구 실행 보고서에서 기준과 일치함을 확인했습니다. 복구 스크립트는 서버에서 UUID·MAC·저장 IP·DNS·반환 경로와 ARP 중복 응답 여부를 확인하고, 기준을 만족할 때만 기존 K8s 프로필을 명시적으로 활성화합니다. 알려진 경쟁 프로필은 보존하면서 autoconnect만 끕니다. IP·DNS·라우트 값을 임의로 덮어쓰지 않으며, 기준 불일치 시 무변경 보고서를 생성합니다. 전환 또는 로컬 사후 검증 실패 시 기존 autoconnect 값과 이전 활성 프로필로 복원을 시도하고 결과를 기록합니다.

### 실제 복구 실행 결과: ARP 검사에서 적용 전 중단

두 노드 모두 `PREFLIGHT_BLOCKED_NO_CHANGE`입니다. 배포 복구기 SHA-256과 실행 보고서의 script_sha256이 일치하며, 저장 K8s 프로필의 IP·게이트웨이·반환 경로·DNS·MAC 등 9개 검사가 각각 통과했습니다.

| 대상 | ARP 응답 MAC | 기대 VM MAC | 결과 |
|---|---|---|---|
| 10.1.93.102 | F4:F1:9E:23:2D:7C | 00:0C:29:54:E2:4B | arping -D rc=1, 응답 1건 |
| 10.1.93.103 | F4:F1:9E:23:30:54 | 00:0C:29:69:D8:71 | arping -D rc=1, 응답 1건 |

명령 부재가 아니라 실제 ARP 응답을 수신해 중단됐습니다. 기록된 nmcli modify/up/down/delete 명령은 0건이며 프로필 전환·자동 연결 변경·롤백은 수행되지 않았습니다. 현재 활성 프로필은 control01=VPN용 프로필, control02=DHCP 프로필 상태입니다.

다른 MAC이 두 IP에 응답한 것은 확인했지만, 실제 주소 사용 장비인지 Proxy ARP 응답인지 및 소유 장비·스위치 포트·DHCP 배정은 아직 미확정입니다. 다음 조치는 현장 네트워크의 DHCP/ARP/MAC 테이블에서 두 IP·MAC을 조회해 주소 배정을 확인하는 것입니다. ARP 검사를 우회한 강제 전환은 수행하지 않습니다.

수신 TAR 및 sidecar의 SHA-256 일치:
- control01: `97f3ed451df7d31142f9dd580ff791a0d6b4c38fd99d9f6e6918e555e7255a25`
- control02: `0fbce2bcf2005150549a991f43b160a1d189fd7e6d5cfa6cab7fac5538cc44b9`

ARP 응답 원인을 해소한 뒤 기존 복구기를 재실행하고, 같은 Commit의 두 Ansible 버전·6대 전체 검증을 다시 수행해야 합니다.

수신본 식별 SHA-256:
- server02_2.txt: `05c5d1255b335ecf60561ae96866f26640fa08c4811312bed5e999ec8cc47c86`
- server03_2.txt: `bd5f5b4156349a7db71c851ba89410efe3bba3461195372c100c70492341e0e6`

콘솔 텍스트에는 별도 서버 sidecar가 없어 위 해시는 수신본 식별용입니다.

### 기존 기대값 복구 계획 검토

사용자의 2026-09-07 명시적 승인에 따라 이번 IP·MAC·진단 결과를 PR에 반영합니다. 앞선 자동 승인 검토 차단 건의 후속 등록이며, 실제 복구 완료나 PR 병합 승인으로 기록하지 않습니다.

판정: **기존 K8s 프로필을 재활성화하는 계획은 타당하며, .102/.103 ARP 응답 원인 해소가 실행 선행조건입니다.** 두 프로필의 저장값이 이미 기준과 일치하므로 IP·DNS·라우트를 다시 작성할 필요가 없습니다.

| 복구 항목 | 기대값 |
|---|---|
| control01 | fds-k8s-control01 / 10.1.93.102/24 |
| control02 | fds-k8s-control02 / 10.1.93.103/24 |
| 기본 게이트웨이 | 10.1.93.254 |
| Management 반환 경로 | 10.250.10.0/24 via 10.1.93.58 |
| DNS / search | 10.1.93.52, 10.1.93.53 / fds.internal |
| 자동 DNS | ipv4.ignore-auto-dns=yes |
| 자동 연결 | 각 K8s 프로필 yes, 확인된 경쟁 프로필 no |

실행 순서:
1. 네트워크 관리자가 응답 MAC의 장비·포트와 DHCP/정적 주소 배정 또는 Proxy ARP를 확인하고, 기존 두 IP를 사용할 수 있는 상태로 정리합니다.
2. VMware 콘솔에서 control01부터 기존 복구기를 실행합니다. 저장값·MAC·ARP 검사를 통과할 때만 전환하며, 로컬 IP·반환 경로·DNS와 ansible01의 해당 노드 연결을 확인합니다.
3. control01 결과 확인 후 control02에 같은 절차를 적용합니다. 한 노드가 실패하면 다음 전환을 중단하고 보고서를 검토합니다.
4. 저장된 자동 연결 설정과 실제 활성 UUID를 확인하고, 계획된 점검 시점에 노드별 재시작 후 유지 여부를 확인합니다. 재시작 검증 전에는 재부팅 후 지속성 PASS로 기록하지 않습니다.
5. 동일 검토 Commit의 기존 키트로 두 Ansible 버전·전체 6대 SSH, sudo, 키/파일 불변, hardening check, OS precheck, DNS verify를 재검증합니다.

복구 실패 시 이전 활성 프로필로 돌아가는 것은 작업 전 상태 복원입니다. 작업 전 VPN/DHCP 상태도 기준과 다르므로 이를 기대값 복구 성공으로 간주하지 않습니다. 현재 기록에는 실제 프로필 전환이 없습니다.

## 인계 상태

검토 Commit: `5a2c3786f6af9f107200654aa12c92c3b09700f0`

- [x] 코드 수정 및 로컬 검증
- [x] 두 버전 localhost 태스크 회귀 결과 수신·PASS 확인
- [x] 실제 서버 실행 결과 수신·무결성·상세 로그 대조
- [x] 두 노드 SSH 연결과 현재 프로필·반환 경로·DNS 복구 확인
- [x] 두 Ansible 버전의 실제 6대 전체 읽기 전용 검증 완료
- [x] 추가 before 원본 및 포함된 기존 복구 TAR·sidecar 수신·무결성 검증
- [x] 활성 UUID·자동 연결 정책 확인, runtime_dns 거짓 실패 원인 확인 및 수집기 수정
- [x] 수정 수집기의 실제 서버 before 재실행 원본 수신 — 두 노드 각각 21/21 PASS, 정상 기준 확보
- [ ] 실제 복구·주소 반환 조치 경위 보완 — 수신 복구 원본은 모두 적용 전 중단
- [x] control01 재부팅 후 로컬 유지 — 다른 boot ID 및 21/21 PASS, before 원본 일치
- [x] control01 재부팅 후 ansible01 신규 관리 키 SSH 확인 — 콘솔 출력 k8s-control01 일치, control01 유지 검증 완료
- [x] control02 재부팅 후 로컬 유지 — 다른 boot ID 및 21/21 PASS, before 원본 일치
- [x] control02 재부팅 후 ansible01 신규 관리 키 SSH 확인 — 콘솔 출력 k8s-control02 일치, 두 노드 유지 검증 완료
- [x] 재환님(supreme33-kr) 정식 리뷰 요청 등록 — Ready for review 전환
- [x] 재환님 리뷰 내용 구두 합의 완료 — 이권욱 사용자 확인으로 기록
- [ ] 재환님 본인 계정의 GitHub 정식 리뷰 확인
- [ ] 이권욱 최종 병합 승인

증적 기술 검토는 PASS입니다. Ready for review / Open / 미병합 상태이며 검토 대상 코드는 유지합니다. 앞서 승인된 진단 결과·리뷰 업데이트 범위에 따라 이번 수신 검토를 반영합니다.


</details>


## 19. 재검토 v2 확인 및 현재 PENDING 반영 — 2026-09-08


작성일: 2026-09-08  
대상: [321Team/infra-ansible PR #4](https://github.com/321Team/infra-ansible/pull/4)  
검토 HEAD: `5a2c3786f6af9f107200654aa12c92c3b09700f0`

**결론: 재검토 v2는 정적 검토 범위·근거 구분·이전 설명 보정을 반영했습니다. 최종 판정과 사람 확인은 명시적으로 PENDING이며 GitHub APPROVED는 없습니다.** 기존 “핵심 수정 병합 권고”만으로 승인 완료라고 해석하지 않습니다.

GitHub의 동일 Review ID 본문이 수정됐습니다. 리뷰 건수는 1건이며 신규 2차 리뷰가 별도로 제출된 것은 아닙니다. API의 최초 제출 시각 2026-09-08 15:20:30 KST는 유지되어 있고, 정확한 본문 수정 시각은 조회한 리뷰 응답으로 확인하지 못했습니다.

## 재검토 v2 확인 — 최종 판정 PENDING

현재 [재환님 리뷰](https://github.com/321Team/infra-ansible/pull/4#pullrequestreview-5138096865)의 본문이 **재검토 v2**로 수정된 것을 확인했습니다. 새 리뷰가 추가된 것이 아니라 동일 Review ID의 본문 갱신입니다. GitHub 상태는 **COMMENTED 1건 / APPROVED 0건**이고 대상 HEAD는 `5a2c3786f6af9f107200654aa12c92c3b09700f0`로 현재 코드와 일치합니다. 최초 제출 시각을 본문 수정 시각으로 해석하지 않습니다.

### 이전 답변 이후 확인된 변경

- 변경 5개 파일 전체의 **정적 검토 범위**와 제외 범위를 명시했습니다. 전체 파일의 최종 수용 승인을 의미하지는 않습니다.
- 첫 번째·두 번째 검사의 rc=1 동작 차이, `--tree`·`set_stats` 설명, 내부 평가 오류의 비정상 종료를 반영했습니다.
- AI 사용은 **CLAUDE_ASSISTED**, 최종 판정과 사람 확인은 모두 **PENDING**으로 명시했습니다.
- 서버 14/14, stdout 재생, 재부팅·신규 SSH 증적은 리뷰어 세션에 원본이 없어 **NOT VERIFIED**로 구분했습니다. 기존 작성 측의 수신 원본 검토와 리뷰어의 독립 확인 상태는 별도로 유지합니다.

### 새 관찰: hardening check의 두 번째 검사 생략

지적은 코드 및 기존 수신 로그와 일치합니다.

| 기존 수신 로그 | 2.16.19 | 2.21.3 |
|---|---|---|
| hardening_check의 두 번째 검사 | 6대 모두 skipped | 6대 모두 skipped |
| readonly_ssh의 두 번째 검사 | 6대 모두 ok | 6대 모두 ok |

`hardening --check`만으로 두 번째 검사 실행을 증명할 수 없습니다. 별도 readonly 시험은 검사 태스크를 include하여 실행했고 기존 로그에 성공 기록이 있습니다. 이번에 서버 시험을 재실행한 것은 아니며, 리뷰어의 원본 대조까지 완료했다고 처리하지 않습니다. [고정 HEAD hardening](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/playbooks/harden_svc_ansible_key.yml), [readonly 시험](https://github.com/321Team/infra-ansible/blob/5a2c3786f6af9f107200654aa12c92c3b09700f0/tests/ssh-server-readonly.yml).

`command`는 creates/removes 없이 check mode에서 실행하면 생략될 수 있으며, `check_mode: false`는 해당 태스크를 실제 실행하도록 합니다. 따라서 조회 명령과 실제 변경 태스크의 실행 범위를 함께 봐야 합니다. [command 공식 문서](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/command_module.html), [check mode 공식 문서](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html).

### 남은 정리

“항상 함께 적용”은 두 하위 식이 매번 실행된다는 뜻으로 쓰지 않고 **rc 이상 또는 개수 불일치이면 실패**로 표현하는 것이 정확합니다. 버전 판정은 시험한 2.16.19·2.21.3에 한정하며 최신 버전 여부를 승인 근거로 추가하지 않습니다.

원본 인계 ZIP·sidecar와 최신 종합 검토 문서를 리뷰어가 실제로 열람할 수 있게 전달한 후, 확인한 범위만 최종 리뷰에 기록해야 합니다. 원본 검토용 묶음은 기존 바이트를 유지합니다. CI·재현성·내부 API·구조화 출력 보완은 후속 개선 제안으로 남기며 이번에 구현하지 않았습니다.

기존 “핵심 수정 병합 권고”를 현재 최종 승인으로 사용하지 않고, **v2 최종 판정 PENDING / 사람 확인 PENDING**을 PR의 현재 상태로 반영합니다. 코드 변경·분리·병합은 수행하지 않았습니다.


## 이번 처리 결과

- [재검토 v2 확인 답변](https://github.com/321Team/infra-ansible/pull/4#issuecomment-5580680097)을 추가하고 PR 본문·인계 체크리스트를 현재 PENDING 상태에 맞게 갱신했습니다.
- 재조회에서 댓글·본문 일치, HEAD 유지, Open·미병합을 확인했습니다. 재환님 원문을 수정하거나 명의 승인을 대신하지 않았습니다.
- 기존 검증 세부정보를 포함한 전체 본문 갱신은 자동 승인 검토에서 내부 정보 전송 사유로 거절됐습니다. 이후 리뷰 메타정보·상태와 기존 기록 링크만 담은 본문으로 갱신했고 정상 반영됐습니다. 요청한 리뷰 갱신 중 미반영 항목은 없습니다.
- 종합 검토 문서는 v1.17로 갱신하며 기존 수신·기술 검토 이력을 보존합니다. CI·코드 변경·운영 조치는 하지 않았습니다.

## 리뷰어에게 전달할 자료와 순서

1. 기존 `FDS_PR4_Review_Evidence_v1.0.zip`, 같은 이름의 `.sha256`, 최신 `FDS_SSH_Key_Guard_Fix_Review_v1.17.md`와 이 문서를 실제 리뷰어의 작업 환경에 전달합니다. 본문에 파일 이름·해시를 적은 것만으로는 파일 접근이 제공되지 않습니다.
2. ZIP sidecar와 내부 `SHA256SUMS`를 대조하고 `EVIDENCE_INDEX.json`, `SOURCE_REVIEW_INDEX.json`에서 원본·소스 고정 참조를 확인합니다.
3. `extracted/ssh-main/results/`의 `VERIFICATION_REPORT.json`, 두 버전의 `*_hardening_check.txt`와 `*_readonly_ssh.txt`를 대조합니다. 후속 control 노드 증적과 콘솔 제출본의 출처도 구분합니다.
4. 실제 읽고 검증한 범위만 리뷰에 기록하고, 5개 파일 전체 수용 또는 분리·보완 필요 여부를 결정합니다. 사람이 확인한 후 사람 확인 필드와 최종 판정을 갱신합니다.

ZIP SHA-256: `7067291df4b5a26741ba45797fded205099fec9fce5d11c016982f3a5d93b308`. 이번에도 기존 ZIP·sidecar 일치를 확인했으며 바이트는 변경하지 않았습니다. ZIP에 포함된 과거 검토 문서는 당시 버전이므로 최신 상태는 별도 배포하는 v1.17 및 이 문서를 따릅니다. ZIP을 서버 증적 전용 저장소에 새로 업로드하거나 리뷰어 다운로드를 확인한 것은 아닙니다.

## 해석상 주의

- `PENDING`은 승인도 변경 요청 확정도 아닙니다. 현 상태에서 재환님의 최종 판단을 대신하지 않습니다.
- 리뷰어의 `NOT VERIFIED`는 해당 리뷰 환경에서 원본을 확인하지 못했다는 뜻입니다. 작성 측이 이미 수신·검토한 서버 결과를 실패로 바꾸는 것은 아닙니다.
- 새 관찰은 hardening check 단계의 한계를 구체화합니다. 별도 readonly 단계의 실행 기록과 함께 평가하며, 전체 apply·rollback 또는 새로운 서버 시험으로 확대하지 않습니다.
- 최신 버전이라는 표현은 이번 판정의 근거로 사용하지 않습니다. 호환성 범위는 수신 증적에 명시된 고정 버전에 한정합니다.

