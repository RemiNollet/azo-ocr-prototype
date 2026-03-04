"""
Module de monitoring et KPI pour le microservice AZO OCR.
Traçabilité des performances et métriques business.
"""

import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ExtractionKPI:
    """KPI pour une extraction unique."""

    timestamp: str
    filename: str
    total_duration_ms: float
    llm_call_count: int
    final_model_used: str
    success: bool
    needs_human_review: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self):
        """Convertit en dictionnaire pour logging/CSV."""
        return asdict(self)


class KPITracker:
    """Suivi des KPI pour l'extraction de données."""

    def __init__(self):
        """Initialise le tracker."""
        self.start_time: Optional[float] = None
        self.llm_call_count: int = 0
        self.current_model: Optional[str] = None
        self.kpi_file = Path(__file__).parent.parent.parent / "resultats" / "kpi.jsonl"
        self.kpi_file.parent.mkdir(exist_ok=True)

    def start_extraction(self):
        """Démarre le chronomètre pour une extraction."""
        self.start_time = time.time()
        self.llm_call_count = 0
        self.current_model = None

    def record_llm_call(self, model: str):
        """Enregistre un appel LLM et met à jour le modèle courant."""
        self.llm_call_count += 1
        self.current_model = model
        logger.debug("LLM call #%d with model %s", self.llm_call_count, model)

    def end_extraction(
        self,
        filename: str,
        success: bool,
        needs_human_review: bool = False,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> ExtractionKPI:
        """Termine l'extraction et enregistre les KPI."""
        if self.start_time is None:
            raise ValueError("Extraction non initialisée (appeler start_extraction)")

        duration_ms = (time.time() - self.start_time) * 1000

        kpi = ExtractionKPI(
            timestamp=datetime.now().isoformat(),
            filename=filename,
            total_duration_ms=round(duration_ms, 2),
            llm_call_count=self.llm_call_count,
            final_model_used=self.current_model or "unknown",
            success=success,
            needs_human_review=needs_human_review,
            error_type=error_type,
            error_message=error_message,
        )

        # Log KPI
        logger.info(
            "Extraction KPI - File: %s | Duration: %.2fms | LLM calls: %d | Model: %s | Success: %s | Review: %s",
            filename,
            duration_ms,
            self.llm_call_count,
            self.current_model,
            success,
            needs_human_review,
        )

        # Enregistrer dans fichier JSONL
        self._write_kpi(kpi)

        return kpi

    def _write_kpi(self, kpi: ExtractionKPI):
        """Écrit le KPI dans le fichier JSONL."""
        import json

        try:
            with open(self.kpi_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(kpi.to_dict()) + "\n")
        except Exception as e:
            logger.error("Erreur écriture KPI: %s", e)


# Instance globale du tracker
kpi_tracker = KPITracker()


def get_kpi_stats() -> dict:
    """Retourne les statistiques KPI agrégées."""
    import json

    if not kpi_tracker.kpi_file.exists():
        return {"total": 0, "success_rate": 0, "avg_duration_ms": 0, "review_rate": 0}

    kpis = []
    with open(kpi_tracker.kpi_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                kpis.append(json.loads(line))

    if not kpis:
        return {"total": 0, "success_rate": 0, "avg_duration_ms": 0, "review_rate": 0}

    total = len(kpis)
    successes = sum(1 for k in kpis if k["success"])
    reviews = sum(1 for k in kpis if k["needs_human_review"])
    avg_duration = sum(k["total_duration_ms"] for k in kpis) / total

    return {
        "total_extractions": total,
        "success_rate": round((successes / total) * 100, 2),
        "failed_count": total - successes,
        "human_review_count": reviews,
        "review_rate": round((reviews / total) * 100, 2),
        "avg_duration_ms": round(avg_duration, 2),
        "min_duration_ms": min(k["total_duration_ms"] for k in kpis),
        "max_duration_ms": max(k["total_duration_ms"] for k in kpis),
    }
