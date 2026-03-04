# AZO OCR Prototype

Microservice d'extraction de données factures de la zone OHADA (PDF ou images) utilisant un Vision-Language Model.

## Démarrage rapide

### Prérequis

- **Python 3.9+**
- **Clé API OpenAI** (https://platform.openai.com/api-keys)
- **Poppler** (pour la conversion PDF→image)
  - **macOS** : `brew install poppler`
  - **Ubuntu/Debian** : `apt install poppler-utils`
  - **Windows** : https://github.com/oschwartz10612/poppler-windows/releases

### Installation

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la clé API
echo "OPENAI_API_KEY=sk-..." > .env
```

### Lancer le serveur

```bash
uvicorn app.main:app --reload
```

Le serveur est accessible sur **http://127.0.0.1:8000**.

## Documentation API

- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

## Endpoints

### `GET /health`

Vérifie que le service répond.

```bash
curl http://127.0.0.1:8000/health
```

**Réponse** :
```json
{"status": "ok"}
```

### `POST /api/v1/extract`

Extrait les données d'une facture (image ou PDF, première page).

**Paramètres** :
- `file` (UploadFile) : Image JPEG/PNG/WebP/GIF ou PDF

**Réponse** :
```json
{
  "data": {
    "fournisseur": "Entreprise XYZ",
    "numero_facture": "F-2025-001",
    "date": "2025-02-23",
    "montant_ht": 1000.00,
    "montant_tva": 200.00,
    "montant_ttc": 1200.00,
    "devise": "XAF",
    "lignes_detail": [
      {
        "description": "Service consulting",
        "quantite": 10,
        "prix_unitaire": 100.00
      }
    ]
  },
  "needs_human_review": false,
  "error_message": null
}
```

**Exemple avec curl** :
```bash
curl -X POST -F "file=@facture.pdf" http://127.0.0.1:8000/api/v1/extract
```

### `GET /api/v1/kpi`

Récupère les statistiques KPI agrégées : taux succès, latence moyenne, temps de traitement, etc.

**Réponse** :
```json
{
  "total_extractions": 25,
  "success_rate": 96.0,
  "failed_count": 1,
  "human_review_count": 3,
  "review_rate": 12.0,
  "avg_duration_ms": 4250.50,
  "min_duration_ms": 3100.0,
  "max_duration_ms": 6200.0
}
```

**Exemple curl** :
```bash
curl http://127.0.0.1:8000/api/v1/kpi
```

## Architecture

Voir [ARCHITECTURE.md](ARCHITECTURE.md) pour les détails sur l'architecture du système.

## Configuration

Les paramètres sont chargés depuis le fichier `.env` :

```env
# Obligatoire
OPENAI_API_KEY=sk-...

# Optionnel (valeurs par défaut)
LLM_MODEL_LIGHT=gpt-4o-mini      # Premier essai (économique)
LLM_MODEL_HEAVY=gpt-4o            # Fallback (plus puissant)
```

## Dépendances

- **fastapi** : Framework web
- **pydantic** : Validation de schémas
- **openai** : Client OpenAI
- **pdf2image** : Conversion PDF → image
- **pillow** : Manipulation d'images

Voir `requirements.txt` pour les versions exactes.

## Tester le prototype

### Tester via Swagger UI (recommandé)

```bash
# Le serveur doit être lancé
uvicorn app.main:app --reload

# Ouvrir l'interface Swagger
open http://127.0.0.1:8000/docs
```

Puis :
1. Cliquer sur **POST /api/v1/extract**
2. Cliquer **"Try it out"**
3. Upload une facture (PDF ou image)
4. Les résultats sont sauvegardés automatiquement dans `resultats/extractions.csv`

### Tester via curl

```bash
curl -X POST -F "file=@/chemin/vers/facture.pdf" \
  http://127.0.0.1:8000/api/v1/extract | jq
```

### Tester le pipeline complet

Le script `test/test_pipeline.py` teste automatiquement toutes les factures du dossier `sample_invoices/` :

```bash
# 1. Ajouter des factures dans le dossier
cp /chemin/vers/vos/factures/*.pdf sample_invoices/

# 2. Lancer le serveur (dans un terminal séparé)
uvicorn app.main:app --reload

# 3. Lancer le script de test (dans un autre terminal)
cd /chemin/vers/azo-ocr-prototype
python test/test_pipeline.py
```

Les résultats seront sauvegardés dans **`resultats/extractions.csv`** avec les colonnes :
- `timestamp` : moment du traitement
- `fichier_source` : nom du fichier
- `statut` : succès ou erreur
- `needs_human_review` : True si revue manuelle nécessaire
- `fournisseur`, `numero_facture`, `date`, montants, devise, etc.
- `error_message` : message d'erreur si applicable

### Tests unitaires et d'intégration

Les tests suivent les bonnes pratiques avec **pytest**, des **fixtures** et des **mocks** :

```bash
# Installer les dépendances de test (déjà dans requirements.txt)
pip install -r requirements.txt

# Lancer tous les tests
pytest test/ -v

# Lancer uniquement les tests unitaires
pytest test/ -v -m unit

# Lancer uniquement les tests d'intégration
pytest test/ -v -m integration

# Lancer les tests avec couverture de code
pytest test/ --cov=app --cov-report=html

# Lancer via le script fourni
bash run_tests.sh
```

**Structure des tests** :
- **`test/conftest.py`** : Fixtures partagées (factures d'exemple, mocks OpenAI, etc.)
- **`test/test_normalization.py`** : Tests des fonctions de nettoyage/normalisation
- **`test/test_validation.py`** : Tests de validation Pydantic et logique métier OHADA
- **`test/test_llm_client.py`** : Tests du client OpenAI (mocking des appels API)
- **`test/test_ocr_pipeline.py`** : Tests du pipeline de cascading/fallback
- **`test/test_routes.py`** : Tests d'intégration des endpoints FastAPI

### Suivi des KPI (Business Intelligence)

L'API expose un endpoint `/api/v1/kpi` pour consulter les métriques business :

```bash
# Récupérer les statistiques
curl http://127.0.0.1:8000/api/v1/kpi | jq

# Résultat exemple :
{
  "total_extractions": 25,
  "success_rate": 96.0,
  "failed_count": 1,
  "human_review_count": 3,
  "review_rate": 12.0,
  "avg_duration_ms": 4250.50,      # Latence moyenne
  "min_duration_ms": 3100.0,       # Latence minimale
  "max_duration_ms": 6200.0        # Latence maximale
}
```

**Fichier de données KPI** : `resultats/kpi.jsonl`
- Format JSONL (une métrique par ligne)
- Contient : timestamp, filename, duration, nb appels LLM, modèle utilisé, succès/erreur, etc.
- `test_normalization.py` : Nettoyage des données
- `test_validation.py` : Validation métier OHADA
- `test_llm_client.py` : Intégration OpenAI
- `test_ocr_pipeline.py` : Logique de cascading/fallback
- `test_routes.py` : Tests d'intégration API

## Structure des résultats

Après chaque extraction, un fichier CSV est créé/mis à jour :

```
resultats/
└── extractions.csv
    ├── timestamp
    ├── fichier_source
    ├── statut (succès/erreur)
    ├── needs_human_review
    ├── fournisseur
    ├── numero_facture
    ├── date
    ├── montant_ht, montant_tva, montant_ttc
    ├── devise
    ├── ifu_fournisseur (OHADA)
    ├── code_mecef (OHADA)
    ├── confiance (score 0-1)
    ├── nombre_lignes
    └── error_message
```

## Problèmes rencontrés et solutions


### **Format décimal français mal parsé par le LLM (300.000 → 300.0 au lieu de 300000.0)**

**Problème** : Les factures françaises utilisent le point (.) comme séparateur de milliers et la virgule (,) comme décimal. Le LLM parsait "300.000" comme 300.0 (format US).

**Cause** : Le LLM n'avait pas d'instructions claires sur le format décimal francophone.

**Solution** : Amélioration du `SYSTEM_PROMPT` avec des exemples concrets

---

### **gpt-4o-mini retournait du JSON mal formé (None, markdown, etc.)**

**Problème** : Le modèle léger retournait des champs None ou du JSON enrobé en markdown (```json...```).

**Causes** :
- Manque de clarté dans les instructions
- Le modèle ajoutait du markdown au JSON

**Solutions appliquées** :
1. Renforcement du prompt avec des règles immuables

2. Ajout d'une fonction de parsing robuste `_clean_json_response()` pour :
   - Enlever les blocs markdown ```json...```
   - Extraire le JSON valide entre les accolades
   - Gérer les cas limites

---

### **TVA = 0 levait une erreur de validation (factures assurance/notaire)**

**Problème** : Les factures d'assurance et de notaire ont souvent une TVA = 0, ce qui déclenchait l'erreur "HT + TVA ≠ TTC".

**Cause** : La validation Pydantic appliquait la règle `montant_ht + montant_tva == montant_ttc` même pour les structures spéciales.

**Solution** : Modification du validateur pour détecter et accepter le cas TVA = 0.0

Le pipeline marque `needs_human_review = True` pour ces cas spéciaux.

---

## Licence

Ce projet a été réalisé par Rémi Nollet. Le code, l'architecture et les prompts fournis restent la propriété intellectuelle de leur auteur. Toute utilisation, reproduction ou exploitation commerciale sans accord préalable est strictement interdite.
