"""
Servicio para manejar las llamadas a Google Gemini usando la nueva API
"""
import asyncio
from google import genai
import json
from typing import Dict, Any
import threading
import time
import fitz  # PyMuPDF
import requests
import tempfile
import os
from io import BytesIO
from .prompts.cv_analysis_prompts import get_cv_analysis_prompt, get_cv_analysis_basic_prompt, get_cv_analysis_detailed_prompt
from .cv_analysis_schema import CVAnalysisResult, CVAnalysisBasic, CVAnalysisDetailed


class AIService:
    def __init__(self, api_key: str):
        """Inicializa el servicio de IA con la API key"""
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

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

    def call_gemini(self, prompt: str, file_url: str) -> CVAnalysisResult:
        """
        Realiza una llamada síncrona a Gemini usando la nueva API con responseSchema
        """
        try:
            print(f"🔄 Iniciando llamada completa con modelo: {self.model}")
            start_time = time.time()
            
            # Realizar la llamada a Gemini directamente con la URL del PDF
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, file_url],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": CVAnalysisResult,
                    "temperature": 1,  # Configuración para análisis completo (fallback)
                },
            )
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"✅ Llamada completa completada en {elapsed_time:.2f} segundos")
            
            # Retornar el objeto parseado directamente
            return response.parsed
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"❌ Error en llamada a Gemini (completa) después de {elapsed_time:.2f} segundos: {e}")
            raise e

    def call_gemini_basic(self, prompt: str, file_url: str) -> CVAnalysisBasic:
        """
        Realiza una llamada síncrona a Gemini para el análisis básico
        """
        try:
            print(f"🔄 Iniciando llamada básica con modelo: {self.model}")
            start_time = time.time()
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, file_url],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": CVAnalysisBasic,
                    "temperature": 0.0,  # Configuración específica para análisis básico
                },
            )
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"✅ Llamada básica completada en {elapsed_time:.2f} segundos")
            
            return response.parsed
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"❌ Error en llamada a Gemini (análisis básico) después de {elapsed_time:.2f} segundos: {e}")
            raise e

    def call_gemini_detailed(self, prompt: str, file_url: str) -> CVAnalysisDetailed:
        """
        Realiza una llamada síncrona a Gemini para el análisis detallado
        """
        try:
            print(f"🔄 Iniciando llamada detallada con modelo: {self.model}")
            start_time = time.time()
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, file_url],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": CVAnalysisDetailed,
                    "temperature": 0.0,  # Configuración específica para análisis detallado
                },
            )
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"✅ Llamada detallada completada en {elapsed_time:.2f} segundos")
            
            return response.parsed
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"❌ Error en llamada a Gemini (análisis detallado) después de {elapsed_time:.2f} segundos: {e}")
            raise e

    def _call_gemini_thread(self, prompt: str, file_url: str, result_container: list, index: int):
        """
        Función auxiliar para llamadas en thread
        """
        try:
            response = self.call_gemini(prompt, file_url)
            if response:
                result_container[index] = response
        except Exception as e:
            print(f"Error en thread {index}: {e}")

    def _call_gemini_basic_thread(self, prompt: str, file_url: str, result_container: list, index: int):
        """
        Función auxiliar para llamadas en thread del análisis básico
        """
        try:
            print(f"🔄 Iniciando análisis básico en thread {index}")
            response = self.call_gemini_basic(prompt, file_url)
            if response:
                result_container[index] = response
                print(f"✅ Análisis básico completado en thread {index}")
            else:
                print(f"❌ Análisis básico retornó None en thread {index}")
        except Exception as e:
            print(f"❌ Error en thread básico {index}: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            result_container[index] = None

    def _call_gemini_detailed_thread(self, prompt: str, file_url: str, result_container: list, index: int):
        """
        Función auxiliar para llamadas en thread del análisis detallado
        """
        try:
            print(f"🔄 Iniciando análisis detallado en thread {index}")
            response = self.call_gemini_detailed(prompt, file_url)
            if response:
                result_container[index] = response
                print(f"✅ Análisis detallado completado en thread {index}")
            else:
                print(f"❌ Análisis detallado retornó None en thread {index}")
        except Exception as e:
            print(f"❌ Error en thread detallado {index}: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            result_container[index] = None



    def _patch_response_with_match_score(self, analysis_result: Dict[str, Any], match_score: float) -> Dict[str, Any]:
        """
        Parchea la respuesta JSON para asegurar que el match_score se incluya en main_analysis.score
        """
        try:
            # Validar que analysis_result no sea None
            if analysis_result is None:
                print("⚠️ analysis_result es None, no se puede parchear")
                return {}
            
            # Validar que analysis_result sea un diccionario
            if not isinstance(analysis_result, dict):
                print(f"⚠️ analysis_result no es un diccionario, es: {type(analysis_result)}")
                return {}
            
            # Validar que match_score esté en el rango correcto (0-100)
            if match_score is not None:
                if match_score < 0 or match_score > 100:
                    print(f"⚠️ Warning: match_score ({match_score}) está fuera del rango 0-100")
                    # Ajustar al rango válido
                    match_score = max(0, min(100, match_score))
                    print(f"✅ Ajustado match_score a: {match_score}")
            
            # Crear una copia del resultado para no modificar el original
            patched_result = analysis_result.copy()
            
            # Asegurar que main_analysis existe
            if 'main_analysis' not in patched_result:
                patched_result['main_analysis'] = {}
            
            # Si se proporcionó match_score, SIEMPRE usarlo exactamente como está
            current_score = patched_result['main_analysis'].get('score', None)
            
            # Si hay match_score, usarlo exactamente sin importar la diferencia
            if match_score is not None:
                patched_result['main_analysis']['score'] = int(match_score)
                
                # Actualizar el ai_feedback si no menciona el match_score
                current_feedback = patched_result['main_analysis'].get('ai_feedback', '')
                if 'match_score' not in current_feedback.lower() and 'ats' not in current_feedback.lower():
                    patched_result['main_analysis']['ai_feedback'] = (
                        f"Score ATS proporcionado: {match_score}. " + current_feedback
                    )
                
                print(f"✅ Parcheado main_analysis.score con match_score: {match_score}")
            
            # También asegurar que ats_compliance tenga el score correcto
            if 'ats_compliance' in patched_result and match_score is not None:
                patched_result['ats_compliance']['score'] = int(match_score)
                print(f"✅ Parcheado ats_compliance.score con match_score: {match_score}")
            
            return patched_result
            
        except Exception as e:
            print(f"⚠️ Error al parchear respuesta con match_score: {e}")
            return analysis_result

    def analyze_cv_complete(self, file_url: str, puesto: str, filename: str, descripcion_puesto: str = None, match_score: float = None) -> Dict[str, Any]:
        """
        Realiza el análisis completo del CV usando procesamiento paralelo optimizado
        Divide el análisis en dos partes que se ejecutan en paralelo para reducir el tiempo de respuesta
        """
        try:
            # Obtener y validar el número de páginas del PDF
            page_count = self.get_pdf_page_count(file_url)
            
            # Generar prompts para cada parte del análisis
            basic_prompt = get_cv_analysis_basic_prompt(puesto, filename, descripcion_puesto, page_count, match_score)
            detailed_prompt = get_cv_analysis_detailed_prompt(puesto, filename, descripcion_puesto, page_count, match_score)
            
            print("🚀 Iniciando análisis paralelo: Parte 1 (Básico) y Parte 2 (Detallado)")
            
            # Contenedores para almacenar las respuestas (usar listas para poder modificar desde los threads)
            basic_results = [None]
            detailed_results = [None]
            
            # Crear threads para análisis paralelo
            basic_thread = threading.Thread(
                target=self._call_gemini_basic_thread,
                args=(basic_prompt, file_url, basic_results, 0)
            )
            
            detailed_thread = threading.Thread(
                target=self._call_gemini_detailed_thread,
                args=(detailed_prompt, file_url, detailed_results, 0)
            )
            
            # Iniciar ambos threads
            start_time = time.time()
            basic_thread.start()
            detailed_thread.start()
            
            print("🔄 Threads iniciados, esperando completación...")
            
            # Esperar a que ambos threads terminen
            basic_thread.join()
            detailed_thread.join()
            
            end_time = time.time()
            total_thread_time = end_time - start_time
            print(f"⏱️ Tiempo total de threads: {total_thread_time:.2f} segundos")
            
            # Obtener los resultados
            basic_result = basic_results[0]
            detailed_result = detailed_results[0]
            
            print(f"📊 Resultados obtenidos:")
            print(f"   - Análisis básico: {'✅ Completado' if basic_result else '❌ Falló'}")
            print(f"   - Análisis detallado: {'✅ Completado' if detailed_result else '❌ Falló'}")
            
            # Mostrar resumen de tiempos
            print(f"📈 Resumen de tiempos:")
            print(f"   - Tiempo total paralelo: {total_thread_time:.2f} segundos")
            print(f"   - Si fuera secuencial: ~{total_thread_time * 2:.2f} segundos (estimado)")
            print(f"   - Ahorro estimado: ~{total_thread_time:.2f} segundos")
            
            # Verificar que ambos análisis se completaron exitosamente
            if basic_result is None:
                raise Exception("No se pudo completar el análisis básico - revisa los logs anteriores para más detalles")
            
            if detailed_result is None:
                raise Exception("No se pudo completar el análisis detallado - revisa los logs anteriores para más detalles")
            
            print("✅ Análisis paralelo completado exitosamente")
            
            # Combinar los resultados
            combined_result = self._combine_analysis_results(basic_result, detailed_result)
            
            # Parchear la respuesta con match_score si se proporcionó
            if match_score is not None:
                combined_result = self._patch_response_with_match_score(combined_result, match_score)
            
            return combined_result
            
        except Exception as e:
            print(f"❌ Error en análisis paralelo: {e}")
            print("🔄 Intentando análisis completo como fallback...")
            
            # Fallback: usar el método original completo
            try:
                print("🔄 Iniciando análisis completo de fallback...")
                fallback_start_time = time.time()
                
                comprehensive_prompt = get_cv_analysis_prompt(puesto, filename, descripcion_puesto, page_count, match_score)
                result = self.call_gemini(comprehensive_prompt, file_url)
                if result:
                    combined_result = result.model_dump()
                    
                    fallback_end_time = time.time()
                    fallback_total_time = fallback_end_time - fallback_start_time
                    print(f"✅ Análisis completo de fallback exitoso en {fallback_total_time:.2f} segundos")
                    
                    # Parchear la respuesta con match_score si se proporcionó
                    if match_score is not None:
                        combined_result = self._patch_response_with_match_score(combined_result, match_score)
                    
                    return combined_result
                else:
                    raise Exception("Análisis completo de fallback retornó None")
            except Exception as fallback_error:
                print(f"❌ Error en análisis de fallback: {fallback_error}")
                raise Exception(f"Tanto el análisis paralelo como el fallback fallaron. Error paralelo: {e}. Error fallback: {fallback_error}")
                
        except Exception as e:
            print(f"Error en analyze_cv_complete: {e}")
            raise e

    def _combine_analysis_results(self, basic_result: CVAnalysisBasic, detailed_result: CVAnalysisDetailed) -> Dict[str, Any]:
        """
        Combina los resultados del análisis básico y detallado en un solo diccionario
        """
        try:
            # Convertir ambos resultados a diccionarios
            basic_dict = basic_result.model_dump()
            detailed_dict = detailed_result.model_dump()
            
            # Combinar los diccionarios
            combined_dict = {**basic_dict, **detailed_dict}
            
            print("🔗 Resultados combinados exitosamente")
            return combined_dict
            
        except Exception as e:
            print(f"Error al combinar resultados: {e}")
            raise e
