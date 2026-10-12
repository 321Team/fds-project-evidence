# Phase 1 병행 준비 — 기존 Deploy 인증 경로와 OID03 설치 현황

이권욱 / CODEX_ASSISTED. 2026-10-13 04:26~04:29 KST 읽기 수집. 새 Phase 2 작업·TokenRequest·Deploy·재부팅·정책 변경은 수행하지 않았다.

## 실제 해소한 항목

`ansible01/server01_ansible → control01/server02`의 기존 인증 경로를 확인했다. 앞선03:13의 `p1_ansible_ed25519` 인증 실패는 보존한다.04:26 공개키 지문 대조에서 기존 `id_ed25519.pub`와 server02의 기존 authorized_keys가 일치했고, 해당 키 파일을 사용한 **정상 server02 SSH 접속 및 SA GET rc0**를 확인했다. 신규 키·authorized_keys·host trust·권한은 변경하지 않았다.

- CP1 key 경로: `/home/server01_ansible/.ssh/id_ed25519` (기존 파일, UID1000/0600).
- Runner key는 앞선 성공 경로 `/home/server01_ansible/.ssh/p1_ansible_ed25519`를 유지한다. CP1과 같은 키라고 가정하지 않는다.
- CP1 공개 CA SHA256 `5e4462b48b67aa3c452119f02578feb5b2ace358782c9b050ba0ad2ea951a49c` 일치.
- 기존 `/home/server02/.kube/config`로 TLS 검증을 유지한 `ci-cd/cicd-runner-sa` GET, UID `8f1ddfef-7bec-4b15-8cb7-c4b1a068a176` 일치.
- 이 결과는 native broker staging·TokenRequest·TokenReview·Runner SA 소비의 성공을 대신하지 않는다. kubeconfig/개인키/토큰 내용을 수집하거나 게시하지 않았다.

실제 수집은 [정상 계정 결과](cp1-existing-auth/stdout.json), [명령·시각·RC](cp1-existing-auth/receipt.json), [공개 지문 대조](broker-key-metadata-controller/stdout.json)와 [CP1 지문·metadata](broker-key-metadata-cp1/stdout.json)에 연결한다. sshd의 `-C` 값은 controller route의 Source이며, CP1 관측 peer/reverse hostname까지 검증한 것으로 확대하지 않는다. 실제 로그인·GET의 성공은 별도 직접 증거다.

## OID03 입력을 좁힌 결과

6노드에서 기존 설치 경로·RPM DB 소유 정보·지정 cache·부팅 unit metadata를 읽었다. [호스트별 요약](OID03_INVENTORY_SUMMARY.json)에 각 원문·receipt가 연결된다.

| 항목 | 이번 관측 | 남은 한계 |
|---|---|---|
| kubeadm/kubelet/kubectl | 6대 모두 RPM DB `1.36.4-150500.1.1`, x86_64 | 설치 RPM 원 archive·서명·binary bytes 검증 아님 |
| containerd/ctr | 6대 모두 containerd.io `2.3.5-1.el10`, x86_64 | 최초 반입 출처·재설치 공급물 증명 아님 |
| crictl | CP3대의 PATH/기존4경로에서 미발견, Worker3대 기존 파일은 RPM 소유 조회rc1 | 임의 설치하지 않음. 전체 디스크 부재나 출처 판정 아님 |
| 지정 RPM cache | 6대 `/var/cache/dnf` 각각28파일 검사, 정해진 패키지 접두사의 RPM0, 검색 상한 미도달 | 다른 보관소의 공급물 부재로 확대하지 않음 |
| unit 현재 상태 | 6대 kubelet/containerd enabled·active, firewalld disabled·inactive | 재부팅 시험 또는 부팅 중 연속 보호 입증 아님 |

**OID02 이미지 사전반입, OID03 패키지/외부 공급 경로, ICR-AC18 재부팅 후 지속성, K8S AC4d② 부팅 중 연속 보호를 분리한다.** 이미 실행한 OID02 archive2개·8조합 import는 반복하지 않는다. 이번 읽기로 OID03을 N/A/PASS로 바꾸거나 control01 drain 제한을 해제하지 않는다. 현재 설치 정보는 오프라인 공급원/경로를 정할 때 필요한 정확 버전 입력이며, 이미 없다고 회신한 과거 원본을 다시 만들라는 요구가 아니다.

## 로컬 준비물

- 현재 CICD main `2d8a14c55ea4b61f53b7ac6d682cd5e97575dda7`의 원 Git blob7개를 그대로 묶었다. [목록·Git blob·SHA](SOURCE_BUNDLE_MANIFEST.json), [bundle](native-source-2d8a14c.json). 전체 SHA256 `8cfdcce5e4b5eb95001d27e35606e5121edf77d8c2c1f5f481016c79933baa5c`. 원본 코드 수정0; 로컬 구문/Git blob/포맷 대조이며 배치·실행 성공 아님.
- [Deploy 준비 입력](DEPLOY_PREPARATION.pending.json)은 관측 전용 schema다. 실제 Workflow record로 전달하지 않는다. 새 Push 영수증·Deploy UUID/창·승인·복구 범위는 null/미승인으로 남겼다.03:10 대상 UID/spec/image는 실행 직전 재확인 대상이며 최신이라고 고정하지 않는다.
- 기존 Push 목표13b50485/10:00 시작한도·12:00 종료창은 변경하지 않았다. Deploy 인증 확인을 Push 선행조건으로 추가하지 않는다.

## 검증과 후속

원격 읽기9묶음의 외부 rc0·receipt hash·정상 계정/SA/CA를 대조했다. Worker crictl의 RPM 소유 조회rc1은 미등록 관측이며 전체 명령PASS로 숨기지 않는다. `verify_collection.py`는 봉인 후 재읽기 검증만 수행한다.

현재 RUNTIME_READ=수행, SOURCE_PACKAGE=STATIC 확인, 독립 REVIEW=대기, native broker/TokenRequest/Deploy/reboot=미실행, AC/티켓종결=미판정. 다음은 새 Push 결과를 입력에 결속하고 실제 Deploy/복구 범위를 한 번에 검토하는 것이다. OID03 경로/부팅 처분과 Runner 운영 인수는 각각 기존 기준에서 독립 진행한다.
