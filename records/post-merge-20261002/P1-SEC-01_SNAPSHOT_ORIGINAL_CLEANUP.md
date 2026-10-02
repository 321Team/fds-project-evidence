# P1-SEC-01 etcd snapshot 임시 원본 정리 기록 — 2026-10-02

대상: [#99](https://github.com/321Team/fds-project-evidence/pull/99)(merge `971249b`)로 편입한 `evidence/P1-SEC-01/received-20261002T0625Z/`의 Secretbox backup 수집. #99 독립 리뷰(supreme33-kr, 비차단 메모 1)와 GWONUK 재리뷰가 남긴 "`/var/lib/etcd/snapshot-sec01.db` 원본 정리는 Lead 결정대로 별도 post-merge evidence로 처리" 후속이다. 병합된 수집회차 폴더에는 파일을 추가하지 않으므로(EVIDENCE_POLICY) 새 경로에 둔다.

## 배경

`sec01-secretbox-backup.sh`는 etcd 컨테이너 안에서 `etcdctl snapshot save /var/lib/etcd/snapshot-sec01.db`로 저장한 뒤 호스트의 `/root/p1-sec01-secretbox-backup-20261002T054208Z/etcd-snapshot-sec01.db`로 **복사만** 하고 원본을 지우지 않았다. 따라서 etcd 데이터 디렉터리(`/var/lib/etcd`)에 전체 snapshot(9.0 MB, 암호문 상태의 Secret 포함) 사본이 남아 있었다. Lead(이하영)가 해시 일치를 확인한 뒤 이 임시 원본을 삭제하기로 결정했다(#99 코멘트의 "B 처리").

## 실행 기록 (콘솔 제출 자료)

| 항목 | 값 |
|---|---|
| 실행 시각 | 2026-10-02T07:18:27Z (16:18:27 KST) |
| 서버·계정 | k8s-control01 · `server02`(sudo) |
| 실행자 | 이하영(P1-SEC-01 Lead)이 콘솔에서 직접 실행. 명령 작성·기록 정리: Claude Code 보조 |
| 방식 | 해시가 같을 때만 삭제하는 조건부 명령 |

실행한 명령:

```bash
sudo bash -c 'D=/root/p1-sec01-secretbox-backup-20261002T054208Z; O=$D/30-snapshot-orig-cleanup.txt; A=$(sha256sum /var/lib/etcd/snapshot-sec01.db | cut -d" " -f1); B=$(sha256sum $D/etcd-snapshot-sec01.db | cut -d" " -f1); { date -u +%FT%TZ; echo "orig=$A"; echo "copy=$B"; } | tee $O; if [ "$A" = "$B" ]; then rm -v /var/lib/etcd/snapshot-sec01.db | tee -a $O; ls -l /var/lib/etcd | tee -a $O; else echo MISMATCH_NOT_DELETED | tee -a $O; fi'
```

콘솔 출력(사용자가 붙여 넣은 것을 그대로 옮김):

```
2026-10-02T07:18:27Z
orig=8ace820ca29488fc5ef8eb46d424a58ef6e0dbbba03f6d0f851f929e6e771e2f
copy=8ace820ca29488fc5ef8eb46d424a58ef6e0dbbba03f6d0f851f929e6e771e2f
'/var/lib/etcd/snapshot-sec01.db'을(를) 제거했습니다
합계 0
drwx------. 4 root root 29 10월  1일  11:24 member
```

## 결과

- `/var/lib/etcd/snapshot-sec01.db`(원본)와 `/root/…/etcd-snapshot-sec01.db`(사본)의 SHA-256이 **일치**했다: `8ace820ca29488fc5ef8eb46d424a58ef6e0dbbba03f6d0f851f929e6e771e2f`.
- 이 값은 #99로 편입한 backup 수집의 snapshot 해시(`8ace820c…771e2f`, 같은 수집회차 README와 `22-snapshot-SHA256SUMS`)와 같다.
- 일치 확인 뒤 `/var/lib/etcd/snapshot-sec01.db`가 제거됐고, 삭제 후 `/var/lib/etcd`에는 `member` 디렉터리만 남았다.

## 범위와 한계

1. **콘솔 제출 자료다.** 위 출력은 사용자가 세션에 붙여 넣은 것을 옮긴 것이다. 같은 명령이 서버에 만든 `/root/p1-sec01-secretbox-backup-20261002T054208Z/30-snapshot-orig-cleanup.txt`는 수신하지 않았으며, 서버 파일 해시 검증을 주장하지 않는다.
2. **삭제 전 목록은 남기지 않았다.** `/var/lib/etcd`에 삭제 전 snapshot 외 다른 임시 파일이 있었는지는 기록으로 확인할 수 없다. 삭제 후 목록이 `member`뿐임만 확인했다.
3. **정리 대상은 `/var/lib/etcd`의 임시 원본 한 개뿐이다.** `/root/p1-sec01-secretbox-backup-20261002T054208Z/`의 snapshot 사본과 `.bak` 2개는 backup 본체로 그대로 남아 있다(root-only). 이 backup은 **같은 호스트(k8s-control01)에만** 있어 호스트 밖 보관본이 없다. 보관 위치·기간·폐기 기준은 정해지지 않았다.
4. **복원 가능성은 시험하지 않았다.** 이 기록은 rollback 증적이 아니다. #99에서 `ROLLBACK=NOT_MET`으로 남긴 상태는 바뀌지 않는다.
5. 다른 CP(control02/03)에는 같은 backup 수집을 하지 않았으므로 이 정리 대상도 없다.

## 하지 않는 것

P1-SEC-01의 AC 체크, Gate, Status는 바꾸지 않는다. AC-05 backup 판정과 rollback·rotation 상태는 #19에서 Review Owner·Lead가 별도로 판단한다.
