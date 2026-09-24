# P1-K8S-01 Gate 2 최종 상태 증적 — 2026-09-22

[fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10) Gate 2(firewalld → Calico GNP/HEP 보호 전환) 완료 시점의 클러스터 상태 스냅샷.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 원본 위치 | `k8s-control01`(`10.1.93.102`) `/root/gate2-final-evidence/` 최상위 파일 9개 |
| 수집 | 2026-09-22 Gate 2 전환 완료 후, 실행자 이하영 (`kubectl`/`ssh` 조회 결과 저장) |
| 전달 경로 | CP1 → ansible01 → 작업 PC. 사용자 제출 ZIP `이하영_증적자료.zip` (SHA-256 `fc374d73513e24b997baadf3eba1d310acf2c75b71e343faf8271990962d2b2e`) |
| 수신 | 2026-09-24 KST |
| 제외 | 같은 폴더의 `logs/`, `manifests/`는 P1-SEC-01 자료이므로 이 수신 범위에 포함하지 않음 |

## 무결성

`SHA256SUMS-20260922.txt`는 원본 폴더에서 수집 시점에 생성된 목록이다. 수신본 8개 파일 모두 이 목록과 일치(`shasum -a 256 -c`, 제출자와 편입 작성자 각각 확인). 파일은 바이트 그대로 편입했고 줄바꿈 변환은 없다(`.gitattributes` `* -text`). 비밀번호·토큰·키 문자열 패턴 검사 결과 해당 없음.

```bash
sha256sum --check SHA256SUMS-20260922.txt
```

## 파일

| 파일 | 내용 | 수신본에서 확인한 사실 |
|---|---|---|
| `01-nodes-final.txt` | `kubectl get nodes -o wide` | 6대 Ready, v1.36.4, containerd 2.3.5 |
| `02-pods-final.txt` | `kubectl get pods -A -o wide` | 수집 시점 Pod 상태 |
| `03-gnp-list.txt` | GlobalNetworkPolicy 목록 | `fds-k8s-host-*` 6개 |
| `04-hep-list.txt` | HostEndpoint 목록 | `fds-k8s-*` 6개 |
| `05-felixconfig-list.txt` | FelixConfiguration 목록 | `default` + 노드별 6개 |
| `06-firewalld-status-all.txt` | 6대 `systemctl is-active firewalld` | 6대 `inactive` |
| `07-gnp-full.yaml` | GNP 6개 전체 YAML | 아래 참고 사항 1 |
| `08-hep-full.yaml` | HEP 6개 전체 YAML | — |

## 참고 사항

1. **CP1 GNP 중복 규칙:** `fds-k8s-host-k8s-control01`에 UDP 123 ingress 규칙이 3개 있다(다른 5개 GNP는 1개). render 산출물 외에 `kubectl patch`로 NTP ingress를 직접 추가했고 같은 patch가 중복 적용된 결과다. 이 규칙은 v4 render 입력(`runtime-input.json`)에 없다. 코드 편입과 정리는 [infra-kubernetes PR #26](https://github.com/321Team/infra-kubernetes/pull/26)에서 추적한다.
2. **중간 증적 소실:** 전환 중 각 노드 `/var/log/fds-evidence/P1-K8S-01/` 아래 생성된 중간 증적(`avc.*`, firewalld checkpoint, felix·policy overlap 조사, 노드별 collect 사본)은 이후 재부팅으로 소실된 것으로 확인됐다. 따라서 **Gate 2 AVC 판정의 원본 rc·stderr는 확인할 수 없다(NOT VERIFIABLE).** 이 폴더의 8개 파일은 `/root` 아래 보관돼 영향이 없다. 원인은 별도 확인 중.
3. `06`은 `is-active` 결과만 담는다. 부팅 시 비활성(`is-enabled`)은 이 파일로 확인되지 않는다.
4. 이 스냅샷은 수집 시점 상태다. 이후 적용된 변경(예: NodePort 30080 GNP)은 포함하지 않는다.

## 범위 한정

- 이 증적은 Gate 2 전환 후 **상태**를 기록한다. 허용/차단·재부팅·복구 시험 결과 자체는 포함하지 않는다(보안 시나리오 9/9는 [#10 보고](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5772355948) 참조).
- 전환에 사용한 v4 코드의 일부 수정본은 독립 리뷰 전에 실행됐다([PR #26](https://github.com/321Team/infra-kubernetes/pull/26)). 이 편입은 그 코드의 리뷰나 Gate 2 인수를 대신하지 않는다.
- 크로스노드 kubelet(10250)/node-exporter(9100) 접근 문제는 #10에서 별도 추적한다.
