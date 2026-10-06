# P1-K8S-01 `t19-cp02-run01` 정정 기록, 2026-10-06

기존 원본은 변경하지 않는다. 대상은 `evidence/P1-K8S-01/t19-cp02-run01-20261006/`([fds-project-evidence#121](https://github.com/321Team/fds-project-evidence/pull/121), merge `3b4821f235bd9a29dbd526df704155393d2fdb07`)이다. 이 폴더의 README·`SHA256SUMS`·압축 원본은 #121 병합 때와 같은 바이트를 유지한다. 책임 티켓은 [fds-project-baseline#10](https://github.com/321Team/fds-project-baseline/issues/10)이다.

**이 문서는 PASS·AC 충족을 주장하지 않는다.** 첫 OFF Negative는 FAIL이고 T19/AC4·#10 Close는 HOLD다. 이 정정은 Runtime PASS나 AC 판정을 바꾸지 않는다.

근거: PMO/QA 직접 검토 [#10 6011434442](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-6011434442), 독립 리뷰 [#121 review](https://github.com/321Team/fds-project-evidence/pull/121#pullrequestreview-5425026968). 대상 archive SHA-256: ansible01 묶음 `f683177c42063ac2fa03b1c85f8fecdbcd41723a002bb43afcc0311fcc11e6eb`(PC 복사본 기준), server-originals `16d4f54b3a30ca3e447c31de42bef6d790e96b3169f46a0ea3aefbe2ab17bf0a`.

## 정정 5건
1. **sidecar 수치.** 원본 README의 "내부 `.sha256` 37쌍은 PC에서 모두 일치 확인"은 틀렸다. 정확히는 **40쌍 중 39쌍 일치, 1쌍 불일치**이며, 불일치 1쌍은 묶음 안에 자기 자신으로 포함된 0바이트 `cp02-evidence-20261006.tgz`와 그 `.sha256`이다. 원본과 sidecar를 고쳐 맞추지 않았다.
2. **감시 표현.** 원본 README의 "5초 감시"는 **설정 주기**다. `restart-watch.txt`(sha256 `b2a8994f46707fd04b4002198b812139bdc30c60669c2fc3dff78b78cbea3a7c`) 782행의 실제 인접 표본 간격은 5초 611회·6초 102회·10초 52회·11초 16회(최대 11초), leader 표본 131회·최대 간격 36초다. 정확히 5초마다 모든 항목을 연속 입증한 것이 아니며 관측 사이의 짧은 변화는 보증하지 않는다.
3. **첫 OFF capture 범위.** control02 `7-tcpdump.txt`는 edge01→control02 SYN 3개만 담고 있어 **응답 방향을 관측한 증적이 아니다.**
4. **attempt02 tcpdump 필터.** `capture.txt`를 만든 실제 tcpdump 필터 명령은 수신된 서버 원본 파일에 보존되지 않았다. 실행자 터미널 출력(heredoc)에 남은 필터식은 `host 10.1.93.50 and host 10.1.93.103 and tcp and (port 6443 or port 10250 or port 2379)`이며, 이 필터와 실제 실행의 동일성은 재현하지 못했다.
5. **Felix 추가 키.** 제출 `4-felix-manifest.json`에는 없던 `nftablesMode: Auto`가 재생성 직후 `4-felix-live.json`(15:17:51 KST)에 있다. 서버 기본값이라는 설명은 추정이며 출처, 시험 전 값, 다른 노드 값은 미확인이다. 승인 failsafe inbound/outbound 두 필드는 manifest와 live가 일치한다.

## 확인 방법
2026-10-06 이 정정은 PC에서 #121의 로컬 원본을 다시 열어 확인했다. sidecar 39/40(불일치는 자기 포함 0바이트 tgz), 감시 간격 집계, manifest/live 차이, 단방향 capture를 확인했고, 같은 수치를 PMO/QA 직접 집계가 재현했다. 새 서버 실행·구성 변경은 없다.

AI usage: CLAUDE_CODE_ASSISTED.
