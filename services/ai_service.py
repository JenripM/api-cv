"""
Servicio para manejar las llamadas a Google Gemini usando la nueva API
"""
from google import genai
from google.genai import types
import json
from typing import Dict, Any
import time
import fitz  # PyMuPDF
import requests
from .prompts.cv_analysis_prompts import get_cv_analysis_prompt
from .cv_analysis_schema import CVAnalysisResult


class AIService:
    def __init__(self, api_key: str):
        """Inicializa el servicio de IA con la API key"""
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash-lite"

    def get_pdf_page_count(self, file_url: str) -> int:
        """
        Obtiene el número de páginas de un PDF desde una URL
        Lanza excepción si el PDF está vacío o corrupto
        """
        try:
            # Descargar el PDF temporalmente
            response = requests.get(file_url, timeout=30)
            response.raise_for_status()
            
            # Verificar que el contenido no esté vacío
            if not response.content or len(response.content) == 0:
                raise Exception("El PDF está vacío")
            
            # Abrir el PDF con PyMuPDF
            pdf_document = fitz.open(stream=response.content, filetype="pdf")
            
            # Obtener el número de páginas
            page_count = len(pdf_document)
            pdf_document.close()
            
            # Verificar que tiene al menos una página
            if page_count == 0:
                raise Exception("El PDF no contiene páginas")
            
            print(f"📄 PDF tiene {page_count} páginas")
            return page_count
            
        except requests.RequestException as e:
            raise Exception(f"No se pudo descargar el PDF: {str(e)}")
        except Exception as e:
            if "vacío" in str(e).lower() or "corrupto" in str(e).lower() or "no contiene páginas" in str(e).lower():
                raise Exception(f"PDF inválido: {str(e)}")
            else:
                raise Exception(f"Error al procesar el PDF: {str(e)}")





    def _patch_response_with_match_score(self, analysis_result: Dict[str, Any], match_score: float) -> Dict[str, Any]:
        """Aplica el match_score a la respuesta del análisis"""
        if not analysis_result or not isinstance(analysis_result, dict):
            return analysis_result or {}
        
        # Ajustar match_score al rango válido
        match_score = max(0, min(100, match_score))
        
        patched_result = analysis_result.copy()
        
        # Aplicar match_score a main_analysis
        if 'main_analysis' not in patched_result:
            patched_result['main_analysis'] = {}
        
        patched_result['main_analysis']['score'] = int(match_score)
        
        # Aplicar match_score a ats_compliance
        if 'ats_compliance' in patched_result:
            patched_result['ats_compliance']['score'] = int(match_score)
        
        return patched_result

    def analyze_cv_single(self, cv_data: dict, pdf_url: str, puesto: str, filename: str, descripcion_puesto: str = None, match_score: float = None) -> Dict[str, Any]:
        """
        Analiza el CV usando una sola llamada a Gemini con thinking habilitado
        """
        try:
            print("🚀 Iniciando análisis de CV")
            
            # Calcular número de páginas del PDF
            page_count = self.get_pdf_page_count(pdf_url)
            
            # Preparar datos y prompt
            cv_text = self._format_cv_data_to_text(cv_data)
            complete_prompt = get_cv_analysis_prompt(puesto, filename, descripcion_puesto, page_count, match_score)
            
            # Llamada a Gemini
            start_time = time.time()
            response = self.client.models.generate_content(
                model=self.model,
                contents=[complete_prompt, cv_text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CVAnalysisResult,
                    temperature=1,
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=1024,
                        include_thoughts=True
                    )
                ),
            )
            
            print(f"⏱️ Análisis completado en {time.time() - start_time:.2f}s")
            
            # Verificar respuesta
            if not response.parsed:
                raise Exception("Fallo en análisis: respuesta vacía")
            
            # Convertir a diccionario y aplicar match_score si existe
            result_dict = response.parsed.model_dump() if hasattr(response.parsed, 'model_dump') else response.parsed
            if match_score is not None:
                result_dict = self._patch_response_with_match_score(result_dict, match_score)
            
            # Generar campos "current" desde cv_data
            result_dict = self._add_current_fields_from_cv_data(result_dict, cv_data)
            
            # Agregar información de tokens al resultado
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                result_dict['token_usage'] = {
                    'input_tokens': response.usage_metadata.prompt_token_count,
                    'output_tokens': response.usage_metadata.candidates_token_count,
                    'total_tokens': response.usage_metadata.total_token_count,
                    'model_used': self.model
                }
            
            return result_dict
            
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            raise e

    def _format_cv_data_to_text(self, cv_data: dict) -> str:
        """Convierte los datos del CV a JSON string"""
        return f"DATOS DEL CV:\n{json.dumps(cv_data, ensure_ascii=False, indent=2)}"

    def _add_current_fields_from_cv_data(self, result_dict: dict, cv_data: dict) -> dict:
        """Agrega campos 'current' desde cv_data al resultado"""
        try:
            # Work Experience Analysis
            if 'work_experience_analysis' in result_dict and 'workExperience' in cv_data:
                for work_analysis in result_dict['work_experience_analysis']:
                    # Buscar experiencia por ID
                    work_id = work_analysis.get('id')
                    if work_id:
                        matching_exp = next((exp for exp in cv_data['workExperience'] 
                                           if exp.get('id') == work_id), None)
                        if matching_exp:
                            # Usar achievements para work experience
                            achievements = matching_exp.get('achievements', [])
                            if achievements:
                                current_desc = ". ".join(achievements)
                            else:
                                current_desc = "No hay logros disponibles"
                            
                            work_analysis['current'] = current_desc

            # Skills Tools Analysis
            if 'skills_tools_analysis' in result_dict and 'skills' in cv_data:
                skills_list = []
                for skill in cv_data['skills']:
                    skill_desc = skill.get('name', '')
                    if skill.get('level'):
                        skill_desc += f" ({skill['level']})"
                    skills_list.append(skill_desc)
                
                result_dict['skills_tools_analysis']['current_skills'] = ', '.join(skills_list)

            # Volunteering Analysis
            if 'volunteering_analysis' in result_dict and 'volunteer' in cv_data:
                for volunteer_analysis in result_dict['volunteering_analysis']:
                    # Buscar voluntariado por ID
                    volunteer_id = volunteer_analysis.get('id')
                    if volunteer_id:
                        matching_volunteer = next((vol for vol in cv_data['volunteer'] 
                                                 if vol.get('id') == volunteer_id), None)
                        if matching_volunteer:
                            # Usar description para volunteering (puede ser 'description' o 'descripcion')
                            current_desc = matching_volunteer.get('description') or matching_volunteer.get('descripcion', 'No hay descripción')
                            volunteer_analysis['current'] = current_desc

            # Executive Summary Analysis
            if 'executive_summary_analysis' in result_dict and 'personalInfo' in cv_data:
                summary = cv_data['personalInfo'].get('summary', '')
                if summary:
                    result_dict['executive_summary_analysis']['current'] = summary

            return result_dict
            
        except Exception as e:
            print(f"⚠️ Error al agregar campos current: {e}")
            return result_dict

    def analyze_cv_complete(self, cv_data: dict, pdf_url: str, puesto: str, filename: str, descripcion_puesto: str = None, match_score: float = None) -> Dict[str, Any]:
        """Analiza el CV usando una sola llamada a Gemini"""
        return self.analyze_cv_single(cv_data, pdf_url, puesto, filename, descripcion_puesto, match_score)


