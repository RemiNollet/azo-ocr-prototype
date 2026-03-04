"""
Tests unitaires pour le module de validation (validation.py, schemas.py).

Teste la logique métier OHADA et les validations Pydantic.
"""

import pytest
from pydantic import ValidationError

from app.models.schemas import InvoiceData
from app.models.constants import MathValidationError


@pytest.mark.unit
class TestInvoiceDataValidation:
    """Tests pour la validation du schéma InvoiceData."""

    def test_valid_invoice_creates_successfully(self, sample_invoice_data):
        """Test qu'une facture valide peut être créée."""
        assert sample_invoice_data.fournisseur == "Entreprise Test SARL"
        assert sample_invoice_data.montant_ttc == 1200.0

    def test_invalid_math_raises_error(self, sample_invoice_invalid_math):
        """Test que math invalide lève une erreur de validation."""
        # Pydantic lève ValidationError qui contient MathValidationError
        with pytest.raises(ValidationError):
            InvoiceData(**sample_invoice_invalid_math)

    def test_zero_tva_accepted(self, sample_invoice_zero_tva):
        """Test que TVA=0 est acceptée (cas assurance/notaire)."""
        # Doit être acceptée sans lever d'erreur
        assert sample_invoice_zero_tva.montant_tva == 0.0
        assert sample_invoice_zero_tva.montant_ht == sample_invoice_zero_tva.montant_ttc

    def test_negative_amounts_rejected(self):
        """Test que montants négatifs sont rejetés."""
        with pytest.raises(ValueError):
            InvoiceData(
                fournisseur="Test",
                numero_facture="F001",
                date="2025-02-26",
                montant_ht=-100.0,  # Invalide
                montant_tva=20.0,
                montant_ttc=1200.0,
                devise="XOF",
            )

    def test_required_fields_validation(self):
        """Test que les champs obligatoires sont requis."""
        with pytest.raises(ValueError):
            InvoiceData(
                # Manque 'fournisseur'
                numero_facture="F001",
                date="2025-02-26",
                montant_ht=100.0,
                montant_tva=20.0,
                montant_ttc=120.0,
                devise="XOF",
            )

    def test_optional_fields_can_be_none(self, sample_invoice_data):
        """Test que les champs optionnels peuvent être None."""
        sample_invoice_data.ifu_fournisseur = None
        sample_invoice_data.code_mecef = None
        assert sample_invoice_data.ifu_fournisseur is None
        assert sample_invoice_data.code_mecef is None

    def test_math_validation_with_tolerance(self):
        """Test que la tolérance de 0.05 fonctionne."""
        # HT + TVA = 120.04, TTC = 120.0, écart = 0.04 < 0.05
        invoice = InvoiceData(
            fournisseur="Test",
            numero_facture="F001",
            date="2025-02-26",
            montant_ht=100.0,
            montant_tva=20.04,
            montant_ttc=120.0,
            devise="XOF",
        )
        assert invoice.montant_ttc == 120.0  # Accepté

    def test_confiance_score_validation(self):
        """Test que score confiance est entre 0 et 1."""
        with pytest.raises(ValueError):
            InvoiceData(
                fournisseur="Test",
                numero_facture="F001",
                date="2025-02-26",
                montant_ht=100.0,
                montant_tva=20.0,
                montant_ttc=120.0,
                devise="XOF",
                confiance=1.5,  # > 1.0
            )

        with pytest.raises(ValueError):
            InvoiceData(
                fournisseur="Test",
                numero_facture="F001",
                date="2025-02-26",
                montant_ht=100.0,
                montant_tva=20.0,
                montant_ttc=120.0,
                devise="XOF",
                confiance=-0.5,  # < 0.0
            )
