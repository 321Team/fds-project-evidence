# Grafana 관리자 자격증명 참조 관계 — 읽기 전용 수집

CODEX_ASSISTED · 이권욱 · MON 이재환 / SEC 이하영 독립 검토 요청. 사용자 단독 창 **2026-10-09 09:10~12:00 KST**에서 기존 정상 SSH 경로 PC → ansible01 → control01 svc_ansible → sudo-n으로 조회했다. [MON41 접근 장부](https://github.com/321Team/infra-monitoring/pull/41)의 Secret 이름·참조 위치 미수집 항목을 보완한다.

**참조 메타데이터 수집 완료. 실제 자격증명 유효성·보관자·접근 배타성은 미검증이다.** Secret 내용·비밀번호/토큰 및 그 해시는 수집하지 않았다. 이 결과는 과거 exec 사용 보고를 현재 로그인 성공으로 바꾸지 않는다.

## 관측

- 호스트 시각 **09:40:15.020800~09:40:15.109524 KST**, PC 수신 시각은 invocation.json 참조. PC/호스트 시계 오차는 검증하지 않았다.
- monitoring-api/grafana Deployment UID `b74852b0-fe0b-468c-984f-760ef66cf820`, generation16 / resourceVersion4371649. 조회 전후 동일하다.
- label `app=grafana`로 조회된 Pod `grafana-f65457bfd-ckjgj`, UID `916b8c8a-ff21-42ba-9815-11dce4cde848`, Ready=true / restartCount0. Deployment template와 Pod의 **선택한 참조 메타데이터**가 일치한다. 모든 spec을 비교한 것은 아니며 ReplicaSet→Deployment 소유 체인은 별도 조회하지 않았다.
- 두 객체의 container `grafana`에 아래 참조가 있다. envFrom0, 관리자 환경변수 literal0. 수집한 volume 참조에는 직접 Secret mount가 없다. ConfigMap 내용·파일·런타임 환경은 미조회이므로 다른 간접 입력 부재를 단정하지 않는다.

| 환경변수 | namespace / Secret 참조 | key |
|---|---|---|
| GF_SECURITY_ADMIN_USER | monitoring-api / grafana-admin-credentials | admin-user |
| GF_SECURITY_ADMIN_PASSWORD | monitoring-api / grafana-admin-credentials | admin-password |

참조 위치: Deployment `.spec.template.spec.containers[name=grafana].env[].valueFrom.secretKeyRef` 및 Pod `.spec.containers[name=grafana].env[].valueFrom.secretKeyRef`. 이 환경변수 참조가 현재 Grafana DB에 저장된 실제 관리자 암호와 일치하는지는 검증하지 않았다. Secret 객체의 존재·UID·버전·회전 시각도 GET하지 않았다.

## 수집·재검증

1. collector.py를 원격 파일로 저장하지 않고 Python stdin으로 실행했다. Deployment GET → selector 기반 Pod GET(limit10, continue가 있으면 중단) → 같은 Deployment GET의 **3건 모두 rc0**. SSH rc0 / stderr0.
2. 고정 날짜/창·호스트/euid gate, API 요청10초·명령15초·SSH전체60초, 응답 크기2MiB 검사. 응답은 subprocess 메모리에 받은 뒤 크기를 검사하므로 하드 스트리밍 메모리 상한은 아니다. 해당 객체만 조회하고 전체 namespace/Secret 목록을 순회하지 않는다.
3. API 원문은 메모리에서 필요한 참조 메타데이터로 투영 후 폐기했다. stdout.json은 **수신한 projection 원본 bytes**이며 API 원문이 아니다. API 원문이나 값의 해시는 제공하지 않는다. 원문 독립 재계산은 불가능하고 같은 조회의 후속 실행은 시점이 다른 관측이다.
4. collector.py/stdout.json 해시2/2를 invocation.json과 대조했다. `python3 analyze_grafana_reference.py .`로 분석을 재생성하면 analysis.json과 일치한다. 수집기 로컬 fixture에서 literal 관리자 값·command가 결과에 나오지 않고 Secret 참조는 보존됨을 확인했다(STATIC, 실제 시험 증적 아님).
5. SHA256SUMS는 파일 무결성만 검사한다. 분석 PASS를 접근 제어·인증 성공·AC 충족으로 확대하지 않는다. 실행 실패 시 자동 재시도·변경을 하지 않고 receipt를 보존한다.

신규 수집기는 REVIEW=NOT PERFORMED (Pre-check)의 순수 조회다. API GET 이외 PF/exec/TokenRequest/RBAC 변경/자격증명 회전/서비스 재시작/장애 주입/Harbor 작업은 없다. 원격 임시파일·리소스 생성이 없어 원복 대상도 없다. admin.conf는 기존 kubectl 인증 입력이며 파일 내용·인증 주체를 별도로 출력/수집하지 않았다.

## 남은 확인과 기존 증적 재사용

- 이재환: 해당 앱 관리자 자격증명의 보관자·회전/회수 이력, 과거 exec 및 앱 API 사용의 실제 주체/단말/시각·감사 연결. 이하영: 클러스터 관리 credential 보유·회수·접근 경계 판단. Support가 그 사실이나 정책을 대신 확정하지 않는다.
- [증적130](https://github.com/321Team/fds-project-evidence/pull/130)의 과거 승인 PF 성공·회수는 재사용하고 단순 반복하지 않는다. [증적175](https://github.com/321Team/fds-project-evidence/pull/175)의 현재 관리 경로 메타데이터와 결합해도 승인 단말만의 배타성은 미입증이다.
- [증적173](https://github.com/321Team/fds-project-evidence/pull/173)의 격리 Probe 전이·복구와 [증적177](https://github.com/321Team/fds-project-evidence/pull/177)의 실제6종 정의/Ready 관측은 서로 범위가 다르다. 새 실제 workload 장애 시험 GO는 아니다.

READONLY=COLLECTED / STATIC=PASS / ACCESS_TEST·FAULT_TEST=NOT_RUN / REVIEW=PENDING / AC·Close=UNCHANGED. 독립 리뷰는 작업창 종료 후 회수한다.
