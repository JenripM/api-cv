"""
Servicio para manejar las llamadas a OpenAI usando la nueva API
"""
import asyncio
from openai import OpenAI
import json
from typing import Dict, Any
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

    def analyze_cv_complete(self, file_url: str, puesto: str, filename: str) -> Dict[str, Any]:
        """
        Realiza el análisis completo del CV usando un solo prompt comprehensivo
        """
        try:
            comprehensive_prompt = get_cv_analysis_prompt(puesto, filename)
            response = self.call_openai(comprehensive_prompt, file_url)
            
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
                
        except Exception as e:
            print(f"Error en analyze_cv_complete: {e}")
            raise e
