# CR-P1-NTP-01-01 읽기 전용 재수집 — 2026-09-24

[infra-ansible PR #44](https://github.com/321Team/infra-ansible/pull/44) 리뷰의 지적을 해소하기 위한 수집이다. 지적은 두 가지였다.
- 9/21 기준이 9/22 HEP/GNP 적용 전 상태다.
- 수집 원본이 증적 저장소에 등록돼 있지 않다.

이 자료는 Gate 2 이후 노드 방화벽·Calico 정책·chrony의 **현재 상태**를 기록한다. A안(Calico GNP 기준 후속 검증)의 입력 근거로 쓴다.

## 출처와 수신

| 항목 | 값 |
|---|---|
| 대상 | k8s-control01~03, k8s-worker01~03 (6대), Calico 객체는 k8s-control01에서 조회 |
| 실행 위치·계정 | `server01_ansible@ansible01`, 원격 `svc_ansible` + 비대화형 sudo, 키 `/home/server01_ansible/.ssh/p1_ansible_ed25519` |
| 실행 방식 | `ansible k8s_nodes -b -m ansible.builtin.script -a "collect-node.sh GWONUK"`, `ansible k8s-control01 -b -m ansible.builtin.script -a "collect-calico.sh GWONUK"` |
| 사용한 checkout | `/home/server01_ansible/p1-ans-01` @ `da7f2ccd52ee407e61376d11375a1361f076f112` (`CHECKOUT.txt`). 사용한 파일은 인벤토리와 `ansible.cfg`뿐이다 |
| 수집자 | GWONUK (각 `meta.txt`의 `collector=`) |
| 수집 시각 | 노드: 2026-09-24T11:27:40Z–11:28:30Z (20:27–20:28 KST)<br>Calico: 11:28:31Z |
| 회수 | ansible01의 `ansible.builtin.fetch`로 회수. 원격·로컬 checksum 일치 |
| 전달 경로 | 노드 `/root` → ansible01 `~/ntp-recapture/raw/` → 이 브랜치에 push (ansible01에서 직접) |
| 수신 | 2026-09-24 21:46 KST, 커밋 `2c840a0` |

## 무결성

실행 로그(`run-*.log`)가 각 tar.gz의 SHA-256을 기록한다. `EXPECTED.sha256`은 이 로그에서 추출했다. 각 tar.gz 안의 `SHA256SUMS`는 수집 시점에 노드에서 생성된 것이다.

```bash
sha256sum --check EXPECTED.sha256                 # 7개 OK
for f in raw/*.tar.gz; do tar -xzf "$f" -C /tmp/x; done
for d in /tmp/x/*/; do (cd "$d" && sha256sum -c --quiet SHA256SUMS && echo "OK $d"); done
sha256sum collect-*.sh                            # SCRIPTS.sha256 과 일치
```

제출자(ansible01)와 편입 작성자가 각각 위 대조를 수행했고 모두 일치했다. tar.gz는 저장소 `.gitignore`의 `*.tar.gz` 규칙 때문에 기존 관례대로 `git add -f`로 원본 바이트 그대로 추가했다. 줄바꿈 변환은 없다(`.gitattributes` `* -text`).

| 파일 | SHA-256 |
|---|---|
| `raw/ntp-recapture-k8s-control01-20260924T112740Z.tar.gz` | `5bd813f32004e6b31456c85b75715aafc63f740808bfbeb50d7bacffe0853b5e` |
| `raw/ntp-recapture-k8s-control02-20260924T112740Z.tar.gz` | `8b1dd24e3e87517934fb6e9bb67a9a5482b28ebd99cba6e239e0f61cf19ab0a7` |
| `raw/ntp-recapture-k8s-control03-20260924T112740Z.tar.gz` | `d13f7936dc9ea9b1eb67b188a0b83e516252aec33bff2cf3a201bc04ac319075` |
| `raw/ntp-recapture-k8s-worker01-20260924T112740Z.tar.gz` | `264b6c579eefe471fd7cf3f6d2a612d38b953ab465653d2b0e93c84206cbb722` |
| `raw/ntp-recapture-k8s-worker02-20260924T112740Z.tar.gz` | `456d955e87334dd8512c0f94787ba1f4b7ef3814b9b1a643113127dc3424f480` |
| `raw/ntp-recapture-k8s-worker03-20260924T112740Z.tar.gz` | `f54a8edb4cbf93451634127a53e7df91be8bba30cbeca6a7af215578a09cd930` |
| `raw/ntp-recapture-calico-20260924T112831Z.tar.gz` | `fdf96e873f830cb2cb594b9dbc6e4df5d0f3e447a65a76c0fc30ca00563989a7` |
| `collect-node.sh` | `f46ff59243e02affd525f586e6b88cd39a9e2719067a1742efd652b313a6cae5` |
| `collect-calico.sh` | `064dcdf6778e1f280aa3de47db218d42f22c8808a7ee7581038cfb021623991f` |

비밀정보:
- kubeconfig·키·토큰 내용은 수집하지 않는다. `kubeconfig.stdout`에는 경로·소유자·권한만 들어 있다.
- 비밀번호·키 패턴을 검사한 결과 해당 없음.
- 내부 IP·호스트명·정책 원문은 포함되며, Private 저장소 기준으로 편입한다.

## 수집 회차 경위

| 회차 | 시각 | 상태 |
|---|---|---|
| 1회차 | 09:29:24Z (노드), 09:30:15Z (Calico) | 정상 실행됐다. 이후 터미널 붙여넣기 사고로 수집 명령이 다시 실행되면서 `run-*.log`가 덮어써졌다. 해시는 화면 캡처에만 남아 **이 편입에서 제외**한다. 원본 tar.gz는 각 노드 `/root`에 삭제하지 않고 남아 있다 |
| **2회차 (정본)** | 11:27:40Z (노드), 11:28:31Z (Calico) | 실행 로그 → `EXPECTED.sha256` → 회수본 → 내부 SHA256SUMS가 끊김 없이 이어진다 |

두 회차 모두 같은 읽기 전용 스크립트다. 서버 상태 변경은 없다. 붙여넣기 사고 때 ansible01의 작업 checkout에 빈 파일 `{`가 생겼으며, 크기 0을 확인한 뒤 삭제했다.

커밋 `2c840a0`의 작성자 이메일은 설정 누락으로 자리표시자 문자열(`<본인 GitHub 계정 이메일>`)로 기록됐다. 수집자는 `meta.txt`로 확인할 수 있다. 출처 해시를 고정하기 위해 커밋은 수정하지 않았고, 이후 커밋을 위해 저장소 설정만 정정했다.

## 수신본에서 확인한 사실

rc 확인 결과:
- 계약 입력(`iptables-save`, `iptables-save -c`, `ip6tables-save`, `nft`, `ipset`, `kubectl get … -o json`)의 rc는 모두 0이다.
- 0이 아닌 rc는 두 가지뿐이다.
  - firewalld 조회: `firewall-cmd`가 `not running`
  - `calicoctl`: 설치돼 있지 않음 (rc 127)

| 항목 | 6대 결과 |
|---|---|
| firewalld | `is-active` **inactive**, `is-enabled` **disabled**. 9/22 Gate 2 증적에서 확인되지 않았던 `is-enabled`가 이번에 확인됐다 |
| 기존 NTP 전용 체인 `FDS_NTP_0101` | IPv4·IPv6 모두 없음 (`iptables -L` rc 1, `No chain`) |
| `/etc/firewalld/direct.xml` | 파일은 남아 있다(9/21 10:55 수정). firewalld가 비활성이라 커널에는 반영되지 않는다 |
| HEP | `fds-k8s-k8s-*` 6개, `interfaceName: ens160`, `expectedIPs`가 인벤토리 IP와 일치 |
| GNP | `fds-k8s-host-*` 6개(order 100), `nodeport-30080-allow`(order 50, TCP preDNAT) |
| FelixConfiguration | default에는 failsafe 설정이 없다. 노드별 설정의 failsafe에는 UDP/123이 없다(TCP 22/6443/2379/2380만) |
| Felix 커널 경로 | `OUTPUT → cali-OUTPUT → cali-to-host-endpoint → (-o ens160 -g) cali-th-ens160 → cali-po-*`, end-of-tier DROP 있음 |
| chrony (1회) | 6대 active<br>클라이언트 5대: `10.1.93.102` 선택<br>control01: `162.159.200.123` 선택<br>offset 모두 1ms 미만 |
| 부팅 | uptime상 6대 모두 **2026-09-23 18:08–18:32 KST에 재부팅**됐다. 9/21 NTP 적용과 9/22 Gate 2 이후다. 재부팅 사유와 절차는 이 자료로 확인되지 않는다 |
| 보존 파일 | chrony.conf, CR drop-in, `original-ntp-pair.json`은 존재한다. `original-ntp-dropin.json`은 6대 모두 없다(ABSENT). 판정하지 않고 기록만 한다 |

## 범위 한정

- 이 자료는 수집 시점의 **상태**만 기록한다. NTP 패킷 시험(정상 경로, 음성 차단, 60초×6회 관측)은 수행하지 않았다(`ntp_probe=false`).
- 9/23 재부팅 이후 chrony와 firewalld 상태가 관측됐다. 하지만 이것은 계획된 재부팅 지속성 시험이 아니므로 AC의 재부팅 항목 PASS로 쓰지 않는다.
- A안 검증기(infra-ansible `claude/hopeful-rubin-yrm9j0`)로 이 자료를 오프라인 평가했다. 결과는 계약 6대 PASS, 커널 구조 6대 PASS다. 이는 코드 리뷰 전의 LOCAL 결과이며 Runtime PASS가 아니다.
- control01의 Cloudflare egress와 NTP ingress 규칙의 승인 여부는 이 편입에서 판정하지 않는다([infra-kubernetes PR #26](https://github.com/321Team/infra-kubernetes/pull/26)).
- 이 편입은 CR-P1-NTP-01-01의 최종 인수나 Gate 2 인수를 대신하지 않는다.
