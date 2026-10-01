# P1-MON-01 — TCP/10250 actual-source Runtime 증적

- Record ID: `P1-MON-01`
- Runtime 관측: 2026-09-29 17:17:25~17:18:17 KST
- Capture host: `k8s-control01`
- Capture interface: `ens160`
- Destination: `10.1.93.102:10250`
- Observed source: `10.1.93.108`
- Archive SHA256: `cb24e212eee711826610453c39790ad2a3029a023a4b2bad42ea257202298c6a`

## 관측 결과

보존된 tcpdump raw에는 `10.1.93.108 → 10.1.93.102:10250` 패킷 라인이 69건 존재하고, `rc.txt`에는 `TCPDUMP_RC=124`가 기록돼 있다. 해당 RC는 원 실행이 `timeout 60 tcpdump ...`였던 관측의 timeout 종료값이다.

원 터미널 세션에서는 tcpdump 직전 Prometheus Pod가 `k8s-worker03`에 배치되고 Pod IP `10.244.39.245`, Ready=true인 것이 확인됐다. tcpdump stderr 통계는 69 packets captured / 72 received by filter / 0 dropped by kernel이었다.

중요: Prometheus placement와 tcpdump stderr 통계는 원 OUT10250 디렉터리에 tee된 raw 파일이 아니므로 archive 내부 `PROVENANCE.txt`에서 **contextual terminal observation**으로 분리 기록했다. 원본 raw는 `control01-10250-tcpdump.txt`와 `rc.txt`이다.

## 원본·전송 무결성

원본:
- `control01-10250-tcpdump.txt` SHA256 `4740fa35951d92ce19d95c7f3aa0f177c110f13c921092d820c802b4131b341d`
- `rc.txt` SHA256 `f7e238ff17a3cc5c190c1d02cb8391df25918a74921d7209d868150d99423ee8`

패키지는 control01에서 원본 hash를 재확인한 후 생성했다. archive/sidecar를 `root:svc_ansible 0640` 최소권한 staging으로 복사하고 ansible01에서 Ansible `fetch(validate_checksum=yes)`로 수신했다.

수신 결과:
- archive expected/actual SHA256 exact match: PASS
- archive 내부 `SHA256SUMS`: 5/5 PASS
- remote control01 staging cleanup: `stat.exists=false`

sidecar에는 원 서버 절대경로가 보존돼 있으므로 다른 위치에서 검증할 때는 첫 번째 SHA256 필드를 archive 실제 hash와 비교한다.

## 판정 범위

이 증적은 **Prometheus가 worker03에 배치된 관측 직후 control01 TCP/10250에서 실제 Node-side source `10.1.93.108`이 관측됐음**을 지원한다.

다음을 단독으로 입증하지 않는다.
- TCP/9100 actual-source
- 모든 Node의 TCP/10250 source/compliance
- Calico named HostEndpoint/GNP 전체 적합성
- P1-MON-01 전체 AC 완료

따라서 해당 복합 요구사항의 부분 근거로만 사용한다.
