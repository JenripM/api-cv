"""
Servicio para manejar las llamadas a OpenAI usando la nueva API
"""
import asyncio
from openai import OpenAI
import json
from typing import Dict, Any
import threading
import time
from .prompts.cv_analysis_prompts import get_cv_analysis_prompt


class AIService:
    def __init__(self, api_key: str):
        """Inicializa el servicio de IA con la API key"""
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5-mini"

    def call_openai(self, prompt: str, file_url: str) -> str:
        """
        Realiza una llamada síncrona a OpenAI usando la nueva API
        """
        try:
            content = [
                {
                    "type": "input_text",
                    "text": prompt
                },
                {
                    "type": "input_file",
                    "file_url": file_url
                }
            ]
            
            params = {
                "model": self.model,
                "input": [{
                    "role": "user",
                    "content": content
                }],
                "reasoning": {
                    "effort": "minimal"
                }
            }
            
            # Usar la versión síncrona del cliente OpenAI
            response = self.client.responses.create(**params)
            
            return response.output_text
        except Exception as e:
            print(f"Error en llamada a OpenAI: {e}")
            return ""

    def _call_openai_thread(self, prompt: str, file_url: str, result_container: list, index: int):
        """
        Función auxiliar para llamadas en thread
        """
        try:
            response = self.call_openai(prompt, file_url)
            if response and response.strip():
                result_container[index] = response
        except Exception as e:
            print(f"Error en thread {index}: {e}")

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extrae y valida JSON de la respuesta de la IA
        """
        if not response or response.strip() == "":
            raise Exception("Respuesta vacía de OpenAI")
        
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

    def analyze_cv_complete(self, file_url: str, puesto: str, filename: str) -> Dict[str, Any]:
        """
        Realiza el análisis completo del CV usando llamadas paralelas para redundancia
        """
        try:
            comprehensive_prompt = get_cv_analysis_prompt(puesto, filename)
            
            # Contenedor para almacenar las respuestas de los threads
            results = [None, None]
            threads = []
            
            # Crear dos threads para llamadas paralelas
            for i in range(2):
                thread = threading.Thread(
                    target=self._call_openai_thread,
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
            
            return valid_result
                
        except Exception as e:
            print(f"Error en analyze_cv_complete: {e}")
            raise e
