# Harbor A2R1 후보 읽기 전용 실제 확인

CODEX_ASSISTED. baseline #13, infra-harbor-trivy #17, evidence #166 후속.
2026-10-08 **18:17:27~18:17:29 KST**, NIC 없는 작업 복제본 harbor01의 server08 콘솔에서 sudo로 실행했다.

## 판정

`CANDIDATE_METADATA_VERIFIED / rc0`이다. 조회29개 모두 rc0, 회수 manifest30항목의 SHA가 일치한다.
현재10개 컨테이너가 모두 running/healthy이며 evidence#166의 봉인 after와 선택 inspect 전체가 같다.
처음/마지막 state stdout도 이 current와 동일하다. 이미지ID10개, 기존 volume9개의 이름/경로/driver/options,
IPv4 127.0.0.1:1514 listener, 승인 profile의 버전·보안 조건을 fresh 확인했다.

Docker29.8.0/GitCommit3ce5872, Compose5.5.1, DockerRootDir/overlayfs/SecurityOptions(seccomp/cgroupns),
호스트 Enforcing이 일치한다. Mode 차이7개를 가진 portal/proxy/registryctl **3개**의
MountLabel/ProcessLabel은 빈 값, SecurityOpt null, Privileged false다. 전체10개 label 조회로 확대하지 않는다.
9개 volume 디렉터리 xattr는 모두 `system_u:object_r:container_file_t:s0`다.
이제 `os.getxattr`와 profile의 실제 Docker 출력 처리까지 읽기 전용 Runtime으로 확인했지만,
최초 A2R1 이전 xattr 보존은 여전히 직접 증명되지 않는다.

## 버전 및 원본 보존

승인 HEAD `1a24d45c7ee6b9418e0b60f059fe13dc78670969`, 병합 `a77990c5c7d52114a4b9f361125248c79f129a42`.
실제 trial SHA256 `0a79b3b70d18211fcacb94903332b81e71168ade18225909ed4d53e26be3d8c4`.
READ_ONLY check-current만 호출했으며 original apply-result는 변경하지 않았다.
기존16:20 회차의 **STOP_RECOVERY_REQUIRED/PRESERVATION_MOUNTS는 그대로**다.
profile는 고정 원본 SHA `b8e8c1966424f43f3a5daa36276a579f595f09f094b09c4d537252af5e74c988`와 현재 after를 검사했다.

게스트 원본 결과 `/root/hbr-a2r1-check-5eke20_f`, 승인 소스 복사본 `/root/hbr-profile-approved-lub3id7i`.
명령·rc·시각·원본 JSON/선별 stdout은 runtime-receipt에 포함한다. Compose base/effective 원문 및 raw stderr는
게스트 private 폴더에 유지하고 stderr는 바이트 수/해시만 회수했다. 인계 래퍼는 자체 검수 코드이며 독립 리뷰를 주장하지 않는다.

## 전달 오류와 복구

최초 공유폴더 직접 실행은 `import hashlib`의 importlib 디렉터리 열거 중 EIO로 실패했다.
STARTED 생성 전이므로 검사 본체는 미실행이었다. 이 실패를 후보 검사 STOP으로 기록하지 않는다.
호스트 HGFS를 재등록하고 별도 `/mnt/hbr-check` 마운트에서 정확한 파일을 root 로컬 경로로 복사·해시 확인한 뒤
Python -I로 실행했다. forward-slash hostPath가 EIO의 원인이었는지는 확정하지 않는다.
실패/성공 콘솔, 기존 인계/보완 기록, 실제 사용 래퍼·stage 및 승인 소스 바이트를 함께 보존한다.

18:18:29 KST host HBR_CHECK 제거·HGFS disable 명령 rc0 및 VMX 로그 DEACTIVATED 확인.
선별 VMX는 NIC FALSE/HGFS disable TRUE/sharedFolder.maxNum0이다. 게스트 mount 해제는 아직 확인하지 않았다.

## 범위와 다음 단계

이번 회차는 후보 메타데이터 조건 확인 성공이다. apply/restore/Docker restart/VM reboot/보안 변경은 수행하지 않았다.
AUTOSTART, SYSLOG_INGESTION, 업무 데이터 무결성, 운영 적용, AC/Issue/Phase1 Close는 미시험/미인수로 유지한다.
현재 IPv4 후보를 유지하고 **A3 실행기(observer/T0/rc/boot ID/journal/상한/증적 회수·스냅샷 복구)**를 별도 독립 리뷰한다.
이번 증적 편입 승인이나 check-current 성공만으로 Docker restart GO를 선언하지 않는다.
