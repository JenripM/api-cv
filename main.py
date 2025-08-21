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
from pydantic import BaseModel
from typing import Optional


# Importar servicios reorganizados
from services.ai_utils import (generate_analysis_id)
from services.pdf_generator.pdf_generator import generar_pdf_con_secciones
from services.pdf_generator.pdf_utils import descargar_imagen
from services.ai_service import AIService

load_dotenv()

# Modelos de datos para el request
class JobPosition(BaseModel):
    title: str
    description: Optional[str] = None

class CVAnalysisRequest(BaseModel):
    pdf_url: str
    filename: str
    position: JobPosition
    match_score: Optional[float] = None

# Clase simple para manejar funciones de CV
class CVProcessor:
    def download_logos(self):
        """Descarga los logos necesarios"""
        try:
            # Crear directorio si no existe
            os.makedirs("static/analisis_pdfs", exist_ok=True)
            
            # Copiar logos si existen
            ruta_logo = "static/analisis_pdfs/logo.png"
            ruta_logo2 = "static/analisis_pdfs/MyWorkIn 2.png"
            
            # Si no existen, crear archivos vacíos o copiar desde public
            if not os.path.exists(ruta_logo):
                shutil.copy("logo.png", ruta_logo) if os.path.exists("logo.png") else None
            if not os.path.exists(ruta_logo2):
                shutil.copy("public/img/MyWorkIn 2.png", ruta_logo2) if os.path.exists("public/img/MyWorkIn 2.png") else None
                
            return ruta_logo, ruta_logo2
        except Exception as e:
            print(f"Error descargando logos: {e}")
            return "logo.png", "public/img/MyWorkIn 2.png"
    
    def generate_pdf_filename(self):
        """Genera nombre único para el PDF"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"analisis_cv_{timestamp}.pdf"
    
    def save_analysis_json(self, analysis_results, original_name, debug_mode=False):
        """Guarda el análisis de IA en un archivo JSON (solo en modo debug)"""
        if not debug_mode:
            print("📝 Modo producción: JSON no guardado (para evitar saturar el deployment)")
            return None
            
        try:
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
            
            print(f"✅ Análisis de IA guardado en: {json_path}")
            return json_path
        except Exception as e:
            print(f"❌ Error al guardar análisis JSON: {e}")
            raise
    
    def build_final_response(self, analysis_results, puesto, candidate_name, nombre_pdf, ruta_pdf):
        """Construye la respuesta final con el PDF en bytes"""
        try:
            # Leer el PDF generado como bytes
            with open(ruta_pdf, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
            
            # Limpiar el archivo temporal después de leerlo
            try:
                os.remove(ruta_pdf)
                print(f"🗑️ Archivo temporal eliminado: {ruta_pdf}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar archivo temporal: {e}")
            
            return {
                "status": "success",
                "message": "Análisis completado exitosamente",
                "data": {
                    "candidate_name": candidate_name,
                    "position": puesto,
                    "pdf_filename": nombre_pdf,
                    "pdf_content": pdf_bytes,
                    "analysis_results": analysis_results
                }
            }
        except Exception as e:
            print(f"❌ Error al leer PDF: {e}")
            raise

# Inicializar servicios después de cargar variables de entorno
ai_service = AIService(api_key=os.getenv("OPENAI_API_KEY"))
cv_processor = CVProcessor()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # permite todos los dominios
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],       # cualquier cabecera
)

app.mount("/static", StaticFiles(directory="static"), name="static")


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

@app.post("/analizar-cv/")
async def analizar_cv(request: CVAnalysisRequest):
    """
    Endpoint principal para analizar CV usando la nueva tecnología de OpenAI para leer archivos directamente desde URL
    """
    try:
        # PASO 1: Verificar que la URL del PDF sea accesible
        print("🔍 Paso 1: Verificando URL del PDF...")
        try:
            response = requests.head(request.pdf_url, timeout=10)
            if response.status_code != 200:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": f"No se puede acceder al PDF en la URL: {request.pdf_url}"
                    }
                )
        except Exception as e:
            print(f"❌ Error al verificar URL del PDF: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Error al verificar URL del PDF: {str(e)}"
                }
            )
        
        # PASO 2: Realizar análisis completo usando la nueva API de OpenAI para archivos
        print("🤖 Paso 2: Realizando análisis de IA...")
        try:
            analysis_results = ai_service.analyze_cv_complete(
                file_url=request.pdf_url,
                puesto=request.position.title,
                filename=request.filename,
                descripcion_puesto=request.position.description,
                match_score=request.match_score
            )
        except Exception as e:
            print(f"❌ Error al realizar análisis de IA: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al realizar análisis de IA: {str(e)}"
                }
            )
        
        # PASO 3: Guardar JSON del análisis de IA (solo en modo debug)
        print("💾 Paso 3: Verificando si guardar JSON (modo debug)...")
        json_path = None
        try:
            # Solo guardar JSON si está en modo debug (variable de entorno DEBUG_MODE=true)
            debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
            if debug_mode:
                json_path = cv_processor.save_analysis_json(analysis_results, request.filename, debug_mode=True)
            else:
                print("📝 Modo producción: JSON no guardado")
        except Exception as e:
            print(f"⚠️ Error al guardar JSON (no crítico): {e}")
            # No fallar el proceso por error al guardar JSON
        
        candidate_name = analysis_results.get("metadata", {}).get("candidate_name", "Nombre no disponible")
        
        # PASO 4: Preparar logos y generar nombre del PDF
        print("📄 Paso 4: Preparando generación de PDF...")
        try:
            ruta_logo, ruta_logo2 = cv_processor.download_logos()
            nombre_pdf = cv_processor.generate_pdf_filename()
        except Exception as e:
            print(f"❌ Error al preparar logos/nombre PDF: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": f"Error al preparar logos/nombre PDF: {str(e)}"
                }
            )
        
        # PASO 5: Generar el PDF con los resultados
        print("📋 Paso 5: Generando PDF...")
        try:
            # Agregar el puesto_postular y descripcion_puesto al objeto analysis_results para que esté disponible en el PDF
            analysis_results['puesto_postular'] = request.position.title
            if request.position.description:
                analysis_results['descripcion_puesto'] = request.position.description
            ruta_pdf = generar_pdf_con_secciones(analysis_results, nombre_pdf, ruta_logo, ruta_logo2)
            print(f"✅ PDF generado exitosamente: {ruta_pdf}")
        except Exception as e:
            print(f"❌ Error al generar PDF: {e}")
            error_response = {
                "status": "error",
                "message": f"Error al generar PDF: {str(e)}"
            }
            # Solo agregar información del JSON si fue guardado
            if json_path:
                error_response["json_saved"] = True
                error_response["json_path"] = json_path
            return JSONResponse(status_code=500, content=error_response)
        
        # PASO 6: Leer PDF y devolver JSON con datos completos
        print("✅ Paso 6: Preparando respuesta completa...")
        try:
            # Leer el PDF como bytes y convertirlo a base64
            import base64
            with open(ruta_pdf, 'rb') as pdf_file:
                pdf_bytes = pdf_file.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Limpiar el archivo temporal después de leerlo
            try:
                os.remove(ruta_pdf)
                print(f"🗑️ Archivo temporal eliminado: {ruta_pdf}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar archivo temporal: {e}")
            
            # Construir respuesta completa
            final_response = {
                "status": "success",
                "message": "Análisis completado exitosamente",
                "data": {
                    "candidate_name": candidate_name,
                    "position": request.position.title,
                    "pdf_filename": nombre_pdf,
                    "pdf_content_base64": pdf_base64,
                    "analysis_results": analysis_results
                }
            }
            
            # Agregar información sobre si se usó descripción del puesto
            if request.position.description:
                final_response["data"]["used_job_description"] = True
                final_response["data"]["job_description_length"] = len(request.position.description)
            else:
                final_response["data"]["used_job_description"] = False
            
            # Agregar información sobre el match_score si fue proporcionado
            if request.match_score is not None:
                final_response["data"]["used_match_score"] = True
                final_response["data"]["match_score"] = request.match_score
            else:
                final_response["data"]["used_match_score"] = False
            
            print("🎉 Análisis completado exitosamente")
            return JSONResponse(content=final_response)
            
        except Exception as e:
            print(f"❌ Error al preparar respuesta completa: {e}")
            error_response = {
                "status": "error",
                "message": f"Error al preparar respuesta completa: {str(e)}"
            }
            # Solo agregar información del JSON si fue guardado
            if json_path:
                error_response["json_saved"] = True
                error_response["json_path"] = json_path
            return JSONResponse(status_code=500, content=error_response)
        
    except Exception as e:
        print(f"❌ Error general en análisis de CV: {e}")
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
    pdf_url = "https://pub-a950f98665ac41c49a6bdc63fff76a40.r2.dev/cv_cv_1755632096197_7e2fac.pdf"
    filename = "CV_15_ojalaEsteSiFuncione.pdf"
    
    # Posición de trabajo con descripción opcional
    position = JobPosition(
        title="Full Stack Intern",
        description="""
        Buscamos un Full Stack Intern para unirse a nuestro equipo de desarrollo.
        
        Responsabilidades:
        - Desarrollar aplicaciones web usando React, Node.js y Python
        - Colaborar con el equipo en el diseño y implementación de nuevas funcionalidades
        - Participar en code reviews y debugging
        - Aprender y aplicar mejores prácticas de desarrollo
        
        Requisitos:
        - Conocimientos básicos de JavaScript/TypeScript
        - Familiaridad con React o frameworks similares
        - Conocimientos básicos de Python
        - Experiencia con bases de datos SQL
        - Conocimientos de Git y control de versiones
        - Capacidad de trabajar en equipo y aprender rápidamente
        
        Habilidades deseables:
        - Experiencia con APIs REST
        - Conocimientos de Docker
        - Familiaridad con metodologías ágiles
        - Experiencia con testing automatizado
        """
    )
    
    # Ejemplo 1: Con match_score
    print("=== PRUEBA 1: Con match_score ===")
    request_with_score = CVAnalysisRequest(
        pdf_url=pdf_url,
        filename=filename,
        position=position,
        match_score=75.5  # Ejemplo de score ATS
    )
    
    # Ejemplo 2: Sin match_score (funcionamiento original)
    print("=== PRUEBA 2: Sin match_score ===")
    request_without_score = CVAnalysisRequest(
        pdf_url=pdf_url,
        filename=filename,
        position=position
        # match_score=None (por defecto)
    )
    
    # Usar el primer ejemplo para la prueba
    request = request_with_score
    
    print("Iniciando prueba del endpoint /analizar-cv/")
    print(f"PDF URL: {pdf_url}")
    print(f"Filename: {filename}")
    print(f"Position: {position.title}")
    if position.description:
        print(f"Job description: {len(position.description)} characters")
    else:
        print("No job description provided (generic analysis)")
    if request.match_score is not None:
        print(f"Match score (ATS): {request.match_score}")
    else:
        print("No match score provided")
    print("-" * 50)
    
    try:
        # Llamar directamente a la función del endpoint
        response = await analizar_cv(request)
        
        # Extraer la URL del PDF generado de la respuesta
        if hasattr(response, 'body'):
            # Si es un JSONResponse, decodificar el body
            import json
            response_data = json.loads(response.body.decode('utf-8'))
            
            # Verificar si hay error en la respuesta
            if response_data.get('status') == 'error':
                print(f"❌ Error en el análisis: {response_data.get('message', 'Error desconocido')}")
                # Mostrar información adicional si está disponible
                if response_data.get('json_saved'):
                    print(f"📄 JSON guardado en: {response_data.get('json_path')}")
                if response_data.get('pdf_generated'):
                    print(f"📋 PDF generado en: {response_data.get('pdf_path')}")
                return
            else:
                # Mostrar información de éxito
                data = response_data.get('data', {})
                print(f"✅ Análisis completado exitosamente")
                print(f"📄 Nombre del candidato: {data.get('candidate_name', 'No disponible')}")
                print(f"📋 PDF generado: {data.get('pdf_filename', 'No disponible')}")
                print(f"🔍 Usó descripción del puesto: {data.get('used_job_description', False)}")
                if data.get('used_job_description'):
                    print(f"📝 Longitud de descripción: {data.get('job_description_length', 0)} caracteres")
                print(f"🎯 Usó match score: {data.get('used_match_score', False)}")
                if data.get('used_match_score'):
                    print(f"📊 Match score (ATS): {data.get('match_score', 'No disponible')}")
        else:
            print(f"⚠️  Respuesta inesperada: {response}")
    
    except Exception as e:
        print(f"❌ ERROR durante la prueba: {e}")
    
    finally:
        # Mostrar tiempo total siempre
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("-" * 50)
        print(f"⏱️  Tiempo total de ejecución: {elapsed_time:.2f} segundos")

# Función para ejecutar la prueba
async def run_test():
    """
    Ejecuta la prueba del endpoint
    """
    await test_analizar_cv()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_test())

