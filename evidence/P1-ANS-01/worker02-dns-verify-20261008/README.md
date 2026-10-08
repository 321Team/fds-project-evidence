# worker02 DNS verify — 2026-10-08

CODEX_ASSISTED. 실행자 이권욱(GWONUK). [infra-ansible#9](https://github.com/321Team/infra-ansible/issues/9)의 **worker02 한 대 DNS verify 1회** 증적이다. 17:18:19~17:18:30 KST, outer rc0. 독립 리뷰·편입 병합·Issue9 전체 인수는 별도다.

## 실행 근거와 비중첩

사용자가 17:17 KST경 이 채팅에서 **“현재 단독 사용 가능 — 15분 동안 Edge·관련 시험 중단 확정”**이라고 확인했다. 기존 Edge 창 해제를 GitHub 기록만으로 추정하지 않고 이 직접 확인 후 실행했다. 이 문장은 실행자의 승인 근거 전사이며 별도 독립 서명 증명이 아니다. Probe는 포함하지 않았다.

명령은 17:18:30 종료했고 17:19:13 controller의 ansible-playbook 프로세스 부재를 추가 확인했다. 이 세션의 Runtime 점유는 종료했다. 다른 담당자의 새 창·GO를 이 문서로 승인하지 않는다.

## 대상·소스·명령

- controller: ansible01 / server01_ansible. 별도 source `/home/server01_ansible/worker02-dns-stage.yJfHG0vS/source`.
- managed host: k8s-worker02 / 10.1.93.107 / svc_ansible. sudo는 기존 Ansible become 경로를 사용했다.
- [PR74](https://github.com/321Team/infra-ansible/pull/74) merge `5111c66f233fe0f84e2d63cef3837fe091a2a268`; 승인 HEAD `d8d99efaf2537c74fb8f412fef65b351af08f67a`와 tree 차이 0.
- core2.21.3: `/home/server01_ansible/ansible-candidate.8oCqVUwx/result/runtime/venv-2.21.3/bin`. controller-stage 원본에 config·Python·CLI 경로가 있다. 엔진 전체 설치물 무결성 감사는 아니다.
- 기존 private key는 경로만 참조했다. 키/known_hosts 소유·0600, 기존 worker02 host-key 항목을 확인하고 host_key_checking=True를 유지했다. 키 내용은 수집하지 않았다.
- 로컬 shallow 이력을 보완한 Git bundle에서 새 checkout을 만들고, controller에서 필수 조상·332개 전체 tracked blob·검토 입력 12개 hash를 확인했다. 실행 직전 source clean 및 12개 hash 재확인, 종료 후 source status도 빈 출력이다.
- 실행: `timeout --signal=TERM --kill-after=10s 120s bash scripts/cr-p1-ans-01-01-run.sh verify-worker02`. `run-once.sh`가 당시 경로·시간 상한·1회 디렉터리·환경 허용 목록을 기록한다. 해당 시간은 만료되므로 재실행용 승인이 아니다.

## 관측과 판정

| 항목 | 실제 결과 |
|---|---|
| localhost 대상 guard | PASS, worker02 주소·계정·그룹·단일 대상 확인 |
| worker02 recap | ok32 / changed0 / unreachable0 / failed0 / skipped5 / rescued0 / ignored0 |
| resolver 영구·현재 설정 | DNS .52→.53, search fds.internal, ignore-auto-dns yes, drift false |
| 질의 | 두 DNS 직접 질의 2/2, 내부 FQDN·short name·외부 github.com PASS |
| API listener | 10.1.93.109:6443 TCP 연결 PASS. API 인증·업무 성공으로 확대하지 않음 |
| 서비스 상태 | kubelet/containerd 전후 동일, service_regression NONE |
| 종료 | outer rc0, 120초 미도달, 자동 재시도 없음 |

`server-originals/`는 controller의 runtime-once 디렉터리에서 받은 원본이다. server SHA256SUMS 11개 항목을 수신 후 모두 대조했다. runtime.stdout은 wrapper의 stderr 병합 출력(tee)을 포함하며, runtime.stderr는 바깥 프로세스의 별도 stderr다. 이를 서로 다른 추가 시험으로 집계하지 않는다. 해시는 수신 바이트 무결성이며 서버 서명·독립 승인과 구분한다.

## 경계와 후속

DNS 설정 적용·rollback·key 복원·운영 checkout/RPM/PATH 전환은 수행하지 않았다. Ansible 임시 파일과 별도 증적/소스 디렉터리 생성은 존재한다. changed0은 Ansible 보고 범위이며 모든 파일의 무변경 감사를 뜻하지 않는다.

이번 성공으로 6노드 DNS 전체, canary apply·재적용, role rollback, 별도 fresh SSH AC, 전역 엔진 전환 또는 Issue9 전체 완료를 선언하지 않는다. 관련 AC별 후속 실행은 별도 범위·창에서 판단한다. 실패 시 원본 보존·재시도/확대 금지였으며 이번에는 rc0으로 종료했다.
