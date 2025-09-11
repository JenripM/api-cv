# AI Consumption Logging Implementation

## Descripción

Se ha implementado un sistema de logging para trackear el consumo de tokens de IA en Firestore. Este sistema registra automáticamente el uso de tokens cada vez que se analiza un CV.

## Archivos Modificados

### 1. `services/ai_consumption_logger.py` (NUEVO)
Servicio para manejar el logging de consumo de IA en Firestore.

**Funcionalidades:**
- Cálculo de costos basado en tokens y modelo
- Registro en Firestore con metadatos completos
- Soporte para diferentes modelos de Gemini
- Manejo de errores no crítico

### 2. `services/ai_service.py` (MODIFICADO)
Se agregó captura de tokens de uso en la respuesta de Gemini.

**Cambios:**
- Se captura `usage_metadata` de la respuesta de Gemini
- Se incluye información de tokens en el resultado del análisis
- Se mantiene compatibilidad con el código existente

### 3. `main.py` (MODIFICADO)
Se integró el logging de tokens en el endpoint principal.

**Cambios:**
- Importación del servicio de logging
- Nuevo paso en el flujo para registrar tokens
- Información de tokens incluida en la respuesta JSON
- Manejo de errores no crítico para el logging

## Estructura del Log en Firestore

Cada entrada en la colección `ai_consumption_logs` contiene:

```json
{
  "input_tokens": 1250,
  "output_tokens": 3200,
  "model_name": "gemini-2.5-flash-lite",
  "feature_name": "CV Analysis",
  "usage_description": "Análisis de CV: CV_John_Doe.pdf para puesto: Full Stack Developer",
  "source_location": "services/ai_service.py",
  "totalCost": 0.0013,
  "created_at": "21 de August de 2024 a las 02:30 PM UTC-5"
}
```

**Nota**: El campo `user_id` solo se incluye si se proporciona en la consulta. En el endpoint actual de análisis de CV, no se pasa `user_id`, por lo que este campo no aparecerá en los logs.

## Precios por Modelo

| Modelo | Input (por 1M tokens) | Output (por 1M tokens) |
|--------|----------------------|------------------------|
| gemini-2.5-flash | $0.30 | $2.50 |
| gemini-2.5-flash-lite | $0.10 | $0.40 |

## Respuesta JSON Actualizada

La respuesta del endpoint `/analizar-cv/` ahora incluye información de tokens:

```json
{
  "status": "success",
  "message": "Análisis completado exitosamente",
  "data": {
    "candidate_name": "John Doe",
    "position": "Full Stack Developer",
    "pdf_filename": "analisis_cv_20240821_143000.pdf",
    "pdf_content_base64": "...",
    "analysis_results": {
      "token_usage": {
        "input_tokens": 1250,
        "output_tokens": 3200,
        "total_tokens": 4450,
        "model_used": "gemini-2.5-flash-lite"
      },
      // ... resto del análisis
    },
    "used_job_description": true,
    "job_description_length": 1250,
    "used_match_score": true,
    "match_score": 85.5,
    "token_usage": {
      "input_tokens": 1250,
      "output_tokens": 3200,
      "total_tokens": 4450,
      "model_used": "gemini-2.5-flash-lite"
    }
  }
}
```

## Características del Sistema

### ✅ Ventajas
- **Automático**: No requiere intervención manual
- **No crítico**: Los errores de logging no afectan el análisis
- **Detallado**: Incluye metadatos completos para análisis
- **Económico**: Calcula costos reales basados en precios actuales
- **Trazable**: Incluye ubicación del código fuente

### 🔧 Configuración
- Los precios se pueden actualizar en `MODEL_PRICING`
- El user_id se genera automáticamente basado en el filename
- Los logs se almacenan en la colección `ai_consumption_logs`

### 📊 Monitoreo
- Cada análisis genera un log automáticamente
- Los costos se calculan en tiempo real
- Se puede consultar el consumo por usuario, modelo o período

## Uso

El sistema funciona automáticamente. Cada vez que se llame al endpoint `/analizar-cv/`, se registrará el consumo de tokens en Firestore sin requerir configuración adicional.

## Consultas de Ejemplo

```javascript
// Obtener logs por modelo
db.collection('ai_consumption_logs')
  .where('model_name', '==', 'gemini-2.5-flash-lite')
  .get()

// Obtener logs por feature
db.collection('ai_consumption_logs')
  .where('feature_name', '==', 'CV Analysis')
  .orderBy('created_at', 'desc')
  .get()

// Calcular costo total por período
db.collection('ai_consumption_logs')
  .where('created_at', '>=', '2024-08-01')
  .get()
  .then(snapshot => {
    let totalCost = 0;
    snapshot.forEach(doc => {
      totalCost += doc.data().totalCost;
    });
    console.log('Costo total:', totalCost);
  });

// Obtener logs con user_id (si existe)
db.collection('ai_consumption_logs')
  .where('user_id', '!=', null)
  .get()
```
