# P1-HBR-01 AC-04 — harbor01 적용 전 상태 원본 편입 (2026-10-05)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). 실행·수집: 이하영(HBR Lead), ansible01 `server01_ansible`. 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 AC-04 PASS 선언이 아니다.** 기존 [apply 원본 편입(evidence#109)](https://github.com/321Team/fds-project-evidence/pull/109)에는 harbor01 서버 상태 파일의 원문이 없었고(목록·일부만), 이 폴더가 그 빈칸을 채운다.

## 무엇인가

2026-10-04 21:32 harbor01에 AC-04 guard를 적용하기 직전, 적용 playbook이 `/var/lib/fds-change/P1-HBR-01-AC04/`에 만든 **적용 전 상태 원본**이다. 같은 디렉터리의 `PRESTATE_SHA256SUMS`가 5개 파일의 해시를 봉인한다(root 소유, 0600).

| 파일 | 크기 | 내용 | 수집 방식 |
|---|---|---|---|
| `server-originals/original-state.json` | 4066 | 적용 전 firewalld/Docker 상태 | 10/5 오전 터미널 출력 **전사** → 봉인 해시와 일치 |
| `server-originals/original-public.xml` | 392 | 적용 전 `public` zone 원문(`443/tcp` 전역 허용 포함, 원본 mtime 8/26) | 전사 → 봉인 해시 일치 |
| `server-originals/iptables-filter-before.txt` | 1434 | 적용 전 iptables filter | 전사 → 봉인 해시 일치 |
| `server-originals/iptables-nat-before.txt` | 890 | 적용 전 iptables nat | 전사 → 봉인 해시 일치 |
| `server-originals/nft-ruleset-before.txt` | 15914 | 적용 전 nft 전체 ruleset | **`ansible fetch`로 harbor01에서 직접 복사(바이트 그대로)** 2026-10-05 22:51 KST → 봉인 해시 일치 |
| `server-originals/PRESTATE_SHA256SUMS` | 444 | 위 5개 파일의 서버 측 봉인 | 전사 |
| `server-originals/applied.txt` | 229 | 적용 시각·backend·nft table 마커 | 전사. **봉인 대상이 아니어서 해시 대조 없음** |

원격 `ls -l`(`observations/remote-ls-sha.txt`)의 크기가 위 표와 일치한다: PRESTATE 444, applied 229, iptables-filter 1434, iptables-nat 890, nft 15914, original-public 392, original-state 4066.

## 해시 대조

`cd server-originals && sha256sum -c PRESTATE_SHA256SUMS` — 5개 모두 OK. 봉인 값:

| 파일 | SHA-256 |
|---|---|
| `original-state.json` | `1090de081eb5969f2fc5e1d890f6f022494cf652356a6b8d541be70d6b62d83f` |
| `original-public.xml` | `cbada46d45b3c1756cbdf45fbbb5d104ea3ecab8ac8a85834c831e670d8a862f` |
| `iptables-filter-before.txt` | `2b02a2f3f112c6b47e81622c7168298bd07cb8fba06c2b33cf425ebcd002efa0` |
| `iptables-nat-before.txt` | `1306255da65229fb4cad5ec03051074cea36d039ec66c3ffdb894001815df1a1` |
| `nft-ruleset-before.txt` | `eea8d726e92f3a2f0367a195ef9f38e3019846ead25797bd7deeb6bb52591553` |

`nft-ruleset-before.txt`는 harbor01 원격 `sha256sum`, ansible01 수신본, 공유 폴더 경유 본 PC 복사본 3곳의 해시가 모두 위와 같다.

## 관측 파일

| 파일 | 내용 |
|---|---|
| `observations/remote-ls-sha.txt` | 2026-10-05 22:51 harbor01 상태 디렉터리 `ls -l`과 `nft-ruleset-before.txt`의 원격 `sha256sum`(ansible 출력) |
| `observations/fetch-result.txt` | `ansible fetch` 결과(원격·로컬 체크섬 일치) |
| `observations/ac04-e1c4458-precheck-20261004T211015.txt` | 10/4 21:10 `e1c4458` 사전 점검 실행의 출력 파일. **37바이트, 내용은 ` [ERROR]: User interrupted execution` 한 줄**(그 실행이 중단되었음을 보이는 이상 기록). 같은 시각대 정적 검증 13/13·사전 점검 PASS는 화면 출력 기준이며 [apply 원본 편입(#109)](https://github.com/321Team/fds-project-evidence/pull/109)과 [baseline #13 코멘트](https://github.com/321Team/fds-project-baseline/issues/13)가 근거이다. 이 파일이 그 PASS를 뒷받침하지는 않는다 |

## 한계 (숨기지 않음)

1. **전사 파일:** `original-state.json`, `original-public.xml`, `iptables-*-before.txt` 4개는 파일을 그대로 복사한 것이 아니라 **터미널 출력을 옮겨 적은 것**이다. 봉인 해시와 일치하므로 내용 동일성은 확인되지만 수집 방식은 전사이다. `PRESTATE_SHA256SUMS`와 `applied.txt`도 전사이며 후자는 대조 대상이 없다.
2. **수집 시점 차이:** 적용은 2026-10-04 21:32:34~21:33:20, 상태 원본 수집은 2026-10-05(전사 오전, nft 22:51)이다. 서버 상태 디렉터리는 적용 후에도 보존되어 있었다(파일 mtime 10/4 21:32~21:33).
3. **적용 후 상태·Docker 재시작 후 유지·임시 예외 제거는 이 폴더 범위 밖**이다. AC-04의 인수 판단은 이 편입과 별개로 이권욱이 한다.
4. 서버에서의 독립 재해시는 하지 않았다. 해시는 실행자 수집값이다.
