# BMMS Changelet

This project provides a **ChangeSet schema + validator + converter pipeline** to normalize LLM outputs into actionable Kubernetes/Helm configurations.

## Features

- **Service Catalogue**  
  Defined in `schema/service_catalogue.yaml`, listing all available microservices, their dependencies, and allowed features.

- **ChangeSet Schema**  
  JSON Schema (`schema/changeset.schema.json`) ensures every ChangeSet follows a standardized structure.

- **Normalizer**  
  `normalize_input.py` converts raw LLM outputs (with `proposal_text` and `features`) into valid ChangeSets:
  - Adds `id`, `intent`, `timestamp`, `request_context`
  - Maps `features[]` into `changes[].config`
  - Service alias mapping (`product_catalog → catalogue`)

- **Validator**  
  `validator.py` enforces:
  - JSON schema compliance
  - Service existence in catalogue
  - Role-based permissions
  - Dependency checks
  - Risk & confidence thresholds

- **Converter**  
  `convert_to_helm.py` translates validated ChangeSets into `values.yaml` for Helm.

- **Testing & CI**  
  - Unit tests with `pytest` (`tests/`)
  - GitHub Actions workflow (`.github/workflows/ci.yml`)
  - Editable install (`setup.cfg`) with `src` layout

## Quickstart

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Normalize raw LLM output**
```bash
python src/bmms_changelet/normalize_input.py tests/llm_output/test1_raw.json tests/changesets/test1.json
```

3. **Validate ChangeSet**
```bash
python src/bmms_changelet/validator.py tests/changesets/test1.json
```

4. **Convert ChangeSet to Helm values**
```bash
python src/bmms_changelet/convert_to_helm.py tests/changesets/test1.json > values.yaml
```

5. **Run tests**
```bash
pytest -q
```

## Repo Structure

```plaintext
bmms-changelet/
├──schema/
│   ├──  service_catalogue.yaml
│   └── changeset.schema.json
├── src/bmms_changelet/
│   ├── __init__.py
│   ├── validator.py
│   ├── normalize_input.py
│   └── convert_to_helm.py
├── tests/
│   ├── test_normalize.py
│   ├── changesets/
│   ├── llm_output/
|   └── test_validator.py 
├── .github/workflows/
│   └──  ci.yml
├── requirements.txt
├── setup.cfg
├── pyproject.toml
├── .github/workflows/ci.yml    
└── README.md
```
