# Funcionalidad Match Score (ATS Score)

## Descripción

Se ha agregado un nuevo parámetro opcional `match_score` al endpoint `/analizar-cv/` que permite proporcionar un score pre-calculado de un sistema ATS (Applicant Tracking System) para que la IA lo analice y explique.

## Formato del Match Score

**IMPORTANTE**: El `match_score` debe ser un valor de **0 a 100** (no de 0 a 1).

### Ejemplos correctos:
```json
{
  "match_score": 80.0    // 80%
  "match_score": 75.5    // 75.5%
  "match_score": 45.2    // 45.2%
  "match_score": 95.0    // 95%
}
```

### Ejemplos incorrectos:
```json
{
  "match_score": 0.8     // ❌ No usar valores de 0-1
  "match_score": 0.75    // ❌ No usar valores de 0-1
}
```

## Uso

### Con Match Score

```json
{
  "pdf_url": "https://ejemplo.com/cv.pdf",
  "filename": "CV_Candidato.pdf",
  "position": {
    "title": "Desarrollador Full Stack",
    "description": "Buscamos un desarrollador con experiencia en React y Node.js..."
  },
  "match_score": 75.5
}
```

### Sin Match Score (funcionamiento original)

```json
{
  "pdf_url": "https://ejemplo.com/cv.pdf",
  "filename": "CV_Candidato.pdf",
  "position": {
    "title": "Desarrollador Full Stack",
    "description": "Buscamos un desarrollador con experiencia en React y Node.js..."
  }
}
```

## Respuesta

Cuando se proporciona un `match_score`, la respuesta incluirá información adicional:

```json
{
  "status": "success",
  "message": "Análisis completado exitosamente",
  "data": {
    "candidate_name": "Juan Pérez",
    "position": "Desarrollador Full Stack",
    "pdf_filename": "analisis_cv_20250101_120000.pdf",
    "pdf_content_base64": "...",
    "analysis_results": {
      "main_analysis": {
        "score": 75,  // ← Usará el match_score proporcionado
        "summary": "...",
        "ai_feedback": "Score ATS proporcionado: 75.5. Análisis del score..."
      },
      "ats_compliance": {
        "score": 75,  // ← También se actualiza con el match_score
        "issues": [...],
        "ai_feedbacks": [...]
      }
    },
    "used_job_description": true,
    "job_description_length": 500,
    "used_match_score": true,
    "match_score": 75.5
  }
}
```

## Análisis de la IA

Cuando se proporciona un `match_score`, la IA realizará un análisis especial que incluye:

1. **Score Inmutable**: El `match_score` proporcionado se usa **exactamente como está**, sin modificaciones
2. **Explicación del Score**: Por qué el candidato obtuvo ese score específico en el ATS
3. **Identificación de Causas**: Posibles razones del score, incluyendo:
   - Falta de palabras clave específicas del puesto
   - Inconsistencias en el formato del CV
   - Falta de información relevante para el puesto
   - Problemas de estructura o presentación
4. **Recomendaciones Específicas**: Para mejorar el score ATS
5. **Análisis de Keywords**: Identificación de palabras clave faltantes que afectan el score

**IMPORTANTE**: Si NO se proporciona `match_score`, la IA calculará el score basándose en su análisis del CV.

## Parcheo Automático

El sistema incluye un mecanismo de parcheo automático que asegura que:

- ✅ El `match_score` se incluya en `main_analysis.score`
- ✅ El `match_score` se incluya en `ats_compliance.score`
- ✅ Se actualice el `ai_feedback` para explicar el score
- ✅ Funciona incluso si la IA no incluye el score correctamente

## Interpretación del Score

- **Score Alto (80-100)**: El CV está bien optimizado para el ATS
- **Score Medio (60-79)**: El CV necesita mejoras moderadas
- **Score Bajo (0-59)**: El CV requiere optimización significativa

## Compatibilidad

- ✅ **Retrocompatible**: El endpoint funciona exactamente igual si no se proporciona `match_score`
- ✅ **Opcional**: El parámetro es completamente opcional
- ✅ **Tipo Float**: Acepta valores decimales (ej: 75.5, 82.3, etc.)
- ✅ **Rango 0-100**: Usar valores de 0 a 100, no de 0 a 1

## Ejemplo de Uso en Python

```python
import requests

# Con match_score (formato correcto: 0-100)
response = requests.post("http://localhost:8000/analizar-cv/", json={
    "pdf_url": "https://ejemplo.com/cv.pdf",
    "filename": "CV.pdf",
    "position": {
        "title": "Desarrollador",
        "description": "Descripción del puesto..."
    },
    "match_score": 65.2  # Score ATS pre-calculado (65.2%)
})

# Sin match_score (funcionamiento original)
response = requests.post("http://localhost:8000/analizar-cv/", json={
    "pdf_url": "https://ejemplo.com/cv.pdf",
    "filename": "CV.pdf",
    "position": {
        "title": "Desarrollador",
        "description": "Descripción del puesto..."
    }
    # No se incluye match_score
})
```
