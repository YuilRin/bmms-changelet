import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Map tên dịch vụ mà LLM hay sinh ra → tên chuẩn trong service_catalogue.yaml
SERVICE_ALIAS = {
    "product_catalog": "catalogue",
    "customer_service": "customer",
    "payment_service": "payment",
    "billing_service": "billing",
    "order_service": "order",
    "inventory_service": "inventory",
    "subscription_service": "subscription",
    "promotion_service": "promotion"
}

def normalize(input_json):
    """
    Convert từ LLM JSON (proposal_text + changeset.features)
    → ChangeSet chuẩn theo schema.
    """
    # Base fields
    proposal_text = input_json.get("proposal_text", "")
    changeset_raw = input_json.get("changeset", {})
    metadata = input_json.get("metadata", {})

    # Sinh id + timestamp (timezone-aware, tránh cảnh báo deprecated)
    changeset_id = "chg-auto-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    timestamp = datetime.now(timezone.utc).isoformat()

    # Lấy model/service và chuẩn hóa bằng alias
    service_raw = changeset_raw.get("model", "unknown_service")
    service = SERVICE_ALIAS.get(service_raw, service_raw)

    # Build config từ features
    config = {}
    for feat in changeset_raw.get("features", []):
        key = feat.get("key")
        val = feat.get("value")
        if key:
            config[key] = val

    # Xác định action (tạm map theo intent)
    intent = metadata.get("intent", "update_config")
    if intent.startswith("change") or intent.startswith("update"):
        action = "update"
    elif intent.startswith("enable"):
        action = "enable"
    elif intent.startswith("disable"):
        action = "disable"
    elif intent.startswith("scale"):
        action = "scale"
    else:
        action = "update"

    # Build ChangeSet chuẩn
    normalized = {
        "id": changeset_id,
        "intent": intent,
        "timestamp": timestamp,
        "request_context": {
            "tenant_id": "tenant-demo",
            "requested_by": "llm",
            "role": "admin"
        },
        "changes": [
            {
                "action": action,
                "service": service,
                "config": config
            }
        ],
        "impacted_services": changeset_raw.get("impacted_services", []),
        "metadata": {
            "intent_type": intent,
            "confidence": metadata.get("confidence", 0.8),
            "risk": metadata.get("risk", "low"),
            "source": "llm",
            "validator_status": "pending",
            "notes": proposal_text
        }
    }
    return normalized

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python normalize_input.py raw.json normalized.json")
        sys.exit(1)

    raw_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_json = json.load(f)

    normalized = normalize(raw_json)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)

    print(f"✅ Normalized ChangeSet written to {out_path}")
