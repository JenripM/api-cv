# Guía de Migración de Formato JSON - Análisis de CV

## Resumen
Este documento explica cómo se reorganizó el formato JSON del análisis de CV para mejorar la legibilidad y mantenibilidad. **No se agregó nueva información**, solo se reorganizó la existente de manera más clara y consistente.

## Cambios Principales

### 1. Estructura General
**Antes:** Claves dispersas y nombres inconsistentes
**Después:** Estructura jerárquica clara con nomenclatura consistente

### 2. Nomenclatura Estandarizada
- **"current"** - Texto actual del CV
- **"recommended"** - Versión alternativa explícita que reemplaza "current"
- **"ai_feedback"** - Feedback neutral de IA (puede ser positivo o de mejora)

## Mapeo Detallado

### Metadata Básica
```json
// ANTES
{
  "candidate_name": "Hector Zerrillo",
  "filename": {
    "file": "Hector_Zerrillo_CV.pdf",
    "comment": "..."
  }
}

// DESPUÉS
{
  "metadata": {
    "candidate_name": "Hector Zerrillo"
  },
  "filename_analysis": {
    "filename": "Hector_Zerrillo_CV.pdf",
    "ai_feedback": "..."
  }
}
```

### Análisis Principal
```json
// ANTES
{
  "mainly_analysis": {
    "percentage": 72,
    "state": "Con potencial",
    "analysis": "..."
  },
  "feedback_summary": "..."
}

// DESPUÉS
{
  "main_analysis": {
    "score": 75,
    "summary": "...",
    "ai_feedback": "..."
  }
}
```

**Nota:** El campo `state` se eliminó porque se puede calcular automáticamente a partir del `score`:
- 0-40: "No aprobado"
- 41-70: "Con potencial" 
- 71-100: "Aprobado"

### Métricas del Documento
```json
// ANTES
{
  "pagination": {
    "pages": 1,
    "comment": "..."
  },
  "spelling": {
    "errors": 3,
    "comment": "...",
    "error_details": [...]
  }
}

// DESPUÉS
{
  "document_size_analysis": {
    "total_pages": 1,
    "ai_feedback": "..."
  },
  "spelling_analysis": {
    "errors_found": [
      {
        "current": "Parnert",
        "recommended": "Partner"
      }
    ],
    "spelling_errors": 1,
    "ai_feedback": "..."
  }
}
```

### Elementos Esenciales
```json
// ANTES
{
  "indispensable": {
    "evaluation": [...],
    "general_comment": "..."
  }
}

// DESPUÉS
{
  "essential_elements": {
    "evaluation": [...],
    "ai_feedback": "..."
  }
}
```

### Optimización de Formato
```json
// ANTES
{
  "format_optimization": {
    "length": {
      "state": "Bajo",
      "suggestion": "..."
    },
    "photo": {
      "state": "Bajo",
      "suggestion": "..."
    },
    "keywords": {
      "state": "Medio",
      "suggestion": "..."
    },
    "impact_verbs": {
      "state": 7,
      "suggestions": [...]
    }
  }
}

// DESPUÉS
{
  "format_optimization": {
    "length": {
      "status": "Medio",
      "ai_feedback": "..."
    },
    "photo": {
      "status": "Bajo",
      "ai_feedback": "..."
    },
    "keywords": {
      "status": "Alto",
      "ai_feedback": "..."
    }
  },
  "impact_verbs_analysis": {
    "score": 6,
    "ai_feedbacks": [...]
  }
}
```

**Nota:** El campo `impact_verbs.state` se movió a una sección independiente y se cambió a `score` porque es más preciso. El status se puede calcular automáticamente:
- 1-3: "Bajo"
- 4-7: "Medio" 
- 8-10: "Alto"

### Análisis de Keywords
```json
// ANTES
{
  "keywords": {
    "jobKeywordsFound": [...],
    "jobKeywordsMissing": [...],
    "suggestion": "..."
  }
}

// DESPUÉS
{
  "keywords_analysis": {
    "found_keywords": [...],
    "missing_keywords": [...],
    "general_skills": [...],
    "ai_feedback": "..."
  }
}
```

### Ajuste al Puesto
```json
// ANTES
{
  "experience": {
    "relevance_score": 8,
    "improvement_suggestions": [...]
  }
}

// DESPUÉS
{
  "role_fit_analysis": {
    "analysis_skills": {
      "level": "Alto",
      "ai_feedback": "..."
    },
    "quantifiable_results": {
      "level": "Medio",
      "ai_feedback": "..."
    }
  }
}
```

### Experiencia Laboral
```json
// ANTES
{
  "work_experience": [
    {
      "Company": "...",
      "Current": "...",
      "Recommended": "..."
    }
  ]
}

// DESPUÉS
{
  "work_experience_analysis": [
    {
      "company": "...",
      "current": "...",
      "recommended": "..."
    }
  ]
}
```

### Habilidades y Herramientas
```json
// ANTES
{
  "skills_tools": {
    "recommendations": [...]
  }
}

// DESPUÉS
{
  "skills_tools_analysis": {
    "current_skills": "...",
    "ai_feedback": "..."
  }
}
```

### Educación
```json
// ANTES
{
  "education": [
    {
      "degree": "...",
      "institution": "...",
      "dates": "..."
    }
  ]
}

// DESPUÉS
{
  "education_analysis": [
    {
      "degree": "...",
      "institution": "...",
      "date": "...",
      "ai_feedback": "..."
    }
  ]
}
```

### Voluntariado
```json
// ANTES
{
  "volunteering": [
    {
      "Organization": "...",
      "Current": "...",
      "Recommended": "..."
    }
  ]
}

// DESPUÉS
{
  "volunteering_analysis": [
    {
      "organization": "...",
      "current": "...",
      "recommended": "..."
    }
  ]
}
```

### Resumen Ejecutivo
```json
// ANTES
{
  "feedback_summary": "..."
}

// DESPUÉS
{
  "executive_summary_analysis": {
    "current": "...",
    "recommended": "..."
  }
}
```

### Cumplimiento ATS
```json
// ANTES
{
  "ats_compliance": {
    "score": 85,
    "issues": [...],
    "recommendations": [...]
  }
}

// DESPUÉS
{
  "ats_compliance": {
    "score": 85,
    "issues": [...],
    "ai_feedbacks": [...]
  }
}
```

## Cambios de Nomenclatura

### Campos Renombrados
- `candidate_name` → movido dentro de `metadata`
- `filename` → `filename_analysis`
- `mainly_analysis` → `main_analysis`
- `percentage` → `score`
- `state` → `status`
- `analysis` → `summary`
- `pagination` → `document_size_analysis`
- `pages` → `total_pages`
- `spelling` → `spelling_analysis`
- `indispensable` → `essential_elements`
- `work_experience` → `work_experience_analysis`
- `skills_tools` → `skills_tools_analysis`
- `education` → `education_analysis`
- `volunteering` → `volunteering_analysis`
- `keywords` → `keywords_analysis`

### Campos Estandarizados
- `comment` → `ai_feedback`
- `suggestion` → `ai_feedback`
- `suggestions` → `ai_feedbacks` (cuando es array)
- `recommendations` → `ai_feedback`
- `original` → `current` (en errores)
- `suggestion` → `recommended` (en errores)
- `Company` → `company`
- `Current` → `current`
- `Recommended` → `recommended`
- `Organization` → `organization`
- `dates` → `date`

### Campos Eliminados
- `feedback_summary` (movido dentro de `main_analysis`)
- `error_details` (renombrado a `errors_found`)
- `impact_verbs` (movido a sección independiente `impact_verbs_analysis`)
- `experience` (reemplazado por `role_fit_analysis`)

### Campos Calculados a partir de Score
Algunos campos `status` fueron eliminados porque se pueden calcular automáticamente a partir del `score` correspondiente:

#### main_analysis.status
**Antes:** Campo independiente con valores "Aprobado/Con potencial/No aprobado"
**Después:** Se calcula automáticamente basado en `main_analysis.score`:
- 0-40: "No aprobado"
- 41-70: "Con potencial" 
- 71-100: "Aprobado"

#### impact_verbs_analysis.status
**Antes:** Campo independiente con valores "Alto/Medio/Bajo"
**Después:** Se calcula automáticamente basado en `impact_verbs_analysis.score`:
- 1-3: "Bajo"
- 4-7: "Medio"
- 8-10: "Alto"

#### ats_compliance.status
**Antes:** Campo independiente con valores "Alto/Medio/Bajo"
**Después:** Se calcula automáticamente basado en `ats_compliance.score`:
- 0-40: "Bajo"
- 41-70: "Medio"
- 71-100: "Alto"

**Beneficios de este cambio:**
- **Consistencia:** Los scores numéricos son más precisos que las categorías
- **Flexibilidad:** Permite cálculos más granulares y personalizados
- **Mantenimiento:** Menos campos que mantener sincronizados
- **Lógica:** Un solo valor fuente de verdad (el score) en lugar de dos campos que pueden estar desincronizados

### Nuevos Campos Agregados
- `executive_summary_analysis` con `current` y `recommended`
- `role_fit_analysis` con análisis de habilidades y resultados cuantificables
- `impact_verbs_analysis` como sección independiente
- `general_skills` en `keywords_analysis`

## Beneficios del Nuevo Formato

1. **Consistencia:** Todos los campos siguen el mismo patrón de nomenclatura
2. **Claridad:** Los nombres de las secciones son más descriptivos
3. **Jerarquía:** Estructura más lógica y fácil de navegar
4. **Mantenibilidad:** Más fácil de entender y modificar
5. **Escalabilidad:** Patrón consistente para agregar nuevas secciones
6. **Tipos Explícitos:** Cada campo tiene su tipo de dato claramente definido

## Notas para el Desarrollador

- **No se perdió información:** Todo el contenido original se preservó
- **Solo reorganización:** Los cambios son estructurales, no de contenido
- **Compatibilidad:** El nuevo formato es más robusto y extensible
- **Documentación:** Cada sección tiene un propósito claro y específico
- **Prompt Actualizado:** El prompt ahora incluye definiciones explícitas de cada campo
