# P1-K8S-01 CP 3대 reboot 지속성 검증 증적 — 2026-09-27

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) HEP/GNP AC의 reboot 지속성 확인 중 **CP 3대(k8s-control01/02/03)** 재부팅 검증. Worker 3대 검증([`../icr39-verification-20260927/`](../icr39-verification-20260927/))에 이은 나머지 절반이다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 위치 | 각 CP 콘솔, 실행자 이하영(K8S/SEC Lead) |
| 순서 | control03 → control01 → control02 (한 대씩, 재부팅 대상 제외 2대로 quorum 유지 확인 후 진행) |
| 시각 | 2026-09-27 17:34~18:03 KST |
| 수집 형태 | 사용자 제출 ZIP `cp-reboot-20260927.zip`, SHA-256 `713d1db2b8e3193993d6b68182297b8379b602019cffc1be45af1b78c4743490` |
| 수신 | 2026-09-27 KST |
| 편입 작성 | Claude Code 세션 (AI 보조) — 독립 검토 필요, 아래 "검토 상태" 참고 |

## 무결성

제출 ZIP 내부 `SHA256SUMS` 기준 43개 파일 `sha256sum -c` **OK** 확인(편입 시 재실행). 비밀번호·개인키 패턴 검사 결과 없음.

```bash
cd control01 && sha256sum -c ../SHA256SUMS --ignore-missing
cd ../control02 && sha256sum -c ../SHA256SUMS --ignore-missing
cd ../control03 && sha256sum -c ../SHA256SUMS --ignore-missing
```

## bootID 변경 확인 (재부팅 실제 발생 증거)

| 노드 | 재부팅 전 | 재부팅 후 |
|---|---|---|
| control03 | `f261af5b-ac5c-4bd7-9340-5e445638a2ac` | `6b0510e7-b893-4075-972c-f0e58682365d` |
| control01 | `69d94725-2e14-4e64-b822-90976fd27322` | `42c1de0b-3e21-45c4-834f-fe61b68e6eee` |
| control02 | `85e12729-c52e-4988-a1ec-51727aa847cc` | `9895aad4-841b-4440-ac3a-e26eec60e545` |

## 확인 사실

- 3대 각각 재부팅 전/후 정책 매트릭스(20칸) 바이트 동일, 호스트 상태(firewalld disabled/inactive, SELinux Enforcing, Cockpit masked) 전/후 동일
- 재부팅 대상 제외 2대 기준 etcd 3 endpoint health/status 확인: 재부팅 후 재합류(learner=false), term 유지·증가, raft index 일치, leader 존재
- API `/readyz` 3/3 정상
- GNP `generation`: control01=4→4, control02=2→2 (전/후 동일, 파일 증적 있음). control03은 after=2만 파일 증적이 있고 before 원본 미수신으로 **직접적인 전/후 동일성은 미확인**(육안 확인 기록은 "알려진 누락" 참고)
- Prometheus 최종 target: **21/21 up** (`control01/targets-final.json`; kubelet 6·kubelet-cadvisor 6·node-exporter 3·fds-engine 2·transaction-api 2·kube-state-metrics 1·prometheus 1)

## 알려진 누락

`control02/reboot-cp03-gen-before.txt` 파일 없음. 재부팅 전 GNP generation을 파일로 저장하는 명령 전에 control03을 재부팅한 것으로 확인됐다(작업 순서 오류). 재부팅 전 화면 출력에서 `gen=2` 육안 확인은 있었으나 파일 증적은 아니다. `reboot-cp03-gen-after.txt`(`gen=2`)와 control02 자신의 `gen=2`(변경 없음, 별도 대상)가 값 일치하는 점으로 간접 뒷받침하나, 이 자체가 control03의 before 값 파일 증적을 대체하지는 않는다.

## 발견 사항 (AC 판정 범위에 포함, 후속 판단 필요)

### 1. 부팅 직후 보호 공백 (보안 — SEC/D34 관련)

`control01/reboot-cp02-*-EARLY.txt`(control02 재부팅 직후, calico-node/Felix 기동 전 18:01:31 KST 수집)에서:
- `probe-cp01`뿐 아니라 `probe-w01/w02/w03`(Worker)까지 control02(`.103`)의 **2379/2380(etcd)·6443(API)·10250(kubelet)에 전부 OK(연결 성공)**
- 9100(node-exporter)만 `ERR(rc=1)`(connection refused — 포트 도달은 됐으나 프로세스 미기동)
- calico-node 기동(약 18:01:39 KST) 이후 재수집에서는 정상 정책대로 복귀

firewalld를 OFF하고 Calico HEP/GNP 단독으로 보호하는 구조(D34)에서, **호스트 부팅~Felix 정책 적용 사이 구간은 무보호 상태**임을 실측으로 확인했다. 이 구간에 Worker를 포함한 임의 노드가 CP의 etcd/API/kubelet 포트에 도달 가능하다.

P1-K8S-01 AC는 HEP/GNP의 실제 집행·차단·회귀·복구·reboot 지속을 함께 요구하며, Gate 기준에도 재부팅 후 보호 확인이 포함된다. 이번 증적이 입증하는 것은 **steady-state(재부팅 완료 후) 기준 정책·호스트 상태 복귀**이며, **부팅 직후 Felix 적용 전 구간까지 포함한 보호 enforcement의 연속 지속성은 아니다**. 따라서 이 증적만으로 "보호 공백 없는 reboot 지속" PASS를 주장하지 않는다. 최종 AC 체크 여부는 [issue #10](https://github.com/321Team/fds-project-baseline/issues/10)에서 T19(`rollback-node`) 복구와 이 부정 증적을 함께 보고 별도 판단한다. P1-SEC-01(#19)·D34 잔여 위험으로도 별도 보고, 완화책(예: 부팅 시 기본 거부 nftables rule을 Calico 기동 전에 선적용) 검토 대상.

### 2. LB 경유 요청 일시 지연

control03 재부팅 중 `control02/reboot-cp03-cluster-during.txt`(LB `10.1.93.109:6443` 경유)에서 TLS handshake timeout/일부 요청 실패 관측, 같은 시각 `reboot-cp03-cluster-during-direct.txt`(CP `.102`/`.103` 직접 접속)는 정상. LB(#9, 이권욱 담당) 헬스체크·backend 전환 소요 시간 확인 필요.

## 검토 상태

**독립 검토 미완료.** AI 세션의 자체 대조(해시·bootID·gen·target 개수·민감정보 패턴)만 거쳤다. `governance/EVIDENCE_POLICY.md` 기준 별도 리뷰어의 독립 검토와 이권욱 확인이 병합 전 필요하다.

## 참고

- Worker 3대 검증: [`../icr39-verification-20260927/`](../icr39-verification-20260927/)
- 복구(T19 `rollback-node`)는 이번 검증 범위 밖 — K8S Lead 판단으로 별도 후속 처리([issue #10 코멘트](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5852872058))
