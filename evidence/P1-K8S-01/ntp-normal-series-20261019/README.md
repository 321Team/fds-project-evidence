# NTP 정상6회 시계열 — 실제 순수 조회 원본

원조건은 [실제09/16 Decision](https://github.com/321Team/fds-project-baseline/issues/10#issuecomment-5697547621)의 **60초 간격6회·offset100ms**다. 기존 보존 archive14개/최근 단발 관측에 없는 이 정상시계열만 추가했다. 기존role185/paired6/OSDNS·CI·reboot/장애시험을 반복하지 않았다.

## 실제 결과

6대 각각6표본, 총36 node-sample·chronyc72명령 실제rc0. 모든 표본의host/machine/boot·SSH계정/실효권한을 결속했고, source·Leap Normal·stratum·두offset 수치를 판독했다. node별실제간격5개와span은 CENTRAL_READBACK.json·원문에 있다. 최소span300초 이상, 최대Last offset0.401770ms·최대System time0.155312ms로100ms이내였다. 전체실행 약300.765초.

이것은 해당6시점의정상상태관측이다. 표본사이연속정확도·모든시점가용성·외부서버의새응답6건을입증하지않는다. CP1은원문에서Poll10·Reach377·Ref time03:18:05UTC·약1031초update interval을보고했다. 조회시점/monotonic과chronyd내부측정시각을분리보존했다. [chronyc공식설명](https://chrony-project.org/doc/4.4/chronyc.html)에따르면Poll은2의지수로표현한간격이고LastRx는마지막유효표본이후시간이다. LastRx만으로이번회차에sync-loss장애를주입/검증했다고판정하지않는다.

client5대는내부10.1.93.102선택,CP1은기존두Cloudflare주소집합과선택1개를관측했다. 후속시간원선정·네트워크변경준비기록은실제egress정책최종승인과구분한다. sync-loss5분·reboot재동기5분·전체NTP/K8S AC와최종인수는이조회로완료하지않는다.

## 출처와 단계

`originals/`는실제시작intent·각요청/실제rc/시각/원문stdout/stderr·표본별판독·최종결과의바이트사본이다. `executed-source/`는실제v2 소스다. 미실행v1의timeout부분원문보존결함은실행전에중앙수정했고v1은보존했다. 별도Codex기술검토는v2delta의R1해소를확인했으며사람의독립승인으로표시하지않는다. parser7개local selfcheck는동일함수원문이불변인범위로재사용했다.

`inputs/round*.stdin`은실행후고정소스·직전실제clock영수증에서정확재구성한입력이다. **실제dispatch시저장된SHA와6/6일치**를확인했으며사전원문캡처라고표시하지않는다. 실행입력은추적/대조용이고재실행허가가아니다.

원격기존SSH+비대화형sudo의메모리stdin으로tracking/sources만읽었다. 서버파일/서비스/설정·chrony시각·upstream/방화벽변경0,새packetprobe·자동retry·forcekill0. 인증/감사체계의통상로그까지0쓰기라고주장하지않는다. 모든요청프로세스정상반환을원문으로확인했다.

새증적편입/독립리뷰/병합은별도단계다. 이수집의성공을실제사람승인·전체AC/Gate/Phase1 Close로확대하지않는다. CODEX_ASSISTED.
