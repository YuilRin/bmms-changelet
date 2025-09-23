import yaml
from pathlib import Path

# trỏ lên repo root
BASE_DIR = Path(__file__).resolve().parents[2]
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


if __name__ == "__main__":
    # demo chạy trực tiếp
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python convert_to_helm.py path/to/changeset.json")
        sys.exit(1)

    ch_path = Path(sys.argv[1])
    with open(ch_path, "r", encoding="utf-8") as f:
        changeset = json.load(f)

    mapping = load_mapping()
    result = convert(changeset, mapping)

    print("YAML output:")
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
