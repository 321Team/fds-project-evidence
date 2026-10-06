# P1-MON-01 — TCP 9100/10250 named HEP·GNP·NAT 원본과 실제 출발지 관측 (2026-10-06 23:05~23:12 KST)

#17 core §2 "TCP 9100/10250은 Calico named HostEndpoint/GNP와 실제 Source 관측으로 검증한다"의 보완 원본입니다. 관련 기록은 다음과 같습니다.
- [대조 기록 6014322597](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6014322597)
- [수집 기록 6018070531](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6018070531)
- [결과 6018178696](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6018178696)

실행자는 MON Lead 이재환이며, 해석은 이 README에만 적습니다. 서버 설정 변경은 없습니다.

## 수집 정보

| 위치 | 계정 | 서버 경로 | 이 PR의 파일 |
|---|---|---|---|
| control01 `10.1.93.102` | `server02` | `~/mon-9100-ro-20261006T2305/` | `control01/ev-control01-9100ro.tgz` + `.sha256` + 풀어낸 파일 |
| k8s-worker02 `10.1.93.107` | `server06` | `~/mon-9100-cap-20261006T2311/` | `worker02/ev-worker02-9100cap.tgz` + `.sha256` + 풀어낸 파일 |

- **전달:** `base64 -w 76`과 줄별 `cksum`으로 받았습니다. 줄 검사합은 control01 114/114, worker02 33/33 일치하고, 복원한 압축본 SHA-256이 서버 출력과 같습니다. 두 회차 폴더 안의 `SHA256SUMS`도 복원본에서 모두 OK입니다.
- **비밀값:** 두 서버 회차 폴더 모두 `eyJ`·`PRIVATE KEY`·`client-key-data`·`token: ` 패턴이 0건이었고(서버 검사), 복원본도 0건입니다. 캡처는 헤더만 남겼습니다(`-s 96`).

## 1. control01 읽기 전용 조회 (23:05:59 KST)

| 파일 | 내용 |
|---|---|
| `01-hep-all.json` | HEP 6개 `fds-k8s-k8s-<node>`. 모두 `interfaceName: ens160`이고 expectedIPs가 노드 IP와 1:1(`.102`·`.103`·`.104` control-plane, `.105`·`.107`·`.108` worker) |
| `02-ippools.json` | `default-ipv4-ippool` `10.244.0.0/16`, `natOutgoing: true`, `ipipMode: Never`, `vxlanMode: CrossSubnet` |
| `03-felixconfig.json` | `default`와 노드별 FelixConfiguration. `defaultEndpointToHostAction` 필드 없음(노드별 failsafe 목록만 있음) |
| `06-calico-node-ds.json`, `07-felix-env.txt` | calico-node env `FELIX_DEFAULTENDPOINTTOHOSTACTION=ACCEPT`. `CALICO_IPV4POOL_*` env가 IPPool과 같음 |
| `04-monitoring-api-pods.txt` | prometheus·grafana·alertmanager → worker03, kube-state-metrics → worker02 |
| `05-summary.txt`, `00-time.txt` | 위 요약과 수집 시각·RC(모두 0) |

## 2. worker02 헤더 캡처 (23:11:50~23:12:18 KST)

| 항목 | 값 | 파일 |
|---|---|---|
| 명령 원문 | `timeout 90 sudo tcpdump -i ens160 -nn -s 96 -c 40 -tttt 'tcp dst port 9100 or tcp dst port 10250'` | `cap-cmd.txt` |
| 종료 | `rc=0`(40패킷 도달) | `cap-rc.txt`, `cap-start.txt`, `cap-end.txt` |
| 통계 | `listening on ens160`, 40 captured / 44 received / 0 dropped | `cap-stats.txt` |
| 출발지 | `10.1.93.108` 40/40 | `cap.txt` |
| 목적지 | `10.1.93.107:10250` 32, `:9100` 8 | `cap.txt` |

## 해석

| 흐름 | named HEP / GNP | 출발지 근거 | 실제 관측 |
|---|---|---|---|
| Prometheus(worker03 Pod) → worker01·02 `:9100`·`:10250` | HEP `fds-k8s-k8s-worker0{1,2}` + GNP `fds-k8s-host-k8s-worker0{1,2}` ingress[3](출발지 `.107/.108`·`.105/.108`) | natOutgoing: IP pool 밖 노드 IP로 갈 때 노드 IP `.108`로 SNAT | **worker02에서 `.108` 관측(이 폴더)** |
| Prometheus → control 3대 `:10250` | HEP `fds-k8s-k8s-control0{1,2,3}` + GNP ingress[1](노드 6대) | 같음 | evidence#81 `.108 → .102:10250` |
| worker03 Pod → 자기 노드 `:9100`·`:10250` | HEP ingress 대상 아님 | `FELIX_DEFAULTENDPOINTTOHOSTACTION=ACCEPT` | 해당 없음 |

GNP 원문은 [evidence#122](https://github.com/321Team/fds-project-evidence/pull/122) `control01/canary-20261006/01-gnp-all.json`(10/6 16:36 수집)을 따릅니다.

## 한계

- worker02 캡처는 이미 열린 keep-alive 연결의 데이터·ACK였고, 새 SYN은 이 구간에 없었습니다. **출발지 관측**으로만 쓰고 연결 수립 시점 관측으로 쓰지 않습니다.
- worker01의 실제 출발지는 관측하지 않았습니다. 같은 규칙과 같은 SNAT 경로라는 원본 결속만 있습니다. #17 기록에는 worker01로 예고했지만 실제 실행은 worker02입니다(결과 코멘트에 기록).
- 차단 쪽(비승인 출발지 거부)은 AC-04 증적(evidence#99·#119)을 따르며, edge 6행 INCONCLUSIVE는 그대로입니다.
- GNP 원문은 16:36 수집, HEP·IPPool·Felix는 23:05 수집으로 시점이 다릅니다. 그 사이 GNP 변경 기록은 없으며, canary GNP는 16:42 삭제 후 목록이 생성 전과 같았습니다(evidence#122 `08-gnp-after.txt`).

## 파일 무결성

- `SHA256SUMS`: 이 폴더 전체 파일(README 포함, 자기 자신 제외)
- `*/ev-*.tgz.sha256`: 압축본 sidecar(서버 출력값과 같음)
- `ARCHIVE_CONTENTS`: 압축본별 파일 목록

AI 사용: CLAUDE_ASSISTED (명령 작성, 전달 복원·대조, README 작성)
