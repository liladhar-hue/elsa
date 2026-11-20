import ipaddress


def _to_port(text):
    try:
        number = int(text)
    except ValueError:
        raise ValueError(f"invalid port: {text!r}")
    if not 1 <= number <= 65535:
        raise ValueError(f"port out of range (1-65535): {number}")
    return number


def parse_ports(text):
    """'102,502,1000-1010' -> sorted list of unique ints."""
    ports = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, _, end_text = part.partition("-")
            start, end = _to_port(start_text), _to_port(end_text)
            if start > end:
                raise ValueError(f"bad port range: {part}")
            ports.extend(range(start, end + 1))
        else:
            ports.append(_to_port(part))
    if not ports:
        raise ValueError("no ports given")
    return sorted(set(ports))


def parse_targets(target_arg, file_path):
    """Collect IPv4 addresses from -t (comma-separated) and/or -f (file)."""
    raw = []
    if target_arg:
        raw += [x.strip() for x in target_arg.split(",") if x.strip()]
    if file_path:
        with open(file_path) as f:
            for line in f:
                line = line.split("#")[0].strip()   # allow comments
                if line:
                    raw.append(line)

    hosts = []
    for item in raw:
        try:
            ipaddress.IPv4Address(item)
        except ValueError:
            raise ValueError(f"invalid IPv4 address: {item!r}")
        if item not in hosts:
            hosts.append(item)

    if not hosts:
        raise ValueError("no targets given (use -t or -f)")
    return hosts
