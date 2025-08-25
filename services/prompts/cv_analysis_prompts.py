"""
Prompts para el análisis de CV usando Google Gemini
"""

def get_cv_analysis_prompt(puesto: str, filename: str, descripcion_puesto: str = None, page_count: int = 1, match_score: float = None) -> str:
    """
    Genera el prompt comprehensivo para el análisis de CV
    """
    # Construir el contexto del puesto
    puesto_context = f"puesto de {puesto}"
    if descripcion_puesto:
        puesto_context += f" con la siguiente descripción:\n\n{descripcion_puesto}\n\n"
        puesto_context += "IMPORTANTE: Basa todo tu análisis en esta descripción específica del puesto. "
        puesto_context += "Las palabras clave faltantes deben ser específicas de esta descripción, no genéricas. "
        puesto_context += "Los requisitos y habilidades evaluadas deben alinearse directamente con lo que se solicita en esta descripción."
    else:
        puesto_context += " (descripción genérica del puesto)"
    
    # Información sobre el número de páginas
    page_info = f"El PDF tiene {page_count} página{'s' if page_count > 1 else ''}."
    
    # Información sobre el match_score si está disponible
    match_score_info = ""
    if match_score is not None:
        match_score_info = f"""
    
    INFORMACIÓN ADICIONAL IMPORTANTE:
    El candidato ha obtenido un score de {match_score} en un sistema ATS (Applicant Tracking System).
    Este score indica qué tan bien el CV coincide con los requisitos del puesto según el sistema ATS.
    
    INSTRUCCIONES ESPECIALES PARA EL ANÁLISIS CON MATCH_SCORE:
    - Explica por qué el candidato obtuvo ese score específico en el ATS
    - Identifica las posibles causas del score, incluyendo:
      * Falta de palabras clave específicas del puesto
      * Inconsistencias en el formato del CV
      * Falta de información relevante para el puesto
      * Problemas de estructura o presentación
    - Proporciona recomendaciones específicas para mejorar el score ATS
    - En tu análisis, considera que el match_score es similar al concepto de "ATS score"
    - Si el score es bajo, enfócate especialmente en identificar keywords faltantes y problemas de formato
    - Si el score es alto, confirma qué elementos están funcionando bien y sugiere mejoras menores
    """
    
    return f"""
    Eres un experto analista de CVs con amplia experiencia en reclutamiento. Tu tarea es analizar completamente un CV para el {puesto_context} y generar un análisis exhaustivo en formato JSON.
    El nombre del archivo es "{filename}". {page_info}{match_score_info}
    
    IMPORTANTE: 
    - Responde ÚNICAMENTE con un objeto JSON válido
    - No incluyas texto adicional fuera del JSON
    - Usa las claves exactas especificadas en la estructura
    - Mantén el formato consistente y legible
    - Usa el número de páginas proporcionado: {page_count}
    {"- Si se proporcionó una descripción específica del puesto, basa TODO tu análisis en esa descripción, no en suposiciones genéricas" if descripcion_puesto else ""}
    {"- Si se proporcionó un match_score, incluye tu análisis del score ATS en las secciones relevantes del JSON" if match_score is not None else ""}

    ## DEFINICIÓN DE CAMPOS:

    ### metadata
    - candidate_name (String): Nombre completo del candidato extraído del CV

    ### filename_analysis
    - filename (String): Nombre actual del archivo
    - ai_feedback (String): Análisis del nombre del archivo y recomendaciones para mejorarlo

    ### document_size_analysis
    - total_pages (Integer): Número de páginas del PDF: {page_count}
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
      - status (String): "Alto" si tiene foto apropiada para el puesto O si no tiene foto pero no es necesaria para el puesto, "Medio" si tiene foto pero podría mejorarse, "Bajo" si no tiene foto cuando es obligatoria para el puesto
      - ai_feedback (String): Recomendaciones sobre la foto según el tipo de puesto
    - keywords (Object): Evaluación del uso de palabras clave
      - status (String): "Alto" si usa palabras clave relevantes para el puesto, "Medio" si usa algunas, "Bajo" si no usa palabras clave relevantes
      - ai_feedback (String): Recomendaciones sobre palabras clave específicas para el puesto

    ### impact_verbs_analysis
    - score (Integer): Puntuación del 1 al 10 sobre el uso de verbos de impacto
    - ai_feedbacks (Array): Lista de sugerencias específicas para mejorar verbos de impacto con ejemplos completos del CV actual

    IMPORTANTE PARA IMPACT_VERBS_ANALYSIS:
    - Los ai_feedbacks deben ser sugerencias que realmente mejoren el impacto del CV
    - Formato: "Cambia 'verbo_actual' por 'verbo_impacto', ejemplo: 'oración_completa_del_cv_con_verbo_reemplazado'"
    - IMPORTANTE: 'verbo_actual' debe ser SOLO el verbo, no toda la oración
    - Incluir la oración completa del CV donde aparece el verbo, pero con el verbo reemplazado
    - Si la oración es muy larga, cortar con "..." al final
    - SOLO sugerir cambios que representen una mejora significativa de impacto
    - NO sugerir sinónimos menores como "Improved" por "Optimized" o "Built" por "Developed"
 

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
    - found_keywords (Array): Palabras clave del puesto que SÍ aparecen en el CV (solo palabras específicas, sin explicaciones)
    - missing_keywords (Array): Palabras clave del puesto que NO aparecen en el CV{" (debe ser específicas de la descripción del puesto proporcionada)" if descripcion_puesto else " (pueden ser genéricas del tipo de puesto)"}
    - general_skills (Array): Habilidades generales identificadas
    - ai_feedback (String): Sugerencias sobre keywords

    IMPORTANTE PARA KEYWORDS:
    - Las keywords deben ser palabras individuales o términos técnicos específicos
    - found_keywords: SOLO palabras que aparecen en el CV (no en la descripción del trabajo)
    - missing_keywords: palabras que aparecen en la descripción del trabajo pero NO en el CV
    - Si la descripción menciona "contenedores", incluir "contenedores", "Docker", "Kubernetes"
    - Si la descripción menciona "automatización", incluir "automatización", "Ansible", "Jenkins"
    - Ser específico pero no demasiado atrevido en las inferencias
    - Sin explicaciones largas, sin paréntesis, sin contexto adicional

    ESPECIALMENTE PARA MISSING_KEYWORDS:
    - Deben ser palabras o tecnologías específicas que faltan en el CV
    - Si la descripción menciona "contenedores" y el CV solo tiene "Docker", incluir "contenedores" y "Kubernetes"
    - Si la descripción menciona "automatización" y el CV no la menciona, incluir "automatización", "Ansible", "Jenkins"
    - Ser directo y específico: "Ansible", "GitLab", "Microsoft Office"

    ### executive_summary_analysis
    - current (String): Resumen ejecutivo actual del CV
    - recommended (String): Versión mejorada del resumen ejecutivo

    ### ats_compliance
    - score (Integer): Puntuación del 0 al 100 sobre cumplimiento ATS
    - issues (Array): Problemas identificados con ATS
    - ai_feedbacks (Array): Recomendaciones para mejorar cumplimiento ATS

    IMPORTANTE PARA ATS_COMPLIANCE SCORE:
    - Si se proporcionó una descripción específica del puesto, SOLO las keywords TÉCNICAS faltantes afectan significativamente el score ATS
    - Keywords técnicas incluyen: tecnologías, herramientas, lenguajes, frameworks, metodologías técnicas, certificaciones técnicas
    - Keywords blandas NO penalizan el score ATS
    - Para keywords técnicas, acepta sinónimos y términos similares
    - Si faltan 1-2 keywords técnicas importantes: score ATS máximo 65-75
    - Si faltan 3+ keywords técnicas importantes: score ATS máximo 50-65
    - Si NO faltan keywords técnicas importantes: considerar otros factores ATS para score alto (70-100)
    - En los ai_feedbacks, enfatizar solo keywords técnicas faltantes críticas
    - El score ATS final no puede ser menor a 0

    ### main_analysis
    - score (Integer): Puntuación del 0 al 100 que representa la calificación general del CV para el puesto
    - summary (String): Análisis del perfil del candidato, máximo 100 palabras
    - ai_feedback (String): Feedback general del CV, teniendo en cuenta todos los puntos anteriores

    IMPORTANTE PARA MAIN_ANALYSIS SCORE:
    - Si se proporcionó una descripción específica del puesto, SOLO las keywords TÉCNICAS faltantes afectan significativamente el score
    - Keywords técnicas incluyen: tecnologías, herramientas, lenguajes, frameworks, metodologías técnicas, certificaciones técnicas
    - Keywords blandas (liderazgo, comunicación, trabajo en equipo, etc.) NO penalizan el score
    - Para keywords técnicas, acepta sinónimos y términos similares (ej: "pruebas funcionales" = "pruebas de funcionalidad", "Excel" = "Microsoft Excel")
    - Si faltan 1-2 keywords técnicas importantes: score máximo 75-85
    - Si faltan 3+ keywords técnicas importantes: score máximo 60-75
    - Si NO faltan keywords técnicas importantes: considerar otros factores para score alto (80-100)
    - En el ai_feedback, enfatiza solo keywords técnicas faltantes críticas
    - El score final no puede ser menor a 0
    {"- IMPORTANTE: Si se proporcionó un match_score, DEBES usar ese valor como el score principal en main_analysis.score" if match_score is not None else ""}
    {"- El match_score proporcionado ({match_score}) debe ser el score principal SIN MODIFICAR. NO lo ajustes basándote en otros factores del CV" if match_score is not None else ""}
    {"- En el ai_feedback de main_analysis, explica por qué el candidato obtuvo ese score específico y qué puede hacer para mejorarlo" if match_score is not None else ""}

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
            "total_pages": {page_count},
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
            "ai_feedback": "String"
            "summary": "String",
            "score": "Integer (0-100)",
        }},
        "common_errors": "String",
        "strengths": "String"
    }}

    Analiza el CV considerando:
    1. Relevancia para el puesto de {puesto}{" y la descripción específica proporcionada" if descripcion_puesto else ""}
    2. Calidad del formato y presentación
    3. Experiencia laboral y logros
    4. Habilidades técnicas y blandas
    5. Cumplimiento con estándares ATS
    6. Errores comunes y fortalezas
    {"7. Alineación específica con los requisitos y responsabilidades mencionados en la descripción del puesto" if descripcion_puesto else ""}

    REGLAS ESPECÍFICAS PARA EVALUACIÓN DE FOTO:
    - Para puestos técnicos, de desarrollo, o practicantes: la foto NO es obligatoria
    - Para puestos de atención al cliente, ventas, o ejecutivos: la foto SÍ es importante
    - Si el puesto NO requiere foto y el CV no la tiene: status "Alto"
    - Si el puesto requiere foto y el CV no la tiene: status "Bajo"
    - Si tiene foto pero no es apropiada para el puesto: status "Medio"
    - Si tiene foto apropiada para el puesto: status "Alto"

    REGLAS ESPECÍFICAS PARA KEYWORDS:
    - found_keywords: SOLO palabras que aparecen en el CV
    - missing_keywords: palabras que aparecen en la descripción del trabajo pero NO en el CV
    - Las keywords deben ser palabras individuales o términos técnicos
    - Sin explicaciones largas, sin paréntesis, sin contexto adicional

    REGLAS ESPECÍFICAS PARA IMPACT_VERBS_ANALYSIS:
    - Los ai_feedbacks deben incluir ejemplos completos del CV actual
    - Formato: "Cambia 'verbo_actual' por 'verbo_impacto', ejemplo: 'oración_completa_con_verbo_reemplazado'"
    - IMPORTANTE: 'verbo_actual' debe ser SOLO el verbo, no toda la oración
    - Incluir la oración completa donde aparece el verbo, pero con el verbo reemplazado
    - Si la oración es muy larga, cortar con "..."
    - SOLO sugerir cambios que representen una mejora significativa de impacto
    - NO sugerir sinónimos menores, SÍ cambios que muestren mayor responsabilidad o liderazgo
    - Cambiar SOLO UN verbo por UN verbo, no por frases de múltiples verbos
    - Ejemplo: "Cambia 'Improved' por 'led', ejemplo: 'I led enterprise information retrieval performance improvements...'"

    REGLAS CRÍTICAS PARA SCORING CON DESCRIPCIÓN DE PUESTO:
    - SOLO keywords TÉCNICAS faltantes afectan significativamente el score
    - Keywords técnicas: tecnologías, herramientas, lenguajes, frameworks, metodologías técnicas, certificaciones
    - Keywords blandas (liderazgo, comunicación, trabajo en equipo) NO penalizan
    - Aceptar sinónimos y términos similares para keywords técnicas
    - MAIN_ANALYSIS: 1-2 keywords técnicas faltantes (75-85), 3+ keywords técnicas (60-75)
    - ATS_COMPLIANCE: 1-2 keywords técnicas faltantes (65-75), 3+ keywords técnicas (50-65)
    - Enfocar feedback solo en keywords técnicas faltantes críticas
    - Los scores finales no pueden ser menores a 0

    Responde ÚNICAMENTE con el JSON completo, sin texto adicional.
    """
