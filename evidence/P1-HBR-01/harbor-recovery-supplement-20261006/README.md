# P1-HBR-01 — harbor01 기동 복구 후 읽기 전용 보완 3건 원본 편입 (2026-10-06)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 실행: 이하영(HBR Lead), ansible01 `server01_ansible`. 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 AC-04 인수, Docker restart persistence, IPv6 차단 시험의 PASS가 아니다.** 서버·Harbor·방화벽을 변경하지 않았고 새 트래픽 시험도 하지 않았다.

## 근거
- 요청: 권욱 님 [복구 결과 수용 6009618698](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6009618698) 3절(최소 보완 3건, 기존 원본 우선 연결·빠진 항목만 읽기 전용 보완)
- 복구 완료 기록: [#13 6009420194](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6009420194) (실제 기동 2026-10-06 13:17:03~13:21:44)

## 중요: 이 값은 복구 당시가 아니라 보완 조회 시점(2026-10-06 22:01~22:02 KST)의 상태이다
복구 전후 원본(`harbor01-ident-…T125715`, `…start-precheck-…`, `…start-run-…`, `…start-post-…`, ansible01 보관)에는 `mounts` 단어(마운트 **수** 확인)는 있으나 `NetworkMode`·`PortBindings`·`Destination`(마운트 정의)은 없음을 확인했다(실행자 터미널에서 4개 파일 `grep -c` 결과, 4개 모두 Mounts=11·나머지 0; 이 확인 출력은 파일로 저장하지 않았다). 그래서 빠진 항목만 읽기 전용으로 새로 조회했다.

## 파일과 해시
| 경로 | 크기 | SHA-256 | 내용 |
|---|---|---|---|
| ★ `server-originals/harbor01-supplement-20261006T220106.txt` | 12855 | `0a20c2f7a8252817383d695c14141500197f0ce7f2dabc409d1f2209d177aebf` | 22:01:07 KST harbor01 읽기 전용 조회(ansible `-b -m shell`, `svc_ansible`): 컨테이너 10개의 id·image·netmode·ports·mounts(Env 제외), `nft list table inet p1_hbr_ac04`, `firewall-cmd --list-all --zone=public`, 443 listener(`ss`), `ip -6 addr` |
| ★ `server-originals/monitoring-api-pods-20261006T220211.txt` | 646 | `db1eae7970457103d0b2ba53621c3f5542286b14d2e7556edeb8a9db0a0829ad` | 22:02:11 control01(`server02`, ssh) `monitoring-api` Pod의 UID·노드·시작 시각·READY |
| `observations/monitoring-api-pods-20261006T220215.txt` | 646 | `1f99cab9731142d5eb95dbe4722f57c9ddfb71bacac1b2dd97624ccb9521f629` | 같은 명령 재실행(22:02:15). 시각 줄만 다르고 Pod 내용은 같음 |
| `observations/harbor01-supplement-20261006T220009.txt` | 580 | `9fc3423fc5fbf4bbb8d1f49958086343b21f74fa6d5564115623866ee1b44585` | **실패한 1차 시도.** ansible이 명령 안의 `{{ … }}`(docker 템플릿)를 자기 템플릿으로 해석해 `template error … unexpected '.'`. **harbor01에 명령이 전달되지 않음** |
| `observations/harbor01-supplement-20261006T220014.txt` | 580 | `9fc3423fc5fbf4bbb8d1f49958086343b21f74fa6d5564115623866ee1b44585` | 같은 오류의 재실행(위와 동일 내용) |
| `observations/container-id-compare.txt` | 280 | (SHA256SUMS 참조) | 22:01 컨테이너 전체 ID의 앞 12자 10개를 복구 전 원본(`ident`)·복구 후 원본(`post`)에서 `grep -c`한 결과 |
| `observations/ansible01-SHA256SUMS.local-20261006.txt` | 621 | (SHA256SUMS 참조) | ansible01에서 파일을 한 폴더로 복사한 뒤 만든 해시 목록 |

ansible01에서 터미널에 출력된 해시 5개와 공유 폴더 경유 본 PC 사본이 5/5 일치했다.

## 보완 ① 컨테이너 마운트 정의·네트워크·포트
22:01:07 현재 컨테이너 10개(`harbor-jobservice`, `nginx`, `trivy-adapter`, `harbor-core`, `redis`, `harbor-db`, `registryctl`, `registry`, `harbor-portal`, `harbor-log`)가 모두 netmode `harbor_harbor`이다. 마운트는 종류(bind/volume), 컨테이너 안 위치(Destination), 호스트 경로(Source), 읽기/쓰기(RW)까지 원본에 있다. 포트: `nginx` 컨테이너 8080→호스트 80, 8443→호스트 443(`HostIp` 빈값), `harbor-log` 10514→`127.0.0.1:1514`, 나머지는 노출 포트 없음. **Env(환경변수)는 출력하지 않았다.** 마운트 Source에는 `/data/secret/...`·`/home/server08/harbor/...` 같은 호스트 **경로**가 보이나 내용은 아니다.

**복구 전후와의 연결:** `container-id-compare.txt`에서 10개 ID 접두(12자) 모두가 복구 전 원본과 복구 후 원본에 있다(각 파일에서 2회 출현). 같은 컨테이너(이름·ID)가 복구 전·후·현재에 이어졌다는 정황이며 12자 접두 비교이다. 복구 전·후에 마운트 정의가 같았는지는 전후 원본에 정의가 없어 **확인하지 못했다.**

## 보완 ② worker03 Pod 귀속
`monitoring-api` Pod(22:02:11): `grafana-f65457bfd-ckjgj`(UID `916b8c8a-ff21-42ba-9815-11dce4cde848`), `alertmanager-6bf6dc555-bs8cg`(`3add1a86-f390-4123-bb69-8a1f5bba8e4a`), `prometheus-d8949bd64-2zc4m`(`265ca811-873c-45e1-8c46-6c1ce034e596`)는 모두 **`k8s-worker03`**에서 시작 `2026-10-06T04:24:02Z`/`04:24:24Z`/`04:24:32Z`(KST 13:24:02/13:24:24/13:24:32), READY true. 복구 완료 기록의 UID·시작 시각과 같다. `kube-state-metrics`(UID `33ee4ee5-723a-400c-831d-9549bafea1a0`)는 `k8s-worker02`에서 2026-10-06T00:57:53Z(KST 09:57:53)부터 정상이다. restart 수는 조회 열에 넣지 않아 이 원본에는 없다.

## 보완 ③ IPv6 listener·정책 경로
- **guard:** `table inet p1_hbr_ac04`, `chain forward_guard` `type filter hook forward priority filter - 1; policy accept`. 규칙 3개(모두 `iifname "ens160" ct status dnat … ct original proto-dst 443`): 승인 IPv4 accept(17962 패킷), 비승인 IPv4 drop(50 패킷), `meta nfproto ipv6` published 443 drop(0 패킷). `approved_v4` 6개: `10.1.93.50, .102, .105, .107, .108, 10.250.10.20`. counter는 규칙 적재 이후 누적이다.
- **firewalld `public`:** interfaces `ens160`, services `cockpit dhcpv6-client ssh`, ports 없음, rich rules 없음, forward yes. 즉 일반 `443/tcp` 허용은 없다.
- **listener:** `0.0.0.0:443`과 `[::]:443`, 모두 `docker-proxy`.
- **IPv6 주소:** `lo`의 `::1`과 Docker 브리지·veth의 link-local만 있고 **`ens160`에는 IPv6 주소 항목이 없다.**

## 한계 (숨기지 않음)
1. **현재(22:01) 상태이다.** 복구 당시 값이 아니며 복구 전후와의 정의 비교는 하지 못했다(위 "중요" 절).
2. **IPv6 차단을 시험으로 증명하지 않았다.** `[::]:443` listener와 `ens160`에 IPv6 주소가 없다는 사실은 외부에서 IPv6로 닿기 어렵다는 정황일 뿐이다. 위 drop 규칙은 FORWARD 경로(`ens160`에서 들어와 DNAT된 443)만 대상이어서 `docker-proxy`가 받는 host 입력 경로를 이 규칙이 검증한다고 주장할 수 없다. 새 트래픽 시험은 하지 않았다.
3. 컨테이너 ID 대조는 앞 12자 비교이며 서버에서 독립 재해시하지 않았다.
4. restart 수와 worker01·worker02의 이미지 경로는 이번에 확인하지 않았다.
5. 원본은 ansible·터미널 출력이며 서버 쪽 봉인이 없다.
6. 이 편입은 AC-04 인수나 Docker restart persistence·임시 예외 제거 승인을 뜻하지 않는다.
