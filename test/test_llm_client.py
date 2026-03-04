"""
Tests unitaires pour le client LLM (llm_client.py).

Teste l'intégration OpenAI et le parsing de réponses structurées.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.services.llm_client import extract_invoice_from_image, _clean_json_response


@pytest.mark.unit
@pytest.mark.mock_llm
class TestCleanJsonResponse:
    """Tests pour la fonction _clean_json_response()."""

    def test_clean_valid_json(self):
        """Test nettoyage JSON valide."""
        raw = json.dumps({"key": "value"})
        result = _clean_json_response(raw)
        assert json.loads(result) == {"key": "value"}

    def test_remove_markdown_json_block(self):
        """Test suppression des blocs markdown ```json...```."""
        raw = '```json\n{"key": "value"}\n```'
        result = _clean_json_response(raw)
        assert json.loads(result) == {"key": "value"}

    def test_remove_text_before_json(self):
        """Test suppression du texte avant JSON."""
        raw = 'Some explanation\n{"key": "value"}'
        result = _clean_json_response(raw)
        assert json.loads(result) == {"key": "value"}

    def test_remove_text_after_json(self):
        """Test suppression du texte après JSON."""
        raw = '{"key": "value"}\nSome explanation'
        result = _clean_json_response(raw)
        assert json.loads(result) == {"key": "value"}

    def test_handle_generic_markdown(self):
        """Test gestion des blocs markdown génériques."""
        raw = '```\n{"key": "value"}\n```'
        result = _clean_json_response(raw)
        assert json.loads(result) == {"key": "value"}


@pytest.mark.unit
@pytest.mark.mock_llm
class TestExtractInvoiceFromImage:
    """Tests pour la fonction extract_invoice_from_image()."""

    @patch('app.services.llm_client.OpenAI')
    def test_successful_extraction(self, mock_openai_class, mock_llm_response_valid, settings, test_image_base64):
        """Test extraction réussie."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_llm_response_valid

        result = extract_invoice_from_image(test_image_base64, model="gpt-4o-mini", settings=settings)

        assert result.fournisseur == "Entreprise Test"
        assert result.numero_facture == "F001"
        assert result.montant_ttc == 1200.0
        assert len(result.lignes_detail) == 1

    @patch('app.services.llm_client.OpenAI')
    def test_invalid_json_raises_error(self, mock_openai_class, mock_llm_response_invalid_json, settings, test_image_base64):
        """Test que JSON invalide lève une erreur."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_llm_response_invalid_json

        with pytest.raises(ValueError):
            extract_invoice_from_image(test_image_base64, model="gpt-4o-mini", settings=settings)

    @patch('app.services.llm_client.OpenAI')
    def test_empty_response_raises_error(self, mock_openai_class, settings, test_image_base64):
        """Test que réponse vide lève une erreur."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_client.chat.completions.create.return_value = mock_response

        with pytest.raises(ValueError, match="Réponse LLM vide"):
            extract_invoice_from_image(test_image_base64, model="gpt-4o-mini", settings=settings)
