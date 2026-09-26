# P1-K8S-01 NTP 원본 3건 출처 해시 교차 대조 — 2026-09-25

대상: [#36](https://github.com/321Team/fds-project-evidence/pull/36)(merge `4d2db33`)로 편입한 CR-P1-NTP-01-01 원본 7개 중, 편입 때 업로드 sidecar와만 대조한 3건. #36 독립 리뷰(이하영 5313410457)의 비차단 요청 2번에 대한 후속이다. 병합된 수집회차 폴더는 수정하지 않고 이 기록을 새 경로에 둔다.

## 대조 방법

- 원본 위치: ansible01 `server01_ansible` 홈 디렉터리(원본이 생성된 위치)
- 명령: `sha256sum ntp-onepass-nyol0g41.tar.gz ntp-network-recovery-w5e5yw5h.tar.gz ntp-onepass-j0juc9np.tar.gz`
- 실행: 이권욱, 2026-09-25. 출력은 Claude Code 세션에서 Git 편입값과 대조했다.

## 결과 — 3/3 일치

| 원본 | ansible01 `sha256sum` | Git 편입본(sidecar·폴더 SHA256SUMS) | 폴더 |
|---|---|---|---|
| `ntp-onepass-nyol0g41.tar.gz` (실제 적용 run f9392ba9) | `e5739fabc66670b846a59290b864eceac21097d4c89d5dbc37700ce007bd7d23` | 일치 | `evidence/P1-K8S-01/cr-p1-ntp-01-01-onepass-apply-20260921T015212Z/` |
| `ntp-network-recovery-w5e5yw5h.tar.gz` | `39de5839e0a2c9249ca984a4a3fbf6553b43767f05c7c4cfc3584b254fa49930` | 일치 | `evidence/P1-K8S-01/cr-p1-ntp-01-01-network-recovery-20260920T112237Z/` |
| `ntp-onepass-j0juc9np.tar.gz` (run d029102a) | `940944fb1a463ff79167e3914435acdedbd8af7a4b9f298ec9e464af56990e23` | 일치 | `evidence/P1-K8S-01/cr-p1-ntp-01-01-onepass-20260920T140154Z/` |

나머지 4건(readonly, onepass-1vu26i8b, chronyd-environment, post-egress)은 편입 때 infra-ansible 문서 기록값과 이미 대조했다. 이로써 7건 모두 업로드 sidecar와 다른 출처의 값으로 확인됐다.

## 범위

원본 파일이 생성된 서버의 현재 바이트가 Git 편입본과 같다는 확인이다. 대조 명령은 실행자(이권욱)가 직접 수행했고 독립 재실행은 아니다. NTP 적용 결과 인수, P1-K8S-01 AC·Status는 바꾸지 않는다.
