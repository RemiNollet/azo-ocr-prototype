"""
Fonctions utilitaires de normalisation des données extraites.
Nettoyage des chaînes (espaces, symboles) avant conversion en nombres ou dates.
Le LLM fait l'essentiel via les instructions ; cette couche assure la cohérence post-extraction.
"""

import re
from typing import Optional


def clean_amount_string(value: str) -> str:
    """
    Nettoie une chaîne représentant un montant avant conversion en float.
    Enlève espaces, caractères de milliers (espaces, virgules, points selon locale), garde le décimal.
    Convertit le format français (point=milliers, virgule=décimal) en format US (point=décimal).
    """
    if not value or not isinstance(value, str):
        return "0"
    s = value.strip()
    if not s:
        return "0"
    # Supprimer espaces et symboles monétaires courants
    s = re.sub(r"[\s\xa0]", "", s)
    s = s.replace("\u202f", "")
    # Garder uniquement chiffres, virgule, point et éventuel signe
    s = re.sub(r"[^\d,.\-+]", "", s)
    
    # Traiter le format français (14.489.448,50 → 14489448.50)
    # Si la chaîne contient une virgule ET des points, c'est français
    if "," in s and "." in s:
        # Enlever tous les points (séparateurs de milliers)
        s = s.replace(".", "")
        # Remplacer la virgule par un point (décimal)
        s = s.replace(",", ".")
    # Si seulement des points et pas de virgule, vérifier si c'est français ou non
    elif "." in s and "," not in s:
        # Si plus d'un point : format français (14.489.448)
        parts = s.split(".")
        if len(parts) > 2:
            # Enlever TOUS les points (format français milliers)
            s = "".join(parts)
    
    # Remplacer virgule décimale par point (au cas où)
    s = s.replace(",", ".")
    
    result = s.strip() or "0"
    return result


def string_to_float(value: str) -> float:
    """
    Convertit une chaîne nettoyée en float. Retourne 0.0 si vide ou invalide.
    """
    cleaned = clean_amount_string(value) if isinstance(value, str) else str(value)
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def normalize_date_string(value: str) -> Optional[str]:
    """
    Tente de normaliser une date en YYYY-MM-DD.
    Pour le proto, retourne la chaîne nettoyée (espaces en moins) ; une regex ou dateutil peut être ajoutée.
    """
    if not value or not isinstance(value, str):
        return value
    return value.strip()
