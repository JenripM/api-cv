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
from .prompts.cv_analysis_prompts import get_cv_analysis_prompt


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

    def call_gemini(self, prompt: str, file_url: str) -> str:
        """
        Realiza una llamada síncrona a Gemini usando la nueva API
        """
        try:
            # Realizar la llamada a Gemini directamente con la URL del PDF
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, file_url],
            )
            
            return response.text
        except Exception as e:
            print(f"Error en llamada a Gemini: {e}")
            return ""

    def _call_gemini_thread(self, prompt: str, file_url: str, result_container: list, index: int):
        """
        Función auxiliar para llamadas en thread
        """
        try:
            response = self.call_gemini(prompt, file_url)
            if response and response.strip():
                result_container[index] = response
        except Exception as e:
            print(f"Error en thread {index}: {e}")

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extrae y valida JSON de la respuesta de la IA
        """
        if not response or response.strip() == "":
            raise Exception("Respuesta vacía de Gemini")
        
        # Limpiar la respuesta para extraer solo el JSON
        response_clean = response.strip()
        
        # Buscar el inicio del JSON
        start_idx = response_clean.find('{')
        if start_idx == -1:
            raise Exception("No se encontró JSON válido en la respuesta")
        
        # Buscar el final del JSON (última llave de cierre)
        brace_count = 0
        end_idx = -1
        for i in range(start_idx, len(response_clean)):
            if response_clean[i] == '{':
                brace_count += 1
            elif response_clean[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break
        
        if end_idx == -1:
            raise Exception("JSON incompleto en la respuesta")
        
        json_str = response_clean[start_idx:end_idx + 1]
        
        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError as e:
            raise Exception(f"JSON inválido: {str(e)}")

    def _patch_response_with_match_score(self, analysis_result: Dict[str, Any], match_score: float) -> Dict[str, Any]:
        """
        Parchea la respuesta JSON para asegurar que el match_score se incluya en main_analysis.score
        """
        try:
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
        Realiza el análisis completo del CV usando llamadas paralelas para redundancia
        """
        try:
            # Obtener y validar el número de páginas del PDF
            page_count = self.get_pdf_page_count(file_url)
            
            # Si llegamos aquí, el PDF es válido y tiene páginas
            comprehensive_prompt = get_cv_analysis_prompt(puesto, filename, descripcion_puesto, page_count, match_score)
            
            # Contenedor para almacenar las respuestas de los threads
            results = [None, None]
            threads = []
            
            # Crear dos threads para llamadas paralelas
            for i in range(2):
                thread = threading.Thread(
                    target=self._call_gemini_thread,
                    args=(comprehensive_prompt, file_url, results, i)
                )
                threads.append(thread)
                thread.start()
            
            # Esperar por la primera respuesta válida
            valid_result = None
            completed_threads = 0
            
            while completed_threads < 2 and valid_result is None:
                for i, result in enumerate(results):
                    if result is not None:
                        try:
                            valid_result = self._extract_json_from_response(result)
                            print(f"Respuesta válida obtenida del thread {i}")
                            break
                        except Exception as e:
                            print(f"Thread {i} retornó respuesta inválida: {e}")
                            results[i] = None  # Marcar como procesado
                
                # Verificar si algún thread terminó
                for i, thread in enumerate(threads):
                    if not thread.is_alive() and results[i] is None:
                        results[i] = ""  # Marcar como completado pero vacío
                        completed_threads += 1
                
                if valid_result is None:
                    time.sleep(0.1)  # Pequeña pausa para no saturar CPU
            
            # Si no se obtuvo respuesta válida, esperar a que terminen todos los threads
            if valid_result is None:
                for thread in threads:
                    thread.join()
                
                # Intentar procesar cualquier respuesta restante
                for i, result in enumerate(results):
                    if result and result.strip():
                        try:
                            valid_result = self._extract_json_from_response(result)
                            print(f"Respuesta válida obtenida del thread {i} después de esperar")
                            break
                        except Exception as e:
                            print(f"Thread {i} retornó respuesta inválida final: {e}")
            
            if valid_result is None:
                raise Exception("No se pudo obtener una respuesta válida de ninguna llamada a la IA")
            
            # Parchear la respuesta con match_score si se proporcionó
            if match_score is not None:
                valid_result = self._patch_response_with_match_score(valid_result, match_score)
            
            return valid_result
                
        except Exception as e:
            print(f"Error en analyze_cv_complete: {e}")
            raise e
