import json
import yaml
import sys
from pathlib import Path
from jsonschema import Draft7Validator

# ------------------------------
# Định nghĩa path tuyệt đối từ repo root
# ------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]  # repo root
CATALOG_PATH = BASE_DIR / "schema" / "service_catalogue.yaml"
SCHEMA_PATH = BASE_DIR / "schema" / "changeset.schema.json"

# ------------------------------
# Loaders
# ------------------------------
def load_catalogue(path=CATALOG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_schema(path=SCHEMA_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_service(catalogue, service_name):
    for s in catalogue.get("services", []):
        if s["id"] == service_name or s["name"] == service_name:
            return s
    return None

# ------------------------------
# Policy configs
# ------------------------------
CLUSTER_QUOTA = {
    "cpu_m": 20000,  # 20 cores (millicores)
    "memory_mib": 65536,  # 64 GiB
}

ROLE_PERMISSIONS = {
    "admin": ["enable", "disable", "scale", "update", "delete"],
    "ops": ["enable", "disable", "scale", "update"],
    "user": ["request"],
}

# ------------------------------
# Validation helpers
# ------------------------------
def validate_schema_instance(changeset, schema):
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(changeset), key=lambda e: e.path)
    if errors:
        return False, [f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors]
    return True, []

def check_services_exist(changeset, catalogue):
    errs = []
    for ch in changeset.get("changes", []):
        svc = ch["service"]
        if not find_service(catalogue, svc):
            errs.append(f"Service not found in catalogue: {svc}")
    return errs

def check_permissions(changeset, role):
    errs = []
    for ch in changeset.get("changes", []):
        if ch["action"] not in ROLE_PERMISSIONS.get(role, []):
            errs.append(
                f"Role '{role}' cannot perform action '{ch['action']}' on service '{ch['service']}'"
            )
    return errs

def check_dependencies(changeset, catalogue):
    errs = []
    requires_human = False
    for ch in changeset.get("changes", []):
        if ch["action"] == "enable":
            svc = find_service(catalogue, ch["service"])
            if svc:
                deps = svc.get("dependencies", [])
                for d in deps:
                    errs.append(
                        f"Dependency check: {ch['service']} depends on {d} (runtime check needed)."
                    )
                    requires_human = True
    return requires_human, errs

def enforce_risk_confidence(changeset):
    meta = changeset.get("metadata", {})
    confidence = meta.get("confidence", 0.0)
    risk = meta.get("risk", "low")

    if risk in ("high", "critical"):
        return "requires_human", [
            f"High risk operation (risk={risk}) requires human approval."
        ]
    if confidence < 0.7:
        return "requires_human", [
            f"Low confidence ({confidence}) — human review recommended."
        ]
    return "validated", []

# ------------------------------
# Main validator
# ------------------------------
def validate_changeset(changeset, catalogue, schema):
    result = {
        "status": "pending",
        "errors": [],
        "warnings": [],
    }

    # 1) Schema validation
    ok, schema_errors = validate_schema_instance(changeset, schema)
    if not ok:
        result["status"] = "rejected"
        result["errors"].extend(schema_errors)
        return result

    # 2) Service existence check
    svc_errs = check_services_exist(changeset, catalogue)
    if svc_errs:
        result["status"] = "rejected"
        result["errors"].extend(svc_errs)
        return result

    # 3) Role permission check
    ctx = changeset.get("request_context", {})
    role = ctx.get("role", "user")
    perm_errs = check_permissions(changeset, role)
    if perm_errs:
        result["status"] = "rejected"
        result["errors"].extend(perm_errs)
        return result

    # 4) Dependency check
    dep_requires_human, dep_errs = check_dependencies(changeset, catalogue)
    if dep_errs:
        result["warnings"].extend(dep_errs)

    # 5) Risk & confidence policy
    status_decision, rc_msgs = enforce_risk_confidence(changeset)
    result["warnings"].extend(rc_msgs)

    # Final status
    if status_decision == "requires_human" or dep_requires_human:
        result["status"] = "requires_human"
    else:
        result["status"] = "validated"

    return result

# ------------------------------
# CLI entrypoint
# ------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py path/to/changeset.json")
        sys.exit(1)

    ch_path = Path(sys.argv[1])
    if not ch_path.exists():
        print(f"Error: changeset file not found: {ch_path}")
        sys.exit(1)

    with open(ch_path, "r", encoding="utf-8") as f:
        changeset = json.load(f)

    catalogue = load_catalogue()
    schema = load_schema()

    res = validate_changeset(changeset, catalogue, schema)
    print(json.dumps(res, indent=2))
