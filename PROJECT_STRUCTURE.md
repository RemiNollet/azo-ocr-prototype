# 📂 Structure du Projet - AZO OCR Prototype

## Vue d'ensemble

```
azo-ocr-prototype/
├── 📋 FICHIERS DE CONFIGURATION
│   ├── pytest.ini                  # Configuration pytest
│   ├── requirements.txt            # Dépendances Python
│   ├── .env                        # Variables d'environnement
│   └── .gitignore
│
├── 📚 DOCUMENTATION
│   ├── README.md                   # Guide démarrage + API
│   ├── ARCHITECTURE.md             # Design du système
│   ├── KPI.md                      # Documentation KPI (NOUVEAU)
│   ├── IMPLEMENTATION_SUMMARY.md   # Résumé implémentation (NOUVEAU)
│   ├── TESTS_KPI_SUMMARY.md        # Résumé tests & KPI (NOUVEAU)
│   ├── CHANGELOG_TESTS_KPI.md      # Changelog détaillé (NOUVEAU)
│   └── USEFUL_COMMANDS.sh          # Commandes utiles (NOUVEAU)
│
├── 🔧 SCRIPTS
│   ├── run_tests.sh                # Script tests (NOUVEAU)
│   └── analyze_kpi.py              # Analyse KPI (NOUVEAU)
│
├── 📁 app/ - CODE APPLICATION
│   ├── __init__.py
│   │
│   ├── main.py                     # FastAPI app + démarrage
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Configuration (OPENAI_API_KEY, modèles)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── constants.py            # MathValidationError, MONTANT_TOLERANCE
│   │   ├── schemas.py              # Pydantic models (InvoiceData, LigneDetail)
│   │   └── validation.py           # Validation helper functions
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py           # Client OpenAI (gpt-4o, gpt-4o-mini)
│   │   ├── normalization.py        # Nettoyage/normalisation données
│   │   └── ocr_pipeline.py         # Orchestration (cascading/fallback)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py               # Endpoints : /health, /api/v1/extract, /api/v1/kpi
│   │
│   ├── monitoring/                 # NOUVEAU - Module KPI
│   │   ├── __init__.py
│   │   └── kpi.py                  # KPITracker, ExtractionKPI, get_kpi_stats()
│   │
│   └── prompt/
│       ├── prompt_v1.txt           # Prompt système pour LLM
│       └── prompt_v2.txt           # Version alternative
│
├── 📁 test/ - TESTS
│   ├── __init__.py
│   │
│   ├── conftest.py                 # Fixtures pytest (NOUVEAU)
│   │   ├── settings
│   │   ├── sample_invoice_data
│   │   ├── sample_invoice_zero_tva
│   │   ├── sample_invoice_invalid_math
│   │   ├── mock_llm_response_valid
│   │   ├── mock_llm_response_invalid_json
│   │   ├── mock_openai_client
│   │   └── test_image_base64
│   │
│   ├── test_normalization.py       # Tests normalization (12 tests) (NOUVEAU)
│   ├── test_validation.py          # Tests validation (10 tests) (NOUVEAU)
│   ├── test_llm_client.py          # Tests LLM client (5 tests) (NOUVEAU)
│   ├── test_ocr_pipeline.py        # Tests pipeline (7 tests) (NOUVEAU)
│   ├── test_routes.py              # Tests API (5 tests) (NOUVEAU)
│   ├── test_pipeline.py            # Integration test (existant)
│   ├── README.md                   # Documentation tests (NOUVEAU)
│   └── __init__.py
│
├── 📁 sample_invoices/ - DONNÉES DE TEST
│   └── facture_exemple.txt
│
├── 📁 resultats/ - RÉSULTATS & MÉTRIQUES
│   ├── extractions.csv             # Données extraites
│   ├── kpi.jsonl                   # KPI individuelles (NOUVEAU)
│   └── kpi_analysis.csv            # Export analyse (NOUVEAU)
│
└── 📁 .cursor/
    └── rules/ ...                  # Règles IDE (optionnel)
```

## Statistiques

### Code Application
```
app/main.py                 : 51 lignes    (FastAPI setup)
app/core/config.py          : ~30 lignes   (Settings)
app/models/schemas.py       : ~80 lignes   (Pydantic models)
app/services/llm_client.py  : 150 lignes   (OpenAI client)
app/services/ocr_pipeline.py: 130 lignes   (Orchestration)
app/services/normalization.py: ~50 lignes  (Nettoyage)
app/api/routes.py           : ~150 lignes  (Endpoints)
app/monitoring/kpi.py       : 250 lignes   (KPI tracking) ✨ NOUVEAU
──────────────────────────────────────────
TOTAL                       : ~890 lignes
```

### Tests & Fixtures
```
test/conftest.py            : 150 lignes   (15+ fixtures) ✨ NOUVEAU
test/test_normalization.py  : 100 lignes   (12 tests) ✨ NOUVEAU
test/test_validation.py     : 110 lignes   (10 tests) ✨ NOUVEAU
test/test_llm_client.py     : 85 lignes    (5 tests) ✨ NOUVEAU
test/test_ocr_pipeline.py   : 95 lignes    (7 tests) ✨ NOUVEAU
test/test_routes.py         : 85 lignes    (5 tests) ✨ NOUVEAU
test/test_pipeline.py       : 70 lignes    (existant)
──────────────────────────────────────────
TOTAL TESTS                 : 39 tests
TOTAL LIGNES                : 695 lignes
```

### Documentation
```
README.md                   : 300+ lignes  (Guide principal)
ARCHITECTURE.md             : 200+ lignes  (Design système)
KPI.md                      : 350+ lignes  (Monitoring) ✨ NOUVEAU
IMPLEMENTATION_SUMMARY.md   : 300+ lignes  (Résumé) ✨ NOUVEAU
TESTS_KPI_SUMMARY.md        : 250+ lignes  (Résumé exécutif) ✨ NOUVEAU
CHANGELOG_TESTS_KPI.md      : 250+ lignes  (Détail changements) ✨ NOUVEAU
test/README.md              : 250+ lignes  (Guide tests) ✨ NOUVEAU
USEFUL_COMMANDS.sh          : 150+ lignes  (Commandes) ✨ NOUVEAU
──────────────────────────────────────────
TOTAL DOCUMENTATION         : 2000+ lignes
```

## Points d'Entrée

### Application
- **Main** : `app/main.py:app` → FastAPI application
- **Server** : `uvicorn app.main:app --reload`
- **Docs** : http://127.0.0.1:8000/docs (Swagger)

### Tests
- **Tous** : `pytest test/ -v`
- **Unitaires** : `pytest test/ -v -m unit`
- **Intégration** : `pytest test/ -v -m integration`
- **Couverture** : `pytest test/ --cov=app --cov-report=html`

### KPI & Analyse
- **API** : `GET http://127.0.0.1:8000/api/v1/kpi`
- **Script** : `python analyze_kpi.py`
- **Données** : `resultats/kpi.jsonl` (JSONL)

## Flux de Données

### Extraction
```
1. POST /api/v1/extract (fichier)
   ↓
2. routes.extract()
   └→ kpi_tracker.start_extraction()
   ↓
3. run_extraction_pipeline(image_base64)
   ├→ kpi_tracker.record_llm_call(model)
   ├→ extract_invoice_from_image() # Appel OpenAI
   ├→ Validation Pydantic
   └→ Cascading/Fallback (si erreur)
   ↓
4. kpi_tracker.end_extraction()
   └→ Sauvegarde KPI dans resultats/kpi.jsonl
   ↓
5. Sauvegarde résultats dans resultats/extractions.csv
   ↓
6. Response : {data, needs_human_review, error_message}
```

### KPI
```
1. run_extraction_pipeline()
   └→ kpi_tracker.record_llm_call(model)  # À chaque appel
   ↓
2. routes.extract()
   └→ kpi.end_extraction(...)
   ↓
3. kpi_tracker._write_kpi(kpi)
   └→ Stockage JSONL dans resultats/kpi.jsonl
   ↓
4. GET /api/v1/kpi
   └→ get_kpi_stats()
      └→ Lecture + agrégation kpi.jsonl
      └→ Return statistiques JSON
```

## Intégrations Clés

### OpenAI
- **Client** : `app/services/llm_client.py`
- **Models** : `gpt-4o-mini` (light), `gpt-4o` (heavy)
- **Mocking** : `test/conftest.py` - `mock_llm_response_*`

### FastAPI
- **Framework** : FastAPI 0.115+
- **Routes** : `app/api/routes.py`
- **Testing** : FastAPI TestClient (test/test_routes.py)

### Pydantic
- **Models** : `app/models/schemas.py` - InvoiceData, LigneDetail
- **Validation** : @model_validator, field validators
- **Testing** : `test/test_validation.py`

### Pytest
- **Framework** : pytest 7.0+
- **Fixtures** : `test/conftest.py`
- **Plugins** : pytest-cov, pytest-mock
- **Config** : `pytest.ini`

## Dépendances Principales

### Production
- fastapi >= 0.115.0
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- openai >= 1.0.0
- python-multipart >= 0.0.9
- pdf2image >= 1.17.0
- pillow >= 10.0.0
- uvicorn[standard] >= 0.30.0

### Test
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- pytest-mock >= 3.10.0
- httpx >= 0.24.0
- requests >= 2.28.0

## Fichiers Clés à Connaître

| Fichier | Responsabilité | Modifier si... |
|---------|----------------|---------------|
| `app/main.py` | FastAPI setup | Ajouter middleware, événements |
| `app/api/routes.py` | Endpoints HTTP | Ajouter/modifier endpoints |
| `app/services/ocr_pipeline.py` | Logique métier | Changer pipeline, modèles, fallback |
| `app/services/llm_client.py` | Appels OpenAI | Modifier prompts, API OpenAI |
| `app/monitoring/kpi.py` | Suivi KPI | Ajouter nouvelles métriques |
| `test/conftest.py` | Fixtures test | Ajouter données/mocks |
| `test/test_*.py` | Tests | Ajouter cas de test |
| `.env` | Configuration | Changer clé API, modèles |

## Checklist Onboarding

- [ ] Lire `README.md` (guide démarrage)
- [ ] Lire `ARCHITECTURE.md` (design système)
- [ ] Lancer `uvicorn app.main:app --reload`
- [ ] Visiter http://127.0.0.1:8000/docs
- [ ] Lancer `pytest test/ -v` pour vérifier tests
- [ ] Lancer `python analyze_kpi.py` après extraction
- [ ] Consulter endpoint `GET /api/v1/kpi`
- [ ] Lire `test/README.md` pour ajouter tests
- [ ] Lire `KPI.md` pour comprendre monitoring

---

**Dernier mise à jour** : Février 2025  
**Version** : v2.0 (Tests & KPI Implementation)  
**Status** : ✅ Production-ready
