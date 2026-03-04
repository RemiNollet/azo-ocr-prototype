# Tests - Documentation

Ce document explique la structure des tests et les bonnes pratiques mises en place.

## Structure des tests

```
test/
├── conftest.py                 # Fixtures pytest partagées
├── test_normalization.py       # Tests du module normalization
├── test_validation.py          # Tests du module validation et schemas
├── test_llm_client.py          # Tests du client OpenAI
├── test_ocr_pipeline.py        # Tests du pipeline d'orchestration
├── test_routes.py              # Tests d'intégration des endpoints
└── __init__.py
```

## Fixtures (conftest.py)

Les fixtures fournissent des données et des mocks réutilisables :

### Données

- **`settings`** : Configuration par défaut pour les tests
- **`sample_invoice_data`** : Facture valide d'exemple
- **`sample_invoice_zero_tva`** : Facture avec TVA=0 (cas assurance)
- **`sample_invoice_invalid_math`** : Facture avec HT+TVA != TTC
- **`test_image_base64`** : Image PNG encodée en base64

### Mocks

- **`mock_llm_response_valid`** : Réponse OpenAI valide
- **`mock_llm_response_invalid_json`** : Réponse avec JSON invalide
- **`mock_openai_client`** : Client OpenAI mocké
- **`temp_csv_file`** : Fichier CSV temporaire

## Catégories de tests

### Tests unitaires (`@pytest.mark.unit`)

Testent une fonction/classe en isolation, sans dépendances externes :

- **`test_normalization.py`**
  - Nettoyage montants (symboles, format français)
  - Conversion string → float
  - Normalisation dates

- **`test_validation.py`**
  - Validation Pydantic (champs obligatoires, types)
  - Règle métier : HT + TVA == TTC
  - Cas spécial : TVA = 0
  - Score confiance (0-1)

- **`test_llm_client.py`**
  - Nettoyage JSON (suppression markdown, etc.)
  - Extraction facture depuis image
  - Gestion erreurs JSON

- **`test_ocr_pipeline.py`**
  - Succès à 1ère tentative
  - Retry et fallback
  - Tous les modèles échouent
  - TVA = 0 déclenche review

### Tests d'intégration (`@pytest.mark.integration`)

Testent plusieurs composants ensemble (avec TestClient FastAPI) :

- **`test_routes.py`**
  - Endpoint `/health`
  - Endpoint `/api/v1/extract` avec PDF valide
  - Rejection type fichier invalide
  - Extraction avec revue manuelle requise

## Bonnes pratiques appliquées

### 1. Utilisation des fixtures

```python
def test_example(sample_invoice_data):
    # On réutilise la fixture au lieu de créer les données
    assert sample_invoice_data.fournisseur == "Entreprise Test SARL"
```

### 2. Tests paramétrés

```python
@pytest.mark.parametrize("input,expected", [
    ("100 XOF", "100"),
    ("1.000,50", "1000.50"),
])
def test_clean_amount_string(input, expected):
    assert clean_amount_string(input) == expected
```

### 3. Mocking des dépendances externes

```python
@patch('app.services.llm_client.OpenAI')
def test_extraction(mock_openai_class, mock_llm_response_valid):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.return_value = mock_llm_response_valid
    # Teste sans appeler OpenAI réellement
```

### 4. Organisation des tests par classe

```python
class TestCleanAmountString:
    """Tests pour la fonction clean_amount_string()."""
    
    def test_basic_amount(self):
        pass
    
    def test_french_format(self):
        pass
```

### 5. Noms explicites

- **Test** : `test_extraction_with_valid_pdf` (clair ce qu'on teste)
- **Assertion** : `assert result.data == sample_invoice_data` (compare ce qui importe)

### 6. Docstrings pour chaque test

```python
def test_zero_tva_accepted(self, sample_invoice_zero_tva):
    """Test que TVA=0 est acceptée (cas assurance/notaire)."""
```

## Exécution des tests

### Tous les tests

```bash
pytest test/ -v
```

### Seulement les tests unitaires

```bash
pytest test/ -v -m unit
```

### Seulement les tests d'intégration

```bash
pytest test/ -v -m integration
```

### Tests d'un fichier spécifique

```bash
pytest test/test_validation.py -v
```

### Tests d'une classe spécifique

```bash
pytest test/test_normalization.py::TestCleanAmountString -v
```

### Tests avec couverture de code

```bash
pytest test/ --cov=app --cov-report=term-missing --cov-report=html
```

La couverture détaillée est générée dans `htmlcov/index.html`.

## Markers disponibles

- `@pytest.mark.unit` : Test unitaire
- `@pytest.mark.integration` : Test d'intégration
- `@pytest.mark.slow` : Test lent
- `@pytest.mark.mock_llm` : Test mocké pour OpenAI

Exemple : `pytest test/ -v -m "unit and not slow"`

## Configuration pytest

Le fichier `pytest.ini` contient la configuration :

```ini
[pytest]
testpaths = test
python_files = test_*.py conftest.py
addopts = -v --strict-markers --tb=short
markers = unit, integration, slow, mock_llm
```

## Améliorations futures

- Ajouter des tests de performance (temps < 5s par extraction)
- Tester les cas limites (fichiers très volumineux, formats rares)
- Augmenter la couverture à > 85%
- Ajouter des fixtures pytest-asyncio pour les tests asynchrones
- Intégrer dans CI/CD (GitHub Actions, GitLab CI)
