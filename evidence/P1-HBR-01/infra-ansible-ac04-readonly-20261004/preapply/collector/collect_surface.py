"""Read-only harbor01 surface collection; stdout is evidence, not acceptance."""
import datetime, hashlib, json, pathlib, socket, subprocess, sys

def command(name, argv, required=True):
    record = {"name": name, "argv": argv, "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=45)
        record.update(rc=r.returncode, stdout=r.stdout.decode(errors="replace"), stderr=r.stderr.decode(errors="replace"))
    except (OSError, subprocess.TimeoutExpired) as exc:
        record.update(rc=124 if isinstance(exc, subprocess.TimeoutExpired) else 127, error=type(exc).__name__)
    record["required"] = required
    print(json.dumps(record, ensure_ascii=False), flush=True)
    return record

def validate_host(host, addresses):
    if host != "harbor01" or "10.1.93.54" not in addresses:
        raise ValueError("TARGET_IDENTITY_MISMATCH")

def main():
    if socket.gethostname().split(".")[0] != "harbor01":
        print("STOP=TARGET_HOSTNAME_MISMATCH")
        return 1
    initial = command("identity-addresses", ["ip", "-j", "address", "show"])
    if initial["rc"] != 0:
        return 1
    try:
        addrs = json.loads(initial["stdout"])
        validate_host("harbor01", [v["local"] for i in addrs for v in i.get("addr_info", [])])
    except (ValueError, KeyError, TypeError):
        print("STOP=TARGET_ADDRESS_MISMATCH")
        return 1
    records = [initial]
    commands = [
        ("interfaces", ["ip", "-j", "-d", "link", "show"], True),
        ("routes4", ["ip", "-j", "-4", "route", "show", "table", "all"], True),
        ("routes6", ["ip", "-j", "-6", "route", "show", "table", "all"], True),
        ("listeners", ["ss", "-H", "-ltn"], True),
        ("current-443-connections", ["ss", "-Htn", "( sport = :443 or dport = :443 )"], True),
        ("nft-version", ["nft", "--version"], True),
        ("nft-ruleset", ["nft", "-n", "list", "ruleset"], True),
        ("iptables-nat", ["iptables", "-t", "nat", "-S"], True),
        ("ip6tables-nat", ["ip6tables", "-t", "nat", "-S"], False),
        ("nftables-unit", ["systemctl", "show", "nftables.service", "--property=LoadState,UnitFileState,ActiveState,SubState,FragmentPath,DropInPaths,Before,After,ExecStart,ExecReload"], True),
        ("firewalld-unit", ["systemctl", "show", "firewalld.service", "--property=LoadState,ActiveState,SubState"], True),
        ("docker-unit", ["systemctl", "show", "docker.service", "--property=LoadState,ActiveState,SubState"], True),
        ("443-conntrack", ["conntrack", "-L", "-p", "tcp", "--dport", "443"], False),
    ]
    for name, argv, required in commands:
        records.append(command(name, argv, required))
    ids = command("docker-container-ids", ["docker", "ps", "--quiet", "--no-trunc"])
    records.append(ids)
    if ids["rc"] == 0:
        for i, container in enumerate(ids["stdout"].splitlines()):
            if len(container) != 64 or any(c not in "0123456789abcdef" for c in container):
                print("STOP=INVALID_DOCKER_ID")
                return 1
            # Deliberately omit container Config/Env, credentials and labels.
            fmt = '{"id":{{json .Id}},"name":{{json .Name}},"ports":{{json .NetworkSettings.Ports}},"networks":{{json .NetworkSettings.Networks}}}'
            records.append(command("docker-surface-" + str(i), ["docker", "inspect", "--format", fmt, container]))
    # Fixed nft configuration paths only. Includes are recorded for review, not executed.
    for name in ["/etc/sysconfig/nftables.conf", "/etc/nftables.conf", "/etc/nftables/main.nft"]:
        p = pathlib.Path(name)
        if p.is_symlink():
            print(json.dumps({"name":"nft-config","path":name,"status":"LINK_REQUIRES_REVIEW"}))
            continue
        if p.is_file():
            try:
                data = p.read_bytes()
                if len(data) > 1048576:
                    raise ValueError("TOO_LARGE")
                # Preserve only nft include/flush/table directives; not arbitrary configuration contents.
                lines = data.decode(errors="replace").splitlines()
                selected = [{"line":i+1,"text":line} for i,line in enumerate(lines)
                            if line.strip().startswith(("include ", "flush ", "table "))]
                print(json.dumps({"name":"nft-config","path":name,"sha256":hashlib.sha256(data).hexdigest(),"selected_directives":selected}))
            except (OSError,ValueError) as exc:
                print(json.dumps({"name":"nft-config","path":name,"status":"READ_FAILED","error":type(exc).__name__}))
                return 1
        else:
            print(json.dumps({"name":"nft-config","path":name,"status":"ABSENT"}))
    failed = [r["name"] for r in records if r["required"] and r["rc"] != 0]
    optional = [r["name"] for r in records if not r["required"] and r["rc"] != 0]
    print(json.dumps({"required_failed":failed,"optional_unavailable":optional,
                     "verdict":"COLLECTION_FAILED" if failed else "NETWORK_SURFACE_CAPTURED_REVIEW_REQUIRED",
                     "full_client_population":"NOT_PROVEN","alternate_paths":"REQUIRES_REVIEW",
                     "loader_include_resolution":"REQUIRES_REVIEW","runtime_apply":False}))
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())

