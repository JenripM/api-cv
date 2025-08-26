#!/usr/bin/env python3
"""
Script de prueba para verificar los parámetros de ThinkingConfig
"""
from google import genai
from google.genai import types
import inspect

def test_thinking_config():
    """Prueba para ver qué parámetros acepta ThinkingConfig"""
    print("🔍 Probando ThinkingConfig...")
    
    # Verificar la documentación de ThinkingConfig
    print(f"📚 ThinkingConfig doc: {types.ThinkingConfig.__doc__}")
    
    # Verificar los parámetros del constructor
    sig = inspect.signature(types.ThinkingConfig.__init__)
    print(f"🔧 Parámetros de ThinkingConfig: {sig}")
    
    # Verificar atributos disponibles
    print(f"📋 Atributos de ThinkingConfig: {dir(types.ThinkingConfig)}")
    
    # Intentar crear una instancia con diferentes parámetros
    try:
        config = types.ThinkingConfig(
            thinking_budget=1024,
            include_thoughts=True
        )
        print(f"✅ ThinkingConfig creado exitosamente: {config}")
        print(f"🔍 Atributos de la instancia: {dir(config)}")
        
        # Verificar valores
        for attr in dir(config):
            if not attr.startswith('_'):
                try:
                    value = getattr(config, attr)
                    print(f"📝 {attr}: {value}")
                except:
                    pass
                    
    except Exception as e:
        print(f"❌ Error creando ThinkingConfig: {e}")

if __name__ == "__main__":
    test_thinking_config()
