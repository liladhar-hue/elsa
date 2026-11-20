# elsa

A lightweight Python CLI for OT / ICS / IoT service inventory in **authorized lab environments**.
It checks which common industrial ports are reachable and shows the service usually
associated with each port.

> **Authorized use only.** Run elsa only against systems you own or have explicit written
> permission to test. In OT environments, even simple connection attempts can disturb
> fragile devices, so use an isolated lab and agree on a scan window with the system owner.

## Install

    git clone https://github.com/liladhar-hue/elsa.git
    cd elsa
    pipx install .

Requires Python 3.8+ and has no third-party dependencies.

## Usage

    elsa -t 172.16.1.10 -sV                      # scan the OT catalog ports
    elsa -t 172.16.1.10 -p 102,502,47808 -sV     # specific ports
    elsa -t 10.0.0.5 -p 1-1024 --proto both      # port range, TCP and UDP
    elsa -f examples/targets.txt -sV -o out.csv  # targets from a file, CSV export

| Option | Meaning |
|---|---|
| `-t, --target` | IPv4 address(es), comma-separated |
| `-f, --file` | File with one IPv4 address per line (`#` comments allowed) |
| `-p, --ports` | Ports and ranges, e.g. `102,502,1000-1010` (default: catalog ports) |
| `--proto` | `tcp`, `udp` or `both` |
| `-sV` | Add a port-based service guess from the catalog |
| `--timeout` | Seconds to wait per port (default 2) |
| `--catalog` | Use your own services JSON file |
| `-o, --output` | Write results to a CSV file |
| `--open` | Show only open / open\|filtered results |

## Port states

- **open**: connection (TCP) or reply (UDP) received
- **closed**: host actively refused
- **filtered**: no reply to a TCP attempt
- **open|filtered**: UDP got no reply, so it cannot be told apart

## Limitations

- `-sV` is a **port-based guess** from `elsa/data/services.json`. An open port 502 does not
  prove Modbus is running, and services can run on non-standard ports.
- UDP results are inconclusive by nature.
- Scanning is sequential and IPv4 only.

## Custom catalog

Edit `elsa/data/services.json` or pass `--catalog`. Each entry:

    {"name": "Modbus TCP", "port": 502, "protocol": "tcp"}

## License

MIT
