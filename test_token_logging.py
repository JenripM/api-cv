"""
Script de prueba para verificar el logging de tokens de IA
"""

import asyncio
import json
from main import test_analizar_cv

async def test_token_logging():
    """
    Prueba el endpoint de análisis de CV y verifica que se registren los tokens
    """
    print("🧪 Iniciando prueba de logging de tokens...")
    print("=" * 60)
    
    try:
        # Ejecutar la prueba del endpoint
        await test_analizar_cv()
        
        print("\n" + "=" * 60)
        print("✅ Prueba completada")
        print("📊 Verifica en Firestore la colección 'ai_consumption_logs'")
        print("🔍 Busca entradas con feature_name: 'CV Analysis'")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

if __name__ == "__main__":
    asyncio.run(test_token_logging())
