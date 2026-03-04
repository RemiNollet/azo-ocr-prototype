"""
Tests d'intégration pour l'API Routes (routes.py).

Teste les endpoints HTTP avec TestClient FastAPI.
"""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import InvoiceData


@pytest.fixture
def client():
    """Fixture pour le TestClient FastAPI."""
    return TestClient(app)


@pytest.mark.integration
class TestHealthEndpoint:
    """Tests pour l'endpoint GET /health."""

    def test_health_endpoint_returns_ok(self, client):
        """Test que /health retourne status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.integration
class TestExtractEndpoint:
    """Tests pour l'endpoint POST /api/v1/extract."""

    @patch('app.api.routes._file_to_image_base64')
    @patch('app.api.routes.run_extraction_pipeline')
    def test_extract_with_valid_pdf(self, mock_pipeline, mock_file_to_image, client, sample_invoice_data):
        """Test extraction avec PDF valide."""
        # Mock la conversion fichier -> image
        mock_file_to_image.return_value = "base64imagedata"
        # Mock le pipeline
        mock_pipeline.return_value = MagicMock(
            data=sample_invoice_data,
            needs_human_review=False,
            error_message=None,
        )

        # Créer un fichier PDF factice
        pdf_content = b"%PDF-1.4\n%test pdf content"
        files = {"file": ("facture.pdf", BytesIO(pdf_content), "application/pdf")}

        response = client.post("/api/v1/extract", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["needs_human_review"] is False
        assert data["data"] is not None
        assert data["data"]["fournisseur"] == "Entreprise Test SARL"

    def test_extract_with_invalid_file_type(self, client):
        """Test rejection d'un type de fichier invalide."""
        files = {"file": ("document.txt", BytesIO(b"text content"), "text/plain")}

        response = client.post("/api/v1/extract", files=files)

        assert response.status_code == 400
        assert "Type de fichier non supporté" in response.json()["detail"]

    def test_extract_with_empty_file(self, client):
        """Test rejection d'un fichier vide."""
        files = {"file": ("empty.pdf", BytesIO(b""), "application/pdf")}

        response = client.post("/api/v1/extract", files=files)

        # Peut être 400 car fichier vide ou parce que pdf2image échoue
        assert response.status_code in [400, 422]

    @patch('app.api.routes._file_to_image_base64')
    @patch('app.api.routes.run_extraction_pipeline')
    def test_extract_with_human_review_needed(self, mock_pipeline, mock_file_to_image, client):
        """Test extraction nécessitant revue manuelle."""
        # Mock la conversion fichier -> image
        mock_file_to_image.return_value = "base64imagedata"
        # Mock le pipeline
        mock_pipeline.return_value = MagicMock(
            data=None,
            needs_human_review=True,
            error_message="HT + TVA != TTC",
        )

        pdf_content = b"%PDF-1.4\n%test pdf content"
        files = {"file": ("facture.pdf", BytesIO(pdf_content), "application/pdf")}

        response = client.post("/api/v1/extract", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["needs_human_review"] is True
        assert data["data"] is None
        assert "HT + TVA != TTC" in data["error_message"]
