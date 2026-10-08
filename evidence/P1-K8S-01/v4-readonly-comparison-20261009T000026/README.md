# P1-K8S-01 AC4e — 5대 v4 적용본 읽기 전용 대조

CODEX_ASSISTED · 이권욱. [#10 잔여4번](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6040248632)의 control02 외5대 적용본을 수집했다. **수집 공백은 보완했지만 적용본 전체 일치는 성립하지 않는다.** 자동 배포·교체·정책 변경·AC 체크는 하지 않았다.

## 수집 범위와 재현 경로

- 서버: control01 `.102`, control03 `.104`, worker01 `.105`, worker02 `.107`, worker03 `.108`. control02의 도구 파일은 이번에 다시 읽지 않았다.
- 실행: 10/9 **00:00:27.517126~00:00:29.433351 KST**, 5대 outer rc0. control01의 API GET4개와 각 노드의 주소/firewalld 상태 조회도 rc0.
- 접근: Windows → 기존 fds-ansible01/server01_ansible → 기존 key/known_hosts의 `svc_ansible` → `sudo -n python3 -`. 새 신뢰·권한·파일·서비스/정책 변경 없음. API는 고정 raw GET을 사용해 discovery cache 생성을 피했다.
- 대조 기준: 10/6 도구 복원에서 인용한 infra-kubernetes `b4303f2df512a8791d2421203cf159567d076b2a`, [기존 적용 승인](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6009176490). 현재 main `81ad791d5a6a611d3c7f0068bd638e60ec8e28f8`에서도 비교9개 파일의 해시가 이 기준과 동일하다(`CURRENT_SOURCE_HASHES.json`). 과거 일부 호스트/파일 적용 승인을 이번9개·5대 일괄 배포 승인으로 확대하지 않는다.
- 기준 파일: RUNBOOK_FINAL.md 및 code 아래8개. `references/approved-v4.json`에 source/deployed 경로·SHA256, `references/approved-v4/`에 정확한 Git blob 사본.
- `*.stdout.json`/`*-invocation.json`/`*.stderr`/`*-collector.py`가 노드별 반환 원문·실행 명령·시각·rc·코드 hash다. 로컬 해석 도구는 `collection-and-analysis/`에 보존했다.

## 1. 도구 배포본 비교: 45항목 중 일치28·불일치17

| 노드 | 9개 중 일치 | 불일치 |
|---|---:|---|
| control01 | 8 | audit-window.py |
| control03 | 5 | audit-window.py, cluster-change.py, node-evidence.py, render.py |
| worker01 | 5 | 위4개 |
| worker02 | 5 | 위4개 |
| worker03 | 5 | 위4개 |

`COMPARISON.json`에 파일별 expected/actual 전체 SHA256이 있다. 같은 이름의 불일치 파일은 수집5대에서 각각 같은 해시였다. control03에서 대표4개를 추가 읽기 전용으로 받아 최초 수집 해시와 다시 대조했다(`differing-sources/`). 이 디렉터리의 `collector.py`는 수신 코드 사본으로, 실제 배포된 운영 코드4개와 구분한다.

`DEPLOYED_SOURCE.diff`는 승인본→현재 배포본의 차이다. 실제 영향을 주는 대표 차이:

- **audit-window.py**: 현재 배포본에는 승인 수정본의 엄격한 ausearch 결과 분류·UTC 날짜 경계 선택이 없다. 단순 rc0/1·빈 출력 처리에 의존한다. 이 파일로 향후 AVC 무발생 판단을 만들기 전에 반영 상태를 해결해야 한다. 과거 모든 AVC 증적을 일괄 무효화했다는 뜻은 아니다.
- **cluster-change.py**(control03/Worker3대): 승인본의 WorkloadEndpoint 부재 시 Pod fallback과 rollback 전에 Felix 검증을 끝내는 순서가 반영되지 않았다. 현 파일을 안전한 승인 rollback 도구로 간주하면 안 된다. 관련 수정 [PR52](https://github.com/321Team/infra-kubernetes/pull/52).
- **render.py**(동일4대): 승인된 후속 CP/Worker 허용 규칙 생성 변경과 차이가 있다. 옛 render로 정책을 재생성·재적용하지 않는다.
- **node-evidence.py**(동일4대): 승인본의 원 규칙 출력/상세 비교 보완과 차이가 있다.

`SCRIPT_SHA256SUMS`는 지정 위치에 없었고, `gate2-state.json` 경로 조회 등 일부 경로는 파일로 읽을 수 없었다. 원문 오류를 보존했다. 특히 control01 `gate2-state.json`은 **디렉터리**로 보고됐으므로 state 소실로 단정하지 않는다. 이 보조 경로 조회 한계를 도구9개 미수집으로 합산하지 않았다.

## 2. 현재 정책과 옛 생성 번들은 다르다

control01의 `/root/generated-gate2-attempt01/config.lock.json` SHA256은 `b42e7e80590ac6fb03e1934499c3f0ceeeab33557ecdf3033c3e206936c8ec43`로 과거 시도 식별값과 같다. 그러나 그 폴더의 GNP YAML에는 후속 정책 변경이 반영되지 않았다.

- `POLICY_DIFF.json`: 서버의 옛 생성 GNP6개와 live의 strict spec 차이. `COMPARISON.json`의 SPEC_DIFFERENT는 이 비교이며 새 승인 소스 재구성 비교와 구분한다.
- `APPROVED_RENDER_COMPARISON.json`: 보존 config를 승인된 render의 순수 `policies(config,node)` 함수에 **로컬에서만** 넣은 값과 live를 비교한다. 운영 render/validate CLI나 apply를 실행하지 않았으며, 증거 입력의 재승인도 아니다.
- HEP6개 spec 일치, Felix6개는 `failsafeInboundHostPorts`/`failsafeOutboundHostPorts` 두 필드 projection 일치. 다른 Felix 유효 설정·프로세스 실행값 전체를 입증하지 않는다.
- Worker GNP3개는 승인 소스 재구성값과 일치(API의 `tier=default` 기본 필드는 별도 기록 후 비교에서 제외).
- control02/03 GNP는 TCP10250 Source nets의 **구성원은 같고 순서만 다름**. 규칙 순서는 보존한 채 nets 구성원 순서만 무시한 비교도 따로 기록했다.
- control01 GNP에는 위 순서 차이 외에 다른5대에서 오는 UDP123 허용 규칙이 **동일 내용으로2회** 있다. [NTP 후속 증적](../cr-p1-ntp-01-01-recapture-20260924/README.md)과 별도 변경 이력이 있는 영역이다. 이것을 새 침해·차단 실패로 단정하거나 이 회차에서 제거하지 않았다. 생성기·후속 NTP 정책의 정합화/중복 처분은 Lead가 판단한다.

관련 기존 정책 반영: [Worker9100/10250 PR39](https://github.com/321Team/infra-kubernetes/pull/39), [CP10250 PR48](https://github.com/321Team/infra-kubernetes/pull/48). 현재 live가 옛 생성 YAML과 다르다는 이유로 이 변경들을 자동 되돌리지 않는다.

## 3. 판정과 다음 조치

1. **COLLECTION=5/5 완료**, SOURCE_CONSISTENCY=일부 불일치, AC4e/AC4/Close는 그대로 HOLD/별도 판단. HEP/Felix 설정 대조는 동작·연속 보호·차단 귀속 시험이 아니다.
2. K8S Lead는 도구 배포 위치/사용 주체를 확인해 실제 사용할 승인 파일로 정합화하는 최소 변경안을 확정해야 한다. 적용 전 현재 파일 backup/hash·owner/mode/context·기존 세션 여부, 적용 후 hash/구문 및 실패 시 파일 복귀 조건을 고정한다. 이번 회차에서는 복사·chmod·정책 재생성/적용을 하지 않았다.
3. 옛 생성 번들은 후속 승인 정책을 빠뜨릴 수 있으므로 그대로 재적용하지 않는다. 승인 원본과 현재 정책의 차이를 반영하는 절차를 검토해야 한다.
4. 수집기는 독립 코드 리뷰 미수행의 순수 읽기 전용 수집기다. 자체 해시/내용 대조는 독립 증적 리뷰를 대신하지 않는다. 민감정보 패턴 점검0건은 휴리스틱 점검으로 한정한다.

첫 수집 후 대표4개 파일만 추가 조회했고 서버 설정·패키지·계정·Secret·방화벽·Calico·서비스를 변경하지 않았다. Harbor 자동기동 세션은 접근하지 않았다.
