import csv


def print_table(results, show_service):
    header = f"{'HOST':<16}{'PORT':<8}{'PROTO':<7}{'STATE':<15}"
    if show_service:
        header += "SERVICE (port-based guess)"
    print(header)
    print("-" * max(len(header), 50))
    for r in results:
        line = f"{r['host']:<16}{r['port']:<8}{r['protocol']:<7}{r['state']:<15}"
        if show_service:
            line += r.get("service", "-")
        print(line)


def write_csv(results, path, show_service):
    fields = ["host", "port", "protocol", "state"]
    if show_service:
        fields.append("service")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
