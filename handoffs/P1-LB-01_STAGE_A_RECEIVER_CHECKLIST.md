# P1-LB-01 Stage A 실제 인수 체크리스트

상태: 인수 검토 준비 완료 / 실제 인수 승인 PENDING. 이 문서는 서명이나 승인 결과가 아니다.

- 인계자: 이권욱
- 인수자: 이하영
- 검토 PR: [fds-project-evidence #1](https://github.com/321Team/fds-project-evidence/pull/1)
- 검토 Commit: 리뷰 시 PR의 현재 HEAD를 실제 승인 기록에 기입
- [기술·무결성 검토 기록](../evidence/P1-LB-01/stage-a/received-20260907/19_stage_a_handoff_review.md)
- [원본/보완 Index](../evidence/P1-LB-01/stage-a/received-20260907/EVIDENCE_INDEX.md)
- [Ansible CR 승인·병합 기록](../records/post-merge-20260907/CR-P1-ANS-01-01_CLOSURE.md)

## 인수자가 확인할 내용

- [ ] PR의 검토 HEAD와 수신 묶음 SHA-256 `62c64dfbd0cc672c96e4b1fbfa0c71a406e0c86d991b663c0ee02a47b82236a3`를 기록한다.
- [ ] 원본 21개, 기존 PACKAGE_SHA256SUMS, 신규 99_SHA256SUMS의 검증 범위를 구분해 확인한다.
- [ ] .109:6443 Listener, Node 6대·Runner Positive 및 비승인 Source Negative 결과를 확인한다.
- [ ] SELinux 및 임시 키 폐기 보완 3건은 이미 수용된 사용자 콘솔 증적임을 확인한다. 동일 파일 재제출이나 시험 재실행을 요구하지 않는다.
- [ ] 기술 원본이 Bootstrap 전 시점의 기록임을 확인한다. 당시 Backend DOWN을 Stage B 완료로 해석하지 않는다.
- [ ] 수신 묶음에 없는 LB-A-01 IP 중복검사와 firewalld Permanent 출력은 기존 Stage A 승인 근거의 참조를 확인한다. 신규 확인이 필요하면 별도 시각의 Supplement로 남긴다.
- [ ] P1-ANS 원본 인계와 후속 OS/Node·Runtime Gate의 완료 근거를 별도로 확인한다.
- [ ] 인수 결과, 인수 범위, 인수일시, 미해결 조건 및 검토 Commit을 실제 기록한다.

## 실제 기록 양식

아래 값은 실제 인수자와 승인자가 작성한다. Codex가 대신 APPROVED로 채우지 않는다.

| 필드 | 실제 입력 |
|---|---|
| 검토 Commit | 미입력 |
| 인수자 | 이하영 |
| 인수 결과 | PENDING |
| 인수 일시 | 미입력 |
| 원본·Hash 대조 결과 | 미입력 |
| 미해결 조건 / 인수 범위 | 미입력 |
| 인수 리뷰 URL | 미입력 |
| 최종 승인자 | 이권욱 |
| Stage A 최종 승인 / 일시 | PENDING / 미입력 |
| OS/Node Gate 참조 | 미입력 |
| Bootstrap Gate | HOLD |

GitHub에서 리뷰를 제출할 때 실제 검토한 HEAD와 위 인수 범위를 본문에 기록한다. 증적 편입 PR 승인이 Stage A 실제 인수를 포함하는지는 리뷰 문구에 명시해야 한다. infra-ansible의 이미 완료된 리뷰를 이 인수 승인으로 전용하지 않는다.

## 인수 후 후속 조건

Stage A 실제 인수 및 필수 OS/Node Gate 확인 후 P1-K8S-01의 Bootstrap 승인 범위를 판정한다. Control Plane API 기동 후 P1-LB-01 Stage B의 Backend 3대 UP·인증 API·Failover를 수행한다. 전체 P1-LB-01은 Stage B가 남아 있으므로 In Progress다.
