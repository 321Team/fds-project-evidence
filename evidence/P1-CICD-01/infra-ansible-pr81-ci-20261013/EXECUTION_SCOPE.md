# PR81 실제 CI + O02 운영 인수 회차 카드

2026-10-13 KST / CODEX_ASSISTED. 사용자 `81번 착수` 및 `이재환 직접 수행 — CI와 O02 함께 진행`에 따른 준비다. 실제 수행자는 이재환, 인계 지원은 이권욱이다. 사용자가 이번 창의 이재환 직접 수행 가능·이권욱 회수 인수를 확인했다. 실제 TTY 로그인·sudo 인증·공급/회수 수행은 별도 실측으로 남긴다.

## 대상과 준비 결과

- PR81 HEAD `874dc8bb052cfe3295fb79038872c785bbcc2592`.
- Run `38330170015` / Attempt `1` / Job `115077894860`, 필수 labels `self-hosted, Linux, X64, fds-ci, ansible-isolated`.
- 이하영·이재환 최신 HEAD APPROVED. 현재 Job queued, 저장소 등록 Runner 0. 이를 호스트 부재 확인으로 대체하지 않았다.
- 별도 호스트 읽기: 검토된 admin/Runner kit SHA256SUMS 전부 일치, kit manifest `e2fbefffa01b8a0f401cd4623b497944d0e41264ad13343d42ff2b272707d5c6`.
- 기존 PREPARED 및 이미지 존재 확인. 준비 이미지 `sha256:3f96787b2a8db29294002677a3e733689439952ad9e95db721acf8e16ff601f1`; 불필요한 image rebuild/prepare 재실행 없음.
- 11:06 읽기에서 ansible-verify 컨테이너 0·runner.py 프로세스 없음. 기존 수신 packet 경로 0. 실제 공급 직전에 다시 확인한다.
- 최초 Podman 읽기는 상속 작업 디렉터리에서 rc125로 중단됐다. `/tmp`에서 같은 읽기를 수행해 성공했고, 실패 원본과 보완 원본 모두 보존했다. 권한·계정·보안 설정 변경 없음.
- 회차 helper는 성공한 PR77 회차의 operator/release를 재사용하여 대상·경로·시각만 교체했다. release에는 실제 참여/회수 확인 전 token 발급을 막는 검사만 추가했다. 제품 Runner/알림 소스는 변경하지 않았다.

## 확정 창과 실제 사람 조건

| 항목 | 값 / 경계 |
|---|---|
| 준비 시작 | 2026-10-13 11:15 KST 이후 |
| 새 공급 시작 상한 | 11:45 KST 이전. 늦으면 token 발급/새 serve를 하지 않고 새 카드로 조정 |
| 종료·정리 목표 | 13:15 KST. 13:30~14:30 점심 제외 회신을 침범하지 않도록 여유 확보 |
| 장기 실행 점검 | 12:45 KST에 실제 상태·잔여 정리 예산 확인, 필요하면 정확한 이 회차만 복구 인수 |
| 기존 실행 예산 | regression Job 30분, launcher container 경로 최대 3600초. 총 정리 시간을 보장하는 수치가 아니므로 시작 상한 뒤 새 공급 금지, 실패/불명확 상태는 인수 |
| 실제 수행자 | 이재환. 같은 TTY에서 정상 계정 접속·sudo·fresh 판단·공급·Job 확인·회수 수행 |
| 복구 인수 | 이권욱. 사용자가 이번 회차 인수 가능 확인. 이전 이하영 후보를 확정자로 표시하지 않음 |
| 상태 | STAGED_ONLY / 사용자 참여·복구 인수 가용성 확인. 실제 터미널 실행 대기, token 0, Runner 공급 0, CI 미실행 |

위 창은 사용자 확인을 받았고 session 입력에 반영했다. 종료/교체된 Job이나 만료한 창에는 재사용하지 않는다. 기존 코드 리뷰를 다시 요청하지 않는다.

## 경로와 순서

1. 관리 PC에서 기존 queue-watch로 최신 HEAD/Job/5labels·queued·중복 Runner/세션 부재를 확인한다. 종료·교체·다른 활동이 있으면 STOP. 이재환 본인의 판단·시각을 남긴다.
2. 기존 정상 경로로 두 터미널을 연다. A는 `cicd-runner01 / server01_cicd-runner`, B는 `ansible01 / server01_ansible`. HOME을 바꾸거나 root 로그인으로 우회하지 않는다. 비밀번호·token은 채팅/댓글에 보내지 않는다.
3. 인계 지원자가 실제 참여·복구 인수 확인 기록에 근거하여 session의 두 확인 필드를 반영한다. 사용자 확인에 따라 두 필드를 반영하고 원격 파일 해시를 대조했다. 원래 false 입력은 별도 보존했으며 임의 변경하지 않는다.
4. 공급 직전 다른 infra-ansible/infra-cicd 실행과 격리 컨테이너가 없는지 재확인한다. 기존 장기 CICD Runner를 정지/제거하지 않는다.
5. **터미널 A**, 창·확인 필드가 준비된 뒤 이재환이 실행:

```bash
bash /home/server01_cicd-runner/ci81-operator.NB1FQsGc/operator-ci81.sh
```

같은 TTY의 sudo 인증 후 `AUTH_READY`를 확인한다. 비밀번호는 해당 터미널에만 직접 입력한다. 180초 안에 B를 연결하지 못하면 기다림이 종료되며 예전 ready/packet을 재사용하지 않는다.

6. **터미널 B**, A의 AUTH_READY 후 즉시 이재환이 실행:

```bash
python3 -I -B /home/server01_ansible/ci81-operator.ZtyyS6Zl/release-ci81.py
```

fresh HEAD·승인·Job/Runner/컨테이너·A 잠금·인증 시각·시작 상한을 확인한 뒤 기존 관리 도구가 registration/removal token을 발급하고 비공개 경로로 전송한다. helper rc0은 CI 성공이 아니다. 실패하면 같은 명령을 자동 반복하지 않는다.

7. A를 유지하면서 Job이 정확한 Runner/source에 연결되고 regression과 upload가 각각 끝나는지 확인한다. 종료/실패 결과와 A의 operator.rc를 따로 판정한다.
8. Runner/proxy/workspace 정리, 등록 Runner 부재, 양단 packet 및 `.incoming` 부재를 확인하고 원본·archive·manifest·SHA를 보존한다. `.incoming`은 전송 실패 때 남을 수 있으므로 별도 확인하며 임의 glob 삭제를 하지 않는다.
9. 이재환이 본인 수행 구간·시간·판단·정리 결과를 #61에 회신한다. 지원자가 대신 수행한 구간은 대행으로 명시하고 O02 직접 수행으로 계산하지 않는다. 원본 private 경로 상세/credential은 공개 댓글에 넣지 않는다.

## 중단·복구

- source/Job/labels/키트/PREPARED/창 불일치, 기존 세션, 인증 만료, 참여·회수 미확인은 발급/공급 전 STOP.
- token 발급/전달 응답이 불명확하면 재발급하지 않는다. 이번 session의 release 결과·packet/incoming 상태와 operator 종료 여부부터 확인한다.
- 다른 Job 수신, PR HEAD 변경, Job 실패·취소, 정리 실패는 자동 rerun/새 공급 없이 원본과 식별값을 보존하고 실제 복구 인수자에게 연결한다.
- 기존 launcher의 정확한 컨테이너 종료·회수 경로를 우선 사용한다. 다른 Runner, 이미지 캐시, 과거 증적, 전체 HOME을 삭제하지 않는다.
- 13:15가 지났다고 실행 창이 닫히거나 강제 종료되는 별도 예약은 만들지 않았다. 종료 목표를 넘기는 장애 상태는 추가 변경 없이 복구 인수·증적 보존을 계속한다.

## 이번 회차와 별도인 잔여

알림 활성화는 포함하지 않는다. 병합 후 Billing 실제 잔여량, exact 수신 login, 점심·근무 외 대응, 실패 Run 확인자와 전달자를 연결하고 실제 발송·수신을 확인해야 한다. 이미 채택된 30분/threshold10과 기존 카카오톡 대체 경로는 재질문하지 않는다. C01·Harbor·Deploy·Phase2·전체 AC 종결은 이 카드의 수행 범위가 아니다.

근거: [운영 입력](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6136035224), [접수·경계](https://github.com/321Team/infra-ansible/issues/61#issuecomment-6136143106), [운영자 카드](https://github.com/321Team/infra-ansible/blob/874dc8bb052cfe3295fb79038872c785bbcc2592/docs/runbooks/Ansible-CI-Operator-Card.md).
