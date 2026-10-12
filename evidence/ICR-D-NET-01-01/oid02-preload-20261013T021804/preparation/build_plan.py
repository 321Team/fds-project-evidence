"""Local execution cards and facts; no server mutation or permission inference."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_bytes())
def put(n,s):(P/n).write_bytes(s.encode())
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
a=read('ANALYSIS.json');s=read('OBSERVED_SUPPLY.json')
K=s['images'][0];C=s['images'][1]
assert K['name']=='kube-controllers' and C['name']=='coredns'
kref='quay.io/calico/kube-controllers@'+K['approved_top_digest']
crefs=['registry.k8s.io/coredns/coredns:v1.14.2','registry.k8s.io/coredns/coredns@'+C['approved_top_digest']]
root='/root/p1-oid02-20261013-r1'
ctr=['/usr/bin/ctr','--address','/run/containerd/containerd.sock','--namespace','k8s.io']
jobs=[]
for name,im,refs in [('kube-controllers',K,[kref]),('coredns',C,crefs)]:
 jobs.append({'image':name,'export_host':'k8s-control01','archive_path':root+'/'+name+'-linux-amd64.oci.tar','refs':refs,'top_digest':im['approved_top_digest'],'manifest_digest':im['linux_amd64_manifest_digest'],'config_digest':im['config']['digest'],'layer_count':len(im['layers']),'export_argv':ctr+['images','export','--local','--platform','linux/amd64','--skip-manifest-json',root+'/'+name+'-linux-amd64.oci.tar']+refs,'import_argv':ctr+['images','import','--local','--platform','linux/amd64','--snapshotter','overlayfs','--label','io.cri-containerd.image=managed',root+'/'+name+'-linux-amd64.oci.tar'],'archive_sha256':None,'archive_size_bytes':None,'archive_verified':False})
plan={'schema':'P1_OID02_BOUNDED_SUPPLY_PLAN_1','scope':'Phase1 known OID02 preloaded gaps only','input_sha256':sha('OBSERVED_SUPPLY.json'),'analysis_sha256':sha('ANALYSIS.json'),'validator_sha256':sha('verify_archive.py'),'cluster_uid':'e1669cff-1435-423f-a6c4-28bc44f488de','root':root,'source':'current control01 k8s.io content store; no historical origin claim','source_adoption_confirmed':False,'runtime_export_import_authorized':False,'new_control02_console_confirmed':False,'image_writer_exclusion_confirmed':False,'source_jobs':jobs,'target_order':['k8s-control02','k8s-control03','k8s-worker01','k8s-worker02','k8s-worker03'],'targets':a['targets'],'max_image_node_imports':8,'max_export_archives':2,'platform':'linux/amd64','cli_revision':'1294c24a7da8e5a793ed378161673abe94118892','minimum_free_bytes_candidate':2147483648,'per_export_deadline_seconds_candidate':120,'per_import_deadline_seconds_candidate':180,'per_target_verify_seconds_candidate':60,'whole_runtime_cap_minutes_candidate':30,'reboot':False,'pull_push_registry_access':False,'pod_change':False,'network_policy_change':False,'ac_accepted':False}
put('EXECUTION_INPUT.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
put('EXECUTION_SCOPE.md',f'''# OID02 실제 공급·반입 범위안 — 2026-10-13

**상태: 현재 상태 수집·구체 실행안 준비 완료 / export·전달·import 미실행.** 이권욱 / CODEX_ASSISTED. 새 Phase2 작업이나 전체 OID 인수 요청이 아니다.

## 이번에 확인한 사실

- 원본 시각 `{a['source_observation_at_utc']}`(UTC), 상세21개 수신 폴더의 KST receipt. 6노드 Linux/amd64·Ready·schedulable. 두 Deployment의 nodeSelector·필수 affinity·taint/toleration을 대조하면6대 모두 배치 후보에 해당한다. 자원 여유/스케줄러의 미래 선택까지 보장하지 않는다.
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
2. 기존 strict SSH·svc_ansible/sudo 경로로 control01의 새0700 `{root}`에 정확한 OCI archive2개를 만든다. `--local --platform linux/amd64 --skip-manifest-json`을 사용한다. 현재 source image refs/content를 변경하지 않는다.
3. OCI root index의 원래 이름, 원 top digest, linux/amd64 child/config/layer 전체 SHA·size·경로 closure를 읽기 검증한다. CoreDNS의 원 index digest는 그대로 보존하지만 다른 architecture content는 이 archive 범위가 아니다. 예상 밖 blob/ref·누락·digest 불일치면 전달/import0.
4. 기존 관리 경로를 통해 ansible01의 새0700 중계 디렉터리와 대상5대의 새0700 동일 회차 경로로 필요한 tar만 전달한다. tar는0600, 새 경로만 사용하고 기존 파일을 덮어쓰지 않는다. 원본·중계·수신 archive SHA가 모두 같아야 한다.
5. **control02 → control03 → worker01 → worker02 → worker03**, 한 대·한 이미지씩 정확한 archive를 기존 `k8s.io` namespace에 import/unpack한다. CP2/3는 kube만, Worker3대는 kube→CoreDNS 순서다. 다른 namespace나 임시 daemon/VM을 만들지 않는다.
6. 호스트별 import 전/후 refs·digest·labels·시각, exact `images check` complete/unpacked, 이미지 manifest/config/layer 해시, node/Pod/Deployment 보존을 확인한다. 각 단계 정상 후에만 다음으로 간다. 완료 후 증적은 기존 PR208에 합친다.

**고정 이미지**

- kube-controllers: `{kref}` (linux/amd64 manifest와 동일).
- CoreDNS 원래 tag: `{crefs[0]}`, digest ref: `{crefs[1]}`. linux/amd64 manifest `{C['linux_amd64_manifest_digest']}`. tag를 child manifest로 갈아끼우지 않는다.

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
''')
exports='\n\n'.join(' '.join(j['export_argv']) for j in jobs)
imports='\n\n'.join(' '.join(j['import_argv']) for j in jobs)
put('RUNBOOK.md',f'''# OID02 한정 공급 실행 카드 — 준비본

**현재 미실행.** 실행 범위·현장 조건 확인 후 `EXECUTION_INPUT.json`과 이 카드가 같은 SHA인 회차에서만 소비한다. 기존 자격증명과 strict SSH 경로를 사용한다. 로컬 준비물 위치를 서버에 있다고 가정하지 않는다.

## 1. 직전 읽기와 파일 전달

실행 위치 control01 및 해당 대상 노드, svc_ansible→sudo. hostname/boot·cluster UID·6Node Ready·systemPod3개·Deployment2개 UID/spec를 ANALYSIS와 대조한다. 바뀌었으면 이번 입력을 사용하지 않는다. control01에서 고정3refs의 top digest/complete/unpacked를, 대상에서 예상 새 ref 부재와 기존 ref 전체 목록을 수신 기록으로 보존한다. daemon/CLI revision·snapshotter·SELinux·가용 디스크 및 동시 작성자 배제를 확인한다.

각 호스트 root 소유 `/root`의 새 `{root}`만 mode0700으로 만든다. 이미 존재하면 자동 재사용하지 않는다. tar/output 이름을 덮어쓰지 않는다. 검증기·OBSERVED_SUPPLY·EXECUTION_INPUT은 LF/원본 SHA 그대로 새 경로에 전달하고 서버에서 대조한다. 실제 shell은1카드마다 자식 프로세스로 실행하며 터미널을 종료하지 않는다.

## 2. control01 export2개

아래 명령 각각의 직전 refs 검사·시작/종료/rc/stdout/stderr를 남긴다. 새 경로/미존재 출력명 확인 뒤 umask077 환경에서 실행한다. 하나라도 실패하면 다음 export/전달/import를 멈춘다. source image의 retag/삭제 없음.

```bash
{exports}
```

원본 archive를 tar로 풀지 않고 아래 읽기 검증을 실행한다. 정상 조건은 ARCHIVE_CLOSURE_VERIFIED와 전체 expected refs/top/amd64/config/layers 일치다. 출력 JSON은 새 파일에 보존하고 rc를 별도 남긴다. archive SHA/실제 크기를 실행 receipt에 고정한다. 실행 전 null값을 임의 값으로 채우지 않는다.

```bash
python3 -B -I {root}/verify_archive.py {root}/OBSERVED_SUPPLY.json kube-controllers {root}/kube-controllers-linux-amd64.oci.tar
python3 -B -I {root}/verify_archive.py {root}/OBSERVED_SUPPLY.json coredns {root}/coredns-linux-amd64.oci.tar
```

정상 archive만 기존 관리 SSH를 통해 새 ansible01 중계 폴더(0700)와 대상 회차 폴더(0700)에 전달하고0600으로 보관한다. 전송계정에 source root credential 파일을 복사하지 않는다. SSH 스트림과 제한된 sudo 읽기/수신으로 archive만 전달하며 원본·중계·대상 SHA를 대조한다. 각 대상에서도 같은 archive 검증기를 읽기로 실행한다. 다른 아키텍처 blob 누락을 오류 해결 목적으로 외부에서 내려받지 않는다.

## 3. 한 대상·한 이미지 import

대상 순서 control02→control03→worker01→worker02→worker03. **첫 두 호스트는 첫 명령만**, Worker는 첫 명령 성공/검수 뒤 두 번째 명령이다. 두 줄을 무조건 연속 실행하지 않는다. 대상의 직전 ref부재·current expected digest·새 archive SHA·동시 작성자 배제 확인을 생략하지 않는다.

```bash
{imports}
```

원래 kube digest ref 또는 CoreDNS tag/digest ref를 그대로 넣는다. `--all-platforms`, `--digests`, `--index-name`, `--base-name`, `--force`를 추가하지 않는다. 기존 이름이 생겼으면 import가 update할 수 있어 STOP한다. 관측된 overlayfs를 명시하며 실행 직전 유효 config와 실제 컨테이너 snapshotter가 다르면 STOP한다.

## 4. 각 단계 사후 검수

해당 exact ref의 `ctr ... images list`와 `ctr ... images check 'name==<exact-ref>'`를 읽고 top digest·complete·unpacked=true를 확인한다. 원래 CoreDNS multiarch index는 e7e6440…이고 child fd507979…로 바뀌면 실패다. manifest/config/layer content는 기존 expected digest·크기로 읽기 해시 대조한다. 전후 image refs 차이, CRI 파생 alias와 labels, import rc를 보존한다. 기존 이미지 record 보존·Node6/Pod3 및 두 Deployment UID/spec를 확인한 뒤 다음 이미지/호스트로 간다.

complete/unpacked는 containerd 상태이며 실제 Pod 재기동 성공이나 향후 자동 GC 이후 보유까지 보장하지 않는다. crictl 경로 미확정을 감추지 않으며 이를 해결하기 위해 설치·재시작을 하지 않는다. 끝에서 앱6Ready/분산·systemPod3Ready를 별도 읽기로 확인한다.

## 5. 중단·부분 복귀

실패 단계/host/image를 기록하고 다음 명령0. export/전달 실패면 image store 변경0인 상태로 부분 파일을 보존한다. import 실패·timeout이면 refs/content/snapshot과 실행 프로세스 진행 여부를 먼저 읽으며 자동 재실행하지 않는다. 이번 새 ref임을 전후 목록과 생성시각·digest로 확인하고 현재 사용Pod가 없으며 동시 writer 배제가 유지될 때만 그 exact ref에 한해 `ctr ... images remove '<exact-ref>'`를 수행할 수 있다. 범위/소유/미사용이 불명확하면 제거0·콘솔 인수다. image remove의 비동기 GC와 content 공유 때문에 완전 byte 원복을 약속하지 않는다. `--sync`·GC/prune·content/snapshot 직접삭제·서비스 restart·control01 drain/reboot는 복귀 절차에 없다.

원본 archive·수신 SHA·실패출력·기존 source는 남긴다. 8개 조합 완료 여부, 보존 대상, 예외/미실행을 증적 PR208에서 구분하며 OID03/AC/티켓 종료는 별도다.
''')
put('CURRENT_EXECUTION_STATUS.md',f'''# OID02 공급 준비 — 2026-10-13

읽기21회 수신·원본해시 대조 완료. 기존8개 image-node 공백 유지, 모든systemPod3개 control01 Ready,6Node Ready. export/import·파일서버배치·Pod/정책/Harbor 변경0. control01 cache 읽기1회는 crictl 고정경로 부재로 일부 중단했고이미성공한ctr조회는보존,누락환경/CLI만보완했다. K8S17 회차와 독립적인 새 준비이며동시변경은없다.

`EXECUTION_SCOPE.md`에현재공급원채택·archive2개·5대8조합한정반입·부분정리·control02콘솔확인범위를구체화했다. 과거동일모드/코드승인을실제export/import허용으로확대하지않는다. 현시점은승인대기이며새Harbor비중첩창확보를주장하지않는다.
''')
print('Prepared concrete scope, exact argv, bounded runbook and current read-only status')
