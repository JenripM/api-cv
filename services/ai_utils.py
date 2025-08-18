import json
import re
import hashlib
from datetime import datetime
from urllib.parse import urlparse

def obtener_nombre_archivo_desde_url(url: str) -> str:
    """
    Extrae el nombre del archivo desde una URL.
    Ej: https://myworkinpe.lat/pdfs/cv_1744315148575_4af9adfd.pdf → cv_1744315148575_4af9adfd.pdf
    """
    parsed_url = urlparse(url)
    return parsed_url.path.split("/")[-1]


def generate_analysis_id(candidate_name):
    """Genera un ID único para el análisis"""
    # Extrae iniciales del nombre
    initials = ''.join([word[0] for word in candidate_name.split() if word]).upper()

    # Fecha y hora actual
    now = datetime.now().strftime('%Y%m%d%H%M%S')

    # Hash corto basado en nombre y timestamp
    hash_short = hashlib.md5((candidate_name + now).encode()).hexdigest()[:6]

    # ID único
    return f"{initials}-{now}-{hash_short}"

def generate_user_id(candidate_name):
    """Genera un ID único para el usuario"""
    normalized_name = candidate_name.lower().replace(" ", "")
    hash_short = hashlib.md5(normalized_name.encode()).hexdigest()[:8]
    return f"user_{hash_short}"

