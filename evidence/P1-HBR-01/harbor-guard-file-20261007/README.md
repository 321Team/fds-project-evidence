# P1-HBR-01 AC-04 — harbor01 guard 규칙 파일 `/etc/p1-hbr-ac04.nft` 내용·해시 (2026-10-07)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 실행: 이하영(HBR Lead), ansible01 `server01_ansible`. 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 AC-04 인수나 Docker restart persistence의 PASS가 아니다.** 읽기 전용 조회이며 서버·방화벽을 변경하지 않았고 규칙을 적용하지 않았다(`nft -c`는 문법 검사만 한다).

## 근거
[권욱 님 심층 리뷰 6017678964](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6017678964) §4(HB-R3)가 Docker restart 실행안에서 "guard 파일·unit/의존성/활성 상태, 현행 source·hook/priority·규칙 원본과 승인 소스/해시를 연결"하도록 요구했다. [실행안 v2 6030202914](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6030202914)가 이 파일의 내용·해시를 시작 전에 추가 수집한다고 밝혔고 이 폴더가 그 결과이다. 서비스 의존성·상태 쪽 원본은 [evidence#132](https://github.com/321Team/fds-project-evidence/pull/132)(`harbor01-docker-prestate-20261007T120724.txt`)에 있다.

## 파일과 해시
| 경로 | 크기 | SHA-256 | 내용 |
|---|---|---|---|
| `server-originals/harbor01-guard-file-20261007T122150.txt` | 1601 | `8b062cf584de313bcbaa0d8c0bd1b0b66ae6ce95b02241c1dce956285246d4e5` | 2026-10-07 12:21:50 KST harbor01(ansible `-b`, `svc_ansible`) 읽기 전용 조회 출력: `ls -l`, 서버 측 `sha256sum`, 파일 내용 `cat`, `nft -c -f` 문법 검사 결과 |
| `server-originals/p1-hbr-ac04.nft.extracted` | 1316 | `cdc84effbb370ac394408294e21a4d3cbb67c3d69e93ea53e86667d4326cf5cc` | **추출본(원본 아님).** 위 출력의 "== 파일 내용" 절을 그대로 잘라 저장한 것. 서버 `sha256sum`과 같은 값 |
| `observations/ansible01-SHA256SUMS.local-20261007.txt` | 106 | (SHA256SUMS 참조) | ansible01에서 파일을 복사해 묶기 전에 만든 해시 목록 |

ansible01 터미널 해시(`8b062cf5…d4e5`)와 공유 폴더 경유 본 PC 사본이 일치했고, 출력의 파일 내용 절을 다시 해시한 값(`cdc84eff…f5cc`, 1316바이트)이 서버가 보고한 값과 크기·해시 모두 같다.

## 내용 요약 (원본 기준)
- 서버 파일 `/etc/p1-hbr-ac04.nft`: 1316바이트, root 소유 `0600`, mtime 2026-10-04 21:32, 서버 `sha256sum` `cdc84eff…f5cc`.
- 첫 규칙이 `destroy table inet p1_hbr_ac04`이고 같은 파일에서 `table inet p1_hbr_ac04`를 다시 정의한다. 파일 주석은 "destroy is idempotent and the nft -f batch is transactional"이라고 설명한다.
- `set approved_v4`(ipv4_addr) 6개: `10.250.10.20`, `10.1.93.105`, `10.1.93.107`, `10.1.93.108`, `10.1.93.50`, `10.1.93.102`.
- `chain forward_guard`: `type filter hook forward priority -1; policy accept`. 규칙 3개(모두 `iifname "ens160"`, DNAT된 `ct original ip daddr 10.1.93.54`의 TCP 443): 승인 IPv4 `counter accept`, 비승인 IPv4 `counter drop`, IPv6 `counter drop`.
- `nft -c -f /etc/p1-hbr-ac04.nft`: **CHECK_OK**(문법 검사만, 적용 없음).
- 이 내용의 허용 IP 6개·규칙 3개·hook/priority는 이전에 병합된 [복구 후 보완 원본](https://github.com/321Team/fds-project-evidence/pull/129)의 `nft list table`(2026-10-06 22:01)과 같다. 현행 소스(infra-ansible `hbr.yml`·템플릿)의 기본4+임시2와 같은 구성이다.

## 한계 (숨기지 않음)
1. **파일 내용은 ansible 출력에서 읽은 텍스트**이며 파일 자체를 바이너리로 복사한 것이 아니다. 다만 내용 절을 다시 계산한 해시가 서버 해시와 일치한다. `extracted`는 그 절을 잘라 만든 파생 파일이다.
2. `nft -c`는 문법·커널 호환성 검사이며 이 파일의 적용 결과나 live 테이블과의 일치를 증명하지 않는다. live 테이블과의 대조는 `nft list table` 원본(#129)에서 한다.
3. 파일에 `destroy table`이 있으므로 같은 파일을 다시 적재하면 테이블이 새로 만들어져 규칙의 `counter` 값이 0에서 다시 시작할 것으로 **추정**한다(nft 동작에 따른 해석이며 이번에 적용 시험으로 확인하지 않았다).
4. 이 파일이 부팅·Docker 재시작 뒤에도 적용되는지(자동 적재 시점)는 이 원본으로 확인하지 못했다. 서비스 의존성은 #132의 `docker.service`/guard unit 출력이 근거이다.
5. 서버 측 봉인·독립 재해시는 하지 않았다.
