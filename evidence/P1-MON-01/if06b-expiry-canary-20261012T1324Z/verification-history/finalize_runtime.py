from pathlib import Path
import datetime as dt,hashlib,io,json,re,tarfile
root=Path(__file__).resolve().parent
r=json.loads((root/'RUNTIME_RESULT.json').read_text())
assert r['runtime']=='PASS_WITHIN_OBSERVED_SCOPE'
at=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat()
report=f'''# Phase 1 MON IF06B 단회 현장 시험 결과

CODEX_ASSISTED · 작성 {at} · 회차 `{r['session_id']}`

**승인된 1회 canary 생성 → 만료 자동 회수 → 기준 복귀 및 임시 권한 정리를 완료했다.** 검증 범위 내 RUNTIME PASS이며 독립 증적 리뷰·정식 발행·최종 AC 판정과 구분한다. 추가 canary를 실행하지 않는다.

| 단계 | 실제 증거와 판정 |
|---|---|
| 승인·범위 | 기존 `EXECUTION_SCOPE.md` 일괄 허용 + 사용자 “작업창을 이쪽에서 먼저 실행하는것으로 했음. 착수”. Phase 1 IF06B 1회, 제품 source `92c182fc58de999536e56d90012bb2686d9f07cf` |
| 선행 검증 | 새 빈 경로·고정 공급 해시15개·11개 허용/거부 권한 검사·validate·preflight 통과. 동일 boot·동일 공급의 앞선 300초 survival 검증을 재사용 |
| canary 생성 | 22:24:11.058 KST, OWNED UID `{r['uid']}`, RV `{r['resource_version']}`. CREATE_INTENT 1건 |
| 443 양성 대조 | 22:24:39.763, 1회 rc0 / HTTP404 / TLS검증0 / `.108:45143→.30:443`. 네 지점 모두 양방향 확인 |
| 8443 음성 대조 | 22:24:59경, 시작 조건 재확인 뒤 1회 rc28. `.108:45843→.30:8443` SYN worker5/gateway-in5/gateway-out0/monitor0. 동일 포트의 TCP 재전송이며 curl 재실행이 아님 |
| 만료 자동 회수 | 22:25:41.047 만료 trigger → UID/RV 조건부 DELETE 1회 → 22:25:43.094 명시적404. 만료 후 약 {r['cleanup_after_expiry_seconds']:.3f}초, 회수 기한 내 종결. 수동 삭제0 |
| 회수 뒤 연결 | 22:26:01.943 새443 요청1회 rc28. TLS·CA·bind 오류 아님. worker NIC에서 새 SYN은 관측되지 않아 정확한 차단 hook은 판정하지 않음 |
| 정책·기준 복귀 | HEP·host GNP UID/RV/spec와 GNP 목록 동일. gateway·monitor 설정 전후 동일(nft 패킷 카운터 제외), worker 경로 동일 |
| MON 영향 | 시험 전·중·후 targets23/23, remote-write 실패 증가0. 사후 heartbeat {r['host_post_reads']['monitor']['post_heartbeat_seconds']:.3f}초, 활성alert0 |
| 정리 | canary NotFound, 임시 Binding→Role→SA 생성 UID 기준 삭제 후 각각 NotFound, token 파일 제거. 네 캡처 모두 정상 종료·drop0 |

## 관측 구간과 원본

공통 유효 캡처 구간은 **22:23:26.463401~22:28:25 KST**다. 443·8443·post-deny와 canary 만료 회수가 모두 이 안에 있다. gateway22개·monitor11개 사후 조회도 rc0이고 마지막 worker 경로 사후 읽기는22:30:56.841 KST에 종료됐다.

| 원본 묶음 | SHA256 |
|---|---|
| control01-evidence.tar.gz (227개 원본+내부 해시목록) | `{r['control_archive_sha256']}` |
| gateway-fetch.tar.gz | `{r['host_post_reads']['gateway']['archive_sha256']}` |
| monitor-fetch.tar.gz | `{r['host_post_reads']['monitor']['archive_sha256']}` |

`worker03-export.json`은 worker 명령 결과·시각·캡처와 파일별 해시를 포함한다. `worker03-route-post.json`은 별도 사후 경로 영수증이다. `RUNTIME_RESULT.json`은 위 원본의 검증 결과이며 템플릿·합성 자료가 아니다. `SHA256SUMS`는 이 회차 로컬 산출물의 무결성 목록이다.

`supervisor.jsonl`의 `ABSENT_BASELINE_UNVERIFIED` 원문은 그대로 보존한다. 이것은 자동 회수가 canary 부재까지만 판단한다는 뜻이며, 정책·MON·통신 기준 복귀는 별도 원본으로 확인했다. journal의 CREATE_INTENT·OWNED·DELETE_INTENT·DELETE_ACK·ABSENT와 watch rc0를 함께 대조했다. FINAL 줄만으로 fsync를 증명한다고 해석하지 않는다.

## 변경·검증의 범위

이전 준비 회차(mon01)는 canary0·시험0으로 종료하고 원본을 보존했다. mon02 입력은 회차 ID와 이를 포함하는 보호 경로5개 항목만 변경했다. API·cluster UID·CA·manifest/spec·RBAC·제품코드·예산은 동일하다. 인증과 사전 조회를 캡처보다 먼저 완료하고, 사후 조회 전에 해당 터미널에서 sudo 인증을 갱신했다. 보안 설정을 완화하지 않았다.

이번 로컬 준비 보조의 문자열 치환 오류1건은 원격 Python 파싱 단계에서 중단됐다(그 호출의 서버 명령·RBAC·canary0). 정확한 치환과 전송 전 구문 검사로 수정하고 원 실패 영수증을 보존했다. 제품코드 수정이 아니다.

초기 로컬 증적 검증기는 post-deny의 SYN이 반드시 worker NIC에 보여야 한다는 추가 조건으로 중단했다. 실행안6.4는 새 연결 실패와 기준 복귀, 캡처에서의 관측 여부 기록을 요구한다. 추가 조건을 제거하고 **실제 미관측 사실과 차단 위치 미확인**을 명시했다. 최초 검증기와 실패 원인 기록을 보존하며 서버 요청은 재실행하지 않았다. 인수조건을 낮춘 것이 아니다.

## 남은 일과 인계 경계

- **REVIEW/PUBLICATION/AC:** 이번 실제 증적의 독립 확인·정식 저장소 기록·최종 인수 판정은 미수행이다. 코드 리뷰·병합 및 이번 현장 검증과 구분한다.
- 실제 재부팅·SIGKILL·다른 실패 분기를 시험한 것은 아니다. 이번 허용은 단회 정상 생성 및 만료 회수였다.
- MON API와 heartbeat는 시점별 관측이며 연속 무장애를 증명하지 않는다. loopback port-forward는 MON 기준선 조회에만 사용했으며 IF06B 경로 증거는 네 패킷 캡처다.
- Harbor22:18 기록과 사용자 지시에 따라 Harbor는 로컬 작업만 병행했다. 이쪽 현장 변경·관측은 종료했으며 Harbor의 다음 현장 작업은 해당 세션의 별도 범위·조건으로 판단한다. Phase 2·영구 정책·서비스 재시작·티켓 종결은 하지 않았다.
'''
(root/'RUNTIME_RESULT.md').write_text(report,encoding='utf-8')
correction={'at_kst':at,'initial_verifier':'verify_runtime.initial.py','error':'AssertionError: post_syn mandatory presence','cause':'Extra verifier assertion not required by runbook 6.4','correction':'Record zero observed SYN and unestablished exact drop hook; retain rc28 and unchanged policy/baseline evidence','runtime_retry':False,'original_sources_changed':False}
(root/'VERIFICATION_CORRECTION.json').write_text(json.dumps(correction,indent=2)+'\n')
# Scan exported evidence for secret forms without printing any matched value.
secret_hits=[]
for name in ['control01-evidence.tar.gz','gateway-fetch.tar.gz','monitor-fetch.tar.gz']:
    with tarfile.open(root/name,'r:gz') as tar:
        for m in tar.getmembers():
            if not m.isfile():continue
            data=tar.extractfile(m).read()
            if b'PRIVATE KEY-----' in data or re.search(rb'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}',data):secret_hits.append((name,m.name))
assert not secret_hits,'SECRET_PATTERN_DETECTED'
manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts}
(root/'SHA256SUMS').write_text(''.join(sha+'  '+name+'\n' for name,sha in manifest.items()),encoding='utf-8',newline='\n')
for name,sha in manifest.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha
main=root.parent/'READINESS_STATUS.json';status=json.loads(main.read_text())
status['previous_preparation_runtime']=status['runtime']
status.update(at_kst=at,execution_window='MON_CLOSED_RUNTIME_VERIFIED: mon02 complete; no active canary, credential or capture',active_session=r['session_id'],next_trial_constraint='One authorized canary consumed; no automatic rerun',runtime={'session_id':r['session_id'],'validate':'PASS','preflight':'PASS','survival_check':'PASS_REUSED_SAME_SOURCE_AND_BOOT','canary_created':1,'trial_requests':3,'automatic_reclaim':'PASS_EXPIRY','canary_absent':True,'rbac_remaining':0,'token_file_present':False,'credential_cleanup':'PASS','captures_ended':True,'policy_and_baseline_restored':True,'AC':'NOT_DECIDED'},pending=['Independent evidence review / formal publication / final AC assessment; no additional runtime trial authorized by the consumed one-canary grant'])
status['observed']={'baseline':r['baseline'],'post_heartbeat_age_seconds':r['host_post_reads']['monitor']['post_heartbeat_seconds'],'post_active_alerts':0,'gateway_query_rc0':22,'monitor_query_rc0':11}
status['files']['runtime-20261012T2220-mon02/RUNTIME_RESULT.json']=manifest['RUNTIME_RESULT.json']
status['files']['runtime-20261012T2220-mon02/RUNTIME_RESULT.md']=manifest['RUNTIME_RESULT.md']
status['files']['runtime-20261012T2220-mon02/SHA256SUMS']=hashlib.sha256((root/'SHA256SUMS').read_bytes()).hexdigest()
main.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'runtime':r['runtime'],'local_artifact_hashes':len(manifest),'report':str(root/'RUNTIME_RESULT.md'),'window':'CLOSED','AC':'NOT_DECIDED','publication':'NOT_PUBLISHED','secret_form_hits':0}))
