# P1-K8S-01 6개 Node identity 중복 0 증적 — 2026-10-01

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) 핵심 요구 "6개 Node identity 중복 0"(Baseline v3.1.19 HO-ANS-03: 6대 hostname·MAC·product_uuid 중복 0)에 대응하는 읽기 전용 조회 결과다.

## 자료 구분

**`CONSOLE_SUBMITTED / RECONSTRUCTED_COPY`.** 두 파일 모두 서버의 `.txt`/`.sha256` 파일을 직접 수신하지 않고 콘솔 출력을 붙여넣어 재구성했다. 서버 원본 파일의 해시 검증을 주장하지 않는다. 확인한 범위는 "실행자가 서버 화면에 보고한 SHA256과 재구성본 SHA256의 일치"로 한정한다.

## 출처와 수신

| 파일 | 수집 위치 | 수집 시각 | 명령 | 서버 화면 보고 SHA256 = 재구성본 |
|---|---|---|---|---|
| `node-identity.txt` | `k8s-control02` `server03` 홈 `~/node-identity.txt` | 2026-10-01T13:00:58+09:00 | `kubectl get nodes -o custom-columns=NAME,INTERNAL_IP,PRODUCT_UUID(.status.nodeInfo.systemUUID),MACHINE_ID(.status.nodeInfo.machineID),UID(.metadata.uid)` | `c7868dcf6ccd647e05933ccab30ed6fba4349af24d02b237fe2503a1fd2d4118` |
| `node-mac.txt` | `ansible01` `server01_ansible` 홈 `~/node-mac.txt` | 2026-10-01T13:23:10+09:00 | `ansible -i inventory/hosts.yml k8s_nodes -m shell -a "hostname -s; cat /sys/class/net/ens160/address" -o` (`~/infra-ansible`, `ANSIBLE_PRIVATE_KEY_FILE` 환경 적용) | `a9b36e23bf33af96ec514a748ba3ef7f304c5667fa5e4bc82bc7f497d47c11db` |

실행자 이하영(K8S/SEC Lead). 두 명령 모두 읽기 전용이다. ansible 출력의 `CHANGED`는 shell 모듈의 기본 표기이며 서버 변경을 뜻하지 않는다(실행 명령은 `cat`뿐). `[sudo]` 암호 프롬프트는 파일에 포함되지 않은 것으로 재구성했고 이 재구성이 보고 해시와 일치한다.

```bash
sha256sum --check SHA256SUMS
```

암호·키 값은 파일에 없다. `ANSIBLE_PRIVATE_KEY_FILE`은 경로 변수이며 이 폴더에 값이 없다.

## 확인한 사실

| Node | InternalIP | product_uuid | machine-id | ens160 MAC |
|---|---|---|---|---|
| k8s-control01 | 10.1.93.102 | 80724d56-7c17-f8a0-b2ea-ece7a154e24b | 43795458b5574726af93975cb8625c2b | 00:0c:29:54:e2:4b |
| k8s-control02 | 10.1.93.103 | f3cc4d56-485a-a0f6-6588-7f9bb969d871 | 6467ff4113f945a4b100a4ae32647d81 | 00:0c:29:69:d8:71 |
| k8s-control03 | 10.1.93.104 | 72fb4d56-6002-228b-b0c2-981cdcd0a1dd | 05447f80fe754454a3c5c8f09f4c9ea6 | 00:0c:29:d0:a1:dd |
| k8s-worker01 | 10.1.93.105 | 3d974d56-c13a-c416-82c1-0dad7ab4aff6 | 19fba8c06cfa4ebf876bacbbc3423bb1 | 00:0c:29:b4:af:f6 |
| k8s-worker02 | 10.1.93.107 | 9aa34d56-6424-7b95-6b22-c42e67fdba46 | bed0e37c3c234c5e85c5b5d352f6fc65 | 00:0c:29:fd:ba:46 |
| k8s-worker03 | 10.1.93.108 | a3394d56-a6ae-2f0f-c17d-c6dc9dff8548 | 0bb03794b5b04dc4bded6bd75d63f701 | 00:0c:29:ff:85:48 |

- hostname(노드 이름) 6개, InternalIP 6개, product_uuid 6개, machine-id 6개, Node UID 6개, ens160 MAC 6개가 각각 모두 서로 다르다(중복 0).
- 일관성 점검: 각 노드의 product_uuid 마지막 6자리(16진)가 해당 노드의 ens160 MAC 마지막 3바이트와 일치한다(예: control01 `…e24b` ↔ `54:e2:4b`). 서로 다른 두 수집 경로의 값이 같은 노드를 가리킨다는 정황이다. control02의 MAC은 별도 수집한 MTU 증적(`../mtu-20261001/`)의 `ens160` 값과도 같다.
- product_uuid의 5~8번째 문자는 6대 모두 `4d56`이다. 같은 VMware 환경에서 생성된 VM의 SMBIOS UUID 공통 형식으로 판단하며, 전체 UUID는 모두 다르므로 복제 노드로 보이지 않는다. 근본 원인은 확인하지 않았다.

## 한계

1. 서버 원본 파일을 직접 수신하지 않았다(위 자료 구분).
2. product_uuid·machine-id는 Kubernetes Node 상태(`nodeInfo`)의 값이며 각 노드에서 `/sys/class/dmi/id/product_uuid`, `/etc/machine-id`를 직접 읽은 값이 아니다. MAC은 각 노드의 `/sys/class/net/ens160/address`를 직접 읽었다. 이 두 값의 동일성은 위 일관성 점검으로 정황 확인만 했다.
3. MAC은 ens160(실 NIC)만 대상이다. `vxlan.calico`·`cali*` 인터페이스 MAC은 포함하지 않는다.
4. 수집 시점 상태다. 이후 변경 여부는 이 파일로 확인되지 않는다.
5. 과거(2026-09-22) ansible01 수집 결과를 요약한 보안시연 문서는 원본이 첨부되지 않았다. 그 문서의 control01 UUID 앞자리 `b072`는 이 수집 값 `8072`와 다르다(요약 문서의 표기 오류로 보이며 이 증적은 해당 문서를 인용하지 않는다).

## 판정 경계

- `NODE_IDENTITY_UNIQUENESS (hostname/product_uuid/machine-id/UID/MAC) = OBSERVED, 중복 0` (콘솔 제출 자료 기준)
- AC 충족 주장은 하지 않는다. 판단은 K8S Lead가 한다.

## 검토 상태

AI 세션의 자체 대조(화면 보고 해시와 재구성본 해시 일치, 6개 값의 중복 검사, MAC·UUID 일관성, 민감정보 확인)이며 `governance/EVIDENCE_POLICY.md`의 독립 검토는 아직 없다.
