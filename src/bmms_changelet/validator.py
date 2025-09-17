# src/validator.py
import json
import yaml
import sys
from jsonschema import validate, Draft7Validator, ValidationError
from datetime import datetime

CATALOG_PATH = "../schema/service_catalogue.yaml"
SCHEMA_PATH = "../schema/changeset.schema.json"

# load catalogue
def load_catalogue(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_schema(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_service(catalogue, service_name):
    for s in catalogue.get('services', []):
        if s['id'] == service_name or s['name'] == service_name:
            return s
    return None

# basic policy settings
CLUSTER_QUOTA = {
    "cpu_m": 20000,  # 20 cores in millicores
    "memory_mib": 65536
}

# permission table
ROLE_PERMISSIONS = {
    "admin": ["enable", "disable", "scale", "update", "delete"],
    "ops": ["enable", "disable", "scale", "update"],
    "user": ["request"]
}

def validate_schema_instance(changeset, schema):
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(changeset), key=lambda e: e.path)
    if errors:
        return False, [f"{'/'.join(map(str,e.path))}: {e.message}" for e in errors]
    return True, []

def check_services_exist(changeset, catalogue):
    errs = []
    missing = []
    for ch in changeset.get('changes', []):
        svc = ch['service']
        if not find_service(catalogue, svc):
            missing.append(svc)
            errs.append(f"Service not found in catalogue: {svc}")
    return missing, errs

def check_permissions(changeset, role):
    errs = []
    for ch in changeset.get('changes', []):
        if ch['action'] not in ROLE_PERMISSIONS.get(role, []):
            errs.append(f"Role '{role}' cannot perform action '{ch['action']}' on service '{ch['service']}'")
    return errs

def check_dependencies(changeset, catalogue):
    # If enabling a service, ensure its dependencies are present/enabled.
    errs = []
    requires_human = False
    for ch in changeset.get('changes', []):
        if ch['action'] == 'enable':
            svc = find_service(catalogue, ch['service'])
            if svc:
                deps = svc.get('dependencies', [])
                for d in deps:
                    # In this prototype, we cannot inspect runtime enabled state; mark as 'requires_human'
                    errs.append(f"Dependency check: {ch['service']} depends on {d} (runtime check needed).")
                    requires_human = True
    return requires_human, errs

def enforce_risk_confidence(changeset):
    meta = changeset.get('metadata', {})
    confidence = meta.get('confidence', 0.0)
    risk = meta.get('risk', 'low')
    if risk in ('high', 'critical'):
        return "requires_human", [f"High risk operation (risk={risk}) requires human approval."]
    if confidence < 0.7:
        return "requires_human", [f"Low confidence ({confidence}) — human review recommended."]
    return "validated", []

def validate_changeset(changeset, catalogue, schema):
    result = {
        "status": "pending",
        "errors": [],
        "warnings": [],
        "actions": []
    }
    ok, schema_errors = validate_schema_instance(changeset, schema)
    if not ok:
        result['status'] = 'rejected'
        result['errors'].extend(schema_errors)
        return result

    missing, errs = check_services_exist(changeset, catalogue)
    if errs:
        result['errors'].extend(errs)
        result['status'] = 'rejected'
        return result

    ctx = changeset.get('request_context', {})
    role = ctx.get('role', 'user')
    perm_errs = check_permissions(changeset, role)
    if perm_errs:
        result['errors'].extend(perm_errs)
        result['status'] = 'rejected'
        return result

    dep_requires_human, dep_errs = check_dependencies(changeset, catalogue)
    if dep_errs:
        result['warnings'].extend(dep_errs)

    status_decision, rc_msgs = enforce_risk_confidence(changeset)
    result['warnings'].extend(rc_msgs)
    if status_decision == 'requires_human' or dep_requires_human:
        result['status'] = 'requires_human'
    else:
        result['status'] = 'validated'
    return result

if __name__ == "__main__":
    # usage: python validator.py path/to/changeset.json
    if len(sys.argv) < 2:
        print("Usage: validator.py changeset.json")
        sys.exit(1)
    ch_path = sys.argv[1]
    with open(ch_path, 'r', encoding='utf-8') as f:
        changeset = json.load(f)

    catalogue = load_catalogue("../schema/service_catalogue.yaml")
    schema = load_schema("../schema/changeset.schema.json")
    res = validate_changeset(changeset, catalogue, schema)
    print(json.dumps(res, indent=2))
