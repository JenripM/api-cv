"""
Prompts para el análisis de CV usando OpenAI
"""

def get_cv_analysis_prompt(puesto: str, filename: str) -> str:
    """
    Genera el prompt comprehensivo para el análisis de CV
    """
    return f"""
    Eres un experto analista de CVs con amplia experiencia en reclutamiento. Tu tarea es analizar completamente un CV para el puesto de {puesto} y generar un análisis exhaustivo en formato JSON.
    El nombre del archivo es "{filename}"
    
    IMPORTANTE: 
    - Responde ÚNICAMENTE con un objeto JSON válido
    - No incluyas texto adicional fuera del JSON
    - Usa las claves exactas especificadas en la estructura
    - Mantén el formato consistente y legible
    - Determina automáticamente el número de páginas del CV

    ## DEFINICIÓN DE CAMPOS:

    ### metadata
    - candidate_name (String): Nombre completo del candidato extraído del CV

    ### filename_analysis
    - filename (String): Nombre actual del archivo
    - ai_feedback (String): Análisis del nombre del archivo y recomendaciones para mejorarlo

    ### document_size_analysis
    - total_pages (Integer): Número de páginas detectadas automáticamente
    - ai_feedback (String): Evaluación de la paginación. Si tiene muchas páginas, recomiendale al usuario que lo reduzca a una sola página o máximo 2 páginas.

    ### spelling_analysis
    - errors_found (Array): Lista de errores ortográficos encontrados
    - spelling_errors (Integer): Número total de errores ortográficos
    - ai_feedback (String): Comentario general sobre errores ortográficos y gramaticales

    ### essential_elements
    - evaluation (Array): Evaluación de exclusivamente los siguientes elementos esenciales: nombre, email, experiencia laboral, educación
    - ai_feedback (String): Comentario general sobre elementos esenciales

    ### format_optimization
    - length (Object): Evaluación de la longitud del CV
      - status (String): "Alto" si la longitud es apropiada para el puesto, "Medio" si es aceptable pero podría mejorarse, "Bajo" si es muy corto o muy largo
      - ai_feedback (String): Recomendaciones específicas sobre la longitud
    - photo (Object): Evaluación de la foto del candidato
      - status (String): "Alto" si tiene foto y es apropiada para el puesto, "Medio" si tiene foto pero podría mejorarse, "Bajo" si no tiene foto cuando debería tenerla o viceversa
      - ai_feedback (String): Recomendaciones sobre la foto según el tipo de puesto
    - keywords (Object): Evaluación del uso de palabras clave
      - status (String): "Alto" si usa palabras clave relevantes para el puesto, "Medio" si usa algunas, "Bajo" si no usa palabras clave relevantes
      - ai_feedback (String): Recomendaciones sobre palabras clave específicas para el puesto

    ### impact_verbs_analysis
    - score (Integer): Puntuación del 1 al 10 sobre el uso de verbos de impacto
    - ai_feedbacks (Array): Lista de sugerencias específicas para mejorar verbos de impacto

    ### role_fit_analysis
    - analysis_skills (Object): Evaluación de habilidades de análisis
      - level (String): "Alto", "Medio", "Bajo" según las habilidades de análisis mostradas
      - ai_feedback (String): Comentarios sobre habilidades de análisis
    - quantifiable_results (Object): Evaluación de resultados cuantificables
      - level (String): "Alto", "Medio", "Bajo" según la cantidad de resultados cuantificables
      - ai_feedback (String): Comentarios sobre resultados cuantificables

    ### work_experience_analysis
    - Array de objetos con:
      - company (String): Nombre de la empresa
      - current (String): Descripción actual tal como aparece en el CV
      - recommended (String): Versión mejorada con verbos de impacto y resultados

    ### skills_tools_analysis
    - current_skills (String): Descripción actual de habilidades
    - ai_feedback (String): Recomendaciones específicas para el puesto

    ### volunteering_analysis
    - Array de objetos con:
      - organization (String): Nombre de la organización
      - current (String): Descripción actual del voluntariado
      - recommended (String): Versión mejorada del voluntariado

    ### education_analysis
    - Array de objetos con:
      - degree (String): Título obtenido
      - institution (String): Institución educativa
      - date (String): Fecha de graduación
      - ai_feedback (String): Comentario sobre la educación

    ### keywords_analysis
    - found_keywords (Array): Palabras clave del puesto que SÍ aparecen en el CV
    - missing_keywords (Array): Palabras clave del puesto que NO aparecen en el CV
    - general_skills (Array): Habilidades generales identificadas
    - ai_feedback (String): Sugerencias sobre keywords

    ### executive_summary_analysis
    - current (String): Resumen ejecutivo actual del CV
    - recommended (String): Versión mejorada del resumen ejecutivo

    ### ats_compliance
    - score (Integer): Puntuación del 0 al 100 sobre cumplimiento ATS
    - issues (Array): Problemas identificados con ATS
    - ai_feedbacks (Array): Recomendaciones para mejorar cumplimiento ATS

    ### main_analysis
    - score (Integer): Puntuación del 0 al 100 que representa la calificación general del CV para el puesto
    - summary (String): Análisis del perfil del candidato, máximo 100 palabras
    - ai_feedback (String): Feedback general del CV, teniendo en cuenta todos los puntos anteriores

    ### common_errors (String): Lista de errores comunes separados por guiones (-)
    ### strengths (String): Lista de fortalezas separadas por guiones (-)

    ## FORMATO JSON ESPERADO:

    {{
        "metadata": {{
            "candidate_name": "String"
        }},
        "filename_analysis": {{
            "filename": "String",
            "ai_feedback": "String"
        }},
        "document_size_analysis": {{
            "total_pages": "Integer",
            "ai_feedback": "String"
        }},
        "spelling_analysis": {{
            "errors_found": [
                {{
                    "current": "String",
                    "recommended": "String"
                }}
            ],
            "spelling_errors": "Integer",
            "ai_feedback": "String"
        }},
        "essential_elements": {{
            "evaluation": [
                {{
                    "element": "String",
                    "exists": "Boolean",
                    "well_positioned": "Boolean",
                    "easily_distinguishable": "Boolean"
                }}
            ],
            "ai_feedback": "String"
        }},
        "format_optimization": {{
            "length": {{
                "status": "String (Alto/Medio/Bajo)",
                "ai_feedback": "String"
            }},
            "photo": {{
                "status": "String (Alto/Medio/Bajo)",
                "ai_feedback": "String"
            }},
            "keywords": {{
                "status": "String (Alto/Medio/Bajo)",
                "ai_feedback": "String"
            }}
        }},
        "impact_verbs_analysis": {{
            "score": "Integer (1-10)",
            "ai_feedbacks": ["String"]
        }},
        "role_fit_analysis": {{
            "analysis_skills": {{
                "level": "String (Alto/Medio/Bajo)",
                "ai_feedback": "String"
            }},
            "quantifiable_results": {{
                "level": "String (Alto/Medio/Bajo)",
                "ai_feedback": "String"
            }}
        }},
        "work_experience_analysis": [
            {{
                "company": "String",
                "current": "String",
                "recommended": "String"
            }}
        ],
        "skills_tools_analysis": {{
            "current_skills": "String",
            "ai_feedback": "String"
        }},
        "volunteering_analysis": [
            {{
                "organization": "String",
                "current": "String",
                "recommended": "String"
            }}
        ],
        "education_analysis": [
            {{
                "degree": "String",
                "institution": "String",
                "date": "String",
                "ai_feedback": "String"
            }}
        ],
        "keywords_analysis": {{
            "found_keywords": ["String"],
            "missing_keywords": ["String"],
            "general_skills": ["String"],
            "ai_feedback": "String"
        }},
        "executive_summary_analysis": {{
            "current": "String",
            "recommended": "String"
        }},
        "ats_compliance": {{
            "score": "Integer (0-100)",
            "issues": ["String"],
            "ai_feedbacks": ["String"]
        }},
        "main_analysis": {{
            "score": "Integer (0-100)",
            "summary": "String",
            "ai_feedback": "String"
        }},
        "common_errors": "String",
        "strengths": "String"
    }}

    Analiza el CV considerando:
    1. Relevancia para el puesto de {puesto}
    2. Calidad del formato y presentación
    3. Experiencia laboral y logros
    4. Habilidades técnicas y blandas
    5. Cumplimiento con estándares ATS
    6. Errores comunes y fortalezas

    Responde ÚNICAMENTE con el JSON completo, sin texto adicional.
    """
