# Ansible 공유 원본17 — 직접 열람 독립 리뷰 요청

이전 증적 PR243·244에서는 **Git 편입분만 독립 승인**했고, 공유 원본17의 직접 열람은 제외했다. 별도 직접 열람 PR이 없어 사용자가10/19 요청한 범위로 이 새 수집회차를 준비했다. 새 원AC·추가 시험 Gate가 아니라 정확한 공유 원본과 리뷰 결과를 연결하는 후속이다.

- [책임 이슈 Ansible#9](https://github.com/321Team/infra-ansible/issues/9)
- [PR243 범위 한정 APPROVED](https://github.com/321Team/fds-project-evidence/pull/243#pullrequestreview-5554850963)
- [PR244 범위 한정 APPROVED](https://github.com/321Team/fds-project-evidence/pull/244#pullrequestreview-5562856473)

## 리뷰어가 할 일

1. INVENTORY.json의17개 정확 공유 파일을 기존 승인 접근으로 읽는다. 두 그룹은 role185 7개, PR87 CI10개다. 파일 탐색기의 UNC 경로로 열거나 이미 승인된 공유 마운트를 사용한다. 접근 불가면 범위/오류를 회신한다. 새 권한·공유 설정 변경을 요청하지 않는다.
2. Byte/전체SHA·sidecar 및 압축 내부 원문을 REVIEW_CHECKLIST.md대로 대조한다. 압축 파일은 실행하지 않는다. 기존 Git 사본/시험 코드를 전수 재검토하거나185/CI/운영 시험을 재실행할 필요가 없다.
3. 정확 PR HEAD, 실제 공유 열람 파일/시각/내용 범위와 판정을 **이 PR 리뷰**에 남긴다. Git 문서만 본 승인을 공유 직접 열람 완료로 쓰지 않는다. 일부 열람도 확인한 범위대로 회신한다.

## 들어 있는 근거와 단계

| 파일 | 의미 |
|---|---|
| INVENTORY.json | 정확17의 UNC·전체SHA·Bytes·그룹·성공/실패 분류 |
| PRIOR_TECHNICAL_READ.json |10/18 19:12 직접 기술 읽기 원본 바이트 그대로, 일부 내부JSON 판독 포함 |
| CURRENT_TECHNICAL_READ.json |이 PR 준비 시17개 공유 파일 Byte/SHA 재대조. 사람 검토/새 시험 PASS가 아님 |
| REVIEW_CHECKLIST.md |실제 열람17 목록·핵심 내용·정확HEAD 회신 양식. 미회신 유지 |
| SHA256SUMS |이번 수집회차5파일 무결성 |

108MB 규모의 원본 archive는 공유에 유지하고 Git에 중복 업로드·재압축하지 않는다. 기존 봉인 폴더·원본17·권한/credential·운영 엔진/서비스·원AC/Status/담당/기한은 변경하지 않는다. 이번 PR은 자료와 검토 요청이며 승인·병합·최종 인수는 아직 수행하지 않았다.

실제 준비 시각/기술 읽기 결과는 CURRENT_TECHNICAL_READ.json을 따른다. SHA 일치·자동화 검사·작성자 AI 점검은 이하영의 실제 독립 열람/인수를 대체하지 않는다. CODEX_ASSISTED.
