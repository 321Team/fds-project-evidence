# OID02 한정 공급 실행 카드 — 준비본

**현재 미실행.** 실행 범위·현장 조건 확인 후 `EXECUTION_INPUT.json`과 이 카드가 같은 SHA인 회차에서만 소비한다. 기존 자격증명과 strict SSH 경로를 사용한다. 로컬 준비물 위치를 서버에 있다고 가정하지 않는다.

## 1. 직전 읽기와 파일 전달

실행 위치 control01 및 해당 대상 노드, svc_ansible→sudo. hostname/boot·cluster UID·6Node Ready·systemPod3개·Deployment2개 UID/spec를 ANALYSIS와 대조한다. 바뀌었으면 이번 입력을 사용하지 않는다. control01에서 고정3refs의 top digest/complete/unpacked를, 대상에서 예상 새 ref 부재와 기존 ref 전체 목록을 수신 기록으로 보존한다. daemon/CLI revision·snapshotter·SELinux·가용 디스크 및 동시 작성자 배제를 확인한다.

각 호스트 root 소유 `/root`의 새 `/root/p1-oid02-20261013-r1`만 mode0700으로 만든다. 이미 존재하면 자동 재사용하지 않는다. tar/output 이름을 덮어쓰지 않는다. 검증기·OBSERVED_SUPPLY·EXECUTION_INPUT은 LF/원본 SHA 그대로 새 경로에 전달하고 서버에서 대조한다. 실제 shell은1카드마다 자식 프로세스로 실행하며 터미널을 종료하지 않는다.

## 2. control01 export2개

아래 명령 각각의 직전 refs 검사·시작/종료/rc/stdout/stderr를 남긴다. 새 경로/미존재 출력명 확인 뒤 umask077 환경에서 실행한다. 하나라도 실패하면 다음 export/전달/import를 멈춘다. source image의 retag/삭제 없음.

```bash
/usr/bin/ctr --address /run/containerd/containerd.sock --namespace k8s.io images export --local --platform linux/amd64 --skip-manifest-json /root/p1-oid02-20261013-r1/kube-controllers-linux-amd64.oci.tar quay.io/calico/kube-controllers@sha256:df00967cbd6d88e1ff3123e1598895845622e2987928b4ebd9d8ac49aefe00c3

/usr/bin/ctr --address /run/containerd/containerd.sock --namespace k8s.io images export --local --platform linux/amd64 --skip-manifest-json /root/p1-oid02-20261013-r1/coredns-linux-amd64.oci.tar registry.k8s.io/coredns/coredns:v1.14.2 registry.k8s.io/coredns/coredns@sha256:e7e6440cfd1e919280958f5b5a6ab2b184d385bba774c12ad2a9e1e4183f90d9
```

원본 archive를 tar로 풀지 않고 아래 읽기 검증을 실행한다. 정상 조건은 ARCHIVE_CLOSURE_VERIFIED와 전체 expected refs/top/amd64/config/layers 일치다. 출력 JSON은 새 파일에 보존하고 rc를 별도 남긴다. archive SHA/실제 크기를 실행 receipt에 고정한다. 실행 전 null값을 임의 값으로 채우지 않는다.

```bash
python3 -B -I /root/p1-oid02-20261013-r1/verify_archive.py /root/p1-oid02-20261013-r1/OBSERVED_SUPPLY.json kube-controllers /root/p1-oid02-20261013-r1/kube-controllers-linux-amd64.oci.tar
python3 -B -I /root/p1-oid02-20261013-r1/verify_archive.py /root/p1-oid02-20261013-r1/OBSERVED_SUPPLY.json coredns /root/p1-oid02-20261013-r1/coredns-linux-amd64.oci.tar
```

정상 archive만 기존 관리 SSH를 통해 새 ansible01 중계 폴더(0700)와 대상 회차 폴더(0700)에 전달하고0600으로 보관한다. 전송계정에 source root credential 파일을 복사하지 않는다. SSH 스트림과 제한된 sudo 읽기/수신으로 archive만 전달하며 원본·중계·대상 SHA를 대조한다. 각 대상에서도 같은 archive 검증기를 읽기로 실행한다. 다른 아키텍처 blob 누락을 오류 해결 목적으로 외부에서 내려받지 않는다.

## 3. 한 대상·한 이미지 import

대상 순서 control02→control03→worker01→worker02→worker03. **첫 두 호스트는 첫 명령만**, Worker는 첫 명령 성공/검수 뒤 두 번째 명령이다. 두 줄을 무조건 연속 실행하지 않는다. 대상의 직전 ref부재·current expected digest·새 archive SHA·동시 작성자 배제 확인을 생략하지 않는다.

```bash
/usr/bin/ctr --address /run/containerd/containerd.sock --namespace k8s.io images import --local --platform linux/amd64 --snapshotter overlayfs --label io.cri-containerd.image=managed /root/p1-oid02-20261013-r1/kube-controllers-linux-amd64.oci.tar

/usr/bin/ctr --address /run/containerd/containerd.sock --namespace k8s.io images import --local --platform linux/amd64 --snapshotter overlayfs --label io.cri-containerd.image=managed /root/p1-oid02-20261013-r1/coredns-linux-amd64.oci.tar
```

원래 kube digest ref 또는 CoreDNS tag/digest ref를 그대로 넣는다. `--all-platforms`, `--digests`, `--index-name`, `--base-name`, `--force`를 추가하지 않는다. 기존 이름이 생겼으면 import가 update할 수 있어 STOP한다. 관측된 overlayfs를 명시하며 실행 직전 유효 config와 실제 컨테이너 snapshotter가 다르면 STOP한다.

## 4. 각 단계 사후 검수

해당 exact ref의 `ctr ... images list`와 `ctr ... images check 'name==<exact-ref>'`를 읽고 top digest·complete·unpacked=true를 확인한다. 원래 CoreDNS multiarch index는 e7e6440…이고 child fd507979…로 바뀌면 실패다. manifest/config/layer content는 기존 expected digest·크기로 읽기 해시 대조한다. 전후 image refs 차이, CRI 파생 alias와 labels, import rc를 보존한다. 기존 이미지 record 보존·Node6/Pod3 및 두 Deployment UID/spec를 확인한 뒤 다음 이미지/호스트로 간다.

complete/unpacked는 containerd 상태이며 실제 Pod 재기동 성공이나 향후 자동 GC 이후 보유까지 보장하지 않는다. crictl 경로 미확정을 감추지 않으며 이를 해결하기 위해 설치·재시작을 하지 않는다. 끝에서 앱6Ready/분산·systemPod3Ready를 별도 읽기로 확인한다.

## 5. 중단·부분 복귀

실패 단계/host/image를 기록하고 다음 명령0. export/전달 실패면 image store 변경0인 상태로 부분 파일을 보존한다. import 실패·timeout이면 refs/content/snapshot과 실행 프로세스 진행 여부를 먼저 읽으며 자동 재실행하지 않는다. 이번 새 ref임을 전후 목록과 생성시각·digest로 확인하고 현재 사용Pod가 없으며 동시 writer 배제가 유지될 때만 그 exact ref에 한해 `ctr ... images remove '<exact-ref>'`를 수행할 수 있다. 범위/소유/미사용이 불명확하면 제거0·콘솔 인수다. image remove의 비동기 GC와 content 공유 때문에 완전 byte 원복을 약속하지 않는다. `--sync`·GC/prune·content/snapshot 직접삭제·서비스 restart·control01 drain/reboot는 복귀 절차에 없다.

원본 archive·수신 SHA·실패출력·기존 source는 남긴다. 8개 조합 완료 여부, 보존 대상, 예외/미실행을 증적 PR208에서 구분하며 OID03/AC/티켓 종료는 별도다.
