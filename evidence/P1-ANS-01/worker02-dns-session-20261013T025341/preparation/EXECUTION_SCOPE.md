# worker02 DNS 후보 엔진 한정 회차 — 실행 범위

2026-10-13 / 이권욱 / CODEX_ASSISTED. 상태: **실행 준비·읽기 검증 완료, 새 백업/prepare/apply/reapply/rollback 미실행**. 이번 사용자 “착수”에 따라 기존 권장 순서의 다음 항목을 구체화했다. Phase1이며 신규 Lead 구현 GO나 반복 독립 코드 리뷰는 추가하지 않는다.

## 현재 확인

- 02:42 KST worker02 `ens160` / `fds-k8s-worker02`, DNS `.52,.53`, search `fds.internal`, ignore-auto-dns=yes. live resolver도 동일하다. 내부 FQDN/short-name→`.109`, DNS2대 직접 질의, 외부 github.com 해석, `.109:6443` TCP 정상.
- NetworkManager/kubelet/containerd active, SELinux Enforcing. Node6·시스템Pod3·앱Pod6 Ready, 앱별 Worker3대1/1/1. 대상 연결 UUID·주소/경로 및 서비스 PID/진입시각을 별도 보존했다. 이후 시점은 실행 직전 재대조한다.
- [PR76](https://github.com/321Team/infra-ansible/pull/76) HEAD `0d58598d8a3ce77ccd7eaa9e1dfba820b0a436ea`의 이하영 독립 코드 승인·병합·[CI SUCCESS](https://github.com/321Team/infra-ansible/actions/runs/37895578228/job/113706062449) 확인. ansible01의 기존 고정 checkout이 이 HEAD, tracked 변경0·실행경로 untracked0·필수11파일 SHA 일치. 명시적 후보 CLI4종 모두2.21.3.
- 기존 소스의 rollback은 **현재값=원본이어도 `connection modify`와 `device reapply`를 실행**한다. PR76의 알려진 비차단 의견이며 새 발견/새 차단으로 반복 리뷰하지 않는다. 동일값 복구 실행을 실제 장애 복원 성공으로 표기하지 않는다.

## 이번 실행 범위

1. 기존 ansible01/server01_ansible → worker02/svc_ansible+sudo, pinned SSH 키·host-key와 승인 source/2.21.3 절대경로를 사용한다. 새 credential·RPM·전역 PATH/엔진 변경 없음.
2. 새 회차 `w02-20261013T024523-85942d67`를 사용한다. controller 새0700 `/home/server01_ansible/p1-worker02-dns-20261013-r1`에 로그, worker02 새 root0700 회차 경로에0600 `original-resolver.json`을 독점 생성한다. 기존 최초 CR 백업·다른 회차를 덮어쓰지 않는다.
3. **prepare → apply check-mode → apply → reapply → rollback check-mode → rollback → 신규 SSH/사후 확인**, 각 단계 성공을 확인하고 순차 실행한다. prepare가 반환한 백업 SHA를 외부 보존·고정하고 이후 호출마다 같은 값을 전달한다. 최초 apply는 백업 생성15분 이내다.
4. 현재 사전값=목표값이므로 apply/reapply의 DNS 변경0이 예상된다. 달라지면 계획 밖 drift로 중단한다. **고의 DNS 장애·drift를 만들지 않는다.** 마지막 rollback은 검증된 동일 원본값을 다시 설정·연결 재적용하는 실제 명령 경로1회로 분류한다. `down/up`, 노드 재부팅, Pod/정책/서비스 변경·전체 Worker 실행은 없다.
5. 사후 persistent/live DNS·내부/외부 해석·직접 DNS2대/API·신규 SSH, NM/kubelet/containerd·주소/경로·Pod/Deployment 보존을 확인한다. 성공하면 기존 PR208에 증적을 합치고 기존 리뷰어를 유지한다. AC/엔진 전체 전환/티켓 종결은 자동 완료하지 않는다.

## 현장 조건·영향·중단

필수 현장 조건은 **worker02 NetworkManager/DNS 동시 변경 배제와 해당 콘솔 복구 인수 가용성**이다. 앞선 이미지 import와 K8S 파일 호출 배제는 이 NM 변경 배제의 증거로 전용하지 않는다. Harbor 변경·사후 관측과는 실제 시작 직전에 다시 비중첩을 확인한다. 이는 새 Lead 판단을 요구하는 절차가 아니다.

동일값이라도 device reapply는 실노드의 네트워크 관리 명령이므로 연결/해석의 일시 영향 가능성을0으로 단정하지 않는다. 새 백업과 현재 상태를 콘솔에서 비교할 수 있어야 한다. 단계당180초, 전체15분 한도이며 timeout/실패/unreachable/예상외changed/소스·연결·값 drift/백업 불일치면 다음 단계0, 자동 재시도0. timeout은 원격 실행 종료나 원복 완료의 증거가 아니므로 진행 프로세스와 실제 상태부터 읽는다.

적용 중 실패하면 기존 role의 해당 호출 사전값 rescue 결과를 확인한다. 수동 복구는 검증된 회차 백업으로 현재값이 원본/목표 중 하나이고 동일 interface/connection일 때만 허용된다. 다른 drift나 연결 손실은 콘솔 인수로 넘긴다. 키 제한·SELinux·방화벽을 해제하거나 원본을 삭제/교체하지 않는다. 같은 값의 rollback 성공은 실패상태 복구/엔진 전체 호환/HA 인수를 증명하지 않는다.

[고정 입력](EXECUTION_INPUT.json), [명령 카드](RUNBOOK.md), [준비 검증](PREPARATION_VERIFICATION.json). 사용자의 현장 조건 확인 전에는 prepare의15분 유효시간을 시작하지 않는다.
