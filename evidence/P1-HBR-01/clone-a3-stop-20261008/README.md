# Harbor A3 Docker restart 1회 — 앱 자동기동 실패 및 원인 보충

CODEX_ASSISTED. baseline #13 / infra-harbor-trivy #18 / evidence #168 후속.

## 판정

**격리 복제본에서 Docker service restart는 성공했으나, 관측창 내 앱9개 자동기동은 미달했다.**
원본 `STOP_RECOVERY_REQUIRED`를 유지한다. 별도 journal 수집 오류를 후속 읽기 전용 조회로 보충했으며,
원본 실패를 소급 PASS로 변경하지 않는다. AC/Issue/Phase1 Close 인수나 운영 적용 승인이 아니다.

## 실행과 출처

- 대상: `D:\FDS-Isolated-Lab\harbor01-20261008\harbor01-test.vmx`, hostname harbor01,
  BIOS UUID `564d9e38-f024-efe2-b68f-137a5047788a` 작업 복제본. NIC FALSE.
- 사용자 GWONUK의 server08 VM 콘솔 sudo 실행. [실행 인계](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6057931734).
- code 승인 HEAD `b0a1c9ca630ed9c1e76303ebd7a23872816a9c1c`, merge `5c6266228fa160446aae06595ebed33cdc3bfe67`.
  driver SHA `b006ea6740435a4ce77a871dad20db2ac86d73f02ba90c3feccc79a668439321`.
- 실행 번들 `/root/hbr-a3-bundle-20261008-192635`, 실제 원본 `/root/hbr-a3-joz3x6ya`.
  원본 result SHA `5df896fd9f501cbac82e1091c6368160d79dbca34baf651681f766f331102fa7`.
- 2026-10-08 19:36:12.246~19:39:18.961 KST. T0 19:36:13.566.
  `systemctl restart docker.service` 정확히1건,19:36:13.567~19:36:24.975/rc0.
  같은boot ID, 새 Docker InvocationID 및 T0 이후 unit 시작 확인.
- 19:30:59 host 공유 해제 후 실행. driver의 HGFS guard 통과 사실은 실행 경로로 확인한다.
  guest umount 명령 자체의 별도 로그는 없다. 이후 회수용 공유는 실행 종료 뒤에만 다시 열었다.

## 관측 결과

재시작 전 표본0은10개 running/healthy. 표본1은 Docker4초 timeout1건. 표본2(19:36:27)부터
표본36(19:39:18)까지 logger만 running이고9개앱은 exited였다. logger healthy는 표본8(19:36:57)부터
관측했다. IPv4 listener는 정상 조회 표본에서 확인되나 폴링 사이의 준비 시점을 증명하지 않는다.
37표본 및 완결footer, observer rc2/COMPLETE_WITH_ERRORS를 그대로 보존한다.

postcheck29항목 모두 COLLECTED. 건강 판정 `POST_NOT_ALL_HEALTHY`로 FAIL.
해당 함수가 건강 검사에서 중단하므로 나머지 메타데이터는 analysis의 별도 오프라인 비교로 검증했다:
전후10개 ID/image/restart/ports/logging/mount·service identity 차이0. volume9개 inventory/xattr,
Engine/Compose/security/Enforcing/영향3개 labels 조건도 PASS. 데이터 내용 무손상까지 증명하지 않는다.

## 확인된 직접 실패 원인과 한계

후속20:13:24 KST 읽기 전용 수집에서 원래boot와 시간창(19:36:13~19:39:19)의 Docker journal62행을
rc0/파싱오류0으로 확보했다. `diagnostic-receipt/SUMMARY.json`은 원문 전체가 아닌
시간·원문SHA·고정 오류문구·컨테이너ID 결속을 추출한 자료다.

19:36:24.838652~19:36:24.842788 KST 이벤트9건이 각각9개앱ID와 결속되고,
`failed to start container`, `failed to initialize logging driver`, `dial tcp`,
`127.0.0.1:1514`, `connection refused`를 모두 포함한다.
후속 동일ID State.Error도9개가 동일한126bytes/SHA
`af8467c764dce9ff2e620a0ea090e216b10d67949b0112cbf5c059a63ed9a9d3` 및 같은 오류문구를 포함한다.
logger는 running/Error빈값이다. 후속 State.Error는 20:13 자료이며 이를19:39 즉시 조회로 표시하지 않는다.

따라서 **이번9개 기동 실패의 직접 원인은 IPv4 syslog 접속 거부에 따른 로깅 드라이버 초기화 실패**다.
logger 준비 전 앱 복원을 시도하는 기동순서 경합과 부합한다. 정확한 readiness 전환의 순간이나
모든 환경에서의 재현 확률을 이1회 관측으로 단정하지 않는다. IPv4 후보만으로 자동기동이 해결된다는
가설은 이번 결과에서 충족되지 않았다. 부팅 순서/준비조건 대책은 다음 설계·코드 리뷰 대상으로 남긴다.

## journal 수집기 오류 — Runtime 실패와 별개

원 driver의 `journalctl -b <하이픈 포함 boot UUID>`는 rc1/stdout0bytes/stderr77bytes였다.
원stderr 고정 문구는 `failed to add match`와 `invalid argument`다. 즉 boot UUID가 정상 필터로
처리되지 않고 match 처리 오류를 일으켰다. 후속에서는 같은boot를
`_BOOT_ID=ec7a9c3c3a914d4a8d42f68ce23ce92b`로 명시해 같은시간창을 정상 조회했다.
이는 조회 방식 보정으로 확보한 후속 증적이며, 최초 journal 명령 성공으로 바꾸지 않는다.
실제 원stderr 전문과 journal-version 원문은 guest private에 있어 여기서 정확한 systemd 버전을 추정하지 않는다.

## 편입 내용·무결성·보안

- runtime-receipt: 최초 회수31개 파일 및 기존manifest. observer 표본/result/선별stdout/claim/승인모듈.
- diagnostic-receipt: 보충 요약1개 및 기존manifest. 원본journal SHA
  `8feb2f394d65f9ef83ce96ca1165422c097ba59b89600586788aa110c14e250a`(74606bytes),
  현재State.Error 원본 SHA `470b0f454ef65728ef2480f70f3501003a83556cbc8d386d4e808a38279d6479`.
- source: 승인 driver 바이트, 실제사용 회수기/보충수집기/전달스크립트 사본. 전달·회수 코드는 자체검수이며
  독립 리뷰된 Runtime driver와 구분한다. 이 저장소의 사본은 보존용이며 재실행 인계가 아니다.
- host: 소스/전달해시/수신기록/공유폐쇄기록. screenshots: 전달·STOP·회수·보충완료 화면.
- analysis: 원본과 분리한 검증스크립트/분석JSON/보충검증JSON. root manifest는 dotfile 포함, 자기파일 제외.
- 원문journal·rawstderr·현재State.Error전문·Compose원문은 guest private에 유지. 보충private는
  `/root/hbr-a3-diagnostic-cm16q39r`. 해시만으로 해당 private 원문 전체를 직접 리뷰했다고 주장하지 않는다.

20:02:20 첫회수공유 폐쇄,20:14:01 보충공유 폐쇄(rc0/DEACTIVATED), 최종NIC FALSE/공유0 확인.
guest의 마지막 `/mnt/hbr-a3-diag` mount 해제는 사용자 콘솔 후속사항이며 미확인.
앞선 `bash` 누락 직접실행 오류는 보충수집기 호출 전이며 Runtime 재시도가 아니다.

## 잔여 작업

1. 증적 편입 독립 리뷰. 실제 회차 STOP/AUTOSTART 미달 유지.
2. journal 인자 처리 수정과 실제 읽기 전용 재검증. restart claim은 삭제하지 않는다.
3. 기동 준비조건 대책 설계·리뷰. 현재 unhealthy 후보에는 기존 #17 healthy profile restore를 적용하지 않는다.
4. 회차 원본 보존 후 별도 복구 판단. 고정스냅샷 존재만 확인했고 복원은 미시험/미실행.
5. 전용SSH는 검토 중이며 NIC추가/계정·키·보안변경 미실행. 기존 무NIC 승인조건을 임의해제하지 않는다.

`RUNTIME=A3_STOP / DIRECT_FAILURE=SYSLOG_IPV4_CONNECTION_REFUSED / JOURNAL=SUPPLEMENT_COLLECTED /
RETRY·RESTORE=NOT_RUN / SYSLOG_INGESTION=NOT_TESTED / AC·Close=UNCHANGED`.
