# AC09 15:35 회차 — SEC 조건 실행 증적 검토

2026-10-15 16:04 KST · CODEX_ASSISTED · 기존 로컬 증적만 독립 대조

**현재 판정: edge 4건과 현행 이미지·메트릭 경계 복귀는 확인됐다. 원 journal/승인/Run 결속 및 전후 6호스트 시계 원문도 확보됐다. 다만 회차 구간에 적용할 시계 오차 상한의 근거가 아직 없어 15/30분은 `시한 미입증 / SEC 사후 검토`로 구분한다. 실제 초과나 사고로 판정한 것은 아니다. 전체 AC09 인수와 작업창 반환은 중앙의 별도 판단이다.**

## 적용 기준과 검증 범위

- 실행 근거: [중앙 Runtime GO 6186064463](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186064463), 로컬 `AC09_USER_AUTHORIZATION_1535.json`. W=15:35, 정상 종료16:20, 별도 현행 전용 복구≤16:35. 별도 복구 권한은 W+45 위험수용을 연장하지 않는다.
- 위험 조건: [6185120164](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185120164), 시각 방식 수용 [6185621755](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6185621755), 기존 [시각 보완](AC09_SEC_TIMING_ADDENDUM.md). 기존 기술v1·addendum는 변경하지 않았다.
- 실행 소스 `fddc76e1c261cd938f06211b7ed035fdcb32e606`. R1 Run **38693979785**, R2 **38694721511**, 각 Attempt1·success. 실행 success와 보안 조건/업무 인수를 구분한다.
- 근거 루트 `deliverables/p1-cicd-ac09-preparation-20261015/runtime-1535/`, edge는 같은 상위 폴더의 `round4/edge-pre`, `round4/edge-during`.
- [독립 로컬 대조 결과](ac09-runtime-1535/LOCAL_VERIFICATION.json), [원본 해시 목록](ac09-runtime-1535/SOURCE_MANIFEST.json). 16:04 대조에서141개 소스 파일,30개 수집 디렉터리 및 정리3건의 영수증/원문 결속을 확인했다. 원본 수집기를 새 실행하지 않았다.

## 조건별 결과

| 조건 | 확인 결과 | 판정 |
|---|---|---|
| 대상·승인 결속 | 두 승인 바이트 및 combined record SHA 일치. 첫/최종 journal의 claim, 연속 SHA chain, plan/approval, Run/Attempt1 일치 | 확인 |
| 두 Deployment 경계 | API UID `8a2af808-ec33-41f2-80b5-addde4e28910`, engine UID `bf825dec-465b-4603-8b71-f768d195531c` 유지. R1 이전 이미지, R2 현행 이미지 복귀. 이미지 외 정규화 spec 해시 동일 | 확인한 두 대상 범위 충족 |
| edge 4GET | 아래 원문4건, Host/Location/본문/크기/SHA 및 no-follow/no-retry 일치 | 조건4 충족 |
| 현행 복귀/노출 회수 상태 | 15:51:34 전체 이전 Pod 부재, 업무 `/metrics`404·전용 메트릭200·Prometheus up6. 15:58:07에도 같은 현행 Pod6 Ready, restart0 | 관측 범위 충족 |
| R2 첫 PATCH≤P+15 | 보정 전 보수 구간6분11.114초. 정확 송신값 미계측, 회차 E_host 미입증 | **시한 미입증**, PASS 아님 |
| 회수≤P+30 | 보정 전 회수 확인 상한까지8분20.490초. 최종 안정 관측까지14분50.433초. 호스트별 오차 구간 결속 미완료 | **시한 미입증**, 실제 미회수 판정 아님 |
| W+45 | 고정 만료16:20 유지. 현재 확보된 원문은15:58 현행 복귀 상태이며 잔여 노출의 증거 없음 | 만료 연장 없음·실제 초과 확인 없음. 창 반환 별도 |
| 시계 원문 | 전후6호스트, 내부 명령 rc0·raw hash 일치, 같은 boot/chronyd process | 수집 충족·구간 오차 입증 별도 |
| 정리 | 16:00:52~53 runner 입력2건/control 복구 kit/ansible 회차 디렉터리 제거와 journal 보존. 세 정리 명령의 rc0·command/stdout/stderr SHA 및 집계본 일치 | 제출 원문 대조 완료. Token·총계 인수는 별도 |

## edge 정확 범위

| 시각(KST) | URI | HTTP | Location |
|---|---|---|---|
| 15:41:12.752~.754 | `/metrics` | 404 | 없음 |
| 15:41:12.754~.757 | `/metrics/` | 404 | 없음 |
| 15:45:29.435~.437 | `/metrics` | 404 | 없음 |
| 15:45:29.437~.439 | `/metrics/` | 307 | `http://10.1.93.50/metrics` |

4건 모두 source=`edge01/svc_ansible`, local socket=`10.1.93.50`, destination=`10.1.93.50:80`, HTTP Host=`10.1.93.50`. Base64 원 wire와 `.http` 파일 바이트, 본문 Content-Length를 대조했다. redirect는 추적하지 않았으며307을 최종404로 바꾸지 않았다. during은 이전 이미지 Ready 관측15:44:35 이후·R2 이전이다. 이 결과를 외부 클라이언트·다른 Host·전체 URI의 안전 증명으로 확대하지 않는다.

## 시각 원값과 정확값의 구분

- R1 첫 PATCH_PENDING 원mtime: **15:43:16.828114**, `1792046596828113610 ns`; 첫 API APPLIED는15:43:17.325656. P_exact=`NOT_MEASURED`. 첫 PATCH 시작10분 조건도 원 구간상15:45 전이지만 시계 보정 전 수치다.
- R2 첫 API APPLIED 원mtime: **15:49:27.941749**, `1792046967941748777 ns`; R2firstPATCH_exact=`NOT_MEASURED`. R2상한−R1하한=**371.113635167초**, 오차 미보정.
- 이전 engine Pod2개 마지막 존재 조회 완료: **15:50:26.995087**. 보다 보수적인 수집 시작 **15:50:26.865217**을 종료 구간 하한으로 두며, 첫 전체 부재 **15:51:34.973257**을 상한으로 보존한다. `terminated.finishedAt`를 합성하지 않는다.
- 회수 관측 완료 상한 **15:51:37.318038**. engine 업무8001은 기존 API Pod 네트워크 공간에서3Pod, API 업무8000은 edge→각 Worker NodePort30080 경로에서3건이다. 후자는 직접 PodIP GET이 아니며, `externalTrafficPolicy=Local`과 노드별 유일한 Ready endpoint UID로 결속했다. 전용9090/9091은6Pod200 및 같은6개 주소의 up=1을 검증했다.
- API 현행 digest `338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0`; engine 현행 `8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d`. **15:58:07.260850** 최종 조회도 동일 Pod6·Ready6·restart0·같은 두 Deployment UID/spec.15:58:06 Runner.Worker0, 기존 Runner.Listener1.

## 시계 검토와 남은 판단

R1 직전15:41:31~33 및 종료 후15:59:16~17 원문이 모두 있다. Runner/control/worker01~03/edge의 boot_id와 chronyd PID·시작시각이 동일하고 Leap Normal이다. wall 경과−monotonic_raw 경과는 각각 **+14.580 / −24.115 / −12.851 / −8.233 / −14.565 / −23.187 ms**로, 관측 끝점에서 큰 불연속의 증거는 없다.

`abs(System time)+Root dispersion+abs(Root delay)/2`로 계산한 **관측 시점** E는 Runner0.002748~0.002869초, control0.071369~0.071435초, worker들0.071282~0.072084초, edge0.003868~0.004615초다. 이는 동기 기준 시계가 정확하다는 전제의 끝점 추정값이다. 두 값의 max나 순 경과 일치만으로 구간 중 최대 오차를 증명할 수 없어, 임의 E=0/1초 또는 유리한 보정을 넣지 않았다. 기존 합의가 지정한 `시한 미입증 / SEC 사후 검토`로 기록한다. **정확 계측을 새로 요구하거나 실행 회차를 반복할 사유로 바꾸지 않는다.**

중앙·CICD 후속: 기존 로컬 증적에서 실제 구간에 적용할 E_host의 근거·적용 범위가 추가되면 `L=Ppending−E_runner`, `U2=R2applied+E_runner`, `Udone=max(각 회수 관측+해당 호스트E)`만 재계산한다. 근거가 없으면 미입증 표지를 유지한 채 SEC 사후 판단으로 넘긴다. 기존 P+30 통지·W+45 만료 기준은 이 증적 판단으로 지연하지 않는다.

16:04 추가 대조: CICD `TIMING_ASSESSMENT.json`의 시한 미입증 판정과6호스트 E_snapshot 계산이 이 독립 계산과 일치한다. 최종 R1/R2 각8개 checkpoint chain도 검증했다. 정리3건은 실제 command/stdout/stderr 해시·rc0·집계본문 일치까지 확인했다. 남은 Token 수명/폐기·dispatch 총계 및 최종 업무 인수는 중앙/CICD가 기존 회차 제출본으로 판단한다. 이 문서는 새로운 서버 확인을 요구하거나 수행하지 않는다. 업무 POST 결과는 R1/R2 모두201·저장/평가 카운터+1로 제출됐지만 DB 일치=`NOT_COLLECTED`이므로 APP/CICD의 업무 인수 항목과 분리한다.

이번 세션은 파일 읽기와 자체 검증/문서 작성만 수행했다. 신규 서버·HTTP·Token·Runner·배포·정책 변경, 외부 댓글 및 타인 위험수용 대행0. Phase1 변경 범위 확대0. 관측 원문/코드 결속은 확인했지만 미수집 NP/GNP/RBAC 전체 변경 이력까지 검증했다고 하지 않는다.

`EDGE4=PASS_OBSERVED / CURRENT_RECOVERY=VERIFIED_OBSERVED / ORIGINAL_BINDING=VERIFIED / CLOCK_BEFORE_AFTER=VERIFIED / TIMING_15_30=UNPROVEN_SEC_POST_REVIEW / ACTUAL_OVERRUN=NOT_ESTABLISHED / AC09_ACCEPTANCE=NOT_ISSUED / WINDOW_RELEASE=NOT_ISSUED_BY_THIS_REVIEW`.
