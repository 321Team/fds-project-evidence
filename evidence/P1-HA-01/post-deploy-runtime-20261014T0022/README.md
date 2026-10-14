# 새 Deploy 후 Worker02 단일 HA 실제 결과

이권욱 · CODEX_ASSISTED · 2026-10-14 KST. **RUNTIME=HA PASS 및 분산 복구 확인. 신규 증적 독립 REVIEW/MERGE=PENDING.**

## 범위와 연결

- [PR220](https://github.com/321Team/fds-project-evidence/pull/220)의 준비 HEAD `0340ce3feaf22dcf25d736e1b3ee8f537de54d06`, 독립 승인 supreme33-kr, merge `9a0d320f3440bd7a244f1ecdc702ebac64409769`에 따른 새 회차 `p1-ha-20261014-0015`다.
- 사용자 `착수` 및 `01:05까지 콘솔 대기·비중첩 확보`를 `AUTHORIZATION.json`에 기록했다. 시작창 00:15~00:25, 종료 01:05를 유지했다. 실제 probe는 **00:22:02~00:37:02 KST** 1회이며 재실행하지 않았다.
- 새 Deploy [PR219](https://github.com/321Team/fds-project-evidence/pull/219)의 API digest `338b8a28…`, engine `8b257adb…`, Deployment/RS와 전체 digest는 `READINESS_BINDING.json` 및 전후 수집값으로 고정한다. 이미지·Deployment spec 변경0.
- 기존 [P1-HA-01 #22](https://github.com/321Team/fds-project-baseline/issues/22) 인수 이력을 대체하지 않는다. 새 이미지·분산 제약 영향만 확인했다. 기존 HA probe/judge bytes를 그대로 사용했으며 별도 HTTP Probe 실패 주입, 업무 POST/APP 회귀, DB 쓰기는0회다.

## 실제 변경과 회복

| 단계 | 실제 결과 |
|---|---|
| 진입 | CP1 boot/cluster/worker02 UID, Deployment UID/generation/spec, 기존6Pod UID·imageID, all-namespace selector 2개, PDB/HPA0, Ready/시각/cache/자원, HTTP/MON 재확인 |
| 준비 파일 | 새 edge 및 CP1 디렉터리0700, 공급2파일0600·SHA 확인. 기존 파일 덮어쓰기 없음 |
| 측정 | edge svc_ansible, 초당6 GET·900초·1801ticks·5403건, outstanding0·saturatedFalse·rc0·프로세스 종료 확인 |
| drain | CP1 기존 sudo/admin.conf, worker02 `app in (transaction-api,fds-engine)` native drain1회·rc0, 지정2Pod만 퇴거 |
| 재배치 Ready | 두 앱 각3Ready, worker02 앱0. drain 시작→관측 Ready37.7초 |
| uncordon | native uncordon1회·rc0, 동일 Node UID 및 unschedulable=false readback |
| W 종료 후 분산 | engine 신규 Pod `fds-engine-65479b5bf-d6kkm` UID6d83bdd9… 1개 → 회복 → API `transaction-api-666c98b5f5-lq66r` UID853a49a2… 1개. 각 fresh UID/RV 조건, grace30, Eviction Status Success. 추가 총2개·반복0 |
| 최종 | 앱별1/1/1·각3Ready·restart0, 전용 MON6개 포함 up23/23, 각 Worker readyz200·업무 metrics404, worker02 schedulable |

native 명령·실제 시각·종료 코드·UID/RV·원본 stdout/stderr는 단계별 디렉터리와 `control-originals/`, `edge-originals/`에 있다. `receive-control/`, `receive-edge/`가 원격 바이트·SHA·mode/owner와 수신 바이트 일치를 연결한다. 원격 원본은 지정된0700/0600 경로에 보존하고 상주 서비스·계정·Secret을 만들지 않았다.

## HA 판정

원 CP1 `timeline.txt`5줄을 사후 수정 없이 edge에 동일 바이트로 전달해 기존 judge로 판정했다. 수신 원본을 PC에서도 같은 judge로 대조했다. 원격 judge rc0과 출력이 일치한다. Windows 로컬 검증기의 최초 문자 디코딩 오류는 UTF-8 출력·플랫폼 줄바꿈 처리로 수정했으며 서버 판정·원본 bytes를 바꾸지 않았다.

- W **00:23:00.483~00:27:48.136 KST**, 287.7초·575ticks·1725요청. 기준선81.6초 / 재배치 Ready 뒤78.3초 / uncordon 뒤90.2초.
- W 전체 측정, 누락tick0, 발사 지연>0.2초0건(최대0.017초), 기준선 비200=0.
- A: 정상 Worker01/03 비200 **0건**. B: 성공 응답 최대 간격 **0.516초 ≤1초**. **PASS**.
- 대상 Worker02 비200 **412건**은 Local 경계에 따른 허용·별도 기록이다. W 종료 뒤 분산 복원은 HA 판정에 합산하지 않는다.
- 로그 SHA256 `9db6f23d453b7d6c0e6fb4f05b667e7692060019daab1777306965b2e538c4c8`, timeline SHA256 `050bb8899236d42d3929b8ff22b2296f77a1e7401bd90e6cfa924bfc3c9333d2`.

## 관측 보조 코드 오류와 정정

`engine-recovery`는 실제 Prometheus 응답에 없는 `pod` 라벨을 기대해 `MON_TIMEOUT`으로 중단됐다. Pod/서비스 실패로 판정하지 않고 다음 API 퇴거를 보류했다. 원본 `rc2`, 전체29응답 및 최초 source를 그대로 보존한다.

실제 응답은 `job`, `instance=PodIP:전용port`를 사용한다. 새 Pod 상태와 이 두 필드로 재대조한 결과 **29/29 모두 현재6대상·전체23up**이었다. 첫 정상 MON 관측은 최초 Ready 확인 후90초 이내다. 새 읽기 전용 보완 관측에서 동일 Pod UID·1/1/1·MON의30초 안정을 확인한 뒤 API1개만 진행했다. API 관측은 수정된 조인을 사용했다. HA judge/원본/기준 변경, probe/drain/Eviction 재실행은 없다.

`engine-observer-supplement/` 및 `control-originals/fds-engine-recovery-supplement.json`에 정정 근거와 새 관측을 구분한다. 수집·대조 보조 코드는 **REVIEW=NOT PERFORMED (Pre-check)**이며 이를 독립 리뷰 완료로 표시하지 않는다. 변경 명령은 PR220에 명시된 기존 native 명령의 이번 회차 입력·실행 기록이다.

## 검증·한계·후속

- `verify_result.py <이 수집회차 절대경로>`는 원본 receipt/해시, 기존 judge, 범위/순서, 최종 이미지·spec·Pod·MON과 정정 근거를 읽기 전용으로 확인한다. `VERIFIED_RESULT.json`은 실행 당시 자체 검증 결과다.
- 이 PR은 신규 증적 편입이며 독립 리뷰와 병합은 아직 대기다. 원본 진위/AC 인수는 SHA 일치만으로 확정하지 않는다. 기존 PR220의 입력 승인을 이 결과 PR의 승인으로 복제하지 않는다.
- 다음은 정확한 HTTP Probe 실패 주입 범위 확정, **동일 KST 날짜05:00 이후** 최종 APP 회귀다. 이번 회차에 포함되지 않는다. DB#11은 사용자의 **최종 앱 회귀 후 판단**, W4 전체HTTP5xx는 **NOT_MEASURED**를 유지한다. Phase1 전체 종결·티켓 상태 변경은 수행하지 않았다.
