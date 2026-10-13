# P1-DB-01 — 현재 앱별 DB 정책 조회와 기존 차단 증적 연결

2026-10-13 KST · 이권욱 작업의 CODEX_ASSISTED 수집·대조. 책임: [DB #11](https://github.com/321Team/fds-project-baseline/issues/11), 소비: [SEC #19](https://github.com/321Team/fds-project-baseline/issues/19). [baseline PR166](https://github.com/321Team/fds-project-baseline/pull/166) 병합 후 사용자의 “후속 작업 착수” 지시에 따라 수행했다. [#30 실행·검증 이관](https://github.com/321Team/fds-project-baseline/issues/30#issuecomment-6082618226) 범위의 읽기 전용 사전 점검이며 사람의 최종 결과 수용·AC 판정은 생성하지 않는다.

## 1. 결과와 범위

**fds-app의 앱별 허용·차단 정책을 현재 API 원본에서 확인하고, 기존 수용된 TCP 관측에 연결했다.** 10/13 조회한 Kubernetes NetworkPolicy 3개와 Calico GlobalNetworkPolicy 7개는 10/8 원본의 같은 객체와 UID·resourceVersion·generation·spec가 모두 같다. Calico namespaced policy는 양 시점 모두 0개다. 조회 전후 앱 Pod 6개의 보존 필드도 동일하다. 상세 값과 재현 결과는 [analysis.json](analysis.json)에 있다.

| 단계 | 실제 확인한 범위 |
|---|---|
| STATIC | 수집기는 호스트/uid 확인 뒤 고정된 `kubectl get` 7건만 실행. 로컬 분석 재현·Manifest 검증은 PR 기록 참조 |
| RUNTIME_READ | control01 실제 API 조회 7/7 rc0, stderr 0B. 서버 시계 2026-10-13 13:24:47.396403~13:24:47.695982 KST |
| RUNTIME 트래픽·DB | 이번 회차 미실행. 과거 10/4·10/8 결과만 원래 범위에서 재사용 |
| REVIEW | 수집기 실행 시 `NOT PERFORMED (Pre-check)`. 증적 편입은 독립 리뷰 대상이며 이 문서 자체가 승인 기록이 아님 |
| CI / MERGE | PR의 실제 검사·병합 기록을 따른다. CI 0건을 PASS로 표시하지 않음 |
| AC / 최종 인수 / PUBLICATION | 이번 수집으로 변경하지 않음 |

## 2. 무엇을 수집했는가

- 대상 `k8s-control01`(.102), 기존 `fds-ansible01` → `svc_ansible` SSH → `sudo -n`(uid0) 경로. 계정·키·known_hosts·인증 설정을 바꾸지 않았다. 실제 전달 명령은 [capture-receipt.json](capture-receipt.json)에 보존했다. 키의 파일 경로만 포함하며 키 내용은 없다.
- 실행 소스 [collect_db_policy.py](collect_db_policy.py), SHA256 `95632fd3064abc79df06f33e5585c909b7b8867900491f0af6234bae488beafb`. 로컬에서 보낸 stdin 바이트의 해시이며 서버가 소스 파일을 재해시한 것은 아니다. 서버는 전달된 환경값을 결과에 기록했다.
- 출력 [policy-current.json](policy-current.json), 수신 SHA256 `68fa2182c134c1c11e35828e87f38623eee4b3d5e952eaa1899d68be58a092ff`. 수신 stdout 바이트와 빈 stderr를 그대로 보존했다.
- 각 조회의 전체 API 응답은 메모리에서 해시한 뒤 필요한 필드만 선택해 출력했다. **이 파일은 원본 API 응답 전체 덤프가 아니라 수집기의 원래 출력**이다. annotations, env, 명령 인자, 자격증명은 저장하지 않았다. 전체 API 응답 바이트는 보관하지 않아 조회별 `stdout_sha256`을 사후 바이트 재검증할 수 없다.
- 보존 범위: fds-app Pod 전후 6개(라벨·UID·노드·이미지·상태 일부), fds-app NetworkPolicy 3개, 전체 Calico namespaced policy 0개, GNP 7개, tier 3개, Namespace 라벨 9개.
- 클라이언트 기록은 13:24:45.902636~13:24:46.755966 KST다. 서버 기록과 시계가 어긋나므로 서로 보정하거나 하나의 연속 타임라인으로 합치지 않았다. 이번 회차는 시각 동기화를 검증하지 않았다.

순수 검증기 근거: 기존 권한으로 제한된 GET만 수행하며 Secret 조회·Pod exec·접속 시험·설정/데이터 쓰기·설치·상주·재시작·부하 시험이 없다. 서버 파일로 저장하지 않고 stdout을 작업 PC의 지정 수집 폴더로 회수했다. [중앙 정책 §3.2 4-1](https://github.com/321Team/fds-project-baseline/blob/c5c854efe3572f65bb2ef7b23dd32b61b7291e8e/governance/REVIEW_AUTHORITY_POLICY.md)을 적용하되 증적 편입의 독립 리뷰 예외로 사용하지 않는다.

## 3. 기존 관측 → 현재 정책 대응

| 요구의 범위 | 기존 직접 증적·판정 | 현재 보완 |
|---|---|---|
| fds-engine 직접 DB 차단 | [증적110](https://github.com/321Team/fds-project-evidence/tree/7c33d459e009da208b06f9341a7801051a241392/evidence/P1-SEC-01/received-20261004T1307Z)의 `results.tsv`: engine Pod → 10.1.93.55:5432 TCP TIMEOUT. [SEC 부분 관측 인수](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5987406281) | 현재 engine Pod 3개 모두 `app=fds-engine`, hostNetwork=false. `default-deny-all`이 egress를 격리하며 `fds-engine-allow`는 CoreDNS UDP/TCP53만 허용. DB5432 허용 규칙 없음 |
| transaction-api 승인 DB 경로 | [증적172](https://github.com/321Team/fds-project-evidence/tree/008eb7e48d52308375481c58a1e22ab38a6ddad9/evidence/P1-DB-01/db-window-20261008T1930): 10/8 W3/W4 거래 HTTP201·DB 각1행, W5 Worker3 Source·pg_hba/firewall 기록 | 현재 API Pod 3개 모두 `app=transaction-api`, hostNetwork=false. `transaction-api-allow`가 DB .55/32 TCP5432 명시 허용 |
| 정책 소스와 live 일치 공백 | [기존 대응표](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5989864190)는 저장소 소스 해석이며 live 일치 미확인으로 남겼음 | [10/8 policy-post.json](https://github.com/321Team/fds-project-evidence/blob/6014e9a961af497e78be9c383d270291013db5cf/evidence/P1-SEC-01/network-gaps-20261008/policy-post.json)과 이번 API 조회의 3개 NP·7개 GNP를 객체별 대조. 모두 UID/RV/generation/spec 동일 |

Kubernetes 정책의 선택·허용 규칙은 해당 방향에서 합산된다([공식 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/)). 위 판단은 현재 fds-app 전체 NP 3개와 Pod 라벨을 함께 확인한 해석이다. GNP 6개는 노드별 `fds.example/bootstrap`·`fds.example/node` selector와 `applyOnForward=false`, 나머지 1개는 Worker NodePort용 preDNAT **Ingress** 규칙이다. 현재 Pod/Namespace 보존 라벨에는 해당 host selector 라벨이 없다. 실제 endpoint label·profile·dataplane은 이번에 조회하지 않았으므로 이 요약을 모든 Calico 적용 경로의 완전한 계산으로 표현하지 않는다([GNP 공식 정의](https://docs.tigera.io/calico/latest/reference/resources/globalnetworkpolicy)).

증적110 archive의 SHA256 `1087547663c339df8167d55056e7cc172bc3b678cffe2e52c172f51eea29ae55`를 이번 로컬 대조에서도 확인했고 정확한 DB 행을 analysis.json에 보존했다. 기존 archive를 다시 압축·복제하지 않았다. TIMEOUT 관측 자체는 개별 목적지 무응답 등 대안 원인을 단독 배제하지 못한다. 이번 API 정책 대응은 그 해석 근거를 보완하며 **10/13 새 차단 성공**을 만들지 않는다.

## 4. 인수에 넘기는 판단과 남은 경계

- **완료한 보완:** fds-app에서 engine/API를 나누는 DB 접근 정책의 실제 객체·라벨 확인 및 10/8 이후 객체 연속성 대조. 독립 리뷰 후 기존 DB/SEC 관측을 같은 요구에 연결할 수 있다. 동일 DB 창 전체 재실행을 제안하지 않는다.
- API에 선언된 정책 확인이며 현재 패킷 차단·DB 저장 재시험은 아니다. 다른 Namespace의 현재 Kubernetes NP, endpoint/profile, DB 호스트 현재 설정을 전수 조회한 결과로 확대하지 않는다. 다른 workload·IF·AC의 상태를 이 회차로 변경하지 않는다.
- 10/8 W5 engine TIMEOUT만으로 차단 지점을 확정하지 않고, Worker Source 방화벽만으로 앱 구분을 증명하지 않는다. W5 원문 `RUNTIME_PERMANENT_MATCH=NO`와 interfaces 제외 정렬 비교의 제한은 기존 기록대로 유지한다.
- **W4 전체 HTTP5xx는 NOT_MEASURED 유지**한다. [PR166의 처분안](https://github.com/321Team/fds-project-baseline/blob/c5c854efe3572f65bb2ef7b23dd32b61b7291e8e/governance/handoffs/phase1-execution-20261010/DB_DR_ACCESS_CLOSEOUT_20261012.md)과 DB 전체 Exit/최종 인수는 이권욱의 판단 대상이다. 해시 일치·정책 연속성을 AC 인수나 위험수용으로 변환하지 않는다.
- 이 회차는 DR 재실행, C01/D01 공유 ACL, Grafana 자격증명·감사와 무관하다. 새 권한·예외·보존 결정을 추가하지 않는다.

## 5. 로컬 재현과 중단 기준

Python3 표준 라이브러리만 사용한다. 이 저장소 루트에서 다음 명령을 실행한다. 서버 접근은 없다.

```text
python3 evidence/P1-DB-01/policy-readback-20261013T132447/analyze.py
python3 tools/check-evidence-layout.py --base origin/main
```

첫 명령 출력이 analysis.json과 같아야 한다. 새 폴더 SHA256SUMS와 루트 REGISTRY_SHA256SUMS는 현재 수신 파일의 무결성·추적성을 확인한다. 기존 비교 입력은 위 고정 commit의 파일이며 변경하지 않는다. 필요한 파일 미수신·해시 불일치·조회 rc 비정상·재현 차이가 있으면 인수 근거 갱신을 중단하고 원본을 보존한다. 로컬 분석 실패를 서버 재실행·정책 변경으로 자동 복구하지 않는다. 원격 재수집은 별도 판단이며 이번 실행은 서버 변경이 없어 설정 원복 대상이 없다.
