# K8S17·OID 다음 실행 입력 — 2026-10-13

이권욱 / CODEX_ASSISTED. 이 자료는 기존 인계 범위의 로컬 준비 결과이며 서버 교체·반입 결과가 아니다. 과거 계획에 적힌 미확정 source/metadata는 현행 H02와 이번 읽기로 보완하고, 별도의 Lead 구현 GO를 새로 요구하지 않는다.

## K8S17

`K8S_EXECUTION_INPUT.json`에 5호스트45경로의 10/13 관측값을 연결했다. 대상17개/보존28개는 기존 범위 그대로다. 공급 바이트는 승인 source b4303f2에서 받은4개이며 `k8s-supply/SHA256SUMS`로 묶었다. 전체 운영 디렉터리에 묶음을 풀지 않는다. control01은 audit-window.py만, control03·worker01·worker02·worker03은4개씩이다. control02는 제외한다.

적용 순서: **control01 1개 → 검수 → 나머지4대 한 대씩**. 다음 호스트로 가기 전 해당 호스트의 대상 집합 검수를 끝낸다.

실행 전 실제 호출자 배제와 각 호스트 콘솔 인수, 새0700 백업 위치를 확정해야 한다. ps 순간 목록0이나 기존 코드 승인으로 이 조건을 대신하지 않는다. APP 회차와 겹쳐 운영 파일을 바꾸지 않는다. 이 단계의 실제 파일 교체는 이번 APP Eviction 허용에 포함되지 않는다.

현장 카드 순서:

1. 기존 strict SSH/sudo 경로로 실제 hostname/boot·대상/부모 일반 파일·nlink1·ACL/xattr·SELinux enforcing·free space 및 원래45개 hash를 읽는다. 관측 hash가 이전/목표 어느 쪽에도 없으면 STOP. 목표와 이미 같으면 bytes 재교체 없이 기록하되 metadata 차이는 별도 판정한다.
2. 해당 호스트의 이번 대상 파일만 새0700 백업에 bytes와 uid/gid/mode/ACL/context/xattr를 보존한다. 공급 SHA는 전송 후 다시 대조한다. 원본·백업·임시 복원 사본의 bytes/복원 가능한 metadata를 대조한 뒤에만 설치 후보를 만든다. inode/ctime까지 동일 복원을 요구하지 않는다.
3. 배치 위치와 같은 filesystem의 새 임시 파일에 정확한 공급 bytes를 쓰고 root:root/0750/기본 rwx-r-x---- ACL 및 `system_u:object_r:usr_t:s0`를 적용·재조회한다. compile만 수행하고 모듈 import나 운영 도구 apply/rollback/validate는 실행하지 않는다. 파일별 rename으로 치환하되 다중파일 전체가 원자적이라고 주장하지 않는다.
4. 대상17개 목표 hash와 metadata, 보존28개 기존 hash/metadata를 확인한다. worker01의 보존5개 user_home_t는 이번에 relabel하지 않는다. 모든 관련 도구 호출은 해당 호스트 집합이 완결될 때까지 보류한다.
5. 부분 실패면 같은 호스트에서 **이번에 바꾼 파일만** 확인된 백업 bytes·원래 metadata로 복귀하고 대조한다. 다른 호스트 진행0. 이전 bytes 복귀의 상태명은 `RESTORED_WITH_KNOWN_TOOL_DEFECT`이며 해당 도구 사용 보류를 유지한다. 도구의 cluster-change rollback/서비스 재시작/정책 수정은 파일 복귀 수단에 포함하지 않는다.

서버 backup·restore trial·설치는 아직 미실행이다. 이 공급 묶음으로 코드가 새로 승인되거나 AC가 충족되는 것은 아니다.

## OID02

`OID_INPUT_SUPPLEMENT.json`에 기존 두 이미지의 top/index/platform manifest/config/layer descriptor를 실제10/13 control01 관측으로 채웠다. `control01-oid-layer-bytes`는 고정15개 layer를 읽고 SHA/size를 대조한 별도 읽기 증적이다. 원래 metadata 수집을 고쳐 쓰지 않는다.

실제 확인한 current-cache를 향후 복구 공급원으로 채택할 경우 출처를 **control01 content store의 관측 회차와 export 회차**로 명시한다. 원래 반입 원본·과거 공급 경로가 확인됐다고 소급하지 않는다. 원본 출처를 추정해 빈칸에 쓰지 않는다.

다음 실행에서는 기존 preloaded 경계 안에서 정확한 image refs/platform으로 새 archive를 export하고 archive SHA·member closure·실제 크기를 대조한 뒤 필요한 대상에만 반입한다. export/import 시점의 명령·version·노드·원본/대상 digest·receipt가 필요하다. 이번15개 layer 읽기는 이 과정을 대신하지 않는다. CoreDNS index의 다른 architecture blob까지 확보한 것으로 확대하지 않는다.

시스템 이미지 공급을 위한 CP→Harbor/외부 registry 허용0. Worker 앱 이미지 공급과 별개이며 OID03 미해결을 자동 해제하지 않는다. 한정 reboot는 앱 분산·local PV·정책 지속성·콘솔 복구·대상 cache를 먼저 확정한 별도 회차이고 전6대 reboot를 새 요구로 추가하지 않는다.

현재 `archive_created=false / import=false / target_cache_verified=false / reboot=false / plan_ready=false / AC=false`를 유지한다.
