# API Endpoint: `/analizar-cv/`

## Descripción

Analiza CVs usando IA y genera reportes en PDF. Incluye evaluación ATS, análisis de habilidades, experiencia y recomendaciones personalizadas.

## Información General

- **Método**: `POST`
- **URL**: `/analizar-cv/`
- **Content-Type**: `application/json`
- **Tiempo de respuesta**: 15-30 segundos

## Request

### Estructura

```typescript
interface JobPosition {
  title: string;           // Título del puesto
  description?: string;    // Descripción del puesto (opcional)
}

interface CVAnalysisRequest {
  cv_data: object;         // Datos del CV en formato JSON
  pdf_url: string;         // URL del PDF para calcular número de páginas
  filename: string;        // Nombre del archivo
  position: JobPosition;   // Información del puesto
  match_score?: number;    // Score ATS pre-calculado (opcional, 0-100)
}
```

### Ejemplos

#### Análisis Básico
```json
{
  "cv_data": {
    "personal_info": {
      "name": "Juan Pérez",
      "email": "juan.perez@email.com"
    },
    "education": [
      {
        "degree": "Ingeniería Informática",
        "institution": "Universidad Complutense de Madrid"
      }
    ],
    "work_experience": [
      {
        "title": "Desarrollador Full Stack",
        "company": "TechCorp",
        "description": "Desarrollo de aplicaciones web"
      }
    ],
    "skills": ["JavaScript", "React", "Node.js"]
  },
  "pdf_url": "https://ejemplo.com/cv.pdf",
  "filename": "CV_Candidato.pdf",
  "position": {
    "title": "Desarrollador Full Stack",
    "description": "Buscamos un desarrollador con experiencia en React y Node.js"
  }
}
```

#### Análisis con Score ATS
```json
{
  "cv_data": {
    "personal_info": {
      "name": "María García"
    },
    "skills": ["Java", "Spring Boot"]
  },
  "pdf_url": "https://ejemplo.com/cv.pdf",
  "filename": "CV_Candidato.pdf",
  "position": {
    "title": "Desarrollador Full Stack"
  },
  "match_score": 75.5
}
```

## Response

### Respuesta Exitosa

```typescript
interface CVAnalysisResponse {
  status: "success";
  message: string;
  data: {
    candidate_name: string;
    position: string;
    pdf_filename: string;
    pdf_content_base64: string;
    analysis_results: {
      metadata: {
        candidate_name: string;
      };
      main_analysis: {
        score: number;
        ai_feedback: string;
      };
      ats_compliance: {
        score: number;
        issues: string[];
      };
      skills_analysis: {
        technical_skills: string[];
        missing_skills: string[];
      };
      experience_analysis: {
        relevant_experience: string[];
      };
      recommendations: {
        immediate_actions: string[];
      };
    };
  };
}
```

### Respuesta de Error

```typescript
interface ErrorResponse {
  status: "error";
  message: string;
}
```

### Ejemplo de Respuesta

```json
{
  "status": "success",
  "message": "Análisis completado exitosamente",
  "data": {
    "candidate_name": "Juan Pérez",
    "position": "Desarrollador Full Stack",
    "pdf_filename": "analisis_cv_20250101_120000.pdf",
    "pdf_content_base64": "JVBERi0xLjQKJcOkw7zDtsO...",
    "analysis_results": {
      "metadata": {
        "candidate_name": "Juan Pérez"
      },
      "main_analysis": {
        "score": 75,
        "ai_feedback": "El candidato muestra experiencia sólida en desarrollo web"
      },
      "ats_compliance": {
        "score": 75,
        "issues": [
          "Faltan palabras clave específicas del puesto"
        ]
      },
      "skills_analysis": {
        "technical_skills": ["JavaScript", "React", "Node.js"],
        "missing_skills": ["Docker", "AWS"]
      },
      "experience_analysis": {
        "relevant_experience": [
          "3 años como desarrollador Full Stack"
        ]
      },
      "recommendations": {
        "immediate_actions": [
          "Agregar keywords faltantes al CV"
        ]
      }
    }
  }
}
```

## Códigos de Estado HTTP

- **200**: Análisis completado exitosamente
- **400**: Error en los datos de entrada
- **500**: Error interno del servidor
