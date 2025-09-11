"""
Servicio para trackear el consumo de IA en Firestore.
"""

from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import firestore
from typing import Optional

# Precios por modelo (por 1M tokens en USD)
MODEL_PRICING = {
    "gemini-2.5-flash": {
        "input_per_1m": 0.30,
        "output_per_1m": 2.50
    },
    "gemini-2.5-flash-lite": {
        "input_per_1m": 0.10,
        "output_per_1m": 0.40
    }
}

def calculate_total_cost(input_tokens: int, output_tokens: int, model_name: str) -> float:
    """
    Calcula el costo total en USD basado en los tokens y el modelo. Con base a los precios por modelo de Gemini.
    
    Args:
        input_tokens: Número de tokens de entrada
        output_tokens: Número de tokens de salida
        model_name: Nombre del modelo (ej: "gemini-2.5-flash")
    
    Returns:
        float: Costo total en USD (ej: 0.0015)
    """
    if model_name not in MODEL_PRICING:
        return 0.0
    
    pricing = MODEL_PRICING[model_name]
    
    # Calcular costo de input tokens (convertir a millones)
    input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
    
    # Calcular costo de output tokens (convertir a millones)
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
    
    # Costo total
    total_cost = input_cost + output_cost
    
    # Redondear a 6 decimales para precisión
    return round(total_cost, 6)

def get_github_source_location(file_path: str) -> str:
    """
    Genera la URL de GitHub para un archivo específico.
    
    Args:
        file_path: Ruta del archivo relativa al repositorio (ej: "services/user_service.py")
    
    Returns:
        str: URL completa de GitHub del archivo
    """
    base_url = "https://github.com/JenripM/jobsMatch/blob/main"
    return f"{base_url}/{file_path}"

async def log_ai_consumption(input_tokens: int, output_tokens: int, model_name: str, feature_name: str, usage_description: str, user_id: str = None, source_location: str = None):
    """Registra el consumo de IA en Firestore."""
    try:
        # Obtener la instancia de Firestore
        db = firestore.client()
        
        # Calcular el costo total
        total_cost = calculate_total_cost(input_tokens, output_tokens, model_name)
        
        log_entry = {
            "inputTokens": input_tokens,
            "outputTokens": output_tokens,
            "modelName": model_name,
            "featureName": feature_name,
            "usageDescription": usage_description,
            "sourceLocation": source_location,
            "totalCost": total_cost,
            "createdAt": datetime.now(timezone(timedelta(hours=-5))).strftime("%d de %B de %Y a las %I:%M %p UTC-5")
        }
        
        # Solo agregar userId si se proporciona
        if user_id is not None:
            log_entry["userId"] = user_id
        
        db.collection("ai_consumption_logs").add(log_entry)
        print(f"✅ AI consumption logged: {feature_name} - {input_tokens} input, {output_tokens} output tokens - ${total_cost:.4f}")
        
    except Exception as e:
        print(f"❌ Error logging AI consumption: {e}")

def log_ai_consumption_sync(input_tokens: int, output_tokens: int, model_name: str, feature_name: str, usage_description: str, user_id: str = None, source_location: str = None):
    """Versión síncrona para registrar el consumo de IA en Firestore."""
    try:
        # Obtener la instancia de Firestore
        db = firestore.client()
        
        # Calcular el costo total
        total_cost = calculate_total_cost(input_tokens, output_tokens, model_name)
        
        log_entry = {
            "inputTokens": input_tokens,
            "outputTokens": output_tokens,
            "modelName": model_name,
            "featureName": feature_name,
            "usageDescription": usage_description,
            "sourceLocation": source_location,
            "totalCost": total_cost,
            "createdAt": datetime.now(timezone(timedelta(hours=-5))).strftime("%d de %B de %Y a las %I:%M %p UTC-5")
        }
        
        # Solo agregar userId si se proporciona
        if user_id is not None:
            log_entry["userId"] = user_id
        
        db.collection("ai_consumption_logs").add(log_entry)
        print(f"✅ AI consumption logged: {feature_name} - {input_tokens} input, {output_tokens} output tokens - ${total_cost:.4f}")
        
    except Exception as e:
        print(f"❌ Error logging AI consumption: {e}")
