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

def clean_and_load_json(response_str):
    """Elimina bloques de markdown como ```json ... ``` y carga el JSON"""
    cleaned = re.sub(r"```(?:json)?\n?", "", response_str.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned.strip())
    return json.loads(cleaned)

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

def extract_email(text):
    """Extrae el email del texto"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    
    if email_match:
        return email_match.group(0)
    else:
        return None

def extract_phone(text):
    """Extrae el teléfono del texto"""
    phone_pattern = r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        return phone_match.group(0)
    else:
        return "No disponible"

def extract_linkedin(text):
    """Extrae el enlace de LinkedIn del texto"""
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+'
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        return linkedin_match.group(0)
    else:
        return "No disponible"

def extract_address(text):
    """Extrae la dirección del texto"""
    address_pattern = r'(?:Calle|Av\.|Avenida|Pje\.)\s?[a-zA-Z0-9\s,.-]+'
    address_match = re.search(address_pattern, text)
    if address_match:
        return address_match.group(0)
    else:
        return "No disponible"

def es_json_valido(texto):
    """Verifica si un texto es un JSON válido"""
    try:
        json.loads(texto)
        return True
    except json.JSONDecodeError:
        return False

def safe_json_load(data):
    """Carga JSON de forma segura"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def process_formatting_response(response):
    """Procesa la respuesta de formato y lenguaje"""
    formatting_data = safe_json_load(response)

    if formatting_data is None or "formattingAndLanguage" not in formatting_data:
        formatting_data = {
            "formattingAndLanguage": {
                "clarity": "No disponible",
                "professionalism": "No disponible",
                "grammarSpellingErrorsCount": 0,
                "actionVerbsUsed": False
            }
        }

    formatting_data["formattingAndLanguage"].setdefault("clarity", "No disponible")
    formatting_data["formattingAndLanguage"].setdefault("professionalism", "No disponible")
    formatting_data["formattingAndLanguage"].setdefault("grammarSpellingErrorsCount", 0)
    formatting_data["formattingAndLanguage"].setdefault("actionVerbsUsed", False)

    return formatting_data

def process_keywords_response(response):
    """Procesa la respuesta de análisis de palabras clave"""
    keywords_data = safe_json_load(response)

    if keywords_data is None or "keywordAnalysis" not in keywords_data:
        keywords_data = {
            "keywordAnalysis": {
                "jobKeywordsFound": [],
                "jobKeywordsMissing": [],
                "generalSkillsKeywordsFound": []
            }
        }

    keywords_data["keywordAnalysis"].setdefault("jobKeywordsFound", [])
    keywords_data["keywordAnalysis"].setdefault("jobKeywordsMissing", [])
    keywords_data["keywordAnalysis"].setdefault("generalSkillsKeywordsFound", [])

    return keywords_data

def process_ats_response(response):
    """Procesa la respuesta de cumplimiento ATS"""
    ats_data = safe_json_load(response)

    if ats_data is None or "atsCompliance" not in ats_data:
        ats_data = {
            "atsCompliance": {
                "score": 0,
                "issues": [],
                "recommendations": []
            }
        }

    ats_data["atsCompliance"].setdefault("score", 0)
    ats_data["atsCompliance"].setdefault("issues", [])
    ats_data["atsCompliance"].setdefault("recommendations", [])

    return ats_data

def process_skills_response(response):
    """Procesa la respuesta de habilidades"""
    skills_data = safe_json_load(response)

    if skills_data is None or "skills" not in skills_data:
        skills_data = {
            "skills": {
                "technical": [],
                "soft": [],
                "languages": []
            }
        }

    skills_data["skills"].setdefault("technical", [])
    skills_data["skills"].setdefault("soft", [])
    skills_data["skills"].setdefault("languages", [])

    return skills_data
