# Harbor A2R1 실제 재생성 후 Mode 차이 STOP

CODEX_ASSISTED. baseline #13의 NIC 없는 작업 복제본 harbor01에서 사용자 server08 콘솔 sudo로 실행한 원본이다. 소스는 infra-harbor-trivy #16 승인 HEAD `75d371eced1f6d381ea022f9192eb78593cea5bd`, 병합 `b0292f71acccb6dd9b7ed0f84d1882f30e2aa79f`, 실행 blob SHA256 `584fe787f78eec41e13390dfa08a8af656183cb9befbbd154e47bb89c4ee41a8`이다.

## 실제 결과와 원본 판정

2026-10-08 16:20:07~16:20:50 KST 앱9개 재생성 명령 rc0, 앱ID9개 변경·logger ID 유지, 10개 running/healthy. 이미지·포트·restart·볼륨 이름/경로·bind mounts는 유지됐고 앱9개 syslog 주소만 후보 IPv4로 바뀌었다. 그러나 portal/proxy 각3개 및 registryctl1개의 volume Mode가 빈 값에서 z로 바뀌어 **원본 결과는 STOP_RECOVERY_REQUIRED / PRESERVATION_MOUNTS**다. 이를 PASS로 덮어쓰지 않는다.

16:26:35 KST 읽기 전용 회수에서 Harbor10개 현재 선택 inspect가 after와 완전히 일치했고, 기존 volume9개 조회와 1514 listener 조회도 rc0였다. 원본 확인 없이 apply/restore 재시도·Docker restart·스냅샷 되돌리기를 하지 않았다. 승인 소스의 restore 검사를 이 before/current에 적용하면 RESTORE_MOUNTS_CHANGED로 거부된다.

## 보안·버전 추가 조회와 해석

16:34:18~19 KST Docker29.8.0 GitCommit3ce5872, Compose5.5.1, 호스트 SELinux Enforcing/enforce=1을 확인했다. Docker가 보고한 SecurityOptions에는 seccomp/cgroupns만 있으며 selinux는 없다. 전체 daemon.json을 수집하지 않았고 selinux-enabled의 부재 여부만 읽었다. volume9개 디렉터리 xattr는 모두 container_file_t:s0이며 변경 전 xattr는 수집하지 않았으므로 직접 전후 보존을 증명하지 않는다.

**배치 조회는 부분 성공이다.** container-labels rc1은 3/10개 객체, image-volume-declarations rc1은 8/10개 객체만 출력했다. 이 3개 컨테이너가 정확히 Mode 차이7개를 가진 portal/proxy/registryctl이다. 각 ID·volume Source/Target·image ID와 선언 목적지를 연결해 7/7 영향 범위가 자료에 포함됨을 확인했다. 해당3개는 MountLabel/ProcessLabel이 비어 있고 SecurityOpt=null, Privileged=false다. 나머지7개 컨테이너 선택 필드와 이미지2개의 선언은 미확인이다. 비공개 stderr는 해시만 반출하여 배치 실패의 정확한 원인은 미확정이다. 선택 map 필드가 없는 경우의 템플릿 오류 가능성이 있어 향후 수집기 수정안을 로컬에 준비했지만 이 회차에 사용하지 않았다.

SOURCE_REFERENCES.json은 실제 보고된 Engine GitCommit 전체 SHA 및 Compose5.5.1 tag가 가리키는 commit에 고정했다. Engine은 Mounts API의 local volume에 setBindModeIfNull을 적용하여 빈 Mode를 z로 채운다. Compose의 기존 volume 상속은 이름을 Source로 사용하는 Mounts 요청이며 실제3개 HostConfig.Mounts가 이 형태다. Engine이 전달하는 MountLabel이 비어 있으면 해당 빌드의 Relabel 함수는 relabel 없이 반환한다.

**해석:** 이번 특정 Mode 차이는 해당 Engine의 기본값 처리로 설명된다. 원본 볼륨 교체나 이번 조회의 SELinux 해제/설정 변경을 뜻하지 않는다. 실제 과거 xattr 전후 비교·임의 다른 Docker 버전/SELinux 활성 환경의 동등성까지 확대할 수 없다. 현재 호스트 Enforcing과 Docker 라벨 통합 상태는 다른 관측값이며, 이를 맞추기 위한 보안 설정 변경은 수행하지 않았다.

## 자료·한계·다음 단계

- runtime-receipt, label-receipt: 사용자 실행 원본과 guest SHA256SUMS. stage-receipt는 이전 전달 시점 기록이므로 당시 NOT_RUN과 이후 실제 실행을 구분한다.
- trial-used.py 및 두 collector-used.py는 당시 실제 바이트다. 수집기는 자체 점검이며 독립 리뷰로 표시하지 않는다. 전체 Compose/env/stderr와 데이터 내용은 반출하지 않는다.
- 원본 SHA·manifest 해시를 확인하고 HBR_RESULT/HBR_LABELS 모두 호스트에서 제거·disable rc0을 확인했다. Windows 긴 경로 복사 제한은 확장 절대경로로 해소하고 같은 바이트를 보존했다.
- MOUNT_ANALYSIS.json은 label 회수 전의 판단 이력이고, ADJUDICATION.json과 이 문서는 이후 보충 근거다. 과거 STOP와 판단 이력을 소급 수정하지 않는다.
- 판정 권고는 **기존 volume 보존 확인 / Docker 기본 Mode 차이 설명 / 현재 격리 후보 유지 후 후속시험 별도 판단**이다. 증적 독립 리뷰를 요청한다. 새 재시작 시험은 아직 실행하지 않았다.
- 현재 실행기는 Mode z를 허용하지 않으므로 동일 apply/restore를 그대로 재사용하지 않는다. 향후 실행기 판정 변경은 source 리뷰 대상이다. A3 설계 시 이번 현재 상태·재시작 전후 fresh 증적·스냅샷 복구·관측 한계를 명시한다.
- Docker restart, VM reboot, 실제 로그 수신 검증, 업무 데이터 무결성, 운영 적용, 자동기동·AC/Issue/Phase1 Close는 NOT_RUN 또는 미인수다.
