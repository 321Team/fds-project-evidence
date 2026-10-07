echo "# host=$(hostname -s) time=$(date --iso-8601=seconds)"
ls -l /root/.docker/config.json
python3 - <<'PY'
import json,base64
d=json.load(open("/root/.docker/config.json"))
for k,v in d.get("auths",{}).items():
    u=""
    if v.get("auth"):
        u=base64.b64decode(v["auth"]).decode().split(":",1)[0]
    elif v.get("username"):
        u=v["username"]
    print(k,"user="+u,"keys="+",".join(sorted(v.keys())))
PY
