## #148 병합 및 Issue9 후속 — MON 후보 엔진 읽기 검증 1회

CODEX_ASSISTED · 2026-10-08 KST. 사용자 요청에 따라 evidence#148을 00:47:31에 병합했습니다. exact HEAD `536fab9af5bf21772c10523efb41007de594b834`, 이재환 독립 APPROVED5444727780 및 evidence-layout SUCCESS, 원격28파일 byte 일치, Ready 전환 후 동일 HEAD 고정 병합. merge `d034e60bc7d31a11f00c231ccd9f5db51c16b0e8`, 승인본 대비 파일 차이0. GitHub required check 지정은0건이며 실제 CI1건 SUCCESS와 구분합니다.

후속은 검토·병합된 infra-ansible `da4e273e7e26a9a0b51211e5146066960df072b5`의 기존 `cr-p1-mon-01-01-run.sh verify`를 후보2.21.3으로 실행하는 단일 검증입니다. 새로운 apply/rollback·운영 전환 명령은 실행하지 않습니다.

- 범위: ansible01/server01_ansible → egress-proxy01(10.1.93.56)/svc_ansible의 기존 sudo. localhost inventory guard + egress_proxy1대. Worker/control-plane 작업 없음.
- 읽기 전용 확인: main role의 영구 파일/패키지/firewall/service 변경 태스크는 모두 `cr_mon_phase == 'apply'` 조건. verify는 현 상태/기존 baseline 읽기와 기존 discord.com 허용·example.com CONNECT403 검사뿐입니다. 출력과 Ansible 임시 작업 파일을 제외한 운영 설정 변경·재시작 없음.
- 선행 확인: 기존 SSH 인증 rc0, root:root0600 baseline 파일 존재(stat rc0,777bytes), source HEAD 일치/tracked clean, 앞선 실제 후보 CLI4개 검증 PASS. baseline 내용의 적합성은 기존 verify가 실제 검사합니다.
- 이번 읽기 검증 창: **00:53~01:00 KST**, 실행 제한120초 + TERM 후10초. 00:58 이후 새로 시작하지 않으며 같은 회차 자동 재시도 없음. 이번 코멘트는 순수 검증 실행 범위 기록이며 쓰기 GO가 아닙니다.
- 시작 전 inventory graph로 egress-proxy01 단일 대상 재확인. 인증/대상/기준선 불일치, unreachable, FAIL, timeout이면 중단·원본 보존. baseline을 새로 생성하거나 apply로 오류를 해소하지 않습니다.
- 성공은 MON verify의 실제 후보 엔진 실행/기존 기준선/허용·거부 판정까지이며 역할 apply·멱등성·복구·전체 엔진 전환·Issue9 인수는 별도로 남습니다. NTP·DNS와 다른 세션 SEC/IF-06B 작업은 건드리지 않습니다.
