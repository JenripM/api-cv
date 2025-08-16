"""
Servicio para procesar y extraer datos del CV
"""
import requests
from io import BytesIO
from datetime import datetime
import time
from services.ai_utils import (
    extract_email, extract_phone, extract_linkedin, extract_address,
    generate_analysis_id, generate_user_id
)
from services.pdf_generator.pdf_utils import descargar_imagen


class CVProcessor:
    def __init__(self):
        """Inicializa el procesador de CV"""
        pass

    def extract_contact_info(self, contenido: str) -> dict:
        """
        Extrae información de contacto del contenido del CV
        
        Args:
            contenido: Texto del CV
            
        Returns:
            Diccionario con la información de contacto
        """
        return {
            "email": extract_email(contenido),
            "phone": extract_phone(contenido),
            "linkedin": extract_linkedin(contenido),
            "address": extract_address(contenido)
        }

    def prepare_analysis_data(self, contenido: str, puesto: str, original_pdf: str, 
                            candidate_name: dict, analysis_results: dict) -> dict:
        """
        Prepara los datos para el análisis final
        
        Args:
            contenido: Texto del CV (ahora es placeholder ya que OpenAI lee directamente)
            puesto: Puesto al que postula
            original_pdf: URL del PDF original
            candidate_name: Nombre del candidato extraído
            analysis_results: Resultados del análisis de IA
            
        Returns:
            Diccionario con los datos preparados para el análisis
        """
        start_time = time.time()
        end_time = time.time()
        processing_time_ms = int((end_time - start_time) * 1000)
        analysis_datetime = datetime.now().isoformat()
        
        # Extraer información de contacto (ahora desde los resultados de IA)
        # Como OpenAI lee directamente el PDF, usamos placeholder para contact_info
        contact_info = {
            "email": "Extraído por IA",
            "phone": "Extraído por IA", 
            "linkedin": "Extraído por IA",
            "address": "Extraído por IA"
        }
        
        # Calcular puntaje general
        parsed = analysis_results.get("mainly_analysis", {})
        overall_score = f"{parsed.get('percentage', 0)}/10"
        
        # Preparar datos extraídos
        extracted_data = {
            "cvAnalysisId": generate_analysis_id(candidate_name.get("name", "")),
            "userId": generate_user_id(candidate_name.get("name", "")),
            "jobPositionApplied": puesto,
            "cvOriginalFileUrl": original_pdf,
            "analysisDateTime": analysis_datetime,
            "processingTimeMs": processing_time_ms,
            "extractedData": {
                "candidateName": candidate_name.get("name", ""),
                "contactInfo": {
                    "email": contact_info["email"],
                    "phone": contact_info["phone"],
                    "linkedin": contact_info["linkedin"],
                    "address": contact_info["address"]
                },
                "professionalSummary": overall_score,
                "workExperience": analysis_results.get("work_experience", []),
                "education": analysis_results.get("education", []),
                "skills": analysis_results.get("skills", {}).get("skills", {}),
                "rawText": "[PDF content read directly by OpenAI]",
            },
            "analysisResults": {
                "overallScore": overall_score,
                "atsCompliance": analysis_results.get("ats_compliance", {}).get("atsCompliance", {}),
                "strengths": analysis_results.get("strengths", ""),
                "areasForImprovement": analysis_results.get("common_errors", ""),
                "keywordAnalysis": analysis_results.get("keywords", {}).get("keywordAnalysis", {}),
                "formattingAndLanguage": analysis_results.get("formatting", {}).get("formattingAndLanguage", {}),
                "feedbackSummary": analysis_results.get("feedback_summary", "")
            }
        }
        
        return extracted_data

    def download_logos(self) -> tuple:
        """
        Descarga los logos necesarios para el PDF
        
        Returns:
            Tupla con las rutas de los logos
        """
        logo_url = "https://myworkin.pe/MyWorkIn-web.png"
        ruta_logo = "static/analisis_pdfs/logo.png"
        ruta_logo2 = "static/analisis_pdfs/MyWorkIn 2.png"
        
        descargar_imagen(logo_url, ruta_logo)
        
        return ruta_logo, ruta_logo2

    def generate_pdf_filename(self) -> str:
        """
        Genera un nombre único para el archivo PDF
        
        Returns:
            Nombre del archivo PDF
        """
        return f"analisis_cv_{int(datetime.timestamp(datetime.now()))}.pdf"

    def build_final_response(self, analysis_results: dict, puesto: str, 
                           candidate_name: dict, extracted_data: dict,
                           nombre_pdf: str, ruta_pdf: str) -> dict:
        """
        Construye la respuesta final del análisis
        
        Args:
            analysis_results: Resultados del análisis de IA
            puesto: Puesto al que postula
            candidate_name: Nombre del candidato
            extracted_data: Datos extraídos del CV
            nombre_pdf: Nombre del archivo PDF
            ruta_pdf: Ruta del archivo PDF generado
            
        Returns:
            Diccionario con la respuesta final
        """
        ruta_completa = f'https://myworkin-cv-2.onrender.com/static/analisis_pdfs/{nombre_pdf}'
        
        # Actualizar la URL del PDF en los resultados
        extracted_data["analysisResults"]["pdf_url"] = ruta_completa
        
        return {
            "name": candidate_name,
            "mainly_analysis": analysis_results.get("mainly_analysis", {}),
            "pagination": analysis_results.get("pagination", {}),
            "spelling": analysis_results.get("spelling", {}),
            "filename": analysis_results.get("filename", {}),
            "indispensable": analysis_results.get("indispensable", {}),
            "repeat_words": analysis_results.get("repeat_words", {}),
            "relevance": analysis_results.get("relevance", ""),
            "impact_verbs": analysis_results.get("impact_verbs", {}),
            "professional_profile": analysis_results.get("professional_profile", {}),
            "position_adjustment": analysis_results.get("position_adjustment", {}),
            "work_experience": analysis_results.get("work_experience", []),
            "skills_tools": analysis_results.get("skills_tools", []),
            "education": analysis_results.get("education", []),
            "volunteering": analysis_results.get("volunteering", {}),
            "format_optimization": analysis_results.get("format_optimization", {}),
            "job_position": puesto,
            "status": "success",
            "message": "CV procesado y análisis guardado exitosamente.",
            "analysis_id": generate_analysis_id(candidate_name.get("name", "")),
            "extractedData": extracted_data,
            "pdf_evaluated": ruta_pdf
        }
