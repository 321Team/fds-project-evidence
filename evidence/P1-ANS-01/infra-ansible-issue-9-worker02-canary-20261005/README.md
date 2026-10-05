# Issue #9 — worker02 2.21.3 canary 수신 검토

책임: [infra-ansible #9](https://github.com/321Team/infra-ansible/issues/9), 상위 Record ID P1-ANS-01. 수신일 2026-10-05 KST. AI usage: CODEX_ASSISTED.

## 판정

**worker02 기존 제한 키 상태: 실제 적용 2회·멱등성·신규 SSH·사후 비교 PASS.** 설정 변경 분기, 실제 백업 복원, 전체 role apply/rollback, 운영 엔진 전환 및 최종 AC는 미완료. 기존 P1-ANS-01 종결 상태와 Issue #9 OPEN을 변경하지 않는다. 이번 증적 편입 독립 리뷰는 미완료다.

| 입력 | 확인값 |
|---|---|
| source | 5454b77d508cdbfd0eef13e489cbc0322d11c653 |
| controller | ansible01 / server01_ansible |
| target | k8s-worker02 / 10.1.93.107 / svc_ansible |
| candidate | /home/server01_ansible/ansible-candidate.8oCqVUwx |
| engine | result/runtime/venv-2.21.3/bin/ansible-playbook, core 2.21.3 / Python 3.12.14 |
| successful run directory | /home/server01_ansible/issue9-worker02-apply.H3oZjpe4 |
| playbook | playbooks/harden_svc_ansible_key.yml |
| setting correction | ANSIBLE_SSH_USETTY=false |
| current-state backup | /var/lib/ansible-issue9-worker02.NXrcqAmF/authorized_keys |

## 원본 수신 및 검증

original/의 11개 파일은 사용자 첨부 바이트 그대로 보존했다. SHA256SUMS는 **수신 후 작성한 편입 manifest**이며 서버 측 전송 전 manifest가 아니다. original/INPUT_SHA256SUMS는 실행 당시 source 파일 4개의 해시를 기록한 데이터이고 로그 전체의 manifest가 아니다. source 4파일을 고정 GitHub raw 원문으로 재계산해 모두 일치함을 확인했다.

- apply-1.rc / apply-2.rc 모두 0. 각각 4개 태스크 ok, recap ok4/changed0/unreachable0/failed0/skipped0/rescued0/ignored0.
- 두 로그는 타임스탬프 없는 동일 출력이며 SHA256도 동일하다. 사용자 콘솔의 순차 STAGE/각 rc와 파일명을 함께 근거로 사용한다. 해시만으로 서로 다른 두 실행의 독립 식별을 주장하지 않는다.
- hosts.txt: worker02 1대. engine.txt: candidate 전용 executable/module/config 및 core2.21.3.
- backup-preflight.txt: 현재 키와 이번 백업 모두 b7923e8c646b7a7dd2ccba1ac48ddf02d264780db9100317644dcf87216cc834.
- postcheck: 신규 연결 SSH source10.250.10.10 → target10.1.93.107; 키 hash 및 uid/gid/mode/context1001:1001:600:unconfined_u:object_r:ssh_home_t:s0 유지.
- CentOS10, Python3.12.14, Enforcing 유지. resolver hash c452a6013b82f5daeec71cbe4234dc696f9e4948197866ac74788285d934827e 유지; 시스템 이름 해석 k8s-api.fds.internal →10.1.93.109.
- postcheck 원본의 STATUS=PASS_FRESH_SSH_AND_POSTCHECK. POSTCHECK_RC=0은 사용자 콘솔 증거이며 첨부 파일 안에는 없다. getent 결과를 각 DNS 서버 직접 질의 결과로 확대하지 않는다.

## 콘솔로만 수신한 이력·미포함 원본

- 02:39 KST 최초 시도 QWov7OCh: 첫 Count 태스크에서 PTY allocation request failed, rc4, ok0/changed0/unreachable1. 두 번째 apply 미실행. **실패 로그 파일 원본은 아직 미수신**이며 성공 로그로 덮어쓰거나 재구성하지 않았다.
- 기본 PTY 요청과 restrict 충돌을 controller 실행 환경 ANSIBLE_SSH_USETTY=false로 교정. 키 제한 및 서버 설정은 완화하지 않음. 교정 후 성공 콘솔은 02:45, 사후 콘솔은 02:50에 수신. 이 시각은 사용자 메시지 시각이며 로그 자체의 실행 타임스탬프가 아니다.
- 02:33 KST 백업 생성 PASS 콘솔: NXrcqAmF, 해시·메타데이터 일치. 원격 RECEIPT.txt는 미수신. authorized_keys 원문은 의도적으로 포함하지 않는다.
- candidate 준비 archive 검토 결과는 책임 이슈의 별도 기록을 참조하며 이 수집회차에 archive를 포함했다고 주장하지 않는다.
- 정확한 실행 shell 파일 및 전체 argv의 독립 원본은 미수신. 대화에 제공·실행한 명령과 설정/host/source 파일을 결합한 검토이며 암호학적 실행 증명이 아니다.

## 다음 단계

1. 최초 PTY 실패의 원본 로그/rc 및 백업 receipt는 기존 파일에서만 보완 수신. 실패 재현/추가 apply 불필요.
2. 이 증적 PR의 정확한 HEAD 독립 검토, evidence-layout 확인 후 편입 판단. 별도 리뷰 요청 메시지는 발송하지 않음.
3. RESTORE_PLAN.md의 복원 시험 준비를 검토. 백업 존재와 실제 복구 성공, 동일 내용 복사와 변경 상태 복구를 구분.
4. 전체 role 검증 및 운영 호출 경로 전환은 Issue #9에서 별도 판단. 다른 노드로 자동 확대하지 않는다.
