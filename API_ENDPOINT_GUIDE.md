# API Endpoint: `/analizar-cv/`

## Descripción

Endpoint para analizar CVs usando IA (Gemini) y generar reportes en PDF. El análisis incluye evaluación de compatibilidad ATS, análisis de habilidades, experiencia y recomendaciones personalizadas.

## Información General

- **Método**: `POST`
- **URL**: `/analizar-cv/`
- **Content-Type**: `application/json`
- **Tiempo de respuesta**: 30-60 segundos (dependiendo del tamaño del CV)

## Estructura del Request

### Modelo de Datos

```typescript
interface JobPosition {
  title: string;           // Título del puesto (requerido)
  description?: string;    // Descripción del puesto (opcional)
}

interface CVAnalysisRequest {
  pdf_url: string;         // URL del PDF del CV (requerido)
  filename: string;        // Nombre del archivo (requerido)
  position: JobPosition;   // Información del puesto (requerido)
  match_score?: number;    // Score ATS pre-calculado (opcional, 0-100)
}
```

### Ejemplos de Request

#### 1. Análisis Básico (sin match_score)

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

#### 2. Análisis con Score ATS

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

#### 3. Análisis Mínimo (solo título del puesto)

```json
{
  "pdf_url": "https://ejemplo.com/cv.pdf",
  "filename": "CV_Candidato.pdf",
  "position": {
    "title": "Desarrollador Full Stack"
  }
}
```

## Estructura del Response

### Modelo de Respuesta Exitosa

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
        email?: string;
        phone?: string;
        location?: string;
      };
      main_analysis: {
        score: number;
        summary: string;
        ai_feedback: string;
      };
      ats_compliance: {
        score: number;
        issues: string[];
        ai_feedbacks: string[];
      };
      skills_analysis: {
        technical_skills: string[];
        soft_skills: string[];
        missing_skills: string[];
      };
      experience_analysis: {
        relevant_experience: string[];
        experience_gaps: string[];
      };
      recommendations: {
        immediate_actions: string[];
        long_term_improvements: string[];
      };
    };
    used_job_description: boolean;
    job_description_length?: number;
    used_match_score: boolean;
    match_score?: number;
  };
}
```

### Modelo de Respuesta de Error

```typescript
interface ErrorResponse {
  status: "error";
  message: string;
  json_saved?: boolean;
  json_path?: string;
}
```

## Ejemplos de Respuesta

### Respuesta Exitosa (con match_score)

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
        "candidate_name": "Juan Pérez",
        "email": "juan.perez@email.com",
        "phone": "+1 234 567 8900",
        "location": "Madrid, España"
      },
      "main_analysis": {
        "score": 75,
        "summary": "Juan Pérez es un desarrollador con 3 años de experiencia...",
        "ai_feedback": "Score ATS proporcionado: 75.5. El candidato muestra..."
      },
      "ats_compliance": {
        "score": 75,
        "issues": [
          "Faltan palabras clave específicas del puesto",
          "Formato inconsistente en secciones"
        ],
        "ai_feedbacks": [
          "Considerar agregar más keywords técnicos",
          "Mejorar estructura del CV"
        ]
      },
      "skills_analysis": {
        "technical_skills": ["JavaScript", "React", "Node.js"],
        "soft_skills": ["Trabajo en equipo", "Comunicación"],
        "missing_skills": ["Docker", "AWS"]
      },
      "experience_analysis": {
        "relevant_experience": [
          "Desarrollador Frontend en TechCorp (2021-2023)"
        ],
        "experience_gaps": [
          "Falta experiencia en DevOps"
        ]
      },
      "recommendations": {
        "immediate_actions": [
          "Agregar keywords específicos del puesto",
          "Reorganizar secciones del CV"
        ],
        "long_term_improvements": [
          "Obtener certificaciones en tecnologías cloud",
          "Desarrollar proyectos con Docker"
        ]
      }
    },
    "used_job_description": true,
    "job_description_length": 500,
    "used_match_score": true,
    "match_score": 75.5
  }
}
```

### Respuesta de Error

```json
{
  "status": "error",
  "message": "No se puede acceder al PDF en la URL: https://ejemplo.com/cv.pdf"
}
```

## Códigos de Estado HTTP

- **200**: Análisis completado exitosamente
- **400**: Error en los datos de entrada (URL inválida, formato incorrecto)
- **500**: Error interno del servidor

## Guía de Integración Frontend

### 1. Función de Análisis Básica

```javascript
async function analyzeCV(pdfUrl, filename, position, matchScore = null) {
  const requestBody = {
    pdf_url: pdfUrl,
    filename: filename,
    position: position
  };

  if (matchScore !== null) {
    requestBody.match_score = matchScore;
  }

  try {
    const response = await fetch('/analizar-cv/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error al analizar CV:', error);
    throw error;
  }
}
```

### 2. Función con Manejo de Estados

```javascript
async function analyzeCVWithStates(pdfUrl, filename, position, matchScore = null) {
  // Estado inicial
  setLoading(true);
  setError(null);
  setResult(null);

  try {
    const result = await analyzeCV(pdfUrl, filename, position, matchScore);
    
    if (result.status === 'success') {
      setResult(result.data);
      setLoading(false);
    } else {
      setError(result.message);
      setLoading(false);
    }
  } catch (error) {
    setError('Error al conectar con el servidor');
    setLoading(false);
  }
}
```

### 3. Descarga del PDF

```javascript
function downloadPDF(base64Content, filename) {
  // Convertir base64 a blob
  const byteCharacters = atob(base64Content);
  const byteNumbers = new Array(byteCharacters.length);
  
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: 'application/pdf' });
  
  // Crear URL y descargar
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
```

### 4. Componente React Completo

```jsx
import React, { useState } from 'react';

function CVAnalyzer() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    pdfUrl: '',
    filename: '',
    positionTitle: '',
    positionDescription: '',
    matchScore: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const position = {
      title: formData.positionTitle,
      description: formData.positionDescription || undefined
    };

    const matchScore = formData.matchScore ? parseFloat(formData.matchScore) : null;

    await analyzeCVWithStates(
      formData.pdfUrl,
      formData.filename,
      position,
      matchScore
    );
  };

  const handleDownload = () => {
    if (result) {
      downloadPDF(result.pdf_content_base64, result.pdf_filename);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="URL del PDF"
          value={formData.pdfUrl}
          onChange={(e) => setFormData({...formData, pdfUrl: e.target.value})}
          required
        />
        <input
          type="text"
          placeholder="Nombre del archivo"
          value={formData.filename}
          onChange={(e) => setFormData({...formData, filename: e.target.value})}
          required
        />
        <input
          type="text"
          placeholder="Título del puesto"
          value={formData.positionTitle}
          onChange={(e) => setFormData({...formData, positionTitle: e.target.value})}
          required
        />
        <textarea
          placeholder="Descripción del puesto (opcional)"
          value={formData.positionDescription}
          onChange={(e) => setFormData({...formData, positionDescription: e.target.value})}
        />
        <input
          type="number"
          placeholder="Score ATS (0-100, opcional)"
          min="0"
          max="100"
          step="0.1"
          value={formData.matchScore}
          onChange={(e) => setFormData({...formData, matchScore: e.target.value})}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Analizando...' : 'Analizar CV'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="result">
          <h3>Resultado del Análisis</h3>
          <p><strong>Candidato:</strong> {result.candidate_name}</p>
          <p><strong>Puesto:</strong> {result.position}</p>
          <p><strong>Score:</strong> {result.analysis_results.main_analysis.score}</p>
          <button onClick={handleDownload}>Descargar PDF</button>
        </div>
      )}
    </div>
  );
}
```

## Validaciones Importantes

### Frontend

1. **URL del PDF**: Debe ser una URL válida y accesible
2. **Match Score**: Si se proporciona, debe estar entre 0 y 100
3. **Título del puesto**: Campo requerido, no puede estar vacío
4. **Nombre del archivo**: Campo requerido, debe incluir extensión

### Backend

1. **Timeout**: La URL del PDF debe responder en menos de 10 segundos
2. **Formato**: El archivo debe ser un PDF válido
3. **Tamaño**: Recomendado máximo 10MB

## Notas Importantes

1. **Match Score**: Si se proporciona, la IA usará ese valor exacto sin modificarlo
2. **Descripción del puesto**: Es opcional pero mejora significativamente el análisis
3. **PDF Base64**: El PDF se devuelve codificado en base64 para facilitar la descarga
4. **Tiempo de respuesta**: Puede variar entre 30-60 segundos dependiendo del tamaño del CV
5. **Modo Debug**: En desarrollo, se guardan archivos JSON adicionales si `DEBUG_MODE=true`

## Ejemplos de Uso por Tecnología

### JavaScript/Vanilla

```javascript
// Ejemplo básico
const result = await analyzeCV(
  'https://ejemplo.com/cv.pdf',
  'CV_Candidato.pdf',
  { title: 'Desarrollador', description: 'Descripción del puesto' },
  75.5
);
```

### TypeScript

```typescript
interface AnalysisResult {
  status: 'success' | 'error';
  message: string;
  data?: {
    candidate_name: string;
    position: string;
    pdf_filename: string;
    pdf_content_base64: string;
    analysis_results: any;
  };
}

const result: AnalysisResult = await analyzeCV(/* params */);
```

### Python (requests)

```python
import requests

response = requests.post('http://localhost:8000/analizar-cv/', json={
    'pdf_url': 'https://ejemplo.com/cv.pdf',
    'filename': 'CV_Candidato.pdf',
    'position': {
        'title': 'Desarrollador Full Stack',
        'description': 'Descripción del puesto...'
    },
    'match_score': 75.5
})

result = response.json()
```
