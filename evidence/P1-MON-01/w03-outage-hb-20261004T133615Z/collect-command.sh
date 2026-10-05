# monitor01(server01_monitor)에서 실행하도록 2026-10-04 22:2x KST 채팅으로 전달한 읽기 전용 조회 명령 전문.
# 실제 실행 화면(셸 기록)은 보존하지 않았다. 결과 폴더 이름(p1-mon-w03-outage-20261004T223615)과
# ts.txt(2026-10-04T22:36:15+09:00)가 이 명령의 형식과 일치한다.
T=$(date +%Y%m%dT%H%M%S); D=~/p1-mon-w03-outage-$T; mkdir -p $D && cd $D && S=2026-10-04T01:30:00+09:00 && E=2026-10-04T16:45:00+09:00 && date -Is > ts.txt && curl -sS -m 30 -G http://127.0.0.1:19090/api/v1/query_range --data-urlencode 'query=ALERTS{alertname="FDSMonitoringHeartbeatMissing"}' --data-urlencode "start=$S" --data-urlencode "end=$E" --data-urlencode step=60 > alerts.json && curl -sS -m 30 -G http://127.0.0.1:19090/api/v1/query_range --data-urlencode 'query=count_over_time(fds_monitoring_heartbeat[1m])' --data-urlencode "start=$S" --data-urlencode "end=$E" --data-urlencode step=60 > hb.json && python3 -c 'import json,datetime as d
z=d.timezone(d.timedelta(hours=9))
f=lambda t:d.datetime.fromtimestamp(float(t),z).strftime("%m-%d %H:%M:%S")
a=json.load(open("alerts.json"))["data"]["result"]
[print("ALERT",s["metric"].get("alertstate"),"first",f(s["values"][0][0]),"last",f(s["values"][-1][0]),"points",len(s["values"])) for s in a]
print("ALERT series",len(a))
p=sorted(float(t) for s in json.load(open("hb.json"))["data"]["result"] for t,_ in s["values"])
print("HB points",len(p),"first",f(p[0]) if p else "-","last",f(p[-1]) if p else "-")
[print("HB gap",f(p[i]),"->",f(p[i+1]),int(p[i+1]-p[i]),"s") for i in range(len(p)-1) if p[i+1]-p[i]>120]' > summary.txt && sha256sum * && cat ts.txt summary.txt
