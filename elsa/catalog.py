import json
import os

DEFAULT_CATALOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "services.json"
)


def load_catalog(path=DEFAULT_CATALOG):
    """Read services.json and return {(port, protocol): name}."""
    with open(path) as f:
        entries = json.load(f)

    catalog = {}
    for entry in entries:
        key = (entry["port"], entry["protocol"])
        catalog[key] = entry["name"]
    return catalog


def identify_service(catalog, port, protocol):
    """Return the likely service name for a port, or 'unknown'."""
    return catalog.get((port, protocol), "unknown")
