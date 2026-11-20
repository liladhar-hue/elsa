import socket


def _result(host, port, protocol, state):
    return {"host": host, "port": port, "protocol": protocol, "state": state}


def check_tcp_port(host, port, timeout=3):
    """TCP handshake check: open / closed / filtered / error."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
        state = "open"
    except ConnectionRefusedError:
        state = "closed"       # host replied with a reset
    except socket.timeout:
        state = "filtered"     # no reply at all
    except OSError:
        state = "error"        # unreachable network, etc.
    return _result(host, port, "tcp", state)


def check_udp_port(host, port, timeout=3):
    """UDP probe: open / open|filtered / closed / error.

    UDP has no handshake. We send one harmless byte and wait:
    - a reply            -> open
    - ICMP unreachable   -> closed
    - nothing (timeout)  -> open|filtered (can't tell which)
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.send(b"\x00")
            sock.recv(1024)
        state = "open"
    except socket.timeout:
        state = "open|filtered"
    except (ConnectionRefusedError, ConnectionResetError):
        state = "closed"       # Linux: Refused, Windows: Reset
    except OSError:
        state = "error"
    return _result(host, port, "udp", state)


def scan_port(host, port, protocol, timeout=3):
    """Dispatch to the right check for the protocol."""
    if protocol == "udp":
        return check_udp_port(host, port, timeout)
    return check_tcp_port(host, port, timeout)
