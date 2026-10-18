# Ansible #9 — 현재 OS/DNS 6대 한정 읽기 보충 증적

CODEX_ASSISTED · 2026-10-18 KST · P1-ANS-01.
**PUBLICATION=PREPARATION_ONLY. 이번 추가 후보의 게시·독립 리뷰·병합은 아직 수행하지 않았다.**

## 실제 판정

2026-10-18 **20:19:10.747250~20:19:14.502430 KST**, 기존 strict SSH/sudo 경로로 6대를 한 번씩 조회했다. 명령 **66건 rc0**(그중 DNS 조회 명령30건), 자동 재시도0이다. 판정은 `PASS_SCOPED_CURRENT_OS_DNS_6`다. 아래 결과는 당시 한정 관측이며 지속 보장이나 전체 엔진 인수가 아니다.

| 항목 | 관측 및 기준 대조 |
|---|---|
| 대상 | control01~03, worker01~03. hostname·machine-id·boot-id 모두 기존 19:56 paired 전후와 일치 |
| OS | CentOS Stream10, SELinux Enforcing, Asia/Seoul·NTPSynchronized=yes, 활성 swap0, 기존 overlay/br_netfilter 및 sysctl3개, 관리 복귀 경로 일치 |
| DNS 설정 | 10.1.93.52 → 10.1.93.53, search fds.internal, ignore-auto-dns=yes |
| 내부 응답 | 각 DNS 직접 조회와 k8s-api.fds.internal·k8s-api 시스템 조회 모두 10.1.93.109 |
| 외부 응답 | github.com IPv4 조회 성공. 반환 IP는 관측값이며 고정 수용 기준이 아님 |
| hosts 경로 | nsswitch의 `files dns myhostname` 관측. 새 AC를 추가하지 않음 |

기준은 기존 성공한 `combined-20260914-review`와 infra-ansible `357965058cdcaa129b14c29a09b3e4e19215195f`의 기존 #6/#7 OS/DNS 항목이다. 정확 baseline 코드3개는 `baseline-source/`, 보고서 위치·SHA 및 당시 단계 결과는 `provenance/BASELINE.json`에 있다. 19:56 chronyd 상태는 상위 `analysis/paired.json`을 재사용했다.

## 원본·연결·무결성

- `originals/<host>/stdout.json`: 명령 argv·시각·rc·원출력과 필요한 설정 관측. `stderr.txt`는 실제 bridge 반환 영수증을 포함한다. `INTENT.json`·`RECEIPT.json`은 대상과 원본 SHA를 연결한다.
- `executed-source/`: 실제 stdin source6개, 공유 reader/dispatcher와 동일 bridge body1개. `LINKAGE.json`이 각 원래 bridge SHA·source·intent를 연결한다. **보존용이며 재실행 허용 또는 새 운영 도구가 아니다.**
- `LINKAGE.json`: 기존 상위 paired 전후 원본12개 및 exact binding을 경로·SHA로 연결한다. 기존 파일은 복사하거나 바꾸지 않았다.
- `provenance/SOURCE_MANIFEST.json`·`SOURCE_FINAL.json`: 출처 디렉터리의 봉인 인덱스이다. 이 추가 후보의 포함 목록은 `PUBLICATION_COPY_MAP.json`과 `SHA256SUMS`를 사용한다. 출처 인덱스의 모든 파일을 편입했다는 뜻이 아니다.
- `analysis/`는 파생 판독이다. 로컬 검증은 원본·명령 출력 SHA와 대상·기준을 대조했다. 최초 분석의 Windows 경로 접두어 중복으로 manifest 생성만 실패한 사실을 보존했으며, 별도 로컬 finalizer에서 완결했다. 서버 조회는 반복하지 않았다.

resolv/nsswitch는 필요한 행과 전체 파일의 관측 SHA만 보존했다. 전체 파일 바이트를 반출·재검증했다고 주장하지 않는다. 호스트·계정·내부 경로와 SSH 키 **경로명**은 추적 메타데이터이며 키 본문·토큰·암호가 아니다. 해시 일치는 바이트 무결성이며 성공·사람 수신·인수를 대신하지 않는다.

## 범위와 남은 조건

이번 서버 실행은 한정 읽기뿐이며 설정·서비스·패키지·원격 임시 설치·토큰/credential 변경0이다. 게시 준비 단계의 신규 원격/CI/GitHub/공통 기록 변경도0이다. 과거 PR87/185/기존 CI는 재실행하지 않았다.

전체 #7 CLI·하드닝·API listener, role/engine 전환, NTP 별도 AC 전체, 장기 연속성은 이번 조회로 입증하지 않는다. 기존 NTP 실패·성공 범위를 바꾸지 않는다. **공유 원본17개 사람 직접 열람 회신은 미완료이며, 최종 caller·Collection·대상 범위 선택과 운영 인수도 별도다.** 이 읽기 결과만으로 #9를 닫지 않는다. 정상 서비스 apply/rollback 시험·새 공통 GO·Phase2 작업을 추가하지 않는다.

중앙이 PR244의 지정 HEAD를 실제 대상과 대조한 후 한 번의 추가 커밋으로 게시할 후보다. 이 폴더 준비자는 PR244·기존121파일·동결 출처를 변경하지 않았다.
