"""
Configuration pytest et fixtures partagées pour tous les tests.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from app.core.config import Settings
from app.models.schemas import InvoiceData, LigneDetail
from app.models.constants import MathValidationError


@pytest.fixture
def settings():
    """Fixture pour les settings avec clé API fictive."""
    return Settings(
        openai_api_key="sk-test-key-12345",
        llm_model_light="gpt-4o-mini",
        llm_model_heavy="gpt-4o",
    )


@pytest.fixture
def sample_invoice_data():
    """Fixture pour une facture d'exemple valide."""
    return InvoiceData(
        fournisseur="Entreprise Test SARL",
        numero_facture="FAC-2025-001",
        date="2025-02-26",
        montant_ht=1000.0,
        montant_tva=200.0,
        montant_ttc=1200.0,
        devise="XOF",
        ifu_fournisseur="1234567890123",
        code_mecef="ABC-DEF-GHI",
        confiance=0.95,
        lignes_detail=[
            LigneDetail(
                description="Consultation 1 jour",
                quantite=1.0,
                prix_unitaire=1000.0,
                montant_ligne=1000.0,
            )
        ],
    )


@pytest.fixture
def sample_invoice_zero_tva():
    """Fixture pour une facture avec TVA = 0 (cas spécial assurance/notaire)."""
    return InvoiceData(
        fournisseur="NSIA Assurances",
        numero_facture="NSIA-2025-001",
        date="2025-02-26",
        montant_ht=1000.0,
        montant_tva=0.0,
        montant_ttc=1000.0,
        devise="XOF",
        ifu_fournisseur="9876543210987",
        code_mecef=None,
        confiance=0.85,
        lignes_detail=[
            LigneDetail(
                description="Prime d'assurance",
                quantite=1.0,
                prix_unitaire=1000.0,
                montant_ligne=1000.0,
            )
        ],
    )


@pytest.fixture
def sample_invoice_invalid_math():
    """Fixture pour une facture avec math invalide (HT + TVA != TTC)."""
    return {
        "fournisseur": "Mauvais Calcul Ltd",
        "numero_facture": "BAD-2025-001",
        "date": "2025-02-26",
        "montant_ht": 100.0,
        "montant_tva": 20.0,
        "montant_ttc": 150.0,  # Devrait être 120.0
        "devise": "XOF",
        "lignes_detail": [],
    }


@pytest.fixture
def mock_llm_response_valid():
    """Fixture pour une réponse LLM valide du client OpenAI."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = json.dumps(
        {
            "fournisseur": "Entreprise Test",
            "numero_facture": "F001",
            "date": "2025-02-26",
            "montant_ht": 1000.0,
            "montant_tva": 200.0,
            "montant_ttc": 1200.0,
            "devise": "XOF",
            "lignes_detail": [
                {
                    "description": "Service",
                    "quantite": 1.0,
                    "prix_unitaire": 1000.0,
                    "montant_ligne": 1000.0,
                }
            ],
        }
    )
    response.usage = MagicMock()
    response.usage.prompt_tokens = 100
    response.usage.completion_tokens = 50
    response.usage.total_tokens = 150
    return response


@pytest.fixture
def mock_llm_response_invalid_json():
    """Fixture pour une réponse LLM avec JSON invalide."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "```json\n{invalid json}\n```"
    response.usage = MagicMock()
    response.usage.prompt_tokens = 100
    response.usage.completion_tokens = 50
    response.usage.total_tokens = 150
    return response


@pytest.fixture
def mock_openai_client(settings):
    """Fixture pour un client OpenAI mocké."""
    client = MagicMock()
    return client


@pytest.fixture
def test_image_base64():
    """Fixture pour une image base64 de test (1x1 pixel transparent PNG)."""
    # Image PNG 1x1 pixel transparent encodée en base64
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def temp_csv_file(tmp_path):
    """Fixture pour un fichier CSV temporaire pour les tests."""
    csv_file = tmp_path / "test_extractions.csv"
    csv_file.write_text(
        "timestamp,fichier_source,statut,needs_human_review,fournisseur,numero_facture\n"
        "2025-02-26T10:00:00,test.pdf,succès,False,Test Co,F001\n"
    )
    return csv_file


# Markers pour catégoriser les tests
def pytest_configure(config):
    """Configure les custom markers pytest."""
    config.addinivalue_line("markers", "unit: Tests unitaires")
    config.addinivalue_line("markers", "integration: Tests d'intégration")
    config.addinivalue_line("markers", "slow: Tests lents")
    config.addinivalue_line("markers", "mock_llm: Tests qui mockent le client LLM")
