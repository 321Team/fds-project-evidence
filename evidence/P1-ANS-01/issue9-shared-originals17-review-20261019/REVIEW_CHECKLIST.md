# 공유 원본17 직접 열람 체크리스트

아래는 작성자가 대신 완료 처리하지 않은 **리뷰어 실제 열람용** 목록이다. 접근 불가/일부 열람이면 확인한 파일 ID와 한계를 그대로 적는다. 모든 파일의 원본 경로·전체 SHA·크기는 INVENTORY.json에 있다. 단순 Git/JSON 열람과 실제 공유 바이트/압축 내부 열람을 구분한다.

| 파일ID | 그룹 | 이름 | 기대 Bytes | 실제 공유 열람 |
|---|---|---|---:|---|
| 1 | role185 | `runtime-originals-20261016T081814170331.tar` | 48,148,480 | 미회신 |
| 2 | role185 | `runtime-originals-20261016T081814170331.tar.sha256` | 110 | 미회신 |
| 3 | role185 | `p1-role-fixture-supply.tar` | 29,132,800 | 미회신 |
| 4 | role185 | `p1-role-fixture-supply.tar.sha256` | 93 | 미회신 |
| 5 | role185 | `runtime-originals-20261015T235358062170.tar` | 30,668,800 | 미회신 |
| 6 | role185 | `runtime-originals-20261015T235358062170.tar.sha256` | 110 | 미회신 |
| 7 | role185 | `SHA256SUMS` | 313 | 미회신 |
| 8 | pr87-ci | `ansible-actions-runner-evidence.tar.gz` | 6,353 | 미회신 |
| 9 | pr87-ci | `ansible-actions-runner-evidence.tar.gz.sha256` | 105 | 미회신 |
| 10 | pr87-ci | `ARCHIVE_INDEX.json` | 227,666 | 미회신 |
| 11 | pr87-ci | `ci-artifact-12052452535.zip` | 515,688 | 미회신 |
| 12 | pr87-ci | `ci-artifact-12052452535.zip.sha256` | 94 | 미회신 |
| 13 | pr87-ci | `CI_SCOPE_VERIFIED.json` | 1,256 | 미회신 |
| 14 | pr87-ci | `CLEANUP_OBSERVATION.json` | 1,021 | 미회신 |
| 15 | pr87-ci | `COMPLETION.json` | 2,750 | 미회신 |
| 16 | pr87-ci | `README.md` | 906 | 미회신 |
| 17 | pr87-ci | `MANIFEST.json` | 2,727 | 미회신 |

내용 판독:
- 성공 runtime tar: 내부 `results/SESSION_RESULT.json`의 PASS_LOCAL_ROLE_FIXTURES, source affaad6b,7단계와 MON45+45/NTP48+25+serial1+transport2+wrapper19=185를 실제 원문에 연결한다. 격리 모의 서비스 결과이며 production_runtime/phase1_acceptance=false를 유지한다.
- 이전 runtime tar: terminal exit1 실패 회차를 별도 실패 이력으로 보존한다. serial 기대 실패 주입의 내부rc2를 전체 실행 실패와 혼동하지 않는다.
- fixture supply tar: 공급물의 출처/식별과 archive/sidecar 대응을 확인한다. 파일을 실행하거나 재시험하지 않는다.
- CI ZIP: CI_RESULT.json의 source625731f3·Run38887094714/attempt1·unit295/syntax78/fixture7, production_apply/operational_engine_transition=false를 확인한다. role185 전체를 CI가 다시 실행했다고 쓰지 않는다.
- Runner tar·CLEANUP_OBSERVATION·COMPLETION: 회수/정리의 해당 회차·실제 원문과 CI_RUN 연결을 확인한다. 현재 서버 상태·현재 계정 부재/운영 인수로 확대하지 않는다.
- ARCHIVE_INDEX/MANIFEST/README·sidecar: 파일명/해시/내부 멤버 대응, MANIFEST의 LOCAL_PACKAGE_READY_NOT_SHARED는 작성 당시 상태임을 확인한다. LF/CRLF 바이트를 임의 정규화하지 않는다.

리뷰 회신 양식 (값은 실제 수행 후 작성):

```
검토 HEAD: <이번 PR 정확40자리>
실제 공유 열람 시각(KST):
직접 읽은 파일 ID / 전체17 중 개수:
원본 Byte/SHA 대조 결과:
실제 압축 내부/내용 판독 범위:
성공/실패·격리/CI/운영 단계 구분 판정:
이상·누락·민감정보 / 미열람 사유:
판정: 승인 / 변경요청 / 범위 한정 의견
이번 범위에서 확인하지 않은 항목:
```

PR243/244의 유효 독립 승인과 기존 한계를 유지한다. 이 PR의 검토/병합은 전체Ansible#9·NTP 전체AC·엔진 전환·Phase1최종 인수를 뜻하지 않는다. 확인하지 않은 실제 열람 사실을 채우지 않는다.
