# ICR 음성 시험 후보 메타데이터 수신 — 2026-09-24 05:20 KST

판정: **실제 메타데이터 수집 완료 / 일반 Pod 후보 4개 확인 / 대상 승인·실제 음성 시험 미완료**.

## 수신·실행 검증

- 원 archive: `ICR_Negative_Candidates_tJeRl5.tar.gz`, 4,604 bytes.
- SHA256: `9f19fd8f06d932f1a3e2c8fe0789414e763bfac9b81c605fb806b83f914c4b30`; 첨부 sidecar 일치.
- 내부 manifest 7/7, 실행 소스 3/3 및 실행 collector hash 일치. 원문 8개는 바이트 그대로 보존했다.
- source `fa33b0dec11d3e02c97739b8a77524c365b939c4`, [순수 Pre-check PR33](https://github.com/321Team/infra-kubernetes/pull/33), merge `24f96f48671e5966d5fd688f31dbc16c349d91de`.
- 05:20:09 KST controller 시작, 05:20:10 control01/svc_ansible에서 3명령 모두 rc0. API URL 로컬 조회 1건 + worker03 Node/Pod API GET 2건이다.
- 실제 Ansible syntax-check 성공. Controller/envelope rc0, stderr 비어 있음. recap ok4/changed1/unreachable0/failed0; changed1은 ansible01의 증적 파일 저장이다.
- LB API `https://10.1.93.109:6443`, worker03 `.108`/Ready=True 확인. Pod 8개, 일반 후보 4개; continuation/잘린 목록 오류 없음.

이번 확인은 사용자가 실행해 제출한 원본 분석이다. 작성자가 새로 VM에 접속하거나 변경하지 않았다. source는 REVIEW=NOT PERFORMED (Pre-check)이며 실제 조회 성공을 독립 코드 리뷰/운영 적용으로 확대하지 않는다.

## 후보 4개 — OWNER_REVIEW_REQUIRED

| Namespace | Pod | Pod IP | ServiceAccount |
|---|---|---|---|
| fds-app | fds-engine-5699669f6f-5rxbt | 10.244.39.220 | fds-engine-sa |
| fds-app | transaction-api-7956485bd4-rfsvm | 10.244.39.216 | transaction-api-sa |
| monitoring-api | alertmanager-7c77f56464-llqps | 10.244.39.218 | default |
| monitoring-api | grafana-7dc57885d4-sk8h2 | 10.244.39.217 | default |

네 후보 모두 worker03, Running/Ready, hostNetwork/hostPID/hostIPC=false, 주 컨테이너 privileged=false다. 원문과 [CANDIDATE_SUMMARY](CANDIDATE_SUMMARY.json)에 UID·컨테이너·관측 imageID를 보존했다. 이미지 태그만으로 도구 존재를 추정하지 않는다. Grafana/Alertmanager가 default SA를 공유하므로 SA 이름만으로 둘을 구분하지 않고 namespace/Pod UID/container/labels를 같이 고정한다.

제외 4개: Calico와 kube-proxy는 시스템·hostNetwork·privileged, node-exporter는 hostNetwork/hostPID, Prometheus는 실제 positive sender다. 제외는 일반 Pod shortlist 용도이며 다른 보안 시나리오의 존재를 부정하지 않는다.

Prometheus UID `46c00f91-2073-440a-800c-6cedba89d291`, PodIP `.219`, host `.108`, SA 및 imageID는 이전 수집과 동일하다. 현재 Target API 성공이나 통신 복구를 뜻하지 않는다.

## 우선 검토 권고와 아직 필요한 확인

**Grafana를 첫 검토 후보로 권고한다. 승인된 시험 대상으로 확정한 것은 아니다.**

- 정확한 후보: `monitoring-api/grafana-7dc57885d4-sk8h2`, UID `00396c87-640c-4704-ac6c-dcbacf6fbc90`, container `grafana`, PodIP `10.244.39.217`, SA `default`.
- imageID: `10.1.93.54/fds/grafana@sha256:7a1ff54408c90357ff1c76189e5bbc24f898531cb771fbbfe6a477f00de37d5b`.
- 근거: 이미 수집된 [01:21 원문](https://github.com/321Team/fds-project-evidence/blob/2f8a238142ad669a35800bb3e8ecc6d372354d60/evidence/ICR-D-NET-01-01/monitoring-precheck-20260924T012110/original/icr-monitoring-precheck.json)의 `default-deny-all`, `grafana-allow`, `allow-grafana-to-prometheus`와 DNS 정책을 확인할 수 있다. app=grafana에 관측된 Kubernetes egress 허용은 Prometheus TCP9090 및 DNS이며 `.105:9100` 허용은 없다. fds-app 후보의 해당 namespace 정책은 이 원문에 포함되지 않는다.
- 이는 과거 정책 snapshot에 따른 후보 선정 근거다. 05:20 현재 정책을 다시 수집한 것이 아니며, Calico 전역/선행 정책까지 고려한 현재 실제 차단을 판정하지 않는다.
- 다음은 기존 담당 K8S/SEC Lead의 대상 선택 기록, 해당 현재 정책의 필요한 범위 확인, 기존 컨테이너의 실제 시험 도구/정확한 명령 확정이다. 별도 상시 ICR 공동 서명이나 신규 승인 양식을 추가하지 않는다.
- Grafana에서 기존 도구 또는 시험 수용 조건이 맞지 않으면 Alertmanager 또는 fds-app 후보를 해당 정책/도구 근거와 함께 검토한다. 도구 설치·Pod 생성·label 변경·접근권 확대는 이번 자료로 승인되지 않는다.
- 실제 음성 시험은 정상 positive endpoint 및 정책에 귀속되는 차단 결과와 짝지어야 한다. timeout/refused/exec 실패/도구 부재만으로 PASS 처리하지 않는다. PR27의 독립 운영 리뷰와 변경창 조건은 그대로다.

후보 목록 확인을 위한 동일 수집 반복은 필요하지 않다. 실행 창 직전의 신원·정책 갱신은 이후 승인된 절차에서 필요한 대상에 한정한다.

## 증거의 한계·보존

Raw API body와 stderr 원문은 소스 설계에 따라 저장하지 않았고, 투영 데이터와 원 응답 hash만 있다. 따라서 원 API 전체 바이트 hash를 이 archive만으로 재검산했다는 주장은 하지 않는다. 전체 Pod/Secret/env/임의 label·annotation을 요청하지 않는다.

원 archive·sidecar는 사용자 첨부 바이트로 보존한다. Git binary/Release 업로드·재압축 없음. 첨부 내부 식별자는 검토자의 팀 접근 URI가 아니며 실제 archive 접근 인계는 미확인이다. 기존 3회차 원문/PARTIAL 기록은 보존한다.

STATIC/LOCAL19 및 소스 병합은 이전 준비 단계다. 이번에 확인한 추가 단계는 **현장 syntax-check 및 순수 조회3/3 성공**이다. 실제 NEGATIVE PROBE·OPERATING APPLY·AC 인수·독립 증적 리뷰·본 증적 PR 병합은 완료하지 않았다. 새 Target API 결과가 없으므로 기존 AC05/06 실패 보고와 AC07 미검증 등 AC 집계를 유지한다.

책임: [ICR #14](https://github.com/321Team/fds-project-baseline/issues/14), [PR27](https://github.com/321Team/infra-kubernetes/pull/27), MON #17·SEC #19. AI assistance: CODEX_ASSISTED.
