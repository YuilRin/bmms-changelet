# src/convert_to_helm.py
import json, yaml, sys
from pathlib import Path

MAP_PATH = "../schema/mapping.yaml"

def load_mapping(p=MAP_PATH):
    return yaml.safe_load(open(p, 'r'))

def set_by_path(dct, path, value):
    # path like "order.replicas"
    keys = path.split('.')
    cur = dct
    for k in keys[:-1]:
        cur = cur.setdefault(k, {})
    cur[keys[-1]] = value

def convert(changeset, mapping):
    values = {}
    for ch in changeset.get('changes', []):
        svc = ch['service']
        cfg = ch.get('config') or {}
        if ch['action'] == 'scale' and 'replicas' in cfg:
            set_by_path(values, f"{svc}.replicas", cfg['replicas'])
        elif ch['action'] == 'enable':
            set_by_path(values, f"{svc}.enabled", True)
            # apply config keys if present
            for k, v in cfg.items():
                # if mapping exists
                mapped = mapping.get('mappings', {}).get(svc, {}).get(k)
                if mapped:
                    set_by_path(values, mapped, v)
                else:
                    set_by_path(values, f"{svc}.{k}", v)
        elif ch['action'] == 'update':
            for k, v in cfg.items():
                mapped = mapping.get('mappings', {}).get(svc, {}).get(k)
                if mapped:
                    set_by_path(values, mapped, v)
                else:
                    set_by_path(values, f"{svc}.{k}", v)
        elif ch['action'] == 'disable':
            set_by_path(values, f"{svc}.enabled", False)
        elif ch['action'] == 'delete':
            set_by_path(values, f"{svc}.delete", True)
    return values

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: convert_to_helm.py changeset.json")
        sys.exit(1)
    ch = json.load(open(sys.argv[1]))
    mapping = load_mapping()
    v = convert(ch, mapping)
    print(yaml.safe_dump(v, sort_keys=False))
