import argparse
import sys

from elsa.catalog import DEFAULT_CATALOG, identify_service, load_catalog
from elsa.report import print_table, write_csv
from elsa.scanner import scan_port
from elsa.targets import parse_ports, parse_targets

BANNER = "elsa - OT service inventory. Use only on systems you are authorized to test."


def build_parser():
    p = argparse.ArgumentParser(
        prog="elsa",
        description="Lightweight OT/ICS service inventory for authorized lab use.",
    )
    p.add_argument("-t", "--target", help="IPv4 address(es), comma-separated")
    p.add_argument("-f", "--file", help="file with one IPv4 address per line")
    p.add_argument("-p", "--ports", nargs="+",
                   help="e.g. 102,502,1000-1010 (default: OT catalog ports)")
    p.add_argument("--ot-preset", action="store_true",
                   help="also scan the OT catalog ports when -p is given")
    p.add_argument("--proto", choices=["tcp", "udp", "both"],
                   help="protocol for -p (default tcp); filters the catalog scan")
    p.add_argument("-sV", "--service-detect", action="store_true",
                   help="add a port-based service guess from the catalog")
    p.add_argument("--timeout", type=float, default=2.0,
                   help="seconds to wait per port (default 2)")
    p.add_argument("--catalog", default=DEFAULT_CATALOG,
                   help="custom services.json")
    p.add_argument("-o", "--output", help="write results to this CSV file")
    p.add_argument("--open", dest="only_open", action="store_true",
                   help="show only open / open|filtered results")
    return p


def build_scan_list(args, catalog):
    """Return an ordered, de-duplicated list of (port, protocol)."""
    pairs = []
    if args.ports:
        ports = parse_ports(",".join(args.ports))
        protos = ["tcp", "udp"] if args.proto == "both" else [args.proto or "tcp"]
        pairs += [(port, proto) for port in ports for proto in protos]
    # no -p given (or --ot-preset given) -> scan the OT catalog ports
    if args.ot_preset or not args.ports:
        for port, proto in catalog:
            if args.proto in (None, "both", proto):
                pairs.append((port, proto))
    if not pairs:
        raise ValueError("nothing to scan")
    return list(dict.fromkeys(pairs))


def main(argv=None):
    args = build_parser().parse_args(argv)
    print(BANNER, file=sys.stderr)

    try:
        hosts = parse_targets(args.target, args.file)
        catalog = load_catalog(args.catalog)
        scan_list = build_scan_list(args, catalog)
    except (ValueError, OSError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    results = []
    interrupted = False
    try:
        for host in hosts:
            for port, proto in scan_list:
                results.append(scan_port(host, port, proto, args.timeout))
    except KeyboardInterrupt:
        interrupted = True
        print("\ninterrupted - showing partial results", file=sys.stderr)

    if args.service_detect:
        for r in results:
            if r["state"] in ("open", "open|filtered"):
                name = identify_service(catalog, r["port"], r["protocol"])
                r["service"] = name if name == "unknown" else f"{name} (possible)"
            else:
                r["service"] = "-"

    shown = results
    if args.only_open:
        shown = [r for r in results if r["state"] in ("open", "open|filtered")]

    print_table(shown, args.service_detect)

    if args.output:
        try:
            write_csv(shown, args.output, args.service_detect)
            print(f"\nsaved: {args.output}", file=sys.stderr)
        except OSError as e:
            print(f"error: could not write CSV: {e}", file=sys.stderr)
            return 1

    return 130 if interrupted else 0
