# OID-02 — 시스템 이미지 보유 현황 읽기 전용 재수집(경로 B) 원본 편입 (2026-10-07)

Record ID: **P1-HBR-01** (OID-02 제출 입력, [baseline #14](https://github.com/321Team/fds-project-baseline/issues/14) / [#13](https://github.com/321Team/fds-project-baseline/issues/13)). 수집·실행: 이하영(HBR Lead·OID-02 Owner), ansible01 `server01_ansible`. 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 OID-02 완료·`approved_registry`/`preloaded` 이행·재스케줄 공백 처분의 PASS가 아니다.** 서버·Pod·이미지를 변경하지 않았고 export/import·retag·삭제를 하지 않았다.

## 근거
- 제출 코멘트: [#14 6033151808](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-6033151808) (이 원본으로 작성, 2026-10-07 18:00 제출분)
- 권욱 님 요청·후속: [#14 6032913513](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-6032913513). 새 도구(infra-kubernetes#68 HEAD `85939569`)는 독립 리뷰 전이라 **사용하지 않았다.**
- 이전 수집(10/5): [oid02-image-inventory-20261006](../oid02-image-inventory-20261006/) — 이번 값은 그 분포와 같은지 대조하는 재수집이다.

## 수집 방식
읽기 전용 명령 10개를 `cap` 함수로 실행해 명령마다 rc·시작/종료 시각·stdout/stderr 크기를 `index.txt`에 남기고 폴더 전체 해시를 `oid02-b-sums.local.txt`로 만들었다. 실행 시각 2026-10-07 16:26:04~16:26:11 KST, **10개 모두 rc=0, stderr 0바이트.** `scripts/oid02-b-collect.sh`는 실행한 명령을 그대로 옮겨 보관한 것이며 터미널 원본이 아니다.

## 파일과 해시
| 경로 | 내용 |
|---|---|
| ★ `server-originals/k1-nodes.out` | control01(`server02`, ssh) `kubectl get nodes -o wide` |
| ★ `server-originals/k2-taints.out` | 노드별 unschedulable·taint |
| ★ `server-originals/k3-pods.out` | kube-system Pod 목록(노드 위치 포함) |
| ★ `server-originals/k4-imageid.out` | kube-system Pod 이름·노드·imageID |
| ★ `server-originals/node-k8s-control01~03.out`, `node-k8s-worker01~03.out` | 노드별 hostname, `ctr -n k8s.io images ls`, containerd 버전, `/var/lib/containerd` 디스크(ansible `-b`, `svc_ansible`) |
| `server-originals/*.err` (10개) | 각 명령 stderr. **모두 0바이트** |
| `observations/index.txt` | 명령별 rc·시각·크기 |
| `observations/oid02-b-sums.local.txt` | ansible01에서 만든 해시 목록 (sha256 `4d4579c658ef6cb315827e6e0a7ef649b06b2bcc1424e42ab1f8bdfeb09f95b1`) |
| `scripts/oid02-b-collect.sh` | 실행한 명령 |

개별 해시는 폴더 `SHA256SUMS` 참조. ansible01에서 만든 ZIP(`oid02-b-20261007T162604.zip`, 본 PC 사본 sha256 `5cf4264167a4bd673b76ddf5625ccc0777eca6295b08ce15a7f084d945d77ef1`)을 공유 폴더로 옮겨 풀었고, ZIP 안 파일 22개가 `oid02-b-sums.local.txt`와 22/22 일치하며 요약 해시가 터미널에서 본 값(`4d4579c6…f95b1`)과 같다.

## 원본이 보여주는 사실 (16:26 KST)
- 노드 6대 모두 `Ready`, `UNSCHED <none>`, control01~03만 `node-role.kubernetes.io/control-plane` taint, containerd `2.3.5`, `/var/lib/containerd` 가용 약 60~62G(worker03 60G).
- `calico-kube-controllers-74f76ddbd-jbpm9`(RESTARTS 42, 마지막 41h 전)·`coredns-589f44dc88-f8l54`·`-qkcws`(각 14)는 **모두 `k8s-control01`** 실행 중.
- imageID: calico `quay.io/calico/kube-controllers@sha256:df00967cbd6d88e1ff3123e1598895845622e2987928b4ebd9d8ac49aefe00c3`, coredns `registry.k8s.io/coredns/coredns@sha256:e7e6440cfd1e919280958f5b5a6ab2b184d385bba774c12ad2a9e1e4183f90d9`.
- `ctr` 이미지 목록: kube-controllers digest는 **control01에만**, CoreDNS(`v1.14.2`, 위 digest)는 **control01~03에 있고 worker 3대에는 없다**(문자열 `df00967c`·`e7e6440c` 검색).

## 한계 (숨기지 않음)
1. 터미널·ansible 출력이며 서버 측 봉인이 없다. 수집 직후 서버에서 해시를 봉인하지 않았다.
2. 이미지 보유 판단은 `ctr images ls` 문자열과 Pod imageID 기준이다. layer 본체·manifest 내용(config/platform/descriptor)은 읽지 않았다(metadata 도구는 리뷰 전이라 미사용).
3. 이 값은 16:26 시점이며 이후 Pod 위치가 바뀔 수 있다.
4. 공급 원본·출처·반입 승인(OID-03)은 이 폴더로 확인되지 않는다.
5. 이 편입은 Due·임시 통제·P0 예외 분류의 승인이 아니다(제출 코멘트 참조).
