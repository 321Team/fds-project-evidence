# SSH 이름 결속 선행조건 — 추가 읽기 전용 수집

CODEX_ASSISTED. baseline#13 / code#22 HEAD `918603f7187bff211cd80347a1f030babf26dc10` 준비.
독립 리뷰는 사용자 결정대로 **2026-10-09 09:00 KST 이후**이며 지금은 증적 편입 후보다.

## 판정

2026-10-09 **01:41:37 KST** 사용자 GWONUK의 server08 VM 콘솔 sudo 실행 결과다.
대상 harbor01 격리 clone, guest UUID `389e4d56-24f0-e2ef-b68f-137a5047788a`.
private `/root/hbr-ssh-naming-_prye0m5`, 수집 명령 `sudo bash /mnt/hbr-ssh-naming/stage-local.sh`.
물리 NIC 없음/UUID/root/hostname/만료를 확인하고 root local 복사본에서 실행했다.

- udev **257**, systemd-udevd **active**, SELinux **Enforcing**, 조회 4건 rc0/stderr0.
- `/etc/systemd/network`, `/run/systemd/network`, `/usr/lib/systemd/network`: root:0755,
  디렉터리 존재·symlink 아님. `/usr/local/lib/systemd/network` 부재는 선택 경로의 부재이며
  실제 설치 부모 `/etc/systemd/network` 부재와 구분한다.
- 기존 `/var/lib/hbr-ssh-control`과 인터페이스 `hbrmgmt0` 없음.
- 조회된 regular 파일 134개, 읽기 생략0. .link 2개는 `98-default-mac-none.link`,
  `99-default.link`; 열거된 범위에서 10-hbr-mgmt.link 이전 파일·동명 파일/drop-in이 보고되지 않았다.
- 네트워크 이름 처리 힌트는 `60-net.rules`, `65-persistent-net-nbft.rules`,
  `71-prefixdevname.rules`, `80-net-setup-link.rules` 4개다. 고정 힌트/원문SHA만 반출했으므로
  규칙 전체 검토나 실제 우선순위 충돌 부재를 주장하지 않는다. 빈 drop-in 디렉터리와
  열거하지 않은 경로까지 완전 부재를 증명하지 않으며, 실제 installer가 다시 확인한다.
- Ed25519 공개 호스트키를 수신하고 **수신 공개키 바이트로 지문을 다시 계산**했다.
  `SHA256:wcqHnqpzbcZfyZ3PhLWYFOuKDURNqQRvU75Nu5ICuvk`로 이전 조회와 일치한다.
  이는 공개 호스트키이며 개인키/신규 사용자 인증키가 아니다.

**ISSUES=0은 이번 선행조건 조회 범위 결과다.** 새 .link 실제 파서·hotplug 이름 결속,
unmanaged/down, SSH 인증·패킷 차단·만료·rollback은 미실행이다. 설치 GO나 AC 인수가 아니다.
기존 NM/SSH/nft 파서 증적과도 실행 회차를 구분한다.

## 출처·검수와 보안

- 원본 receipt manifest 2항목 SHA256:
  `08efcfb7bd6df4dc5542bacd335d13cba25b3e9232a7dffb185ed4de63463e8d`.
- collector SHA256 `851c181607c00521dc1ba62d942754753151ff35409b2fecc81a185ea239dcef`.
- 전달 manifest `435e36c284c9e6266a0b09017e06fe2e14f20d983aadfcee878bbb3815072659`.
- source/는 실제 전달본의 collector/stage/manifest/만료값을 원래 바이트로 보존한다.
  이력 사본이며 재실행·설치 입력으로 쓰지 않는다. helper는 순수 검증기 Lead 자체 검수,
  **REVIEW=NOT PERFORMED (Pre-check)**이며 code#22 독립 승인이 아니다.
- analysis/verification.json은 회수 뒤 호스트에서 수행한 오프라인 검수다. 원문 134개는
  guest private에 유지되고, 여기에는 경로·권한·SHA·선별 설정 및 고정 힌트만 있다.
- 전달 중 HGFS 열기/닫기와 local 작업·결과 파일 생성은 수행했지만, guest /etc 설정,
  계정, 서비스, 방화벽, NIC, Docker 변경이나 udev test/trigger/reload는 수행하지 않았다.
- 로컬 전용 known_hosts를 이 공개키로 준비했다. 아직 연결하지 않았고 해당 로컬 파일이나
  관리 개인키는 이 증적에 포함하지 않는다.

01:42:53 KST 호스트 HBR_SSH_NAMING 제거/HGFS 비활성 각각 rc0, DEACTIVATED,
clone NIC FALSE/공유0 확인. guest `/mnt/hbr-ssh-naming` 마지막 umount는 콘솔 후속사항이며
수행 로그를 받지 않았으므로 미확인이다.

[실행 인계](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6064586308).
A3 STOP/claim, AC·Issue·Phase1 Close는 유지한다. 다음은 오전 소스/증적 리뷰이며,
05:14 KST 만료의 기존 설치 후보는 오전에 재생성·봉인해야 한다.
