> 후속: 이 문서는00:01~00:14의 당시 관측을 보존한다. 앱 집중은 이후 승인 회차에서 복구됐으며, 현재 판단은 [분산 복구·추가 검증 결과](p1-redistribution-followup-20261013.md)를 함께 따른다.

# Phase 1 독립 후속 작업 결과 — 2026-10-13 KST

이권욱 / CODEX_ASSISTED. 사용자 “리뷰 대기 건 제외 … 권장 순서대로 착수”에 따라 실행한 읽기 수집·대조 결과다. 시작일이 10/12여서 로컬 폴더 이름은 20261012이며 서버 관측은 10/13 00:01~00:10 KST다. 기존 PR164(DB/DR/C01)·207(MON) 리뷰 대상과 Harbor 구현은 변경하지 않았다.

## 결론과 순서 수정

**현재 앱 Pod 6개가 모두 worker02에 집중돼 있다.** 각 Deployment Ready3/3와 노드6대 Ready는 확인했지만, Worker3대 분산은 유지되지 않는다. 따라서 worker02 DNS 변경·Drain·재부팅을 먼저 하면 앱 전체에 영향을 줄 수 있다. 해당 변경은 시작하지 않았다. 현재 HTTP 장애나 집중 원인을 이번 읽기 결과로 단정하지 않는다.

1. 앱 배치 집중의 복구 회차를 먼저 구체화한다. 기존 분산 조건을 유지하고, worker01/03의 해당 이미지·실행 가능 상태, edge Local endpoint 관측, MON과 비중첩을 확인한 뒤 앱 하나씩 단계적으로 분산시킨다. 모든 Pod 일괄 삭제, worker02 Drain을 분산 복구 수단으로 쓰지 않는다. 기존 Deployment UID/image/template을 기준선으로 보존하고 예상 외 형상·Ready 감소·재배치 실패이면 다음 변경을 중단한다. 이번 패키지는 복구 명령 실행이나 그 결과가 아니다.
2. K8S17파일은 별도 도구 호출을 배제할 수 있는 회차에 진행 가능하다. 현행 해시가 기존 계획과 같고 공급 바이트도 확보됐으므로 같은 소스의 전체 코드 리뷰는 반복하지 않는다. 서버 새 백업·복원 확인·동시 호출 배제 및 복구 콘솔 조건을 채워 control01의 audit-window.py 1개부터 적용하고 이후 대상에 확대한다.
3. OID는 이번에 확보한 2개 이미지 메타데이터를 기존 오프라인 공급 계획에 반영한다. 실제 layer 내용·export/import·대상별 cache·reboot 검증은 구분한다. 전 노드 재부팅이나 공급 출처를 소급 생성하지 않는다.
4. worker02 DNS는 앱 분산 복구 뒤에 기존 단일 회차 prepare/apply/reapply/rollback을 진행한다. 목표와 현재 DNS가 같으므로 고의 drift를 만들지 않는다. 이미 같은 값에서 무변경으로 끝나면 그 범위만 인수한다.
5. Runner 두 번째 운영자는 다음 실제 필요한 Job 공급 회차에 함께 인수한다. 조회 시 queued0/in_progress0/등록 Runner0이므로 연습 목적으로 완료 CI를 재실행하지 않는다.
6. Delivery/APP의 실제 후보 배포 후 영향받은 HA 한정 시험과 Final E2E를 연결한다. 현재 집중 위험은 먼저 다루되 최종 이미지 전에 전체 회귀를 반복하지 않는다. 격리 Harbor 복구 전체 완료를 운영 Delivery의 새 공통 Gate로 만들지 않는다. 실제 사용하는 Registry의 현재 health·scan/TLS/Robot 및 자원 비중첩은 필요하다.
7. 위 결과와 기존 독립 리뷰를 기존 AC/Exit에 연결한다. 이번 문서·읽기 성공으로 AC 체크·Close·정본 Freeze를 올리지 않았다.

## 실제 수행

| 작업 | 이번 결과 | 아직 수행하지 않은 것 |
|---|---|---|
| HA 형상·현황 | control01 API GET9종 rc0, 앱2개/Pod6개/서비스·EndpointSlice·노드·PDB/PV/PVC 확인. 10/7 서버 YAML과 선택한 spec 필드 차이0. 이미지도 10/2 표본과 동일하지만 배치는 worker02 집중 | HTTP/POST/DB 요청, Drain, 배치 복구, 최종 HA 인수 |
| K8S17파일 | 5호스트×9파일=45, 이전 관측과45/45 동일. 목표 일치28·교체17. 승인 소스 b4303f2와 현행 main92c182f의9파일씩18blob 모두 계획 SHA/크기 일치 | 파일 교체, 서버 백업, 복원시험, ACL/context 변경, 도구 실제 호출 |
| OID02 | 승인 수집기 PR68 HEAD8593956 원본17349B/SHA ccdaaee… 일치. control01의 두 이미지 메타데이터 읽기7명령 rc0, 두 이미지 linux/amd64 manifest/config 확인 | layer bytes·원래 공급 출처·archive 크기·export/import·재부팅 |
| Ansible | worker02 DNS .52/.53, fds.internal, ignore-auto-dns yes; NM/kubelet/containerd active, SELinux Enforcing. 컨트롤러 source0d58598·tracked clean·고정5파일 동일, 후보 CLI4종2.21.3 | prepare/apply/reapply/rollback, 전역 엔진 전환 |
| Runner | 00:14 REST 읽기3건 rc0, queued0/in_progress0/등록0. 다음 운영 인수 카드 정리 | 신규 Job/Runner/token, 두 번째 운영자의 실제 수행·상시 알림 |
| Delivery/최종 인수 | 현행 Deployment UID·image·Ready를 다시 연결하고 후보/현재/복귀를 분리, 잔여 입력을 아래 한 표에 고정 | 후보 Push/Deploy, rollback 승인·실행, 새 Final E2E·최종 인수 |

실패도 보존했다. Ansible 최초 버전 조회는 수집기가 설정한 LC_ALL=C 때문에4개 모두 rc1이었다. 영향받은 버전 조회만 프로세스 범위 C.UTF-8로 재수행해 locale UTF-8 및 CLI4종 rc0을 확인했다. 시스템 locale은 바꾸지 않았다. OID 전달 wrapper의 로컬 placeholder 구문 오류는 SSH 전에 발견·수정됐으며, 실제 OID 수집은1회다. 로컬 Windows 증적 checkout의 긴 경로 오류는 새 checkout의 core.longpaths 설정으로 해소했다.

## 주요 근거와 해석

### HA: 과거 결과 보존, 현재 Exit는 분리

- [10/2 제한 수용](https://github.com/321Team/fds-project-baseline/issues/22#issuecomment-5965966537): worker02 1회 `/readyz` GET, A 실패0/B최대0.510초/누락tick0. 기존 AC8/8 이력은 보존한다. 9/27 NOT_VERIFIED는 합산하지 않는다.
- [10/7 PR65](https://github.com/321Team/infra-kubernetes/pull/65): 분산 조건 적용 뒤 각 Worker당 앱1개였다. 현재에도 maxSkew1/DoNotSchedule/nodeTaintsPolicy Honor/matchLabelKeys 조건은 남아 있으나 실제 Pod·ready endpoint는 worker02에만3개씩이다. transaction-api-nodeport는 externalTrafficPolicy=Local이다.
- 대조는 보존한 YAML의 replica/strategy·이미지/자원·probe·SA/분산/선택 storage 등 **수집기 투사 필드에 한정**한다. 모든 manifest/보안 설정·env 값이 같다는 주장이 아니다. annotations/env literal/credential을 내보내지 않았다. 현재 generation은 transaction-api9/engine5다.
- [Kubernetes 공식 설명](https://v1-36.docs.kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)의 제한대로 분산 조건은 새 Pod 스케줄링에 사용되며 기존 Pod의 자동 재분산 증거가 아니다. 현황은 이 특성과 양립하지만 집중의 발생 원인·시각·과거 node 가용 상태는 이번 결과만으로 확인하지 못했다. 새 descheduler/PDB 도입을 Phase1 잔여로 추가하지 않는다.
- fds-app PDB0/PVC0. 클러스터 PV3개는 worker03의 MON local PV이며, 이를 이유 없이 포함하는 전체 node Drain은 추가하지 않는다. worker02 집중은 과거 성공을 무효로 만들지 않지만 현재 전체 HA/Exit 완료를 주장할 수 없게 한다.

### K8S: 기존 17개 범위 유지

- control01 변경1개, control03·worker01·worker02·worker03 각4개. control02 제외.
- 모든45파일 root0:0/0750, 기본 rwx/r-x/--- ACL. 수집 중 파일/부모 메타데이터 안정, SELinux enforcing. 프로세스 순간 목록0은 향후 도구 호출 배제를 증명하지 않는다.
- worker01의9파일은 user_home_t, 나머지36은 usr_t이며 관측 label user는 unconfined_u다. 기존 H02 목표 system_u:object_r:usr_t:s0는 교체17개에 적용할 값이다. worker01 보존5파일·부모 디렉터리까지 몰래 확장하지 않는다.
- 새 source 공급은 로컬 바이트 확보까지만 했다. 오래된 비공개 백업 준비물을 새 서버 백업으로 표시하지 않는다. 복원은 bytes/mode/ACL/context 대상이고 inode/ctime 동일 복원은 보장하지 않는다. 과거 도구 결함으로 복귀하면 기존 RESTORED_WITH_KNOWN_TOOL_DEFECT 제한을 유지한다.

### OID: 두 metadata 공백 해소

| 이미지 | linux/amd64 manifest | descriptor+읽은 문서의 고유 바이트 합 |
|---|---|---:|
| kube-controllers | df00967cbd6d88e1ff3123e1598895845622e2987928b4ebd9d8ac49aefe00c3 | 61,097,614 |
| CoreDNS | fd5079792b93909db3adefa91e41c3995455013394f0197c7346786ae19079fc | 23,257,541 |

위 합계는 tar 용량이나 실제 layer 읽기 검증이 아니다. CoreDNS top index e7e6440…와 단일 platform manifest를 구분했다. 현재 control01 cache는 관측 출처이며 최초 공급 provenance가 아니다. 승인된 수집기 바이트를 anonymous Linux memfd에서 실행해 지속 파일을 배치하지 않았다. config 원문 Env/Labels/History는 수집기 내부에서만 읽고 폐기했다. plan_ready=false/AC=false를 유지한다.

## 남은 입력 — 중복 회신을 요구하지 않는 단일 목록

| ID | 필요한 사실·결정 | 누구/언제 | 이미 끝난 것으로 재요구하지 않을 것 |
|---|---|---|---|
| HA-1 | 분산 복구 회차의 대상 UID/image·worker01/03 실행 가능성·edge/MON 관측·실제 비중첩/복귀 인수 | 이권욱, 다음 공유클러스터 변경 전 | PR65 코드 재설계, 과거 HA 전수 재시험 |
| K-1 | 도구 호출자 배제·해당 호스트 콘솔·새 백업과 부분 복원 검수 | 이권욱, 파일 교체 직전 | 기존 승인 소스 재리뷰·45파일 재작성 |
| O-1 | 현 cache를 복구 공급원으로 사용할 범위, layer/패키지/대상별 검증·한정 재부팅 카드 | 기존 OID 담당 범위로 이권욱 실행 | 이번2이미지 metadata 재수집, 원 공급 출처 추정 |
| A-1 | worker02 콘솔 인수·NM 타작성자 배제·실제 단일 회차 범위 | 이권욱, HA-1 후 | DNS 고의 변경, engine 전체 재설치 |
| R-1 | 적격 두 번째 운영자, 실제 필요한 Job, 참여 시각/기존 접근, queue 관측·알림 인수 채널 | 실제 공급 회차 확정 후 이재환 또는 적격 대체자 참여 확인 | H01/J01 보관 수령 회신, 완료 CI 재실행 |
| D-1 | fresh scan/Robot/TLS·push receipt·한정 credential 잔여·target/rollback·비중첩 | 실제 Delivery 회차 직전 이권욱/운영 Registry 책임 | Harbor 타세션 구현/복구 코드 중복 작업 |
| F-1 | 최종 이미지·배치에서 HTTP/Rule/DB·metrics·해당 HA/rollback 결과, 독립 증적 리뷰/유효 제한 처분 | 실제 실행 뒤 기존 AC/Exit에 연결 | Initial E2E를 Final로 명칭만 변경 |

현재 운영 image는 API a7093136…/engine5e2a081c…이며 승인 공급 후보 API ef0afe42…/engine de34afb7…와 다르다. 후보 source affbc69beef9967f7977d09a6fec14f7fb6c0e94, supply source8eac4c982076e3c219840a13686b15c46879981f를 유지한다. current main을 새 승인 후보로 치환하지 않는다. 현재 이미지가 관측됐다는 사실은 rollback_approved=true가 아니다. 기존 이미지 복귀 시 업무 metrics 노출이 되돌아올 수 있다는 제한도 유지한다.

R-1은 [기존 O02 카드](https://github.com/321Team/fds-project-baseline/blob/4e9f8d61f8ec8c4cfc8adca29c2fae020a3c0d49/governance/handoffs/phase1-execution-20261010/SESSION_AND_HANDOVER.md)를 사용한다. 실제 Job이 생기면 정확한 Run/Attempt/Job/HEAD/labels·fresh 인증·기존 Runner 충돌 확인 → 한 번 공급 → Job관측 → deregister/proxy/workspace/token 정리 → operator identity·명령/rc·receipt를 보존한다. 실제 실패면 그 단계에서 중단/인수하고 재공급하지 않는다. 아직 Job이 없으므로 운영자 실습 완료도, 상시 알림 완료도 아니다.

## 증적과 단계

- 수집기 자체 결과와 SSH 수신 바이트는 각 receipt 폴더에 보존했다. HA API·OID 내부 원문 전체는 영구 보존하지 않았으며 투사/검증된 출력과 응답 해시만 남겼다. 해시만으로 폐기한 원문을 재구성하거나 완전한 API 응답이라고 주장하지 않는다.
- K8S collector·HA projection·Ansible 읽기 collector는 이번 작성한 순수 검증기다. **REVIEW=NOT PERFORMED (Pre-check)**. OID collector만 PR68 v2 독립 승인 소스다. 새 SSH/memfd 전달 wrapper까지 기존 코드승인 대상이라고 확대하지 않는다.
- STATIC: 수집 소스 구문·고정 source/hash 대조. RUNTIME: 명시한 읽기만 수행. MOCK/CI: 이번 서버 수집의 성공 근거가 아님. 파일/정책/DNS/앱/서비스 변경0, token 발급0. SSH·sudo·감사 로그 등 통상 접근 흔적까지0이라는 뜻은 아니다.
- REVIEW/MERGE/PUBLICATION: 실제 증적 PR의 결과를 별도로 따른다. PR 등록은 독립 승인·병합이나 AC 인수가 아니다.

기계 판독 대조본: HA_ANALYSIS.json, K8S_ANALYSIS.json, K8S_SOURCE_BINDING.json, OID_ANALYSIS.json, ANSIBLE_ANALYSIS.json, RUNNER_READINESS.json. 기존 PR164·207의 리뷰를 우회하거나 재요청하지 않았다.
