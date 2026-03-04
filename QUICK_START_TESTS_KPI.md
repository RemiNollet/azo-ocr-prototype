# ⚡ Quick Start - Tests & KPI

## En 5 minutes

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Lancer les tests
```bash
pytest test/ -v
# ✅ 39 tests réussis
```

### 3. Serveur
```bash
uvicorn app.main:app --reload
```

### 4. Consulter KPI
```bash
curl http://127.0.0.1:8000/api/v1/kpi | jq
```

### 5. Analyser
```bash
python analyze_kpi.py
```

---

## Commandes Essentielles

### Tests
```bash
pytest test/ -v                          # Tous
pytest test/ -v -m unit                  # Unitaires
pytest test/ -v -m integration           # Intégration
pytest test/ --cov=app --cov-report=html # Couverture
```

### KPI
```bash
curl http://127.0.0.1:8000/api/v1/kpi | jq    # Via API
python analyze_kpi.py                          # Analyse
cat resultats/kpi.jsonl | jq .                 # Brutes
```

### API
```bash
curl -X POST -F "file=@facture.pdf" \
  http://127.0.0.1:8000/api/v1/extract | jq   # Extraction
  
curl http://127.0.0.1:8000/docs                # Swagger
```

---

## 📊 Qu'est-ce qui a été créé

### Tests (39 total)
- ✅ 12 tests normalization
- ✅ 10 tests validation
- ✅ 5 tests llm_client
- ✅ 7 tests pipeline
- ✅ 5 tests routes

### KPI
- ✅ Module `app/monitoring/kpi.py`
- ✅ Endpoint `GET /api/v1/kpi`
- ✅ Stockage JSONL `resultats/kpi.jsonl`
- ✅ Script analyse `analyze_kpi.py`

### Documentation
- ✅ `test/README.md` - Tests guide
- ✅ `KPI.md` - KPI documentation
- ✅ `IMPLEMENTATION_SUMMARY.md` - Résumé
- ✅ `PROJECT_STRUCTURE.md` - Structure

---

## 🎯 Métriques KPI Collectées

```
- Total extractions
- Success rate (%)
- Average duration (ms)
- LLM call count
- Final model used
- Needs human review
- Error tracking
```

**Exemple response:**
```json
{
  "total_extractions": 25,
  "success_rate": 96.0,
  "avg_duration_ms": 4250.50,
  "review_rate": 12.0
}
```

---

## 🚀 Prochaines Étapes

1. **Lancer les tests** : `pytest test/ -v`
2. **Consulter doc** : `cat IMPLEMENTATION_SUMMARY.md`
3. **Utiliser l'API** : Voir `README.md`
4. **Analyser KPI** : `python analyze_kpi.py`
5. **Ajouter tests** : Voir `test/README.md`

---

**Temps pour démarrer** : < 5 minutes ⚡
**Tests** : 39 disponibles ✅
**Documentation** : Complète 📚
**Production-ready** : Oui 🚀
