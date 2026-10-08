# Edge 실제 전환 — 실행 전 결정안

2026-10-08 KST / GWONUK / CODEX_ASSISTED. 아직 apply하지 않았다.

## 확보된 현장 입력

- 03:05:59 KST edge01 svc_ansible(uid1003) 읽기 조회 성공.
- 디스크 `/etc/nginx/conf.d/fds.conf`, root소유0644,
  SHA256 `4d13819ab9ff50b34c4c783b0f48db058a22e6503e6df821b5b25feb5d74c562`.
- upstream transaction_api 한 블록, 유효 .50:30080 한 줄, 주석 Worker105/107/108 각1줄.
- nginx/k3s active. 이것은 nginx -t, 전체 include 형상, 실행 중 worker의 디스크 설정 반영,
  옛 E-K3S 로그 접근·복구 성공까지 확인한 결과가 아니다.
- 현재 구성 source-preservation3/3는 evidence#156. 미래 전환 직전 gate를 대체하지 않는다.
- 코드 infra-kubernetes#70 merge `95af5b09e50f31f28101fb6f9840aef42c227a3f`.
  검토HEAD258c1dbec77d1fcb7a8c078047e2db90b451213f, review5445427676 APPROVED.

## 정확한 변경 범위

```diff
-    server 10.1.93.50:30080;
+    # server 10.1.93.50:30080;  # E-K3S, Edge Cutover <RUN>
-    # server 10.1.93.105:30080;
-    # server 10.1.93.107:30080;
-    # server 10.1.93.108:30080;
+    server 10.1.93.105:30080;
+    server 10.1.93.107:30080;
+    server 10.1.93.108:30080;
```

RUN은 확정 실행시각을 사용하는 새 회차 ID다. 위 diff는 읽은 현재 파일로 계산한 제안이며 적용 입력이 아니다.
현장 코드가 apply 직전 before 사본을 만들고 예상형상·8개 diff행을 검사한다.
nginx upstream 변경·nginx reload, GET 표식9건 및 smoke POST1건이 실제 전환 범위다.
정본과 nginx/HAProxy 차이, XFF, backend timeout은 기존 별도 처분으로 유지한다.

## 순서와 완료 기준

1. 실행자·T0/종료·비중첩 및 현장 sudo/rollback 가용성을 확정하고 #19에 정확한 코드/범위의 GO 기록.
   기존 계획10/10 오전·이재환 실행이며 GWONUK의 현재 구성 P4 1회 GO는 이미 소비됐다.
2. control01 fresh `pre <RUN>`:6Ready, endpoint각1, ETP Local30080/.50허용/32085없음/MON23정상.
3. edge01 `check <RUN>`: sudo 인증, nginx -t/디스크 반영·현재 edge/Worker경로, E-K3S active,
   E-K3S 표식 TRACE_READY. control01 `trace <RUN> check<HHMMSS>`도 TRACE_READY여야 한다.
4. edge01 `apply <RUN>` → control01 `trace <RUN> apply`.
   edge EDGE_OK만으로 완료로 읽지 않는다. Worker로그에 1~9·smoke가 각각1번 나와야 C1 완료다.
5. C2: edge200/metrics404, DB smoke 거래1행의 false/false, P4 .50보존,
   승인되지 않은 PC source N1(기존계획 .29), control01 post. PC .29와 DB 관측 담당/접근 필요.
6. C3 30분간5분간격 edge/MON 관찰. 전환전체 T0+75분, 복구완료 목표T0+90분.
   완료증적은 별도 PR. #47 DB 변경은 이 실행에 포함하지 않는다.

## 중단·복구

사전 gate 실패면 apply 금지. 적용 후 오류/미확정/표식누락/잘못된경로/업무실패/N1 FAIL이면
실행자·Review Owner가 즉시 rollback 또는 한정 보완 관측을 판단하며 완료로 기록하지 않는다.
복구는 같은 RUN `edge01-cutover.sh rollback <RUN>`로 apply직전 사본 복원→nginx -t→reload→
실행설정 반영→E-K3S 표식3건+smoke1건 각1회 확인. control01 rollback trace0건은 보조 증적.
복구에도 sudo와 E-K3S 로그 접근이 필요하다. k3s·옛 DB허용을 유지해 복구경로를 보존한다.

## 현재 실행을 막는 입력

- edge01 svc_ansible `sudo -n -l`은 암호 필요로 실패. 실제 전환뿐 아니라 nginx -t/E-K3S로그·rollback도
  현재 비대화형 경로로 보장되지 않는다. 계정/권한을 임의로 바꾸지 않는다.
- 기존10/10 이재환 실행을 유지할지, 사용자 지시로 지금 GWONUK 실행에 이관할지 확정 필요.
- 앞당기면 exact 실행창, sudo 가능한 기존 접속, PC .29/DB C2 관측과 동시 작업 조정도 필요하다.

필요한 인증은 사용자 터미널에서 입력하며 비밀번호·키내용을 채팅/증적에 남기지 않는다.
현재 요청에 대해 읽기 수집/정확한변경안/실행·중단·복구 조건까지 준비했다.
동일 P4나 Backup을 반복하지 않았고, 파일변경/reload/POST/DB변경은 수행하지 않았다.
