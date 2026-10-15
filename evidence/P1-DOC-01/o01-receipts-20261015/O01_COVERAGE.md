# O01 완료 범위와 잔여 판단

2026-10-15 KST · DOC Lead 이권욱 지원 · CODEX_ASSISTED. [DOC #24](https://github.com/321Team/fds-project-baseline/issues/24)의 승인된 AC를 대응시키는 표다. 새 AC·수행자·기한·현장 실행을 지정하지 않는다.

| 요구/범위 | 현재 확보 | 아직 판단할 부분·완료조건 |
|---|---|---|
| 제3자 원본 탐색·오프라인 판독 | AC07 이재환 최초 판독, Probe223 기존 참여자 재확인; 명령·출력·시각·rc와 도움 범위 기록 | 이 두 사례가 전체 Runbook 핵심 검증을 덮는지 DOC Lead가 기존 요구·기존 실습 결과와 대응. 새 초견 참여자 요구를 자동 추가하지 않음 |
| Runbook 전제·중단·복구의 재현성 | AC07 D1~D5 보완·수행자 확인, Probe223 관측 한계·시각 출처 안내 | 아직 대응되지 않은 핵심 절차를 특정. 기존 O02 실습은 그 범위로만 재사용. 현장 작업이 필수인 미충족 요구가 확인될 때만 정확 대상·소스·계정·창·관측·복구·정리 조건을 완성 |
| P0 Ticket별 Evidence 연결 | 기존223/231·수신19파일 및 검수 기록 연결, PR173 문서 병합 | 전체 P0의 AC→실행→증적→승인/인수 연결은 전수 최종 대조 전. 본 묶음만으로 완비 판정 불가 |
| As-built/Baseline 차이 | 기존 MON/SEC·APP/E2E 대응표와 변경/관측 한계가 있음 | 최종 운영 버전/IP/Port/이미지/정책과 문서를 대조하고 차이를 유효 Change/Known Issue에 연결 |
| Critical 문서 결함0 | 이번 범위 D1~D5·시각 안내 공백 처분 | 전체 Architecture/Test/Evidence/Runbook 검수 전이며 전 범위 Critical0은 미판정 |
| DOC Freeze/인수 | 회차별 수행·검수 결과 확보 | 선행 HA/DR/E2E 인수 범위와 미완료 Known Issue의 풀네임 Owner·Due/유효 처분, 버전·Source·재현성 검토를 집계한 뒤 DOC Lead 판단 |

## 병행할 담당자 판단 입력

- APP/E2E/MON Lead 이재환: D03 격리 범위 최종 처분, D04 기존169+224/228+234 결합 재사용, D02 확인자·기존 화면/복구 Runbook·자동 통보 공백 영향·외부 Probe별 근거, I01 명시적 offset/naive·미래 이력 영향 판단. [기존 처분안](https://github.com/321Team/fds-project-baseline/issues/20#issuecomment-6181579432)을 재사용한다. 추가 시험은 부족한 요구가 특정되는 경우에만 구체화한다.
- SEC Lead 이하영: 현재 부팅 보호와 기존 위험수용의 적용 범위, AC02/04/05/06 잔여 행의 증거·인수 판단. 정상/격리 시험을 일괄 반복하지 않는다.
- Grafana 보관·회수 책임 이권욱: 수령 확인 불가·전달/회수 기록 없음·별도 사본 미확인이라는 [현황 회신](https://github.com/321Team/fds-project-baseline/issues/17#issuecomment-6181744126)을 유지하고 MON/SEC와 공백의 영향·처분을 정리한다. 수령·회수·회전 완료로 바꾸지 않는다.

이 문서는 담당자에게 메시지를 보냈거나 새 인수 결정을 받았다는 기록이 아니다. Phase2 이관·새 Due·위험수용을 자동 확정하지 않는다. PR173/234 편입과 본 PR 병합은 DOC Freeze·G3·Review·Sign-off·Close의 대체 승인이 아니다.
