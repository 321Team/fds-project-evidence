# OID-02 — 시스템 이미지 노드별 보유 현황 수집 원본 편입 (2026-10-05 수집, 2026-10-06 편입)

Record ID: **P1-HBR-01** (OID-02 결정 입력, [baseline #14](https://github.com/321Team/fds-project-baseline/issues/14) / [#13](https://github.com/321Team/fds-project-baseline/issues/13)). 수집·실행: 이하영(HBR Lead·OID-02 Owner), ansible01 `server01_ansible`. 정리: Claude Code(CLAUDE_ASSISTED). 이 폴더는 한 수집회차이며 병합 후 닫힌 폴더로 취급한다.

상태: 수신·자체 검수 완료 / **독립 리뷰·편입 병합 PENDING**. **이 편입은 OID-02 완료·`approved_registry`/`preloaded` 이행·재스케줄 공백 처분의 PASS가 아니다.** 권욱 님이 [#14 5994756924](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5994756924)에서 완료조건의 첫 단계로 지정한 "기존 ★원본 3파일 증적 편입"이다.

## 근거
| 항목 | 값 |
|---|---|
| 대응표·공백 보고 | [#14 5989994993](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5989994993) (이 원본을 근거로 작성) |
| 권욱 님 검토·후속 범위 | [#14 5994756924](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5994756924) |
| OID-02 결정·승인 | [Owner 결정 5977963213](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5977963213), [재검토 결정 5986546423](https://github.com/321Team/fds-project-baseline/issues/14#issuecomment-5986546423) |

## 폴더 구성 (정본은 ★)
| 경로 | 크기 | SHA-256 | 내용·성격 |
|---|---|---|---|
| ★ `server-originals/oid02-k8s-20261005T110428.txt` | 11938 | `840d488a9e111205bde8096bdf2f147b85b1a3598428592ad19db67886877b8e` | 2026-10-05 11:04:28 control01(`server02`, ssh) `kubectl`: kube-system Pod의 노드·이미지·pullPolicy·imageID, Deployment/DaemonSet 스케줄 제약, 노드 플랫폼 |
| ★ `server-originals/oid02-nodes-control3-20261005T114311.txt` | 21385 | `929271315d7f5848b381f6a56f179d779d89c8a6af7604173e1b2763539e32bf` | 11:43 control01~03 `ctr -n k8s.io images ls`(ansible `-b`, `svc_ansible`)와 sandbox(pause) 설정 |
| ★ `server-originals/oid02-nodes-workers3-20261005T114450.txt` | 9869 | `3e152f38dd48f38a54b3dbbc1e1ed3052ed1347ae1fea93bd066b241c2a9a623` | 11:44:50 worker01~03 `ctr` 이미지 목록 |
| `observations/oid02-nodes-control3-20261005T114316.txt` | 21385 | `1513c2b6ea0fb506e4cd15d4b7d56287c6c29c2a6ef54cb0b50faafa61519f60` | 같은 명령 2회째(11:43:16). 호스트 블록 순서·시각만 다르고 나머지 내용은 정본과 같음(헤더·`CHANGED` 줄 제외 정렬 비교에서 차이 없음) |
| `observations/oid02-nodes-control-20261005T113715.txt` | 9928 | `99bbdff162e15de678709105dd1975b33c05d41cc949383d2c4f12d8a6ed26cb` | 11:37 1차 시도. **`crictl`이 control 노드에 없어 이미지 목록이 비어 있음**. 반입 원본 후보 tar 검색 출력은 들어 있음 |
| `observations/oid02-nodes-control-20261005T113721.txt` | 9928 | `d7bebcce1eadc82cf0498260d879cfa493e239791c4d44d21aeee567f6cde4a3` | 11:37 같은 명령 재실행(같은 한계) |
| `observations/oid02-nodes-control2-20261005T114054.txt` | 3900 | `d730ad84c46fb94f39364965c1b053de5961687c73c023bd52d4928e70135704` | 11:40 `-m shell` 시도. 이미지 부분은 `crictl` 없음으로 비었고 tar 검색 출력은 들어 있음 |
| `observations/oid02-k8s-20261005T110342.txt` | 35 | `4c833929fbe04a107aae1b5a773b8b78bdfd02e745b0bfd399dcd5efbbb73839` | 11:03 첫 시도. 내용은 `Connection to 10.1.93.102 closed.` 한 줄뿐(수집 데이터 없음) |
| `observations/ansible01-SHA256SUMS.local-20261006.txt` | 1072 | (아래 폴더 SHA256SUMS 참조) | 2026-10-06 ansible01에서 파일을 한 폴더로 복사한 뒤 만든 해시 목록 |
| `scripts/oid02-k8s.sh` | 1032 | `072310a410a519fd2c799cd98ddb7f530280dd8b8c673640364a3abc5295e280` | `kubectl` 수집 스크립트 |
| `scripts/oid02-node.sh` | 832 | `f1577a9ca00a8ad0c7cc70907033b966573678f0f58d5ea9205ee312f619e3c9` | `crictl` 기반 노드 수집 스크립트(control에서 `crictl` 없음으로 이미지 부분 실패) |
| `scripts/oid02-node2.sh` | 456 | `4b9e9273d2ff886acf1e12ee5cc23279c0d1272775b951d81a16faa6afd2e889` | `ctr` 기반 노드 수집 스크립트(정본 수집에 사용) |

## 해시 대조
- ansible01에서 2026-10-06 16:18:43 KST 조회한 `sha256sum ~/oid02-*` 값 11개와, ansible01 → 압축 → 공유 폴더 → 본 PC로 옮긴 사본의 해시가 **11/11 일치**한다.
- 2026-10-06 ansible01에서 만든 `SHA256SUMS.local`(압축 안에 포함)도 사본과 일치한다.
- 서버 측 독립 재해시는 하지 않았다.

## 반입 원본(archive) 검색 결과
`observations/`의 `control-…T113715`, `control-…T113721`, `control2-…T114054`에 control01~03의 `/root /home /opt /var/tmp /tmp`(깊이 3) tar/tgz 목록이 들어 있다. 확인한 파일 이름 중 칼리코·쿠버네티스 시스템 이미지 archive로 보이는 것은 없었다(`ntp-recapture-calico-…`는 NTP 증적 묶음 이름, `bb-recv/blackbox-exporter-…tar`는 모니터링 이미지, 나머지는 증적 수집물). **파일 이름만 본 것이고 내용은 열어 보지 않았다.** 이 결과는 "반입 원본이 있다/없다"를 확정하지 않으며, 공급 원본·출처·승인 근거는 **미확인**으로 남는다.

## 한계 (숨기지 않음)
1. 이미지 보유는 `ctr -n k8s.io images ls` 출력 기준이며 digest 전체 대조는 #14 5989994993 작성 때 정본 3개에서 문자열 검색으로 했다. 이 폴더에는 그 검색 결과 파일이 없다.
2. 원본은 ansible 출력과 터미널 출력으로 서버 측 원본 파일이 아니다. 수집 직후 서버 쪽에서 해시를 봉인하지 않았다.
3. `crictl`이 control 노드에 없어 1차 시도들은 이미지 부분이 비었고, 정본은 `ctr`로 다시 수집한 것이다.
4. tar 후보 검색은 깊이 3·지정 5개 경로만 대상이며 이름 기준이다.
5. Pod imageID와 노드 `ctr` digest의 일치, 재스케줄 공백(kube-controllers·CoreDNS)에 대한 해석은 #14 5989994993에 있으며 이 폴더는 원본만 편입한다.
6. 이 편입은 공급 원본·재반입 절차, 이미지 import/retag, Pod 삭제·Drain, 변경창 GO를 뜻하지 않는다. OID-03은 이 편입으로 해소되지 않는다.
