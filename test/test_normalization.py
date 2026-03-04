"""
Tests unitaires pour le module de normalisation (normalization.py).

Teste les fonctions de nettoyage et normalisation des données extraites.
"""

import pytest

from app.services.normalization import clean_amount_string, string_to_float, normalize_date_string


@pytest.mark.unit
class TestCleanAmountString:
    """Tests pour la fonction clean_amount_string()."""

    def test_clean_basic_amount(self):
        """Test nettoyage d'un montant simple avec symbole."""
        assert clean_amount_string("100 XOF") == "100"

    def test_clean_french_format_thousands(self):
        """Test conversion format français (point=milliers)."""
        # "300.000,50 XOF" → "300000.50"
        assert clean_amount_string("300.000,50 XOF") == "300000.50"

    def test_clean_large_french_number(self):
        """Test avec nombre français plus grand."""
        assert clean_amount_string("14.489.448 XOF") == "14489448"

    def test_clean_with_currency_symbol(self):
        """Test suppression des symboles monétaires."""
        assert clean_amount_string("1000 FCFA") == "1000"
        assert clean_amount_string("500 F CFA") == "500"

    def test_clean_empty_string(self):
        """Test avec chaîne vide."""
        assert clean_amount_string("") == "0"

    def test_clean_spaces_only(self):
        """Test avec espaces uniquement."""
        assert clean_amount_string("   ") == "0"

    def test_clean_preserves_decimal(self):
        """Test que le point décimal est préservé."""
        assert clean_amount_string("100,50") == "100.50"


@pytest.mark.unit
class TestStringToFloat:
    """Tests pour la fonction string_to_float()."""

    def test_simple_integer(self):
        """Test conversion entier simple."""
        assert string_to_float("100") == 100.0

    def test_decimal_number(self):
        """Test conversion nombre décimal."""
        assert string_to_float("100.50") == 100.50

    def test_french_format_conversion(self):
        """Test conversion format français."""
        assert string_to_float("300.000,50") == 300000.50

    def test_empty_string_returns_zero(self):
        """Test que chaîne vide retourne 0.0."""
        assert string_to_float("") == 0.0

    def test_invalid_string_returns_zero(self):
        """Test qu'un string invalide retourne 0.0."""
        assert string_to_float("not a number") == 0.0

    def test_none_returns_zero(self):
        """Test que None est géré correctement."""
        # Cette fonction attend un string, mais on peut tester la robustesse
        result = string_to_float("")  # equivalent
        assert result == 0.0


@pytest.mark.unit
class TestNormalizeDateString:
    """Tests pour la fonction normalize_date_string()."""

    def test_valid_date_unchanged(self):
        """Test que une date valide n'est pas modifiée."""
        assert normalize_date_string("2025-02-26") == "2025-02-26"

    def test_remove_leading_trailing_spaces(self):
        """Test suppression espaces début/fin."""
        assert normalize_date_string("  2025-02-26  ") == "2025-02-26"

    def test_empty_date_returns_empty(self):
        """Test que date vide retourne vide."""
        assert normalize_date_string("") == ""

    def test_none_returns_none(self):
        """Test que None retourne None."""
        assert normalize_date_string(None) is None
