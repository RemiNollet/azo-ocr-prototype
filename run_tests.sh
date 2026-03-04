#!/bin/bash
# Script pour exécuter les tests pytest

set -e

echo "=== AZO OCR Prototype - Test Suite ==="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Tous les tests
echo -e "${BLUE}Tous les tests (unit + integration):${NC}"
python3 -m pytest test/ -v

# Tests unitaires uniquement
echo -e "\n${BLUE}Tests unitaires uniquement:${NC}"
python3 -m pytest test/ -v -m unit

# Tests d'intégration uniquement
echo -e "\n${BLUE}Tests d'intégration uniquement:${NC}"
python3 -m pytest test/ -v -m integration

# Avec couverture de code (si pytest-cov est disponible)
echo -e "\n${BLUE}Couverture de code:${NC}"
python3 -m pytest test/ --cov=app --cov-report=term-missing --cov-report=html || true

echo -e "\n${GREEN}Tests terminés!${NC}"
