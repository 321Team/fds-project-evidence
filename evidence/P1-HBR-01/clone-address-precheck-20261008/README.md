# Harbor 격리 복제본 주소 후보 A1 읽기 전용 검사

CODEX_ASSISTED. 2026-10-08 14:21:56 KST, NIC 없는 작업 복제본 harbor01에서 사용자가 기존 server08 콘솔의 sudo로 실행했다. 소스 기준은 infra-harbor-trivy merge 58b9e21bf3af2cfe85fae6fd560dddc6d6e943d7의 승인된 checker/override/observer이며, precheck.py는 이들을 연결한 읽기 전용 일회 수집 래퍼(별도 독립 코드 리뷰 미수행)다. 정확한 파일 SHA는 SOURCE.json과 결과에 결속했다.

## 결과

- CONFIG_DELTA=PASS: logging 주소 9개만 localhost→127.0.0.1로 달라짐. 나머지 정규화 구성은 동일.
- 원 Compose SHA 0a84f57692268335eeedf45411e025d784e520bf749fa3501a3800cdfcb14ef0 전후 동일.
- 10개 컨테이너 running/healthy, logger healthy 및 IPv4 listener 표본 1개. 자동기동·실제 syslog 수신·TLS/전체 AC 성공은 아니다.
- 5개 명령 rc0, 후보 적용·컨테이너 재생성·Docker restart·VM reboot 미실행.
- 비공개 Compose 렌더링/stderr는 게스트 /root/hbr-clone-a1-4yaonwsj에만 보존. 이 PR에는 제한 필드 결과와 소스·콘솔 수신 자료만 편입한다.

## 회수 편차와 한계

사용자는 처음 /mnt/hbr-out/precheck.py를 입력해 파일 없음으로 중단했고, /mnt/hgfs/HBR_NEXT/precheck.py로 실행해 A1_COLLECTED_REVIEW_REQUIRED를 확인했다. 오류 명령이 실제 A1 실행이었다고 세지 않는다.

호스트 자동 회수기의 Get-FileHash 명령을 찾지 못해 ERROR가 났다. 결과 JSON/sidecar는 전용 호스트 폴더에 정상 전달돼 있었고, 후속 Python으로 해시 및 전송 소스 결속을 검증해 바이트 그대로 회수했다. 자동 회수 실패 원본을 보존하고 정상 자동 회수로 고쳐 쓰지 않았다. remove/disable rc0과 fresh VMX의 공유0/HGFS disable/NIC false를 확인했다. 수신 화면은 명시 마운트 umount 명령이 오류 없이 돌아온 것까지 보이며 게스트 자동 HGFS 마운트 표를 재조회한 것은 아니다.

후속 주소 후보 소비/원복 도구: https://github.com/321Team/infra-harbor-trivy/pull/15 . 해당 새 실행 코드는 이 회차에서 실행하지 않았다. 본 증적 편입은 독립 리뷰 대상이며 자동기동 결함 해결·운영 적용·AC 인수가 아니다.
