> 최종 현황: 이후 사용자가 시작 마감16:45/종료17:00을 명시 승인하여 추가 Run38364658401을 실행했다. 새 transaction-api 이미지의 파일 권한 오류로 실패했고 이전 이미지 복귀·두 앱 각Ready3을 확인했다. [추가 회차 결과·원인·수정안](../deploy-additional-20261013T1645/README.md)이 현재 판정이다. 아래 내용은 해당 준비/첫 회차 시점의 이력으로 보존한다.

# Deploy 구체 입력·복귀안 — 2026-10-13

CODEX_ASSISTED · 준비/통합 실행 책임 이권욱. **입력 준비 완료, 실제 배포 미실행, Runtime 미승인.**

이 문서는 사용자 “권장안으로 착수”에 따라 기존 [baseline PR166](https://github.com/321Team/fds-project-baseline/pull/166)의 Deploy 선행 준비를 수행한 결과다. 기존 Source·Push 결정을 재요청하지 않는다. DB 최종 인수는 사용자 결정대로 최종 앱 회귀 뒤에 판단한다.

## 1. 실제 확보한 값

- CICD main/검토 구현: `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`. 준비 시 원격 main 및 로컬 clean checkout 일치.
- APP Source: `affbc69beef9967f7977d09a6fec14f7fb6c0e94`, [APP Lead 입력 확정](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6074515472).
- TBS Run `37890963668`/Attempt1 → [Push Run38318968352](https://github.com/321Team/infra-cicd/actions/runs/38318968352)/Attempt1, [증적208 병합](https://github.com/321Team/fds-project-evidence/pull/208). 현재 준비에서 재빌드·재Push하지 않았다.
- Push result 원문 SHA256 `012545c60017ab1120ab9b61459451a794c67b7a0a803d4f079798b5ed97f905`. 병합된 원본의 base64를 로컬에서 복원하고 기존 hash와 대조했다. 이전 Push 허용창은 만료됐으며 새 Deploy 허용으로 재사용하지 않는다.
- 새 plan UUID `2fb09791-d0ca-443f-9c1b-77747c3f3a73`; 정확 파일 [deploy-plan.unapproved.json](deploy-plan.unapproved.json), SHA256 `5c2d8367f5b81875693165055234a30e5c69944e345c8ad8c5277ef30ebd8387`.
- plan의 `template_only=false`는 실제 관측을 채운 구체 입력이라는 뜻이다. **승인 문서/Deploy record/Run은 아직 없고, 실행을 허용하지 않는다.**

15:39:44~45 KST 읽기에서 두 앱 replicas/ready/available/updated=각3, 현재 UID·spec/image·SA UID·CA가 이전 관측과 동일했다. fds-app의 배포 변경 권한은 두 이름으로 한정됐고 HPA0이다. CP1 기존 정상계정 named SA GET 및 Runner→API TLS1.3 검증이 성공했다. Secret 값 조회·TokenRequest·TokenReview·Runner SA 인증·서버 파일 배치·API 변경은 하지 않았다. [cluster](cluster/stdout.json), [CP1](cp1-auth/stdout.json), [Runner](runner-auth/stdout.json).

| 대상 / fds-app | UID | 배포 image digest | 실패 시 이전 digest |
|---|---|---|---|
| transaction-api | `8a2af808-ec33-41f2-80b5-addde4e28910` | `sha256:ef0afe42feb0f9e50f54b5aaab99a34bbeb01f10bc9fb8a0580519101645dc39` | `sha256:a7093136d12640da00570c18ed278eacbb8e9ba3637c7d509571346eac45cc33` |
| fds-engine | `bf825dec-465b-4603-8b71-f768d195531c` | `sha256:de34afb7a557d6ccc844fb74613ebc971eb493260236acc35ef3051935122813` | `sha256:5e2a081cd51a957c3fad038b3eab07884c446ea3c2a814a905e3f41c24f67369` |

registry prefix는 `10.1.93.54/fds/<서비스>@`다. replicas·NetworkPolicy·RBAC·DB·노드 상태를 변경 대상으로 추가하지 않는다.

15:48:05~07 KST Worker01/02/03의 CRI image 목록에서 **이전 두 digest 모두 존재(6/6)**를 확인했다. 각 명령 rc0, 내부 stderr135B(원문 대신 hash 보존), 원격 Python 외부 stderr0B다. IfNotPresent 및 현재 구동 상태와 함께 복귀 준비에 소비한다. 이미지 layer 바이트 전수 검증·Harbor 재Pull·실제 복귀 성공은 미검증이다. 레지스트리 불통 때 공급 성공을 보장하지 않는다. cache-worker*/stdout.json에 원본 투영 결과를 보존했다.

## 2. 제안하는 1회 실행 범위 — 아직 승인값 아님

**후보 시간창: 2026-10-13 16:15~17:00 KST.** Harbor manager 변경·사후 관측이 종료되고 동시 작업이 없음을 실행 직전에 확인한 경우에만 시작한다. 16:30까지 조건이 안 되면 이 후보 창에서는 dispatch하지 않고 시간창을 다시 정한다. H6 전체 종결을 새 공통 gate로 추가하지 않는다.

실행/중단 관측은 이권욱이 맡는 안이며, 콘솔 접근 가능 여부는 실행 전에 확인한다. 후보 시간창·콘솔 대기·다음 복귀 범위의 사용자 확정이 필요하다. 기존 Source/APP Lead 입력의 재승인은 필요 없다.

1. 이 문서의 plan bytes/hash와 후보 창·복귀 허용을 사용자 결정에 결속한다. 기존 구현 형식의 detached approval을 infra-cicd #11 GWONUK JSON 원문으로 기록한 후 readback한다. approval은 plan/Workflow SHA·start/end·allow_rollback을 포함한다. 승인 원문을 받기 전에 승인자·시각·허용값을 가공하지 않는다.
2. 현재 main/Deployment UID·image/spec·readiness/SA UID·CA·Harbor 비중첩을 재조회한다. 다르면 기존 계획으로 진행하지 않는다. 원본/입력/해시의 필요한 독립 검토를 확인하고, 새 approval+원 Push receipt+plan+SA UID를 묶은 record의 정확한 bytes/hash를 고정한다.
3. 기존 보호 경로에 이번 소스/입력만 배치한다. ansible01 정상계정 HOME 아래 UUID 전용 새0700 디렉터리, Runner HOME의 `FDS_CICD_DeployInputs`0700 및 `deploy-2fb09791-d0ca-443f-9c1b-77747c3f3a73.json`0600을 사용한다. 기존 파일/디렉터리 덮어쓰기·키/known_hosts/RBAC 변경은 없다. 배치 시 소유·권한·symlink·hash를 대조하고 경로를 실제 수신 기록에 남긴다.
4. 기존 `app-deploy.yml`을 main 고정 SHA에서 `execute=false` 1회 실행한다. 성공 기준: `PREFLIGHT=SUPPLIED_BYTES_MATCH`, `TOKEN_ISSUED=false`, `DEPLOY=NOT_EXECUTED`. 이 단계도 Runner 증적 디렉터리를 만드는 실행이므로 순수 조회로 표시하지 않는다.
5. 별도 새 Run/Attempt1로 `execute=true` 1회. 실제 dispatch의 Run/Workflow/record/plan/SA를 확인해 broker binding을 만든다. 기존 ansible01 broker와 CP1 기존 키로 native SA 최신 확인·TokenRequest900초·TokenReview·비공개 Runner 전달을 수행한다. broker 대기120초, 발급 허용 잔여640초 조건을 유지한다. 별도 token 진단 회차는 추가하지 않는다.
6. 정상 기준: 실제 Session 반환, `ROLLOUT=READY`, error 없음, 두 target 새 digest/ready 각3, 실행 Run·journal·정리 결과 수집. 이후 업무/DB TLS·Probe·업무 포트 `/metrics` 차단 등을 APP/HA 카드에 따라 따로 검증한다. rollout만으로 HEALTH_E2E/Delivery/DB 인수하지 않는다.

controller package는 기존 `deploy-controller-2d8a14c.tar`(13members,266240B), SHA256 `67df6be5d7f935f2618e55365b7c3f0250bea99b771a579873e7961f9061f261`; remote7파일 bundle SHA256 `8cfdcce5e4b5eb95001d27e35606e5121edf77d8c2c1f5f481016c79933baa5c`를 재검증해 재사용한다. 패키지 재작성/재업로드는 아직 없다. 실제 인자·계정·키 경로는 [기존 실행 카드](https://github.com/321Team/infra-cicd/blob/2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7/docs/deploy-workflow-handoff.md) 및 cluster/cp1-auth/runner-auth receipt에 결속한다.

## 3. 중단·복귀 조건

- UID/hash/승인/시간/권한 불일치, 동시 변경, 연결 이상, 복귀 전제 상실 시 중단한다. 발급/배포 여부가 불명확하면 actual Run/result/claim/Deployment를 먼저 대조한다.
- 복귀 허용 제안은 **이번 두 Deployment의 위 이전 digest에 한정**한다. 기존 구현의 checkpoint와 승인/자격증명 유효기간 내 복귀 조건을 따른다. 다른 리소스 변경·DB 복구·새 token 발급·claim 삭제·자동 rerun은 포함하지 않는다. 창/자격증명 만료 또는 판단 불명확이면 상태를 보존하고 수동 인계한다.
- 이전 이미지로 복귀하면 업무 포트 `/metrics` 노출도 돌아온다. 이는 새 제한의 영구 위험수용이 아니다. 복귀 시 해당 한계를 명시해 #15/#19에 기록하고 업무/Ready/DB TLS와 보안 종료 상태를 확인한다.
- 소켓/참조 정리는 해당 실행이 만든 대상에만 수행한다. claim/journal/로그는 보존한다. 참조 해제를 서버측 token 폐기로 표현하지 않으며 원래 TTL까지 유효할 수 있다.
- 성공 후 순서는 최종 배포 형상 고정 → 별도 허용된 단일 Worker HA/원복 → 최종 앱 회귀 → DB 최종 인수 판단이다. 이번 배포 허용을 drain/reboot/전체 인수로 확대하지 않는다.

## 4. 검증 범위와 후속

- STATIC: 기존 pure payload validator, plan 필드/schema/두 target/Push hash·context·image 일치, 기존 package2개 hash 확인. validator의 실제 Run 관련 인자는 메모리 내 STATIC sentinel1을 사용했으며 실제 Deploy Run으로 기록하지 않았다. [PLAN_VALIDATION.json](PLAN_VALIDATION.json).
- RUNTIME_READ: cluster GET5건, CP1 named SA GET, Runner TLS, Worker3개 CRI images. 각 collector source REVIEW=NOT PERFORMED (Pre-check); 독립 소스 리뷰 완료로 표시하지 않는다. 수집 source·argv·시각·receipt·hash 보존.
- 미실행: server staging, false/true dispatch, native token, 배포, 복귀, HA/최종 E2E. detached approval/실제 context 전체 검증도 미실행.
- 새 증적 편입의 독립 검토/병합과 실제 사용자 Runtime 결정은 별개다. 새 과거 감사·접근 배타성 입증 또는 Phase1 완료를 선언하지 않는다.
- Grafana 증적 [PR212](https://github.com/321Team/fds-project-evidence/pull/212)는 승인 HEAD `d4cb2f7f38108e04972ecdd721528e4db0cdc340`에서15:38:14 KST merge `44beaf0f4b44b0286b26e1d08196db8223ef7a1e`로 편입됐다. 책임자 확정/현재 선언 조회의 범위를 유지한다.
- Harbor8앱 후속은 [15시 완료 기록](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6139379896)을 소비한다. manager 설치/H6는 별도 구축 작업 중이며 이 준비가 작업창을 점유하지 않는다.
- Runner는 새 장애 주입/중복 알림 실행을 하지 않고 기존 #61에서 최초 schedule 및 실제 필요한 장기 대기 수신을 추적한다. O01 재현과 O02를 구분한다.
