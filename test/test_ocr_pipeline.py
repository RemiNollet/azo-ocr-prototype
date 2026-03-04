"""
Tests unitaires pour le pipeline OCR (ocr_pipeline.py).

Teste l'orchestration et la logique de cascading/fallback.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.ocr_pipeline import run_extraction_pipeline, ExtractionResult


@pytest.mark.unit
class TestExtractionResult:
    """Tests pour la classe ExtractionResult."""

    def test_successful_extraction_result(self, sample_invoice_data):
        """Test création d'un résultat d'extraction réussi."""
        result = ExtractionResult(data=sample_invoice_data, needs_human_review=False)

        assert result.data == sample_invoice_data
        assert result.needs_human_review is False
        assert result.error_message is None

    def test_failed_extraction_result(self):
        """Test création d'un résultat d'extraction échouée."""
        result = ExtractionResult(
            data=None,
            needs_human_review=True,
            error_message="HT + TVA != TTC",
        )

        assert result.data is None
        assert result.needs_human_review is True
        assert result.error_message == "HT + TVA != TTC"


@pytest.mark.unit
@pytest.mark.mock_llm
class TestRunExtractionPipeline:
    """Tests pour la fonction run_extraction_pipeline()."""

    @patch('app.services.ocr_pipeline.extract_invoice_from_image')
    def test_first_attempt_success(self, mock_extract, sample_invoice_data, settings, test_image_base64):
        """Test succès à la première tentative (gpt-4o-mini)."""
        mock_extract.return_value = sample_invoice_data

        result = run_extraction_pipeline(test_image_base64, settings=settings)

        assert result.data == sample_invoice_data
        assert result.needs_human_review is False
        # Doit être appelé une seule fois (pas de fallback)
        assert mock_extract.call_count == 1

    @patch('app.services.ocr_pipeline.extract_invoice_from_image')
    def test_retry_then_success(self, mock_extract, sample_invoice_data, settings, test_image_base64):
        """Test retry gpt-4o-mini puis succès."""
        from app.models.constants import MathValidationError

        error = MathValidationError("HT+TVA != TTC", 100, 20, 150)
        mock_extract.side_effect = [error, sample_invoice_data]

        result = run_extraction_pipeline(test_image_base64, settings=settings)

        assert result.data == sample_invoice_data
        assert result.needs_human_review is False
        # Doit être appelé 2 fois (1er essai + 1 retry)
        assert mock_extract.call_count == 2

    @patch('app.services.ocr_pipeline.extract_invoice_from_image')
    def test_fallback_success(self, mock_extract, sample_invoice_data, settings, test_image_base64):
        """Test fallback vers gpt-4o et succès."""
        from app.models.constants import MathValidationError

        error = MathValidationError("HT+TVA != TTC", 100, 20, 150)
        mock_extract.side_effect = [error, error, sample_invoice_data]

        result = run_extraction_pipeline(test_image_base64, settings=settings)

        assert result.data == sample_invoice_data
        assert result.needs_human_review is False
        # Doit être appelé 3 fois (1er essai + retry + fallback)
        assert mock_extract.call_count == 3

    @patch('app.services.ocr_pipeline.extract_invoice_from_image')
    def test_all_attempts_fail(self, mock_extract, settings, test_image_base64):
        """Test que tous les modèles échouent."""
        from app.models.constants import MathValidationError

        error = MathValidationError("HT+TVA != TTC", 100, 20, 150)
        mock_extract.side_effect = [error, error, error]

        result = run_extraction_pipeline(test_image_base64, settings=settings)

        assert result.data is None
        assert result.needs_human_review is True
        assert result.error_message is not None
        # Doit être appelé 3 fois (2x mini + 1x 4o)
        assert mock_extract.call_count == 3

    @patch('app.services.ocr_pipeline.extract_invoice_from_image')
    def test_zero_tva_triggers_review(self, mock_extract, sample_invoice_zero_tva, settings, test_image_base64):
        """Test que TVA=0 déclenche le flag human_review."""
        mock_extract.return_value = sample_invoice_zero_tva

        result = run_extraction_pipeline(test_image_base64, settings=settings)

        assert result.data == sample_invoice_zero_tva
        assert result.needs_human_review is True  # TVA = 0 requiert revue
