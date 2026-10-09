# 격리 Harbor SSH 설치·부팅 영향 조회 — 2026-10-09

CODEX_ASSISTED. baseline#13, 실행자 GWONUK(server08 VM 콘솔 sudo), 수신·검수 GWONUK/Codex.
증적 편입 독립 리뷰 대기. A3 STOP 및 AC/Issue/Phase1 Close 판정 유지.

## 판정과 시간

대상은 harbor01-isolated-firstboot-20261008, guest UUID
`389e4d56-24f0-e2ef-b68f-137a5047788a`이며 운영 Harbor가 아니다.

- 11:11:10 KST 전달 receipt: `/root/hbr-ssh-bundle-20261009-110630` STAGED_ONLY.
- 설치 시작 11:36:52 KST(회수 SUMMARY의 started_epoch), 콘솔 정상 출력
  `INSTALLED_LINK_DISABLED`. 이후 읽기 전용 조회도 같은 상태를 보고한다.
- 11:59:23.462~11:59:24.517 KST 부팅 영향 조회, 33명령 rc0/stderr0, ISSUES=0.
  명령: `sudo bash /mnt/hbr-ssh-bootcheck/stage-local.sh`.
- 12:00:36 KST host 공유 제거/HGFS 비활성 각 rc0, NIC FALSE/공유0 확인.
  guest 마지막 umount는 미확인이다.

설치 소스는 [code#22](https://github.com/321Team/infra-harbor-trivy/pull/22)
독립 승인 HEAD `74e4f1761f0b0e351d545e3d56bc71ff0ec83c85`, merge
`23e3cdc965e31b18445cf05a338f6d0c20d5f37a`다. 설치 시 사용 소스3개의
SUMMARY 해시를 호스트의 승인·병합 소스와 대조했다. 설치 기록의 명령16개 rc0,
설치 파일12개 해시 일치가 보고됐다. 원 state/파일은 guest private에 있으며
호스트에서 12개 원문 전체를 다시 읽었다고 주장하지 않는다.

## 결과와 실제 차단사항

| 항목 | 확인 결과 / 의미 |
|---|---|
| 설치 | INSTALLED_LINK_DISABLED; SSH session.claim 없음, 실제 인증/접속 NOT_RUN |
| 환경 | A3와 같은 boot, SELinux Enforcing, 물리 NIC 없음, 기존 두 NM profile autoconnect=no |
| A3 보존 | 원 result 해시 일치. 같은 고정10개 ID에서 logger1 running/healthy, 앱9 exited/unhealthy 유지 |
| 부팅 영향 | Docker enabled, 10개 컨테이너 restart=always. Docker Requires에 docker.socket 및 fds-harbor-ac04-guard 포함 |
| SSH 보호 | nft 전용 테이블 조회 rc0, expiry timer active/static, session inactive/static. nftables inactive/disabled |
| VMware UI | Connected 및 MAC 입력란이 비활성. 지정 MAC을 적용 전 고정하는 무재부팅 추가 경로가 현재 화면에서 막힘 |

재부팅 시 Docker 기동·컨테이너 복원 시도가 발생할 수 있다. 기존 컨테이너 성공/실패
상태가 유지된다고 가정하지 않는다. 코드 install은 현재 커널에 nft 테이블을 적용하고
expiry timer를 start하며 부팅 자동 구성을 하지 않는다. `static`만으로 모든 자동시작이
불가능하다고 일반화하지 않지만, 현재 전달 코드에 재부팅 후 보호 복구 경로가 없다.
즉시 재부팅/NIC/SSH GO는 아니다. `fds-harbor-ac04-guard`의 원문 및 신규 부팅의
실제 동작은 이 수집에서 검토하지 않았다. 실행 중 VMX 수정이나 guard 완화도 하지 않았다.

## 출처와 무결성

- receipt/의 수신 manifest2개 항목 SHA256:
  `4bebc3e789d2f51e88249860f377cb5bf2fe5ec1d47b2c9a26e3d6b0ab565be7`.
- collector SHA256 `da11603dfe06d7424d5c59687138b4fbd05973981133468bca841f0df9828705`.
- source/는 실제 전달 helper/만료값/manifest의 원래 바이트다. 보존용이며 재실행 입력이 아니다.
  순수 검증기 Lead 자체 검수, **REVIEW=NOT PERFORMED (Pre-check)**다.
  code#22 독립 승인이 이 수집기를 승인한 것은 아니다.
- private `/root/hbr-ssh-bootcheck-k_awxzgk`에 설치 state/소유파일/A3 result/claim 및
  명령 stdout/stderr 원문을 보존했다. PRIVATE_SHA256SUMS 82항목은 경로가 이 private
  디렉터리 기준이다. 원문82개를 반출한 것이 아니다. 호스트에서는 SUMMARY가 보고한
  파일15개/명령66개 해시와 SUMMARY 자체 해시의 일관성을 대조했다.
- 설치 번들 manifest 및 receipt는 이전 전달 기록이다. 전체 번들/실제 관리키는
  편입하지 않아 이 폴더만으로 그 번들 manifest를 재검산할 수 있다고 주장하지 않는다.
- screens/5장은 전달/설치/UI차단/수집 사용자 화면이며 비밀번호·개인키는 없다.
  raw unit 내용, private state 및 컨테이너 State 원문(health log 포함)은 반출하지 않았다.
  원본 CRLF 등 바이트를 유지했고 기존 증적은 수정하지 않았다.

## 남은 작업

1. guest umount 및 증적 편입 독립 리뷰.
2. 원 A3와 분리한 전원 전환 계획: 종료 전 보존 완료, 부팅 시 Docker/기존 guard 영향,
   고정MAC NIC의 케이블 미연결 유지, 재부팅 후 SSH nft/만료 보호 복구 및 검증,
   변경 상태·rollback/만료 처리 경로를 먼저 정한다.
3. 새 코드/실행 설정은 별도 PR 리뷰 뒤 적용한다. 기존 state/claim 삭제·만료 수동 연장 금지.

만료: 기존 SSH 설정 15:06:30 KST, 이 조회 전달본 15:52:46 KST. 서로 별개이며
조회가 SSH 유효기간을 연장하지 않는다. 만료는 연결 차단이지 계정/파일 완전 철거가 아니다.
전원 종료/재부팅/새 부팅 시험은 NOT_RUN. 이전 A3 실패를 소급 PASS 처리하지 않는다.

관련: [수집 인계](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6073289808),
[설치 범위](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6072849630),
[UI 차단 정정](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6073244782),
[원 A3 증적 #171](https://github.com/321Team/fds-project-evidence/pull/171),
[선행 사전조회 #179](https://github.com/321Team/fds-project-evidence/pull/179).
