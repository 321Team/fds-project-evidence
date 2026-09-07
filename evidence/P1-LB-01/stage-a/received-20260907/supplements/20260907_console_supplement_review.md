# P1-LB-01 Stage A Console Supplement Review

Version: v1.0 · Date: 2026-09-07 · Result: requested supplements PASS 3/3

## Provenance

사용자가 이 대화에 제출한 3개 서버의 콘솔 출력을 근거로 작성했다. 아래 내용은 해당 출력의 필요한 필드를 정리한 기록이며, 서버 .txt 원본이나 .sha256 Sidecar 파일을 수신한 것으로 표시하지 않는다. Markdown의 escape 표기는 가독성을 위해 정상 문자로 정리하고 중복 EVIDENCE/SIDECAR 출력은 한 번만 기록했다.

해시가 생성되는 경우 이 정리 문서의 수신 후 무결성을 뜻하며, 서버 원본 파일의 SHA-256을 확인한 것으로 해석하지 않는다. 이전 응답에서 허용한 콘솔 제출 경로로 검토를 완료했으며, 같은 시험의 재실행이나 원본 tar.gz 재제출은 요구하지 않는다.

## LB-HO-OBS-01 — LB SELinux

| Field | Submitted value |
|---|---|
| source_host / source_user | k8s-api-lb01 / server01_k8s-api-lb |
| timestamp | 2026-09-07T03:02:59.930113+00:00 |
| KST | 2026-09-07 12:02:59.930113 |
| collection | READ_ONLY |
| getenforce | exit_code=0; Enforcing |
| sestatus | exit_code=0; SELinux status=enabled |
| Loaded policy name | targeted |
| Current mode / Mode from config file | enforcing / enforcing |
| getsebool haproxy_connect_any | exit_code=0; haproxy_connect_any --> on |
| EVIDENCE | /home/server01_k8s--api-lb/P1-LB-01_Stage_A_Supplement_f4cj8nna/20_selinux_state_k8s-api-lb01.txt |
| SIDECAR | /home/server01_k8s--api-lb/P1-LB-01_Stage_A_Supplement_f4cj8nna/20_selinux_state_k8s-api-lb01.txt.sha256 |
| Review | PASS — 2026-09-07 조회 시점의 Runtime/설정 파일 enforcing 확인 |

이번 조회 결과를 2026-09-03 당시 상태의 직접 증명으로 소급하지 않는다.

## LB-HO-OBS-02 — ansible01 temporary key

| Field | Submitted value |
|---|---|
| source_host / source_user | ansible01 / server01_ansible |
| timestamp | 2026-09-07T03:03:22.852184+00:00 |
| KST | 2026-09-07 12:03:22.852184 |
| private_key_path | /home/server01_ansible/.ssh/p1-lb-01-stage-a-ansible-ed25519 |
| private_key_state / public_key_state | ABSENT / ABSENT |
| historical_log | PRESENT |
| historical_revocation_log | /home/server01_ansible/.local/state/p1-lb-01-stage-a-transfer/revoke_local_ansible.txt |
| history.timestamp | 2026-09-03T18:29:11+09:00 |
| history.role / history.source_host | ansible / ansible01 |
| history.key_tag | p1-lb-01-stage-a-ansible-20260903 |
| history.key_fingerprint | SHA256:IMzyrRaluEPISRA8a6++E2ljufMna9QL3/kLUJIrPSo |
| historical_fingerprint_match | True |
| history.server_revocation_prerequisite | operator-confirmed |
| history.verdict | PASS_REVOKED |
| EVIDENCE | /home/server01_ansible/P1-LB-01_Stage_A_Supplement_7y230q3g/21a_key_revocation_ansible.txt |
| SIDECAR | /home/server01_ansible/P1-LB-01_Stage_A_Supplement_7y230q3g/21a_key_revocation_ansible.txt.sha256 |
| Review | PASS — 승인된 임시 키의 기록과 Fingerprint 일치, 지정 경로의 현재 파일 부재 확인 |

## LB-HO-OBS-03 — cicd-runner01 temporary key

| Field | Submitted value |
|---|---|
| source_host / source_user | cicd-runner01 / server01_cicd-runner |
| timestamp | 2026-09-07T03:03:14.009706+00:00 |
| KST | 2026-09-07 12:03:14.009706 |
| private_key_path | /home/server01_cicd-runner/.ssh/p1-lb-01-stage-a-runner-ed25519 |
| private_key_state / public_key_state | ABSENT / ABSENT |
| historical_log | PRESENT |
| historical_revocation_log | /home/server01_cicd-runner/.local/state/p1-lb-01-stage-a-transfer/revoke_local_runner.txt |
| history.timestamp | 2026-09-03T18:28:28+09:00 |
| history.role / history.source_host | runner / cicd-runner01 |
| history.key_tag | p1-lb-01-stage-a-runner-20260903 |
| history.key_fingerprint | SHA256:iJ7UOsZJHE8U/HDICq2/Mai7Wsqn3dTjgR9NQFPSacw |
| historical_fingerprint_match | True |
| history.server_revocation_prerequisite | operator-confirmed |
| history.verdict | PASS_REVOKED |
| EVIDENCE | /home/server01_cicd-runner/P1-LB-01_Stage_A_Supplement_bmc6ej93/21b_key_revocation_runner.txt |
| SIDECAR | /home/server01_cicd-runner/P1-LB-01_Stage_A_Supplement_bmc6ej93/21b_key_revocation_runner.txt.sha256 |
| Review | PASS — 승인된 임시 키의 기록과 Fingerprint 일치, 지정 경로의 현재 파일 부재 확인 |

## Cross-check and boundary

- 두 Fingerprint는 수신한 18a/18b/18c의 Source별 Fingerprint와 정확히 일치한다.
- LB 임시 Public Key 제거 기록은 2026-09-03 18:12:47 KST이며, 이후 Runner 18:28:28, Ansible 18:29:11의 폐기 기록이 이어진다.
- 지정된 임시 Key 경로의 부재를 확인한 것이며 다른 위치의 사본 존재 여부를 전수 검사한 결과는 아니다.
- 수집기가 출력한 `handoff_acceptance=PENDING` 및 `verdict=REVIEW_REQUIRED`는 자동 승인하지 않는 수집기 동작이다. 이를 기술 시험 실패로 해석하지 않는다.
- 이 문서의 PASS는 보완 출력에 대한 검토 판정이다. 이하영 인수 승인, 이권욱 최종 승인, main 병합 및 P1-K8S-01 Runtime Gate는 별도다.
