from io import BytesIO
import requests
import re
from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import json
import shutil
import hashlib
import zipfile
import io
import time
from fastapi.middleware.cors import CORSMiddleware

# Importar servicios reorganizados
from services.ai_utils import (
    obtener_nombre_archivo_desde_url, clean_and_load_json, generate_analysis_id,
    generate_user_id, extract_email, extract_phone, extract_linkedin, extract_address,
    es_json_valido, safe_json_load, process_formatting_response, process_keywords_response,
    process_ats_response, process_skills_response
)
from services.pdf_generator.pdf_generator import generar_pdf_con_secciones
from services.pdf_generator.pdf_utils import descargar_imagen
from services.ai_service import AIService
from services.cv_processor import CVProcessor

load_dotenv()

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # permite todos los dominios
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],       # cualquier cabecera
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar servicios
ai_service = AIService(os.getenv("OPENAI_API_KEY"))
cv_processor = CVProcessor()

@app.get("/backup-static/")
async def backup_static():
    static_folder = "static"
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Añadir archivo al zip con ruta relativa
                arcname = os.path.relpath(file_path, static_folder)
                zip_file.write(file_path, arcname=arcname)

    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=static_backup.zip"})

@app.get("/analizar-cv/")
async def analizar_cv(pdf_url: str, puesto_postular: str, original_name: str):
    """
    Endpoint principal para analizar CV usando la nueva tecnología de OpenAI para leer archivos directamente desde URL
    """
    try:
        # 1. Verificar que la URL del PDF sea accesible
        try:
            response = requests.head(pdf_url, timeout=10)
            if response.status_code != 200:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": f"No se puede acceder al PDF en la URL: {pdf_url}"
                    }
                )
        except Exception as e:
            print(f"Error al verificar URL del PDF: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Error al verificar URL del PDF: {str(e)}"
                }
            )
        
        # 2. Realizar análisis completo usando la nueva API de OpenAI para archivos
        try:
            # Usar la nueva API que lee el archivo directamente desde la URL
            analysis_results = await ai_service.analyze_cv_complete(
                file_url=pdf_url,
                puesto=puesto_postular,
                filename=original_name,
                num_paginas=1  # OpenAI determinará automáticamente el número de páginas
            )
        except Exception as e:
            print(f"Error al realizar análisis de IA: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al realizar análisis de IA: {str(e)}"
                }
            )
        
        # 3. Preparar datos para el análisis final
        try:
            candidate_name = analysis_results.get("candidate_name", {})
            extracted_data = cv_processor.prepare_analysis_data(
                contenido="[PDF content read by OpenAI]",  # Ya no necesitamos el contenido extraído
                puesto=puesto_postular,
                original_pdf=pdf_url,
                candidate_name=candidate_name,
                analysis_results=analysis_results
            )
        except Exception as e:
            print(f"Error al preparar datos de análisis: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al preparar datos de análisis: {str(e)}"
                }
            )
        
        # 4. Descargar logos y generar PDF
        try:
            ruta_logo, ruta_logo2 = cv_processor.download_logos()
            nombre_pdf = cv_processor.generate_pdf_filename()
        except Exception as e:
            print(f"Error al descargar logos/generar nombre PDF: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al descargar logos/generar nombre PDF: {str(e)}"
                }
            )
        
        # 5. Generar el PDF con los resultados
        try:
            ruta_pdf = generar_pdf_con_secciones(analysis_results, nombre_pdf, ruta_logo, ruta_logo2)
            
            # Crear carpeta examples_ai_response si no existe
            examples_folder = "examples_ai_response"
            if not os.path.exists(examples_folder):
                os.makedirs(examples_folder)
            
            # Generar nombre único para el archivo JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"ai_response_{timestamp}_{original_name.replace('.pdf', '')}.json"
            json_path = os.path.join(examples_folder, json_filename)
            
            # Guardar la respuesta de IA en JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            
            print(f"Respuesta de IA guardada en: {json_path}")
            
        except Exception as e:
            print(f"Error al generar PDF o guardar respuesta de IA: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al generar PDF o guardar respuesta de IA: {str(e)}"
                }
            )
        
        # 6. Construir respuesta final
        try:
            final_response = cv_processor.build_final_response(
                analysis_results=analysis_results,
                puesto=puesto_postular,
                candidate_name=candidate_name,
                extracted_data=extracted_data,
                nombre_pdf=nombre_pdf,
                ruta_pdf=ruta_pdf
            )
        except Exception as e:
            print(f"Error al construir respuesta final: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al construir respuesta final: {str(e)}"
                }
            )
        
        return JSONResponse(content=final_response)
        
    except Exception as e:
        print(f"Error general en análisis de CV: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error general durante el análisis: {str(e)}"
            }
        )

async def test_analizar_cv():
    """
    Función de prueba para el endpoint /analizar-cv/
    """
    import time
    start_time = time.time()
    
    # Datos de prueba
    pdf_url = "https://pub-a950f98665ac41c49a6bdc63fff76a40.r2.dev/cv_cv_1755351487038_883b13.pdf"
    puesto_postular = "AI ENGINEER"
    original_name = "CV_15_ojalaEsteSiFuncione.pdf"
    
    print("Iniciando prueba del endpoint /analizar-cv/")
    print(f"PDF URL: {pdf_url}")
    print(f"Puesto: {puesto_postular}")
    print(f"Nombre original: {original_name}")
    print("-" * 50)
    
    try:
        # Llamar directamente a la función del endpoint
        response = await analizar_cv(pdf_url, puesto_postular, original_name)
        
        # Extraer la URL del PDF generado de la respuesta
        if hasattr(response, 'body'):
            # Si es un JSONResponse, decodificar el body
            import json
            response_data = json.loads(response.body.decode('utf-8'))
            
            # Verificar si hay error en la respuesta
            if response_data.get('status') == 'error':
                print(f"❌ Error en el análisis: {response_data.get('message', 'Error desconocido')}")
                print("💡 Posibles causas:")
                print("   - Problemas de conectividad con OpenAI API")
                print("   - API key inválida o expirada")
                print("   - Límites de rate limit alcanzados")
                print("   - Problemas temporales del servicio")
                return
            
            # Buscar pdf_url en diferentes ubicaciones posibles
            pdf_url = None
            if 'pdf_url' in response_data:
                pdf_url = response_data['pdf_url']
            elif 'extractedData' in response_data and 'analysisResults' in response_data['extractedData']:
                pdf_url = response_data['extractedData']['analysisResults'].get('pdf_url')
            
            if pdf_url:
                print(f"✅ URL del PDF: {pdf_url}")
            else:
                print(f"⚠️  Respuesta recibida pero no contiene pdf_url: {response_data}")
        else:
            print(f"⚠️  Respuesta inesperada: {response}")
    
    except Exception as e:
        print(f"❌ ERROR durante la prueba: {e}")
        print("💡 Detalles del error:")
        if "502" in str(e):
            print("   - Error 502: Problema de conectividad con OpenAI API")
            print("   - Verifica tu conexión a internet")
            print("   - Intenta nuevamente en unos minutos")
        elif "Expecting value" in str(e):
            print("   - Error de parsing JSON: La API no devolvió una respuesta válida")
            print("   - Posible problema con OpenAI API")
        import traceback
        traceback.print_exc()
    
    finally:
        # Mostrar tiempo total siempre
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("-" * 50)
        print(f"⏱️  Tiempo total de ejecución: {elapsed_time:.2f} segundos")

# Función para ejecutar la prueba
def run_test():
    """
    Ejecuta la prueba del endpoint
    """
    import asyncio
    asyncio.run(test_analizar_cv())

if __name__ == "__main__":
    run_test()

