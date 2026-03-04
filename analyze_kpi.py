#!/usr/bin/env python3
"""
Script d'exemple pour analyser et visualiser les KPI.
À exécuter après avoir lancé plusieurs tests via le pipeline.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_kpi_data():
    """Charge les données KPI depuis le fichier JSONL."""
    kpi_file = Path(__file__).parent / "resultats" / "kpi.jsonl"
    if not kpi_file.exists():
        print("Aucune donnée KPI trouvée. Lancez d'abord le pipeline.")
        return []

    kpis = []
    with open(kpi_file, "r") as f:
        for line in f:
            if line.strip():
                kpis.append(json.loads(line))

    return kpis


def analyze_kpi(kpis):
    """Analyse les KPI collectées."""
    if not kpis:
        print("Pas de données à analyser.")
        return

    print("\n" + "=" * 60)
    print("ANALYSE DES KPI")
    print("=" * 60)

    # Statistiques globales
    total = len(kpis)
    successes = sum(1 for k in kpis if k["success"])
    reviews = sum(1 for k in kpis if k["needs_human_review"])
    failures = sum(1 for k in kpis if not k["success"])

    print(f"\nSTATISTIQUES GLOBALES")
    print(f"  Total extractions          : {total}")
    print(f"  Succès                     : {successes}/{total} ({100*successes/total:.1f}%)")
    print(f"  Écheccs                    : {failures}/{total}")
    print(f"  Revue manuelle requise     : {reviews}/{total} ({100*reviews/total:.1f}%)")

    # Latence
    durations = [k["total_duration_ms"] for k in kpis]
    print(f"\n⏱LATENCE (en ms)")
    print(f"  Moyenne                    : {sum(durations)/len(durations):.0f} ms")
    print(f"  Minimum                    : {min(durations):.0f} ms")
    print(f"  Maximum                    : {max(durations):.0f} ms")
    print(f"  Médiane                    : {sorted(durations)[len(durations)//2]:.0f} ms")

    # Appels LLM
    print(f"\nAPPELS LLM")
    call_counts = defaultdict(int)
    for k in kpis:
        call_counts[k["llm_call_count"]] += 1

    for call_count in sorted(call_counts.keys()):
        percent = 100 * call_counts[call_count] / total
        print(f"  {call_count} appel{'s' if call_count > 1 else ''}            : {call_counts[call_count]:3d} ({percent:5.1f}%)")

    # Modèles utilisés
    print(f"\nMODÈLES UTILISÉS")
    models = defaultdict(int)
    for k in kpis:
        models[k["final_model_used"]] += 1

    for model in sorted(models.keys()):
        percent = 100 * models[model] / total
        print(f"  {model:20s} : {models[model]:3d} ({percent:5.1f}%)")

    # Erreurs
    errors = [k for k in kpis if k["error_type"]]
    if errors:
        print(f"\nERREURS RENCONTRÉES")
        error_types = defaultdict(int)
        for err in errors:
            error_types[err["error_type"]] += 1

        for error_type in sorted(error_types.keys()):
            print(f"  {error_type:30s} : {error_types[error_type]:3d}")

    # Fichiers problématiques
    failed_files = [k["filename"] for k in kpis if not k["success"]]
    if failed_files:
        print(f"\nFICHIERS ÉCHOUÉS")
        for filename in failed_files:
            print(f"  - {filename}")

    review_files = [k["filename"] for k in kpis if k["needs_human_review"] and k["success"]]
    if review_files:
        print(f"\n🔍 FICHIERS EN REVUE MANUELLE")
        for filename in review_files[:5]:  # Affiche les 5 premiers
            print(f"  - {filename}")

    # Dernières extractions
    print(f"\nDERNIÈRES EXTRACTIONS")
    for k in kpis[-3:]:
        status = "Yes" if k["success"] else "No"
        review = " (revue)" if k["needs_human_review"] else ""
        print(f"  {status} {k['filename']:30s} - {k['total_duration_ms']:6.0f}ms - {k['llm_call_count']}x {k['final_model_used']}{review}")

    print("\n" + "=" * 60)


def cost_analysis(kpis):
    """Analyse le coût OpenAI."""
    if not kpis:
        return

    print("\n" + "=" * 60)
    print("ANALYSE DES COÛTS")
    print("=" * 60)

    # Répartition des appels
    mini_calls = sum(1 for k in kpis if k["final_model_used"] == "gpt-4o-mini" or k["llm_call_count"] >= 1)
    heavy_calls = sum(1 for k in kpis if k["final_model_used"] == "gpt-4o")

    # Estimation tokens (approximatif)
    print(f"\nRÉPARTITION DES MODÈLES")
    print(f"  gpt-4o-mini appels         : ~{mini_calls} (économique)")
    print(f"  gpt-4o appels (fallback)   : ~{heavy_calls} (coûteux)")

    # Coûts (tarif avril 2024)
    mini_input_cost_per_million = 0.15  # $ pour 1M tokens
    mini_output_cost_per_million = 0.60

    heavy_input_cost_per_million = 5.00
    heavy_output_cost_per_million = 15.00

    # Estimation : ~500 tokens par requête en moyenne
    avg_tokens = 500

    mini_estimated = (mini_calls * avg_tokens / 1_000_000) * (mini_input_cost_per_million + mini_output_cost_per_million)
    heavy_estimated = (heavy_calls * avg_tokens / 1_000_000) * (heavy_input_cost_per_million + heavy_output_cost_per_million)
    total_cost = mini_estimated + heavy_estimated

    print(f"\nESTIMATION DE COÛTS")
    print(f"  gpt-4o-mini                : ${mini_estimated:.3f}")
    print(f"  gpt-4o (fallback)          : ${heavy_estimated:.3f}")
    print(f"  TOTAL ESTIMÉ               : ${total_cost:.3f}")

    print(f"\nCOÛT PAR EXTRACTION")
    print(f"  Coût moyen                 : ${total_cost / len(kpis):.4f}/extraction")

    print("\n" + "=" * 60)


def export_csv(kpis):
    """Exporte les KPI en CSV pour analyse."""
    if not kpis:
        return

    csv_file = Path(__file__).parent / "resultats" / "kpi_analysis.csv"
    csv_file.parent.mkdir(exist_ok=True)

    import csv
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=kpis[0].keys())
        writer.writeheader()
        writer.writerows(kpis)

    print(f"\nDonnées exportées en CSV : {csv_file}")


if __name__ == "__main__":
    print("\nAnalyse des KPI - AZO OCR Prototype\n")

    kpis = load_kpi_data()

    if kpis:
        analyze_kpi(kpis)
        cost_analysis(kpis)
        export_csv(kpis)
        print("\nConseil : Ouvrez 'resultats/kpi_analysis.csv' dans Excel pour plus d'analyse.")
    else:
        print("Aucune donnée KPI disponible.")
        print("Lancez d'abord le pipeline :")
        print("  python test/test_pipeline.py")
