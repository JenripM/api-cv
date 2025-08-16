"""
Servicio para manejar las llamadas a OpenAI de forma asíncrona usando la nueva API
"""
import asyncio
from openai import OpenAI
import json
import requests
from typing import Dict, Any, List
from services.ai_utils import clean_and_load_json, process_formatting_response, process_keywords_response, process_ats_response, process_skills_response, safe_json_load


class AIService:
    def __init__(self, api_key: str):
        """Inicializa el servicio de IA con la API key"""
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.temperature = 1

    def _is_valid_response(self, response: str) -> bool:
        """
        Verifica si una respuesta de OpenAI es válida
        
        Args:
            response: La respuesta a verificar
            
        Returns:
            True si la respuesta es válida, False en caso contrario
        """
        return response and response.strip() != ""



    async def call_openai_async(self, prompt: str, max_tokens: int = None, file_url: str = None) -> str:
        """
        Realiza una llamada asíncrona a OpenAI usando la nueva API
        
        Args:
            prompt: El prompt a enviar
            max_tokens: Número máximo de tokens (opcional)
            file_url: URL del archivo PDF a analizar (opcional)
            
        Returns:
            La respuesta de OpenAI
        """
        try:
            # Crear una tarea asíncrona para la llamada a OpenAI
            loop = asyncio.get_event_loop()
            
            # Preparar el contenido del mensaje
            content = []
            
            # Agregar el texto del prompt
            content.append({
                "type": "input_text",
                "text": prompt
            })
            
            # Si hay una URL de archivo, agregarla
            if file_url:
                content.append({
                    "type": "input_file",
                    "file_url": file_url
                })
            
            # Preparar parámetros para la llamada a OpenAI usando responses.create
            params = {
                "model": self.model,
                "input": [{
                    "role": "user",
                    "content": content
                }]
            }
            
            # Solo agregar max_tokens si tiene un valor válido
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            
            # Usar run_in_executor para ejecutar la llamada síncrona de OpenAI en un thread separado
            response = await loop.run_in_executor(
                None,
                lambda: self.client.responses.create(**params)
            )
            
            return response.output_text
        except Exception as e:
            print(f"Error en llamada a OpenAI: {e}")
            return ""

    async def analyze_basic_info(self, file_url: str, filename: str) -> Dict[str, Any]:
        """
        Analiza información básica del CV usando la nueva API de archivos
        """
        try:
            from services.prompts.cv_analysis_prompts import BASIC_INFO_PROMPTS
            
            # Crear tareas asíncronas para ambos análisis
            tasks = [
                self.call_openai_async(
                    BASIC_INFO_PROMPTS["candidate_name"].format(contenido="[PDF content will be read by AI]"),
                    file_url=file_url
                ),
                self.call_openai_async(
                    BASIC_INFO_PROMPTS["filename_analysis"].format(
                        filename_json=json.dumps(filename),
                        contenido_json="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                )
            ]
            
            # Ejecutar ambas tareas en paralelo
            candidate_name, filename_response = await asyncio.gather(*tasks)
            
            # Verificar si las respuestas son válidas
            if not self._is_valid_response(candidate_name):
                print("⚠️  Respuesta vacía para candidate_name")
                candidate_name = "{}"
            
            if not self._is_valid_response(filename_response):
                print("⚠️  Respuesta vacía para filename_analysis")
                filename_response = "{}"
            
            return {
                "candidate_name": clean_and_load_json(candidate_name),
                "filename": clean_and_load_json(filename_response)
            }
        except Exception as e:
            print(f"Error en analyze_basic_info: {e}")
            raise e

    async def analyze_main_content(self, file_url: str, puesto: str) -> Dict[str, Any]:
        """
        Analiza el contenido principal del CV usando la nueva API de archivos
        """
        try:
            from services.prompts.cv_analysis_prompts import MAIN_ANALYSIS_PROMPTS
            
            # Crear tareas asíncronas para ambos análisis
            tasks = [
                self.call_openai_async(
                    MAIN_ANALYSIS_PROMPTS["overall_analysis"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    MAIN_ANALYSIS_PROMPTS["feedback_summary"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                )
            ]
            
            # Ejecutar ambas tareas en paralelo
            mainly_analysis, feedback_summary = await asyncio.gather(*tasks)
            
            return {
                "mainly_analysis": clean_and_load_json(mainly_analysis),
                "feedback_summary": feedback_summary.strip()
            }
        except Exception as e:
            print(f"Error en analyze_main_content: {e}")
            raise e

    async def analyze_format(self, file_url: str, num_paginas: int, puesto: str) -> Dict[str, Any]:
        """
        Analiza el formato del CV usando la nueva API de archivos
        """
        try:
            from services.prompts.cv_analysis_prompts import FORMAT_ANALYSIS_PROMPTS
            
            # Crear tareas asíncronas para todos los análisis de formato
            tasks = [
                self.call_openai_async(
                    FORMAT_ANALYSIS_PROMPTS["pagination"].format(num_paginas=num_paginas),
                    file_url=file_url
                ),
                self.call_openai_async(
                    FORMAT_ANALYSIS_PROMPTS["spelling"].format(contenido="[PDF content will be read by AI]"),
                    file_url=file_url
                ),
                self.call_openai_async(
                    FORMAT_ANALYSIS_PROMPTS["indispensable_elements"].format(contenido="[PDF content will be read by AI]"),
                    file_url=file_url
                ),
                self.call_openai_async(
                    FORMAT_ANALYSIS_PROMPTS["repeat_words"].format(contenido="[PDF content will be read by AI]"),
                    file_url=file_url
                ),
                self.call_openai_async(
                    FORMAT_ANALYSIS_PROMPTS["format_optimization"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]", num_paginas=num_paginas
                    ),
                    file_url=file_url
                )
            ]
            
            # Ejecutar todas las tareas en paralelo
            pagination, spelling, indispensable, repeat_words, format_optimization = await asyncio.gather(*tasks)
            
            return {
                "pagination": clean_and_load_json(pagination),
                "spelling": clean_and_load_json(spelling),
                "indispensable": clean_and_load_json(indispensable),
                "repeat_words": clean_and_load_json(repeat_words),
                "format_optimization": clean_and_load_json(format_optimization)
            }
        except Exception as e:
            print(f"Error en analyze_format: {e}")
            raise e

    async def analyze_content(self, file_url: str, puesto: str) -> Dict[str, Any]:
        """
        Analiza el contenido del CV usando la nueva API de archivos
        """
        try:
            from services.prompts.cv_analysis_prompts import CONTENT_ANALYSIS_PROMPTS
            
            # Crear tareas asíncronas para todos los análisis de contenido
            tasks = [
                self.call_openai_async(
                    CONTENT_ANALYSIS_PROMPTS["experience_analysis"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    CONTENT_ANALYSIS_PROMPTS["education_analysis"].format(
                        contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    CONTENT_ANALYSIS_PROMPTS["skills_analysis"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    CONTENT_ANALYSIS_PROMPTS["achievements_analysis"].format(
                        contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                )
            ]
            
            # Ejecutar todas las tareas en paralelo
            experience, education, skills, achievements = await asyncio.gather(*tasks)
            
            return {
                "experience": clean_and_load_json(experience),
                "education": clean_and_load_json(education),
                "skills": clean_and_load_json(skills),
                "achievements": clean_and_load_json(achievements)
            }
        except Exception as e:
            print(f"Error en analyze_content: {e}")
            raise e

    async def analyze_sections(self, file_url: str, puesto: str) -> Dict[str, Any]:
        """
        Analiza las secciones del CV usando la nueva API de archivos
        """
        try:
            from services.prompts.cv_analysis_prompts import SECTION_ANALYSIS_PROMPTS
            
            # Crear tareas asíncronas para todos los análisis de secciones
            tasks = [
                self.call_openai_async(
                    SECTION_ANALYSIS_PROMPTS["work_experience"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    SECTION_ANALYSIS_PROMPTS["skills_tools"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    SECTION_ANALYSIS_PROMPTS["education"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    SECTION_ANALYSIS_PROMPTS["volunteering"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                )
            ]
            
            # Ejecutar todas las tareas en paralelo
            work_experience, skills_tools, education, volunteering = await asyncio.gather(*tasks)
            
            return {
                "work_experience": clean_and_load_json(work_experience),
                "skills_tools": clean_and_load_json(skills_tools),
                "education": clean_and_load_json(education),
                "volunteering": clean_and_load_json(volunteering)
            }
        except Exception as e:
            print(f"Error en analyze_sections: {e}")
            raise e

    async def analyze_advanced(self, file_url: str, puesto: str) -> Dict[str, Any]:
        """
        Realiza análisis avanzados del CV usando la nueva API de archivos
        """
        try:
            from services.prompts.cv_analysis_prompts import ADVANCED_ANALYSIS_PROMPTS
            
            # Crear tareas asíncronas para todos los análisis avanzados
            tasks = [
                self.call_openai_async(
                    ADVANCED_ANALYSIS_PROMPTS["formatting_language"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    ADVANCED_ANALYSIS_PROMPTS["keywords"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    ADVANCED_ANALYSIS_PROMPTS["ats_compliance"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    ADVANCED_ANALYSIS_PROMPTS["skills"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    ADVANCED_ANALYSIS_PROMPTS["education_extraction"].format(
                        puesto=puesto, contenido="[PDF content will be read by AI]"
                    ),
                    file_url=file_url
                ),
                self.call_openai_async(
                    ADVANCED_ANALYSIS_PROMPTS["common_errors"].format(contenido="[PDF content will be read by AI]"),
                    file_url=file_url
                ),
                self.call_openai_async(
                    ADVANCED_ANALYSIS_PROMPTS["strengths"].format(contenido="[PDF content will be read by AI]"),
                    file_url=file_url
                )
            ]
            
            # Ejecutar todas las tareas en paralelo
            formatting, keywords, ats_compliance, skills, education_extraction, common_errors, strengths = await asyncio.gather(*tasks)
            
            # Procesar las respuestas
            formatting_processed = process_formatting_response(formatting)
            keywords_processed = process_keywords_response(keywords)
            ats_compliance_processed = process_ats_response(ats_compliance)
            skills_processed = process_skills_response(skills)
            
            # Procesar educación
            education_data_json = safe_json_load(education_extraction)
            education = education_data_json.get("education", []) if education_data_json else []
            
            return {
                "formatting": formatting_processed,
                "keywords": keywords_processed,
                "ats_compliance": ats_compliance_processed,
                "skills": skills_processed,
                "education": education,
                "common_errors": common_errors.strip(),
                "strengths": strengths.strip()
            }
        except Exception as e:
            print(f"Error en analyze_advanced: {e}")
            raise e

    async def analyze_cv_complete(self, file_url: str, puesto: str, filename: str, num_paginas: int) -> Dict[str, Any]:
        """
        Realiza el análisis completo del CV usando la nueva API de archivos
        """
        try:
            # Crear tareas asíncronas para todos los grupos de análisis
            tasks = [
                self.analyze_basic_info(file_url, filename),
                self.analyze_main_content(file_url, puesto),
                self.analyze_format(file_url, num_paginas, puesto),
                self.analyze_content(file_url, puesto),
                self.analyze_sections(file_url, puesto),
                self.analyze_advanced(file_url, puesto)
            ]
            
            # Ejecutar todas las tareas en paralelo
            basic_info, main_content, format_analysis, content_analysis, sections_analysis, advanced_analysis = await asyncio.gather(*tasks)
            
            # Combinar todos los resultados
            return {
                **basic_info,
                **main_content,
                **format_analysis,
                **content_analysis,
                **sections_analysis,
                **advanced_analysis
            }
        except Exception as e:
            print(f"Error en analyze_cv_complete: {e}")
            raise e
