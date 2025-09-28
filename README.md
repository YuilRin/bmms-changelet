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

nó sẽ tạo ra value.yaml tạo thư mục gốc

5. **Run tests**
```bash
pytest -q
```


## Test trên Django

1. **Kiểm tra đã có virtual environment chưa**

Trong thư mục project (bmms-changelet) thường sẽ có thư mục venv hoặc .venv. Nếu chưa có thì tạo mới:

```bash
python -m venv venv
```

Rồi kích hoạt môi trường ảo:
```bash
.\venv\Scripts\activate
```
2. **Cài Django và dependencies**

Cài luôn tất cả thư viện:

```bash
pip install -r requirements.txt
```

3. **Chạy migration và server**

```bash
python manage.py migrate
python manage.py runserver
```
## Dry-run & Apply

Dry-run
```bash
helm upgrade --install demo ./charts/demo -f values.yaml --namespace tenant-demo --dry-run
```

Apply thật
```bash
helm upgrade --install demo ./charts/demo -f values.yaml --namespace tenant-demo
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
