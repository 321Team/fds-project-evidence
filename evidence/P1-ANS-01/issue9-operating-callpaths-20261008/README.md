# P1-ANS-01 — 운영 checkout·Runner 호출 경로 보완

CODEX_ASSISTED · 2026-10-08 KST. 책임: [infra-ansible#9](https://github.com/321Team/infra-ansible/issues/9), 실행/수집 GWONUK. 기존 SSH 계정에서 읽기 명령을 실행했고 stdout/stderr/rc/명령/UTC 시각을 그대로 저장했다. 서버 원본 파일을 수정하거나 운영 checkout을 갱신하지 않았다. 저장된 SHA256은 수신 바이트 무결성이며 서버 서명/독립 인수는 아니다.

## 신규 관측

| 경로 | 관측 | 의미 |
|---|---|---|
| ansible01/server01_ansible `/home/server01_ansible/p1-ans-01` | HEAD `e1c4458cf95dacca76870d7b9b012f8615f6974a`, tracked status 빈 출력 | 운영 위치가 최신 main da4e273e가 아님. untracked 파일은 조사하지 않음 |
| 위 checkout의 cfg + wrapper4개 | 원격 hash를 e1c4458c Git 원문과 대조 5/5 일치 | 해당 다섯 파일의 기준 source 확인 |
| `scripts/lib/ansible-engine.sh` | 경로 없음, hash 명령 rc1 보존 | 이 checkout은 opt-in helper가 없는 이전 경로. 옵션을 주면 엔진이 바뀐다고 가정하면 안 됨 |
| 위 위치에서 `/usr/bin/ansible --version` | core2.16.19, Python3.12.14, 해당 checkout의 ansible.cfg, /usr/lib/python3.12/site-packages/ansible | 명시한 명령·작업 위치의 실제 선택. 다른 로그인/예약 경로 전체의 증명 아님 |
| cicd-runner01 systemd | `actions.runner.321Team-infra-cicd.cicd-runner01.service` active/running, User=server01_cicd-runner, WorkingDirectory=HOME/actions-runner, MainPID1289의 exe=/usr/bin/bash, drop-in 없음 | 장기 CICD Runner의 현재 서비스 진입점. child 전체 감사/Ansible 배포 실행 성공은 아님 |
| GitHub Runner | infra-cicd ID2 online/idle; infra-ansible 0대, PR74 한 건 queued | 분리된 Runner 모델. 0대 자체는 장애 아님 |

조회 범위는 COMMANDS.json에 명시했다. 첫 Podman 상태 질의는 svc_ansible HOME을 다른 계정이 열 수 없어 rc1이었다. 작업 디렉터리를 /tmp로 지정한 기존 절차의 질의는 rc0/[]로 확인했다. 권한·HOME mode는 변경하지 않았다. 정상 실행 계정의 sudo -n rc1과 별개이며 사용자 TTY 인증을 우회하지 않았다. CI_PREPARATION.json은 **준비 당시** 상태로, 이후 CI 결과는 별도 기록을 따른다.

## 재사용한 관측과 제외 범위

Issue9의 10/5 기록에는 RPM NEVRA/From repo appstream, 현재 shell CLI, Collection 조회, cron/anacron, timer/logrotate/raid-check 및 연결 unit 조사가 이미 있다. 이를 미수집으로 되돌리거나 동일 조회를 반복하지 않았다. 배포사 전체 CVE 보장, 다른 사용자 manager·비표준 scheduler·동적 간접 호출 전체 부재는 여전히 주장하지 않는다.

[evidence148](https://github.com/321Team/fds-project-evidence/pull/148)의 후보 CLI/Gate0 syntax와 [150](https://github.com/321Team/fds-project-evidence/pull/150)의 MON verify는 별도 checkout `/home/server01_ansible/issue9-native-engine-2rz3_9f4/source`의 da4e273e로 수행됐다. 운영 p1-ans-01이 자동 갱신되었다는 증거로 쓰지 않는다.

## 다음 실행 경로와 복귀

1. 현재 운영 checkout/RPM/PATH는 유지한다. worker02 DNS 시험은 PR74 정확한 리뷰·CI SHA를 새 checkout에 고정하고 기존 엔진 선택 변수로 후보 경로를 명시한다. 오래된 운영 wrapper에서 동일 환경변수가 효력을 갖는다고 가정하지 않는다.
2. 기존/후보 엔진 경로와 사용한 checkout을 실행별로 기록한다. opt-in 해제는 호출 엔진 선택의 복귀일 뿐 대상 서버 설정 복원이 아니다.
3. infra-cicd main `4e9324cd8acf0ba67b35f950b4c952db8064540e`의 실제 APP Run37642123031은 Python→Test/Build/Scan 경로다. 이를 Ansible 운영 배포 호출 경로 또는 Kubernetes Deploy 완료로 확대하지 않는다.
4. 운영 호출 경로 전환은 role별 Runtime/복구·독립 리뷰·전환 범위를 충족한 뒤 별도로 판단한다. 이번 원본 수집만으로 Issue9 첫 AC 전체·운영 전환·티켓 Close를 체크하지 않는다.

단계: LIVE_READONLY_CAPTURE=COMPLETE / SOURCE_COMPARISON=5_MATCH / ENGINE_TRANSITION=NOT_RUN / INDEPENDENT_REVIEW=PENDING.
