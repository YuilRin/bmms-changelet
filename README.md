# 🧩 BMMS ChangeSet Toolkit

[![CI](https://github.com/your-username/bmms-changelet/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/bmms-changelet/actions)

Toolkit hỗ trợ **chuẩn hóa ChangeSet / service catalogue** cho hệ thống microservices.  
Bao gồm:
- JSON Schema cho ChangeSet
- Service Catalogue (YAML)
- Validator (schema + dependency + risk check)
- Converter ChangeSet → Helm values
- Bộ test & CI/CD

---

## 📂 Cấu trúc repo

bmms-changelet/
├── src/
│ └── bmms_changelet/
│ ├── init.py
│ ├── validator.py # Validator chính
│ └── convert_to_helm.py # Converter sang Helm values
├── schema/
│ ├── changeset.schema.json # JSON Schema cho ChangeSet
│ ├── service_catalogue.yaml # Service catalogue
│ └── mapping.yaml # Mapping feature → helm path
├── tests/
│ └── test_validator.py # Unit tests
├── requirements.txt
├── setup.cfg
├── pyproject.toml
├── .github/workflows/ci.yml # CI pipeline
└── README.md

---

## 🚀 Cài đặt

Yêu cầu Python ≥ 3.9.

```bash
git clone https://github.com/your-username/bmms-changelet.git
cd bmms-changelet

# Cài dependency
pip install -r requirements.txt

# Cài package ở chế độ editable
pip install -e .

✅ Chạy test
```bash
pytest -q

Nếu thành công:
```bash
.                                                                   [100%]
1 passed in 0.11s