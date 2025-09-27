import yaml
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # repo root
MAPPING_PATH = BASE_DIR / "schema" / "mapping.yaml"

def load_mapping():
    """
    Load mapping.yaml. Nếu không tồn tại thì trả về rỗng.
    """
    if not MAPPING_PATH.exists():
        print(f"⚠️ mapping.yaml not found at {MAPPING_PATH}")
        return {"mappings": {}}
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def unflatten_dict(flat_dict):
    """
    Convert dict với key chấm (a.b.c) thành nested dict:
    {"a.b": 1, "a.c": 2} -> {"a": {"b": 1, "c": 2}}
    """
    result = {}
    for k, v in flat_dict.items():
        keys = k.split(".")
        d = result
        for subkey in keys[:-1]:
            d = d.setdefault(subkey, {})
        d[keys[-1]] = v
    return result

def convert(changeset, mapping=None):
    """
    Convert ChangeSet -> Helm values dựa trên mapping.yaml.
    """
    if mapping is None:
        mapping = load_mapping()

    flat_output = {}
    for ch in changeset.get("changes", []):
        svc = ch["service"]
        config = ch.get("config", {})

        if svc in mapping.get("mappings", {}):
            feature_map = mapping["mappings"][svc]
            for key, value in config.items():
                if key in feature_map:
                    helm_path = feature_map[key]
                    flat_output[helm_path] = value

    return unflatten_dict(flat_output)

def export_to_file(changeset, out_path="values.yaml"):
    values = convert(changeset)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(values, f, sort_keys=False)
    print(f"✅ Exported Helm values to {out_path}")

if __name__ == "__main__":
    # demo chạy trực tiếp
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: convert_to_helm.py changeset.json [output.yaml]")
        sys.exit(1)

    ch_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("values.yaml")

    import json
    with open(ch_path, "r", encoding="utf-8") as f:
        changeset = json.load(f)

    export_to_file(changeset, out_path)
    # đồng thời in ra màn hình để tiện debug
    with open(out_path, "r", encoding="utf-8") as f:
        print(f.read())
