# 과거 Runner packet 28개 정리 범위 — 실행 전

대상은 ansible01의 `server01_ansible` HOME에 있는 **`LEGACY_FRESH_METADATA.json`에 열거한28개 경로만**이다. 2026-10-13 12:00:07 KST 기존 인증 경로로 lstat만 수행했고, 11:29 원본의 경로·uid1000·mode0600·mtime/ctime와 일치했다. 모두 regular·link1, 마지막 변경은9/16~10/5 UTC다. 내용·token값·token해시·실제 유효성은 조회하지 않았다.

## 전제와 순서

1. 이재환/이권욱이 해당28개를 더 사용하지 않는다고 확인하고 정리하는 동안 ansible01의 Runner token 발급·전달·파일변경을 배제한다. 현재CI81 회차 정리 허용은 과거28개 삭제 허용과 구분한다.
2. 실행 직전 고정 `ansible-regression.yml`의 활성 Job 및 등록 Runner, 기존 Runner 프로세스·컨테이너가 없는지 기존 읽기 경로로 재확인한다. 등록Runner0만으로 token 만료를 증명했다고 기록하지 않는다.
3. 기존 `fds-ansible01` SSH alias / host-key 검사 / 일반 계정 UID1000으로 실행한다. sudo·새 인증·파일 배치 없이 `python3 -I -B -c <검토된 legacy_cleanup.py>`에 메타데이터 JSON을 stdin으로 전달한다. 기본 실행은 읽기 전용이다.
4. dry-run에서 host/boot/uid, 정확한28개 경로, device/inode/size/mtime_ns/ctime_ns/link/owner/mode 전체가 맞아야 `ALL_TARGETS_MATCH`다. 한 개라도 다르면 삭제0건으로 중단한다.
5. 사용자 범위 확인 후 같은 명령에 `--execute`만 더한다. 전체 대조 후에도 각 unlink 직전에 다시 대조한다. HOME 디렉터리 fd를 고정하고 심볼릭 링크를 따라가지 않는다. glob 삭제·재귀 삭제·다른 경로 삭제는 없다.
6. 경로별 `DELETED` 시각과 마지막 `ALL_TARGETS_ABSENT`를 보존하고 독립 사후 lstat로 정확한28개 부재를 확인한다. 새로 생긴 다른 packet은 건드리지 않는다.

## 중단·복구·한계

- 동시 사용 배제를 확인하지 못하면 실행하지 않는다. 메타데이터 검사와 unlink 사이의 원자적 동일객체 삭제 보장은 없으므로 동시 파일변경 배제가 필수다.
- 최초 전체 대조 실패는0건 삭제. 도중 변화·권한·SSH 오류면 다음 삭제를 중단하고 받은 경로별 영수증 및 다시 읽은 부재/잔존 목록으로 부분 상태를 확인한다. 전체 재실행으로 덮지 않는다.
- 삭제는 복구 불가다. 비밀 내용을 새 백업으로 복제하지 않는다. 후속업무는 기존 정상 절차에서 새 단기 token을 발급하며 이번에는 발급하지 않는다.
- 토큰 파일의 삭제와 credential의 서버측 만료·폐기를 구분한다. 이 실행은 파일 위생 정리이며28개 개별 credential 만료 판정이 아니다.
- CI81의 이미 삭제된 관리자 packet 정확한 경로는 사후 복원하지 않는다. 향후 업무상 공급 helper에는 삭제 전 경로와 삭제 후 부재 기록을 추가하는 별도 비차단 보완으로 남긴다. 이번 CI를 재실행하지 않는다.

실제 삭제 상태는 아직 `NOT_PERFORMED`다. 허용 뒤에는 새 증적을 사용하고 병합된 증적209는 수정하지 않는다.
