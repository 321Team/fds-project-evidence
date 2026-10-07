# Issue9 — 실제 후보 엔진의 제어 서버 연동 점검

CODEX_ASSISTED · 2026-10-08 KST. 사용자 요청에 따라 CICD Push/증적 리뷰 대기와 독립적인 Ansible #9 제어 서버 검증으로 이동했다.

## 실행 기준과 범위

- source infra-ansible main da4e273e7e26a9a0b51211e5146066960df072b5. 명시적 엔진 선택 구현 PR71은 exact d40589e 독립 승인·10/5 병합 완료. source 조회 시점 현재 main에 포함됨을 확인했다.
- 실행 ansible01/server01_ansible UID1000, 10/8 00:37:38~00:37:45 KST. 별도 HOME/issue9-native-engine-2rz3_9f4/source checkout에 Git bundle을 전달했으며 HEAD·tracked clean을 대조했다. 기존 운영 checkout/전역 PATH/venv/RPM/키는 변경하지 않았다.
- bundle SHA256 28a3ab3ff99c46112693a1e0338352bb3c8805a02194e15d901385a9e065e905. bundle 자체는 source code 운반용이며 이 증적에 포함하지 않았다. source는 해당 고정 Git commit으로 재현한다.
- 실제 candidate 경로 HOME/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin. mock CLI·mock hostname/id·가상 Git HEAD를 사용하지 않았다.
- stage/호출/회수 스크립트는 실제 실행 명령 기록이다. 운영 source의 새로운 승인이나 대상 노드 실행기로 전용하지 않는다.

## 실제 결과

1. helper가 실제 ansible-playbook / ansible-inventory / ansible / ansible-config 4개를 2.21.3으로 선택: 각 rc0. 실제 CLI별 executable/config/module/python 위치는 원본 --version stdout에 있다.
2. 실제 p1-k8s-01-gate0-run.sh syntax → 선택된 ansible-playbook --syntax-check rc0. 선택 경로·CORE2.21.3·SSH_USETTY=false는 stderr에 기록됐다. 이 action은 inventory/플레이북 구문만 읽었으며 대상 노드 실행은 하지 않았다. inventory의 worker01 존재를 worker01 canary 실행으로 해석하지 않는다.
3. 동일 candidate를 2.16.19로 잘못 선언한 입력: rc64 / version mismatch STOP, stdout 없음. PATH fallback으로 실행을 이어가지 않았다.
4. 시스템 /usr/bin/ansible --version은 전후 core2.16.19, stdout byte-identical. 운영 엔진 전환이 아니다.

명령8개: 정상조회/구문7개 rc0 + 의도된 잘못된 버전1개 rc64. MOCK8개 또는 원격 Runtime8개 PASS라고 표현하지 않는다.

## 원본·무결성

원본 /home/server01_ansible/issue9-native-engine-2rz3_9f4/evidence. stdout/stderr16개+REPORT1개, 내부 SHA256SUMS17항목.
서버에서 manifest 대조 후 archive 생성, 수신 시 서버 hash와 수신 hash 일치, 내부18파일 원본 byte 일치 확인.
archive SHA256 5efccb03582d003a772459f6809a173e30307af3d98c043513cfda6e4bf5afc3.
파일 해시는 무결성 근거이며 운영 역할/AC 완료의 근거로 확대하지 않는다. 원본은 보존했다.

## 남은 단계와 재실행 조건

CONTROLLER_NATIVE_SYNTAX=PASS. Gate0 check/run, DNS/MON/NTP wrapper 실제 역할 실행, 대상 호스트의 변경/복구, 운영 엔진 전환, Issue9 인수는 NOT_RUN/PENDING.
키 복원은 기존 worker02 읽기 결과에서 불필요했고 이번에 다시 수집하거나 정상 키를 변경하지 않았다.
DNS/MON/NTP는 범용 worker02 --limit 인터페이스가 아니므로 기존 canary 승인을 그대로 대입하지 않는다.
다음은 역할별 action/대상·기존 승인·실행창·중단/복구를 확정한 실행안이다. NTP 실제 잠금/FD 검증은 별도로 남는다.
같은 helper/후보 경로·source가 유지되면 이 버전·구문 점검을 이유 없이 반복하지 않는다. 변경된 부분만 재검증한다.

이 증적의 독립 REVIEW/PUBLICATION은 PR 결과를 따르며 자동 인수·티켓 종결은 하지 않는다.
