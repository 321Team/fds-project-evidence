# OID02 실제 공급·반입 범위안 — 2026-10-13

**상태: 현재 상태 수집·구체 실행안 준비 완료 / export·전달·import 미실행.** 이권욱 / CODEX_ASSISTED. 새 Phase2 작업이나 전체 OID 인수 요청이 아니다.

## 이번에 확인한 사실

- 원본 시각 `2026-10-12T16:27:31.548174+00:00`(UTC), 상세21개 수신 폴더의 KST receipt. 6노드 Linux/amd64·Ready·schedulable. 두 Deployment의 nodeSelector·필수 affinity·taint/toleration을 대조하면6대 모두 배치 후보에 해당한다. 자원 여유/스케줄러의 미래 선택까지 보장하지 않는다.
- kube-controllers1개·CoreDNS2개는 모두 control01에서 Ready. 기존 Pod를 삭제·재시작하거나 control01을 drain/reboot하지 않는다.
- 아래8개 조합은 현재 정확한 workload ref 미관측. 일부 content blob 자체가 전부 없다는 뜻은 아니다. control01의 두 이미지와 control02/03 CoreDNS는 complete/unpacked를 확인했다.
- 기존검증은 control01의15 layer84,341,850B + top/index/manifest/config 관계다. 새 archive 크기·SHA·최초 공급 출처 증명이 아니다. 최초 출처는 여전히 미확인이다.

| 반입 대상 | kube-controllers | CoreDNS |
|---|---|---|
| control01 | 공급원만, import0 | 공급원만, import0 |
| control02 | 1회 | 기존 보유, import0 |
| control03 | 1회 | 기존 보유, import0 |
| worker01 | 1회 | 1회 |
| worker02 | 1회 | 1회 |
| worker03 | 1회 | 1회 |

## 제안하는 한 번의 허용 범위

1. **현재 control01 캐시를 앞으로의 복구 공급원으로 채택**한다. 출처는 이번 관측·export 회차이며 과거 원 공급 archive나 서명 검증을 확보했다고 표기하지 않는다.
2. 기존 strict SSH·svc_ansible/sudo 경로로 control01의 새0700 `/root/p1-oid02-20261013-r1`에 정확한 OCI archive2개를 만든다. `--local --platform linux/amd64 --skip-manifest-json`을 사용한다. 현재 source image refs/content를 변경하지 않는다.
3. OCI root index의 원래 이름, 원 top digest, linux/amd64 child/config/layer 전체 SHA·size·경로 closure를 읽기 검증한다. CoreDNS의 원 index digest는 그대로 보존하지만 다른 architecture content는 이 archive 범위가 아니다. 예상 밖 blob/ref·누락·digest 불일치면 전달/import0.
4. 기존 관리 경로를 통해 ansible01의 새0700 중계 디렉터리와 대상5대의 새0700 동일 회차 경로로 필요한 tar만 전달한다. tar는0600, 새 경로만 사용하고 기존 파일을 덮어쓰지 않는다. 원본·중계·수신 archive SHA가 모두 같아야 한다.
5. **control02 → control03 → worker01 → worker02 → worker03**, 한 대·한 이미지씩 정확한 archive를 기존 `k8s.io` namespace에 import/unpack한다. CP2/3는 kube만, Worker3대는 kube→CoreDNS 순서다. 다른 namespace나 임시 daemon/VM을 만들지 않는다.
6. 호스트별 import 전/후 refs·digest·labels·시각, exact `images check` complete/unpacked, 이미지 manifest/config/layer 해시, node/Pod/Deployment 보존을 확인한다. 각 단계 정상 후에만 다음으로 간다. 완료 후 증적은 기존 PR208에 합친다.

**고정 이미지**

- kube-controllers: `quay.io/calico/kube-controllers@sha256:df00967cbd6d88e1ff3123e1598895845622e2987928b4ebd9d8ac49aefe00c3` (linux/amd64 manifest와 동일).
- CoreDNS 원래 tag: `registry.k8s.io/coredns/coredns:v1.14.2`, digest ref: `registry.k8s.io/coredns/coredns@sha256:e7e6440cfd1e919280958f5b5a6ab2b184d385bba774c12ad2a9e1e4183f90d9`. linux/amd64 manifest `sha256:fd5079792b93909db3adefa91e41c3995455013394f0197c7346786ae19079fc`. tag를 child manifest로 갈아끼우지 않는다.

## 영향·보존·한계

변경은5대의 누락 이미지 참조·content·unpacked snapshot 추가와6대/중계의 새 회차 파일이다. 실행 중 Pod/Deployment·서비스·DNS·정책·SELinux·Registry 접근 경계·credential은 바꾸지 않는다. 로컬 cache에 반입된 이미지가 향후 자연 재스케줄에 사용될 수는 있으며 이번 회차가 재스케줄을 유발하지는 않는다. import는 원자적 트랜잭션이 아니므로 부분 결과가 남을 수 있다.

containerd CLI는 v2.3.5, 실행 파일 SHA를 수신했다. 설치된 옵션과 [동일 revision의 import 구현](https://github.com/containerd/containerd/blob/1294c24a7da8e5a793ed378161673abe94118892/cmd/ctr/commands/images/import.go)을 대조했다. `import --local`도 기존 이름을 update할 수 있으므로 **예정 ref가 직전에 없음을 확인하고, 새로 나타나거나 drift면 STOP**한다. `--force`, 임의 tag, 전체 image/prune·GC·snapshot 삭제는 사용하지 않는다. CRI가 파생 image ID alias를 만들 수 있으므로 전후 전체 ref 차이를 남기고 예상 범위를 벗어나면 추가 반입을 중단한다.

6대의 기존 컨테이너 표본에서 overlayfs 사용과 해당 plugin 정상 상태를 확인했다. 같은 daemon 실행 파일의 config dump로 conf.d import까지 해석한 유효 설정도6대 모두 overlayfs이고 runtime별 다른 override는 없었다. 실행 직전 drift를 다시 확인한다. import에는 관측된 overlayfs를 명시한다.

현재 control01 root PATH/일반7경로에서 crictl을 발견하지 못했다. 도구를 새로 설치하지 않는다. `ctr images check`의 containerd cache 검증과 실제 CRI/Pod 재기동 사용 검증을 구분한다. 이번 범위의 완료를 강제 Pod 재기동 시험으로 확대하지 않는다.

## 시작 조건·중단·복구

- Harbor 변경·사후 관측과의 비중첩을 직전에 확인하고, 이미지 import/delete/tag·이미지 GC 수동 작업의 동시 작성자를 배제한다. kubelet의 정상 동작까지 중지하지 않는다.
- **control02 콘솔은 이전 K8S17의5대 확인에 없었다.** control02를 포함한 대상5대의 필요 시 콘솔 인수 가용성을 확인한다. 나머지 확인을 처음부터 재요청하는 것은 아니다.
- cluster UID·hostname/boot·source refs/digest·대상 ref 부재·기존Pod3개/Node6 Ready·실제 ctr SHA·snapshotter·새 경로·여유 공간을 직전 대조한다. 단일 snapshotter/expected unpack target이 달라지면 실행하지 않는다.
- 후보 한도: host마다 가용2GiB 이상, export당120초·import당180초·대상 사후검수60초·전체30분. 시간 초과는 성공으로 보지 않고 같은 import를 자동 재시도하지 않는다. 해당 명령 자식 종료는 daemon 작업의 완전한 원복을 보장하지 않으므로 현재 결과를 먼저 읽는다.
- export/전달 실패면 부분 파일과 rc를 보존하고 import0. import 후 실패면 다음 대상 진행0. 새 참조가 어떤 단계까지 생겼는지, 예상 digest·생성 시각·라벨과 이번 영수증을 대조한다.
- 복귀는 **이번에 새로 생성했고 소유·미사용을 확인한 정확한 image ref만** 조건부로 제거하는 범위다. 기존 ref·source image·공유 content/snapshot은 삭제하지 않는다. 부분 content가 남거나 CRI 파생 alias의 소유/사용을 확인할 수 없으면 제거하지 않고 인수한다. 전체 바이트가 실행 전과 동일해지는 복귀를 약속하지 않는다.
- 새 참조를 이미 사용하는 Pod가 생겼거나 동시 변경·SSH 결과 불명확·daemon RPC 진행 여부 불명확이면 읽기/콘솔 인수로 전환한다. 서비스 재시작·노드 재부팅·보안 통제 해제로 우회하지 않는다.

## 이번 확인이 필요한 근거

기존 [OID02 임시 통제](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-6033151808)와 [후속 범위](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-6034027526)는 export/import와 구체 변경창을 별도 대상으로 남겼다. K8S17 파일 교체 허용은 이미지 store 변경을 포함하지 않는다. 이번 안에서 **공급원 채택·archive2개·8개 조합 반입·반입 범위의 부분 정리·control02 콘솔**을 한 번에 확인하며 새 Lead 구현 GO나 별도 반복 코드 리뷰를 요구하지 않는다.

[명령 카드](RUNBOOK.md), [고정 입력/명령 인자](EXECUTION_INPUT.json), [관측 분석](ANALYSIS.json), [검증기](verify_archive.py). 검증기10개 MOCK은 합성 tar만 사용했으며 실제 archive 검증·서버 export/import 결과는 아니다. OID03·AC/티켓 종결·reboot 검증은 이번에 승인/완료로 바꾸지 않는다.
