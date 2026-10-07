#!/usr/bin/python3
import json, hashlib, subprocess, datetime
D = "/var/lib/fds-change/P1-HBR-01-AC04"
def run(a, shell=False):
    p = subprocess.run(a, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return p.returncode, p.stdout.splitlines(), p.stderr.splitlines()
def sec(t, a, shell=False):
    rc, o, e = run(a, shell); print("== %s rc=%d" % (t, rc)); print("\n".join(o))
    if e: print("-- stderr:"); print("\n".join(e))
    return o
print("KST", datetime.datetime.utcnow() + datetime.timedelta(hours=9))
sec("uptime", "uptime -s; uptime", True)
raw = open(D + "/original-state.json", "rb").read()
print("original-state.json sha256", hashlib.sha256(raw).hexdigest(), len(raw))
sec("PRESTATE sha256sum -c", "cd %s && sha256sum -c PRESTATE_SHA256SUMS" % D, True)
sec("guard file sha256", ["sha256sum", "/etc/p1-hbr-ac04.nft"])
sec("nft -c syntax only", ["nft", "-c", "-f", "/etc/p1-hbr-ac04.nft"])
O = json.loads(raw)
cmds = {"forward_rules": ["iptables","-w","5","-t","filter","-S","FORWARD"],
 "docker_user_rules": ["iptables","-w","5","-t","filter","-S","DOCKER-USER"],
 "docker_forward_rules": ["iptables","-w","5","-t","filter","-S","DOCKER-FORWARD"],
 "docker_filter_rules": ["iptables","-w","5","-t","filter","-S","DOCKER"],
 "docker_nat_rules": ["iptables","-w","5","-t","nat","-S","DOCKER"]}
C = {}
for k, c in cmds.items():
    rc, C[k], _ = run(c)
    print("== %s rc=%d current:" % (k, rc)); print("\n".join(C[k]))
    if O[k] != C[k]: print("-- original:"); print("\n".join(O[k]))
def tail_ok(key, head_n, tail_rules):
    o, c = O[key], C[key]
    return len(o)==6 and len(c)==6 and o[:head_n]==c[:head_n] and sorted(o[head_n:])==sorted(c[head_n:])==sorted(tail_rules)
df_tail = ["-A DOCKER-FORWARD -i docker0 -j ACCEPT","-A DOCKER-FORWARD -i br-835092bfcbbc -j ACCEPT"]
d_tail = ["-A DOCKER ! -i docker0 -o docker0 -j DROP","-A DOCKER ! -i br-835092bfcbbc -o br-835092bfcbbc -j DROP"]
print("A2_DOCKER_FORWARD =", "PASS" if tail_ok("docker_forward_rules",4,df_tail) else "FAIL", "| exact =", O["docker_forward_rules"]==C["docker_forward_rules"])
print("A2_DOCKER_FILTER  =", "PASS" if tail_ok("docker_filter_rules",4,d_tail) else "FAIL", "| exact =", O["docker_filter_rules"]==C["docker_filter_rules"])
for k in ("forward_rules","docker_user_rules","docker_nat_rules"): print("EXACT_%s =" % k, "PASS" if O[k]==C[k] else "FAIL")
sec("nft table (counters before)", ["nft","list","table","inet","p1_hbr_ac04"])
sec("systemd docker", "systemctl show docker -p ActiveState -p SubState -p ActiveEnterTimestamp -p NRestarts -p Requires -p After", True)
sec("systemd guard", "systemctl show fds-harbor-ac04-guard -p ActiveState -p SubState -p UnitFileState -p Before -p RequiredBy -p ActiveEnterTimestamp", True)
sec("firewalld state/runtime", "firewall-cmd --state; firewall-cmd --list-all --zone=public", True)
sec("firewalld permanent", "firewall-cmd --permanent --list-all --zone=public", True)
rc, o, e = run("docker ps -aq | xargs docker inspect", True)
print("== containers (Env/LogConfig.Config 제외) rc=%d" % rc)
for c in sorted(json.loads("\n".join(o)), key=lambda x: x["Name"]):
    hc, st, ns = c["HostConfig"], c["State"], c["NetworkSettings"]
    print(json.dumps({"name": c["Name"], "id": c["Id"], "image": c["Image"], "config_image": c["Config"]["Image"],
      "status": st["Status"], "health": st.get("Health", {}).get("Status"), "started": st["StartedAt"], "exit": st["ExitCode"],
      "restart": hc["RestartPolicy"]["Name"], "log_type": hc["LogConfig"]["Type"], "netmode": hc["NetworkMode"],
      "ports": ns["Ports"], "mounts": [[m["Type"], m.get("Source"), m["Destination"], m["RW"]] for m in c["Mounts"]]}, sort_keys=True))
sec("docker info", "docker info --format 'live_restore={{.LiveRestoreEnabled}} logging={{.LoggingDriver}}'", True)
sec("443 listeners", "ss -ltn sport = :443", True)
sec("localhost resolve", ["getent","ahosts","localhost"])
sec("localhost:1514 tcp", "timeout 3 bash -c 'exec 3<>/dev/tcp/localhost/1514; exec 3>&-; exec 3<&-'; echo tcp_rc=$?", True)
