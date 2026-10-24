# P2 창 C 원본 (#47) — 2026-10-22, 이재환

- G T0 20:32:06 KST, VPN_RUN 20261022T1500(창 B 유지), DB_RUN 20261022T2038
- A2-ON 20:39:49 OK → A4 회귀 21:09:50~52 → 녹화 21:44:12~37 → C-STOP(하영) 22:00:55 → A2-OFF 22:02:49~57 OK(W0 일치)
- GitHub 기록: baseline#47 6340047661(G·W0·A2-ON), 6341600008(A4·녹화·A2-OFF·VPN 증분)

## 구성
- db01/windowC-db01-20261022T2038.tgz — db01 원본(W0 check·firewall check, a2-apply·a2-rollback 출력, receipt·pg_hba rules 전후·NM routes, tcpdump pcap·log, A4 DB 조회 23행). db01에서 묶은 SHA-256 b2748f7dee8ed872a39c115012fbb2daf4f416c33015a8f763095a74c5d8502b, scp 후 PC 재해시 일치
- pc/a4-regression — p2e2e.py(a00ae029…a07d), PLAN·OUT_B1·OUT_B2(RUN 202610221209), db01 조회 결과
- pc/recording — 로컬 프록시 로그 2개(21:20 첫 시도·21:45 녹화), 원본 영상, 최종 영상(짧은 표시 + ROSA 관측), db01 녹화 거래 11행
- pc/rosa-monitoring — OpenShift 기본 모니터링(Prometheus) query_range 원데이터 2개(네트워크·Pod 수, 20:40~22:05 KST), 2단 그래프 PNG

## 제외
- DB 비밀번호·DSN·Secret 값·kubeconfig·토큰은 없음(파일 검사 0건). pcap은 TCP 5432 헤더·TLS 시작부(snaplen 128)만
