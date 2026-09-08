# FDS PR #4 제출 리뷰 검토 v1.1

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

