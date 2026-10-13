# 사용자 승인과 정확 입력 결속

CODEX_ASSISTED · 2026-10-13 22:55 KST. 사용자가 PR219 실행안에 **“제안 범위 허용·콘솔 대기·비중첩 확보”**로 답했다. plan bytes는 변경하지 않았다. 이 문서는 초기 collection의 승인 대기 상태를 후속 갱신하는 별도 기록이다.

- 승인 창: 10/13 23:15~23:25 KST 실제 시작, 10/14 00:15 정리 종료. 준비 배치→false1회→true Deploy1회, TokenRequest1회, 자동 재실행0회.
- 대상: fds-app 두 앱 image 교체와 기존 실행기 조건을 충족하는 지정 이전 image 복귀. 복귀 시 업무 포트 /metrics 노출 재발. Push·HA/drain/reboot·Probe 장애·업무 POST/DB 쓰기·최종 인수는 제외.
- 승인 원문: [infra-cicd#11 정확 JSON](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6147190360). GWONUK 작성자와 원문 UTF-8 bytes를 재조회했다. 사용자 결정을 대리 기록했으며 AI·타인의 독립 승인으로 표시하지 않는다.
- 콘솔/비중첩: 이권욱 확인. 실행 직전 main/두 앱 기준선/Harbor·다른 변경/Worker·SA/CA·권한을 재확인하며 독립 입력 검토 전에는 실행하지 않는다.

| 파일 | SHA256 |
|---|---|
| plan (초기 collection, 동일 bytes) | `ed7787673f5b8f8f1f97e49e78a9359ec1c09f8835acda19cc93d7e130ee2ad4` |
| approval.json | `fb1458a22db9fa91397810293cbbb0f66198b08786e6e365150cef18e0bebb4d` |
| deploy-37a528cd-184a-4e0f-8f17-62416ca2e4e4.json | `fb8b603e6e9ee4449767d74a5d22fb864c1ef7a0a11d75e1eef0c3144d1c58db` |

`deploy_plan.validate()`로 제안 시작 시각·정적용 Run1을 대입한 전체 pure byte 결속 MATCH. 실제 Run 생성·서버 입력 배치·발급·Deploy는 미실행이다. **독립 검토는 위 record hash까지 포함해야 한다.** 실제 RunID는 dispatch 뒤 GitHub와 Runner dispatch 원본을 대조해 결속한다.

broker UTC 인자 `2026-10-13T15:15:00+00:00`는 10/14 00:15 KST와 파서상 일치한다. 기존 strict SSH/CA, SA/audience/TTL900, 원본·claim 보존, 권한/결과 불명 시 중단은 초기 실행안 그대로다.
