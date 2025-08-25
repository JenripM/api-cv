# Migración a Google Gemini 2.5 Flash

Este proyecto ha sido migrado de OpenAI a Google Gemini 2.5 Flash para el análisis de CVs. La migración mantiene toda la funcionalidad existente mientras aprovecha las capacidades avanzadas de Gemini.

## Cambios Principales

### 1. Biblioteca de IA
- **Antes**: `openai>=1.0.0`
- **Después**: `google-genai>=0.1.0`

### 2. Cliente de IA
- **Antes**: `from openai import OpenAI`
- **Después**: `from google import genai`

### 3. Modelo de IA
- **Antes**: `gpt-5-mini`
- **Después**: `gemini-2.5-flash`

### 4. Procesamiento de Archivos
- **Antes**: OpenAI leía archivos directamente desde URLs
- **Después**: Gemini requiere subir el archivo primero usando `client.files.upload()`

## Estructura de la Migración

### Archivos Modificados
1. **`services/ai_service.py`**
   - Cambio de `OpenAI` a `genai.Client`
   - Nuevo método `call_gemini()` que reemplaza `call_openai()`
   - Actualización del procesamiento de archivos PDF

2. **`main.py`**
   - Actualización de importaciones
   - Cambio de variable de entorno de `OPENAI_API_KEY` a `GOOGLE_API_KEY`

3. **`requirements.txt`**
   - Reemplazo de `openai>=1.0.0` por `google-genai>=0.1.0`

4. **`services/prompts/cv_analysis_prompts.py`**
   - Actualización de comentarios para reflejar el uso de Gemini

## Configuración

### Variables de Entorno
Cambia tu variable de entorno:
```bash
# Antes
OPENAI_API_KEY=tu_api_key_de_openai

# Después
GEMINI_API_KEY=tu_api_key_de_google
```

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

## Funcionalidades Mantenidas

✅ **Análisis completo de CVs** - Todos los análisis se mantienen igual
✅ **Procesamiento de PDFs** - Soporte completo para archivos PDF
✅ **Llamadas paralelas** - Redundancia con múltiples threads
✅ **Prompts personalizados** - Todos los prompts se mantienen sin cambios
✅ **Generación de reportes** - Generación de PDFs con análisis
✅ **Manejo de errores** - Sistema robusto de manejo de errores
✅ **Match score** - Integración con scores ATS

## Ventajas de Gemini 2.5 Flash

1. **Mejor Rendimiento**: Gemini 2.5 Flash es más rápido y eficiente
2. **Mejor Comprensión**: Capacidades avanzadas de comprensión de documentos
3. **Costos Optimizados**: Mejor relación costo-beneficio
4. **Integración Google**: Mejor integración con el ecosistema de Google
5. **Capacidades Multimodales**: Mejor manejo de diferentes tipos de contenido
6. **ResponseSchema**: Validación automática de JSON con Pydantic

## Estructura del Código

### Clase AIService
```python
class AIService:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key)
        self.model = "gemini-2.5-flash"
    
    def call_gemini(self, prompt: str, file_url: str) -> str:
        # Descarga y sube el PDF a Gemini
        # Realiza la llamada al modelo
        # Retorna la respuesta
```

### Procesamiento de Archivos
```python
# Llamar al modelo directamente con la URL del PDF
response = self.client.models.generate_content(
    model=self.model,
    contents=[prompt, file_url],
    config={
        "response_mime_type": "application/json",
        "response_schema": CVAnalysisResult,
    },
)

# Usar el objeto parseado directamente
result = response.parsed
```

## ResponseSchema con Pydantic

### Validación Automática
- **Antes**: Procesamiento manual de JSON con extracción y validación
- **Después**: Validación automática con Pydantic y `responseSchema`

### Beneficios
1. **Validación Automática**: Gemini garantiza que la respuesta cumple con el esquema
2. **Menos Código**: Eliminación del procesamiento manual de JSON
3. **Mejor Tipado**: Objetos Pydantic con tipos definidos
4. **Manejo de Errores**: Errores de validación más claros
5. **Serialización**: Conversión automática a diccionario con `model_dump()`

### Estructura del Schema
```python
class CVAnalysisResult(BaseModel):
    metadata: Metadata
    filename_analysis: FilenameAnalysis
    document_size_analysis: DocumentSizeAnalysis
    # ... todos los campos del análisis
```

## Compatibilidad

### Prompts
- Todos los prompts existentes son compatibles
- No se requieren cambios en la estructura de prompts
- El formato JSON de respuesta se mantiene igual

### API Endpoints
- Todos los endpoints se mantienen sin cambios
- La estructura de request/response es idéntica
- No se requieren cambios en el frontend

## Testing

Para probar la migración:

1. **Configurar API Key**:
   ```bash
   export GEMINI_API_KEY=tu_api_key_de_google
   ```

2. **Ejecutar el servidor**:
   ```bash
   python main.py
   ```

3. **Probar endpoint**:
   ```bash
   curl -X POST "http://localhost:8000/analizar-cv" \
        -H "Content-Type: application/json" \
        -d '{
          "pdf_url": "https://ejemplo.com/cv.pdf",
          "filename": "cv.pdf",
          "position": {
            "title": "Desarrollador Python"
          }
        }'
   ```

## Troubleshooting

### Errores Comunes

1. **Error de API Key**:
   - Verificar que `GEMINI_API_KEY` esté configurada correctamente
   - Asegurar que la API key tenga permisos para Gemini

2. **Error de Archivo**:
   - Verificar que la URL del PDF sea accesible
   - Asegurar que el archivo sea un PDF válido

3. **Error de Modelo**:
   - Verificar que el modelo `gemini-2.5-flash` esté disponible
   - Asegurar que la cuenta tenga acceso al modelo

### Logs
Los logs incluyen información detallada sobre:
- Procesamiento de archivos
- Llamadas a Gemini
- Errores y excepciones
- Respuestas de la IA

## Migración Reversa

Si necesitas volver a OpenAI:

1. Revertir cambios en `services/ai_service.py`
2. Cambiar `GEMINI_API_KEY` por `OPENAI_API_KEY`
3. Actualizar `requirements.txt`
4. Reinstalar dependencias

## Soporte

Para soporte técnico o preguntas sobre la migración:
- Revisar logs del servidor
- Verificar configuración de API keys
- Consultar documentación de Google Gemini
