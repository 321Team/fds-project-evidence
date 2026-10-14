# P1-CICD-01 AC05 과거 원본 회수 — 2026-10-14

CODEX_ASSISTED · 이권욱. 기존 Runner 원본 148개를 읽기 전용으로 회수했다. 과거 앱 scanner rc1 / SCANNER_EXECUTION_ERROR 및 rc10 / HIGH 57·CRITICAL 3 차단은 확인됐고, 기존 Run35683010080 payload 56개도 잔존 서버 원본의 해시와 일치했다.

- [회차별 원본·범위·한계](../evidence/P1-CICD-01/ac05-history-20261014/README.md) · [수집 요약](../evidence/P1-CICD-01/ac05-history-20261014/AUDIT_RESULT.json)
- [두 실패 유형의 후속 준비안](../evidence/P1-CICD-01/ac05-history-20261014/NEXT_CASES.md) · [읽기 전용 사본 검증기](../evidence/P1-CICD-01/ac05-history-20261014/verify.py)
- **AC05 PARTIAL 유지:** 각 실패 당시 배포 전후 이미지 관측 미확보. Push/Deploy 미호출만으로 이미지 유지 실측을 대신하지 않는다. 신규 시험은 실행하지 않았다.
- [PR222](https://github.com/321Team/fds-project-evidence/pull/222) Unit-negative 증적은 10:36 KST 병합됐지만 AC04 최종 인수와 구분한다. 이번 원본 회수의 독립 편입 검토·AC05 최종 인수는 대기다.
