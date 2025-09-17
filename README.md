# 📘 BMMS ChangeSet Toolkit

[![CI](https://github.com/your-username/bmms-changelet/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/bmms-changelet/actions)  
Toolkit for **standardizing ChangeSets & Service Catalogue** in **microservices systems**.  

---

## ✨ Features
- ✅ JSON Schema for **ChangeSet**  
- ✅ Service Catalogue (**YAML**)  
- ✅ Validator (schema + dependency + risk check)  
- ✅ Converter **ChangeSet → Helm values**  
- ✅ Test suite & CI/CD pipeline  

---

## 📂 Repository Structure
```plaintext
bmms-changelet/
├── src/bmms_changelet/
│   ├── __init__.py
│   ├── validator.py         # Main Validator
│   └── convert_to_helm.py   # Converter to Helm values
│
├── schema/
│   ├── changeset.schema.json   # JSON Schema for ChangeSet
│   ├── service_catalogue.yaml  # Service catalogue
│   └── mapping.yaml            # Mapping feature → helm path
│
├── tests/
│   └── test_validator.py       # Unit tests
│
├── requirements.txt
├── setup.cfg
├── pyproject.toml
├── .github/workflows/ci.yml    # CI pipeline
└── README.md


## 🚀 Installation
Requirement: **Python ≥ 3.9**

```bash
# Clone repo
git clone https://github.com/your-username/bmms-changelet.git
cd bmms-changelet

# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

## ✅ Run Tests
```bash
pytest -q
```
If successful, you should see:
```bash
.                                                                   [100%]
1 passed in 0.11s
```

