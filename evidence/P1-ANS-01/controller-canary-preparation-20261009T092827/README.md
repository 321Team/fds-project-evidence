# Ansible controller 입력·canary 준비 확인

CODEX_ASSISTED · 이권욱 · 독립 리뷰 요청 이하영. 2026-10-09 **09:28 KST**, 사용자 단독 창09:10~12:00에서 ansible01/server01_ansible의 고정 경로만 조회했다. exact 시작/종료는 invocation.json과 stdout.json을 따른다. PC/호스트 시각 오차는 미검증이다.

**READONLY 수집 완료 / CANARY_APPLY·ROLLBACK·ENGINE_SWITCH NOT_RUN.** 운영 checkout이 후보 엔진 선택을 지원한다고 가정하지 않고 기존 호출 위치와 준비된 시험 위치를 분리했다. [Issue9](https://github.com/321Team/infra-ansible/issues/9), [기존 호출 관측](https://github.com/321Team/infra-ansible/issues/9#issuecomment-6042409863), [worker02 DNS 성공](https://github.com/321Team/infra-ansible/issues/9#issuecomment-6055824006)을 잇는 후속이다.

## 실제 결과

| 위치/입력 | 관측 | 의미와 한계 |
|---|---|---|
| 운영 `/home/server01_ansible/p1-ans-01` | HEAD e1c4458cf95dacca76870d7b9b012f8615f6974a, 선택10파일 Git blob 일치, helper·worker02 verify playbook 없음 | FDS_ANSIBLE_ENGINE_DIR만 설정해 새 wrapper 동작을 기대할 수 없음 |
| 별도 `/home/server01_ansible/worker02-dns-stage.yJfHG0vS/source` | HEAD5111c66f233fe0f84e2d63cef3837fe091a2a268, 고정12입력 Git blob 일치 |10/8 DNS 성공에 쓴 준비 경로 유지. 새 canary 실행 승인은 아님 |
| 두 checkout | tracked 변경0, shallow=false, 필수 조상98cf3f8 존재, 조회 전후 HEAD 동일 | untracked는 미조회, 모든332개 파일의 개별 내용 재해시는 하지 않음 |
| 후보 엔진 bin4개 | 일반 파일 hash·동일 venv Python shebang 확인 | CLI를 실행하지 않았으며 전체 설치물 무결성/실제 CLI 버전 성공이 아님 |
| 설치 선언 | ansible-core METADATA의2.21.3, pyvenv.cfg의Python3.12.14 | 설치 기록의 값. 실행 중 interpreter·import 동작의 검증이 아님 |
| key·known_hosts | 정상 계정 UID1000·0600·일반 파일, .ssh0700 | stat만 수행. 키 내용·known_hosts 지문·실제 인증 성공은 확인하지 않음 |

고정 입력은 ansible.cfg, inventory2개, wrapper4개, engine helper, worker02 verify playbook, DNS role main/verify, workers apply playbook이다. inventory/변수의 **내용은 출력하지 않고 hash만 대조**했다. 동적 inventory 해석·실제 선택 대상·추가 변수/환경 override·활성 세션·예약 작업 전수는 이번 수집 범위가 아니다.

## canary 대상 확대를 막는 확인

고정 Source5111c66의 [DNS wrapper](https://github.com/321Team/infra-ansible/blob/5111c66f233fe0f84e2d63cef3837fe091a2a268/scripts/cr-p1-ans-01-01-run.sh)의 `workers`는 [workers apply playbook](https://github.com/321Team/infra-ansible/blob/5111c66f233fe0f84e2d63cef3837fe091a2a268/playbooks/cr-p1-ans-01-01-apply-workers.yml)을 실행하며 `hosts: k8s_workers`, `serial: 1`이다. [그 inventory](https://github.com/321Team/infra-ansible/blob/5111c66f233fe0f84e2d63cef3837fe091a2a268/inventory/hosts.yml)에는 worker01·02·03이 포함된다. **serial1은 한 대씩 실행한다는 의미이며 worker02 한 대 제한이 아니다.** worker01 제외 canary에 이 명령을 쓰거나 wrapper guard를 직접 playbook/--limit로 우회하지 않는다.

worker02 전용 action은 `verify-worker02`이며 이미10/8에 rc0/ok32/changed0/failed0/unreachable0을 수집했다([증적167](https://github.com/321Team/fds-project-evidence/pull/167)). 이번 수집에서 이를 반복하거나 새 Runtime PASS로 옮겨 적지 않았다. DNS 단일 대상 **apply**를 선택한다면 별도 scope guard·승인·복구를 갖춘 최소 소스 변경과 독립 리뷰가 필요하다. 이 문서에서 canary role을 임의로 DNS로 확정하지 않는다.

## 후속 순서와 완료 조건

1. 기존 Issue9의 worker02 SSH hardening apply2회/changed0·fresh SSH 및 DNS verify 성공을 재사용한다. 이미 완료한 분기를 반복하기 위해 키 제한을 해제하거나 운영 설정을 일부러 바꾸지 않는다. 전체 role 변경 분기·rollback·운영 진입점 전환은 별도 미완료다.
2. Lead가 다음 실제 canary의 **role·worker02 한 대·예상 변경·백업 대상·기존 복구 경로·복구 인수자**를 정한다. 실행 가능한 단일 대상 진입점이 없는 role이면 먼저 소스 guard/시험을 PR로 준비하고 리뷰한다. 관리 대상 그룹 전체를 단일 canary로 사용하지 않는다.
3. 선정된 회차의 정확한 source·inventory·변수·engine/config/key 참조를 고정하고, 기존 운영 checkout 갱신 없이 검토된 별도 경로를 사용한다. 후보의 source나 엔진이 달라지면 이번 hash/설치 선언을 재사용하지 않는다. 실행직전 fresh 인증·대상·비중첩과 복귀 가능성을 확인한다.
4. 승인된 apply→같은 입력 재적용→새 SSH→해당 role rollback을 수행하고 각각의 실제 rc/변경/백업/원본 로그를 연결한다. 엔진 경로 복귀는 DNS/SSH/MON/NTP 설정 복귀를 대신하지 않는다. 실패 시 다음 대상 확대·자동 재시도·키 복원을 중단한다.
5. 수동·예약·Runner 진입점별 전환은 해당 호출 source/config/절대 CLI·원복값을 고정한 후 별도로 진행한다. 과거 RPM/cron/Collection 조사는 재사용하되 누락 manager/동적 호출을 이번 조회로 닫지 않는다.

## 재현성·무결성·수집 통제

- collector.py/stdout.json/stderr.txt/invocation.json은 원 수신 bytes다. SSH rc0/stderr0, collector·stdout hash2/2 대조. source-inputs.json은 고정 두 Git Commit의22개 blob SHA256과2개 부재를 로컬 Git 객체에서 별도 대조한 입력이다.
- `python3 analyze_ansible_controller.py .` 출력은 analysis.json과 일치한다. 원본 hash/쿼리 rc·22개 hash·부재2개·설치 선언/키 metadata를 재검사한다. 정상 stat/hash는 Runtime 또는 독립 진위 증명이 아니다.
- 고정9:10~12:00/hostname/UID1000 gate, 파일당1MiB·O_NOFOLLOW/O_NOATIME·전후 metadata 대조. Git은 optional locks/fsmonitor/hooks 비활성화, 명령별12초, SSH 전체55초다. fixed12파일/2checkout 및 후보CLI4개·설치선언2개·접근metadata4개만 수집했다.
- sudo·Ansible CLI·wrapper·inventory plugin·managed host접속·키내용·환경변수 dump·DNS질의·서버파일생성·checkout갱신·서비스조작0. 신규 수집기는 **REVIEW=NOT PERFORMED (Pre-check)**의 순수 조회이며 기존 실행 도구 승인과 혼동하지 않는다.
- 결과가 불완전하면 정상으로 보정하지 않고 원 수신을 보존한다. 이번에는 서버 변경/임시파일이 없어 원격 정리·원복 대상이 없다. 준비 문서/증적 독립 리뷰는 연장 작업창 종료 후 회수한다.
