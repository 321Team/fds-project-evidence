## 사용자 결정 반영 — 버전 복구 검증은 미결 잔여로 유지

이권욱 / CODEX_ASSISTED · 2026-10-26 KST. 사용자 직접 지시 **“버전 복구처리는 미결로 정리하고 권장순으로 후속 처리”**를 반영합니다.

| 항목 | 현재 결정 |
|---|---|
| 대상 | #46의 이전 승인 P2 digest로 버전 복구 → Health 검증 |
| 실행/판정 | **NOT_EXECUTED / 미검증·미결(UNRESOLVED)**. 이번 회차 추가 복구 실행은 보류 |
| 사유 | 승인된 상이한 이전 P2 digest·복구 렌더 없음. 현 baseline previous는 current와 같은 두 digest이며, [앱 계약 §9](https://github.com/321Team/fds-msa/blob/69e28c494a120c388afe18d901043d05333d7c7c/deploy/DELIVERY-CONTRACT-rosa.md#9-앱별-currentprevious-채택-43-2026-10-15)의 최초 previous 없음과 구분해 보존 |
| 남는 위험 | 다른 버전으로 전환할 때의 pull/호환성/rollout·복구 후 Health 경로가 Runtime으로 검증되지 않음 |
| 책임/일정 | 이권욱. 재개일 미정. 유효한 상이 이전 승인본이 확보되면 별도 범위·가용 작업창으로 재판정 |
| 보존/재개 조건 | 기존 정상 source/render/contract/digest와 원본 보존. 상이한 이전 이미지의 승인·registry 가용성·DB/설정 호환성·복구 렌더·실행 범위가 확인될 때 재개 |

- 현재 정상 A3 배포·imageID·Health·Rule 관측과 B1 실제 Unit 실패/reader 거부/ROSA 불변은 유지합니다. 같은 digest 재적용·앱0·과거 P1 관측값을 버전 rollback 성공으로 만들지 않습니다.
- **이 결정은 미결 상태의 기록이며 복구 AC를 PASS로 바꾸거나 면제·전체 #46/G5/Close 완료로 만드는 결정이 아닙니다.** #46은 In Progress를 유지하고, #45/#55/#57에서는 이 항목을 알려진 미검증 잔여로 연결합니다.
- 후속은 증적 PR253의 독립 검토·편입, 기존 담당자 인수 회신 처리, 최종 회수 준비 순으로 진행합니다. 같은 previous 자료·동일 시험을 다시 요청하지 않습니다.
- **08:30 소비 종료·12:00 최종 정리/복구/반출/보고 유지**. 현재 본인 STOP/db01 복구 가용05:20을 자동 연장하지 않습니다. 이번 기록으로 새 자격 발급·권한 변경·워크로드/DB/네트워크 쓰기·삭제는 하지 않았습니다.

근거: [실제 검증 결과6402063899](https://github.com/321Team/fds-project-baseline/issues/46#issuecomment-6402063899), [증적 PR253](https://github.com/321Team/fds-project-evidence/pull/253), [담당자 통합 회신 요청6402170348](https://github.com/321Team/fds-project-baseline/issues/55#issuecomment-6402170348).
