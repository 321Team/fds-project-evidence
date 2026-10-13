# P1-MON-01 — Grafana 관리 경계와 API 감사 인자 현재 조회

2026-10-13 KST · 이권욱 요청에 따른 CODEX_ASSISTED 읽기 전용 사전 점검. [MON #17](https://github.com/321Team/fds-project-baseline/issues/17), 소비 [SEC #19](https://github.com/321Team/fds-project-baseline/issues/19), 통합 [#30](https://github.com/321Team/fds-project-baseline/issues/30).

## 결과

기존 [PR166 관리 접근 입력표](https://github.com/321Team/fds-project-baseline/blob/c5c854efe3572f65bb2ef7b23dd32b61b7291e8e/governance/handoffs/phase1-execution-20261010/DB_DR_ACCESS_CLOSEOUT_20261012.md#5-grafana--이미-받은-입력과-남은-입력)의 현재 설정 미조회 부분을 좁혔다. 고정 GET 3건 모두 rc0, stderr 0B다. Secret 조회·Pod exec·인증 시험·권한/정책/설정 변경·서비스 재시작은 하지 않았다.

| 직접 관측 | 판정 범위 |
|---|---|
| API 서버 mirror Pod 3개가 Running이고, command/args에서 `--audit-`로 시작하는 인자 0개 | 조회한 Pod 선언에 감사 인자 없음. 실제 프로세스 argv, 호스트 설정 파일·auditd·외부 감사 저장소를 검사한 것은 아님 |
| Grafana Deployment Ready 1/1, SA `grafana-sa`, hostNetwork=false | 당시 선언과 상태. 접속·로그인 성공이나 실제 사용자 식별 검증 아님 |
| env의 admin-user/admin-password가 `grafana-admin-credentials`를 참조 | Secret 값·암호 유효성·실제 사람 보유/회수 이력은 미조회 |
| 조회한 Grafana Service는 ClusterIP/TCP3000 | 해당 Service 노출 형식. Ingress·프록시·exec/PF·관리자 사본 등 모든 경로의 배타성을 증명하지 않음 |

서버 시각은 14:27:22.936233~14:27:23.049345 KST, 클라이언트 기록은 14:27:21.389818~14:27:22.058330 KST다. 두 시계가 어긋나므로 동일한 연속 시각으로 보정하지 않았다. 원본은 `grafana-boundary.json`과 `grafana-capture-receipt.json`에 보존한다.

## 책임 결정과 기존 한계

사용자는 이번 작업 채팅에서 **Grafana 관리 자격증명 보관·회수 책임자를 이권욱 본인으로 확정**했다. 이는 역할 확정이며 Secret 값 수령·접속 성공·권한 회수 완료를 새로 주장하는 기록이 아니다. 기존 팀 3명의 control01 관리 경로 사용 가능 사실, 개인별 사용 기록 미보유, 비상 콘솔 사용 조건 미정은 [PR166의 MON·SEC 회신](https://github.com/321Team/fds-project-baseline/pull/166) 범위대로 유지한다. 미보유 과거 원본 재요청이나 감사 공백의 위험수용·AC 통과를 자동 생성하지 않는다. C01 확인이나 DR 인수를 Grafana에 확대하지 않는다.

## 출처와 재검증

- 실행 대상/계정: `k8s-control01`, 기존 `fds-ansible01` → `svc_ansible` → `sudo -n` uid0 경로. strict host-key 검증 유지. 정확한 전달 명령은 receipt에 있다.
- 실행 소스: `collect_grafana_boundary.py`. SHA256은 receipt의 source_sha256 및 Manifest와 대조한다. 호스트·uid 확인 후 kubectl GET 3건, 각 timeout25초, 선택 필드만 출력한다.
- 로컬 전달기: `capture_grafana_boundary.py`. Python3 표준 라이브러리와 기존 SSH가 필요하다. 원 출력 바이트와 빈 stderr를 수신 파일로 저장했다. 단순 검토 시에는 다시 실행하지 않는다.
- JSON은 API 응답 전체가 아니라 수집기 원 출력이다. 조회별 전체 stdout hash는 당시 메모리에서 계산했으나 전체 API 응답 바이트는 미보관이므로 사후 해시 재계산을 주장하지 않는다.
- 오프라인 검증: receipt source_sha256과 실행 소스, stdout_sha256과 JSON, stderr_sha256과 stderr가 일치해야 한다. reads는 정확히3개이고 각각 rc0, 예상 Pod3/Deployment1/Service1이다. 폴더 SHA256SUMS와 루트 REGISTRY_SHA256SUMS를 함께 검사한다.
- 누락·해시 불일치·형상 불일치 시 해당 결론 사용을 중단하고 원본을 보존한다. 서버 변경이 없어 설정 원복 대상은 없다. 새 수집·감사 활성화·자격증명 회전은 이 회차 결과로 자동 실행하지 않는다.

## 단계와 남은 일

STATIC 및 RUNTIME_READ 완료. 실행 소스 REVIEW=`NOT PERFORMED (Pre-check)`. 중앙 순수 검증기 예외로 읽었으며 증적 편입은 독립 리뷰 대상이다. CI/REVIEW/MERGE는 PR의 실제 기록을 따른다. MON·SEC 전체 AC/최종 인수는 변경하지 않는다.

남은 일은 현재 관리 자격증명/접근의 배타성·회수 범위와 과거 개인별 감사 공백의 인수 판단이다. 새 감사 구성을 채택한다면 관측 범위·개인 식별·민감정보 제외·보존/용량·HA API 서버 변경/복구 영향을 갖춘 별도 검토안이 필요하다. 이 읽기 결과만으로 새 보안 요구나 광범위 변경을 승인하지 않는다.
