"""
Prompts para análisis de CV organizados por categorías

IMPORTANTE: Todos los JSON de respuesta deben usar claves (keys) en inglés únicamente.
Todas las estructuras JSON en los prompts deben tener sus claves en inglés.
"""

# Prompts para extracción de información básica
BASIC_INFO_PROMPTS = {
    "candidate_name": """
    Actúa como un analista experto en CVs. Tu tarea es **extraer el nombre completo del candidato** que aparece en el siguiente contenido textual de un currículum. El nombre suele estar ubicado al inicio o en una sección de datos personales o encabezado.

    - Si identificas un nombre completo, devuélvelo.
    - Si solo aparece un nombre parcial, extrae lo más completo posible.
    - Si no encuentras un nombre claro, responde con "No identificado".

    Devuelve exclusivamente un objeto JSON con esta estructura:

    {{
    "name": "Nombre completo extraído o 'No identificado'"
    }}

    Contenido del CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "filename_analysis": """
    Eres un experto en marca personal y empleabilidad. Tu tarea es analizar el nombre del archivo de un currículum (CV) para determinar si es profesional.

    Evalúa únicamente el **nombre del archivo PDF**: {filename_json}

    Considera si:
    - Es fácil de identificar por el reclutador.
    - Contiene el nombre del candidato o al menos algo representativo.
    - Evita combinaciones de números aleatorios o palabras genéricas.
    - Transmite orden y seriedad profesional.

    Considera este contenido del CV: {contenido_json}

    Responde SOLO en JSON con esta estructura:

    {{
    "file": {filename_json},
    "comment": "Habla en primera persona. Dime si el nombre del archivo es adecuado o no, explícame por qué con lenguaje directo y profesional (por ejemplo: 'Tu archivo actual no es fácil de identificar porque...'). Si aplica, sugiere un nombre más claro y profesional (por ejemplo: 'Te sugiero cambiarlo por algo como Nombre_Apellido_CV.pdf')."
    }}
    """
}

# Prompts para análisis principal
MAIN_ANALYSIS_PROMPTS = {
    "overall_analysis": """
    Eres un reclutador profesional. Recibirás el perfil de un candidato en formato JSON y deberás evaluar su idoneidad para el puesto de "{puesto}".

    Evalúa cuidadosamente estos aspectos:
    - Experiencia laboral relevante para el puesto.
    - Habilidades técnicas y blandas necesarias.
    - Formación académica y complementaria alineada al rol.
    - Actitudes y aptitudes generales que favorezcan un buen desempeño en el puesto.

    Con base en tu análisis, responde exclusivamente con un **objeto JSON** con la siguiente estructura:

    {{
        "percentage": number between 0 and 100, indicating how aligned the profile is with the position,
        "state": a legend based on the percentage, following this scale:
            - 75 or more: "Approved"
            - Between 50 and 74: "With potential"
            - Less than 50: "Not approved",
        "analysis": a single brief paragraph, starting with "Your CV", and that expresses a single clear idea about the most relevant point of the profile (whether it's a strength or an opportunity for improvement)
    }}

    Example of valid output:

    {{
        "percentage": 78,
        "state": "Approved",
        "analysis": "Your CV demonstrates attitude, technical base and experiences that sum. But today it describes tasks, not communication
        impact. With adjustments in writing, metrics, sectoral language and presentation, you can convert a promising profile
        into a competitive one."
    }}

    Do not include any other text outside the JSON.

    Next, the candidate's profile:

    {contenido}
    """,
    
    "feedback_summary": """
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. Por favor, proporciona un resumen general del feedback para el candidato, considerando los siguientes aspectos:

    - La calidad general del CV, incluyendo su claridad y profesionalismo.
    - La relevancia de la experiencia laboral para el puesto al que está aplicando.
    - La adecuación de las habilidades técnicas y blandas para el puesto.
    - Cualquier área de mejora significativa o notoria en el CV.
    - La estructura general del CV y su legibilidad.

    Tu tarea es resumir el feedback en un párrafo breve, claro y directo. No incluyas detalles extensos ni repitas información ya mencionada, mantén el análisis conciso y práctico.

    Contenido del CV a evaluar:
    {contenido}
    """
}

# Prompts para análisis de formato y estructura
FORMAT_ANALYSIS_PROMPTS = {
    "pagination": """
    Eres un reclutador senior con amplia experiencia en la evaluación de currículums para procesos de selección competitivos.

    Tu tarea es analizar únicamente el número de páginas de un CV y emitir una evaluación profesional, comenzando siempre con una frase clara de diagnóstico general.

    Primero debes comenzar el comentario con una de estas frases (elige según el caso):
    - "¡Tu CV tiene el tamaño ideal!"
    - "Tu CV es demasiado extenso y puede jugar en contra."
    - "Tu CV tiene buen contenido, pero se puede optimizar en longitud."

    Luego, continúa con una observación más desarrollada y fundamentada, teniendo en cuenta:
    - Si facilita o no una lectura ágil por parte del reclutador.
    - Si permite resaltar la información clave.
    - Si sigue buenas prácticas de presentación ejecutiva (especialmente para perfiles no académicos).

    Responde con un único objeto JSON que contenga:

    Example of response:

    {{
        "pages": the total number of pages of the CV (already provided).
        "comment": a clear and professional evaluation, starting with one of the phrases mentioned and then developing a brief but expert recommendation, max 37 words.

    }}

    Do not include any text outside the JSON.

    Number of pages of the CV: {num_paginas}
    """,
    
    "spelling": """
    Actúa como un corrector profesional de ortografía con experiencia en revisión de currículums (CVs).

    Analiza el siguiente texto y detecta únicamente errores ortográficos reales.

    Debes ignorar lo siguiente:
    - Enlaces o URLs (por ejemplo: https://..., http://...).
    - Correos electrónicos y nombres de usuario.
    - Nombres propios de personas, empresas, instituciones, países, etc.
    - Siglas y abreviaciones en mayúsculas (como UX, TI, HTML).
    - Uso de mayúsculas al inicio de oración (no lo consideres error).

    Detecta únicamente errores como:
    - Palabras mal escritas o con letras cambiadas.
    - Tildes mal colocadas o faltantes.
    - Errores ortográficos frecuentes (como "desarollo" en lugar de "desarrollo").

    Tu respuesta debe ser exclusivamente un JSON con la siguiente estructura:

    {{
        "errors": total number of errors found (integer),
        "comment": comment corresponding to the number of errors, written in first person (for example: "I found 3 errors that I suggest you correct to make the CV look more professional."),
        "error_details": if there are errors, a list with objects in the format:
            [
            {{
                "original": "word with error",
                "suggestion": "corrected word"
            }}
            ],
            if no errors, it must be null
    }}

    Only include "error_details" words where "original" and "suggestion" are different.

    Do not add text outside the JSON.

    Text to analyze:
    \"\"\"{contenido}\"\"\"
    """,
    
    "indispensable_elements": """
    Actúa como un reclutador profesional experto en evaluación de currículums.

    Analiza si los siguientes elementos clave están presentes, bien ubicados y son fácilmente identificables en el CV:

    - Nombre
    - Correo electrónico
    - Experiencia laboral
    - Formación académica

    Responde exclusivamente en formato JSON con la siguiente estructura (no incluyas ningún texto fuera del JSON):

    {{
    "indispensable": {{
        "evaluation": [
        {{
            "element": "Name",
            "exists": boolean,
            "well_positioned": boolean,
            "easily_distinguishable": boolean
        }},
        {{
            "element": "Email",
            "exists": boolean,
            "well_positioned": boolean,
            "easily_distinguishable": boolean
        }},
        {{
            "element": "Work experience",
            "exists": boolean,
            "well_positioned": boolean,
            "easily_distinguishable": boolean
        }},
        {{
            "element": "Academic education",
            "exists": boolean,
            "well_positioned": boolean,
            "easily_distinguishable": boolean
        }}
        ],
        "general_comment": "Personalized comment in third person, with a maximum of 40 words. Use phrases like 'Your CV', 'it is recommended', 'it is considered'."
    }}
    }}

    Text of the CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "repeat_words": """
    Actúa como un revisor profesional de CVs. Tu tarea es detectar únicamente **palabras que se repiten de forma innecesaria o excesiva** en el siguiente texto.

     **Ignora las siguientes categorías de palabras**:
    - Artículos: el, la, los, las, un, una, unos, unas
    - Preposiciones: de, en, con, por, para, sobre, entre, hasta, hacia, desde
    - Conjunciones y conectores: y, o, u, pero, aunque, sino, mientras, así, entonces
    - Pronombres comunes: yo, tú, él, ella, nosotros, ustedes, ellos
    - Verbos muy comunes: ser, estar, haber, tener, hacer (solo si no están en exceso)
    - Monosílabos vacíos de contenido: a, e, es, al, lo, sí, no, se, que, qué, ya, más
    - Palabras similares con diferencia de género o número (ej: "capacidad" y "capacidades" se cuentan como una sola)
    - No me repitas la misma palabra como palabras diferentes, acumula 1 vez mas en el contador de veces.
    - SOLO PALABRAS REPETIDAS DONDE VECES SEA COMO MINIMO 2
    - SOLAMENTE DAME UN MAXIMO DE 12 PALABRAS

    Devuelve **solo** un JSON con esta estructura:

    {{ 
    "repeated_words": [
        {{ "word": "x", "times": n }},
    ]
    }}

    Do not include any text outside the JSON.

    Text to review:
    \"\"\"{contenido}\"\"\"
    """,
    
    "format_optimization": """
    Actúa como un experto en revisión profesional de currículums (CVs), con énfasis en formato, claridad y atracción para reclutadores. Tienes que responder de tu a tu a un candidato que busca mejorar su CV para el puesto de **{puesto}**.

    Evalúa el siguiente contenido extraído de un CV:

    \"\"\"{contenido}\"\"\"

    El rol objetivo es: **{puesto}**

    Tu tarea es analizar el formato del CV con base en los siguientes criterios, orientados a mejorar su presentación y efectividad:

    1. **Longitud**: Evalúa si el CV excede 1 página (en perfiles junior o intermedios) o si es innecesariamente largo para el rol. el num de paginas es {num_paginas} . recuerda que un CV debe ser conciso y fácil de leer. si es 1 hoja el estado es "Alto", si es 2 hojas "Medio" y si es más de 2 "Bajo".

    2. **Foto**: Verifica si el CV incluye una foto. La mayoría de los filtros automáticos de RRHH no lo recomiendan, especialmente en países donde se evita por sesgos. ENtonces, si hay foto el estado es "Bajo", si no hay foto el estado es "Alto". 
    
    3. **Palabras clave**: Evalúa si incluye términos relevantes al puesto, como tecnologías, habilidades técnicas, o conceptos específicos (por ejemplo, en el caso de {puesto}, busca términos como: análisis de riesgo, scoring, producto financiero, gestión, liderazgo, procesos, herramientas, etc.).
    4. **Verbos de impacto**: Evalúa si se utilizan verbos potentes y orientados a resultados, como: "lideré", "implementé", "optimicé", "logré", en lugar de verbos vagos o pasivos como "encargado de", "apoyé", "participé".

    Para cada uno de estos 4 criterios, responde con:

    -"state"`: Can be **"Alto"**, **"Medio"** or **"Bajo"**, depending on the quality or presence of the element.
    - "suggestion"`: Tell me from your point of view, something like The length of your CV is appropriate, or The photo you uploaded is not necessary in a CV, or I recommend including more keywords related to the position of {puesto}, or Use impact verbs to highlight your achievements. but from your point of view, it feels like a professional direct advice, max 30 words.

    Devuelve exclusivamente un JSON con el siguiente formato:

    {{
    "length": {{
        "state": "",
        "suggestion": ""
    }},
    "photo": {{
        "state": "",
        "suggestion": ""
    }},
    "keywords": {{
        "state": "",
        "suggestion": ""
    }},
    "impact_verbs": {{
        "state": "",
        "suggestion": ""
    }}
    }}
    """
}

# Prompts para análisis de contenido
CONTENT_ANALYSIS_PROMPTS = {
    "experience_analysis": """
    Actúa como un reclutador profesional especializado en el puesto de {puesto}. Analiza la experiencia laboral del candidato en el siguiente CV.

    Evalúa:
    - Relevancia de la experiencia para el puesto objetivo
    - Antigüedad y continuidad de la experiencia
    - Logros y responsabilidades destacadas
    - Alineación con las competencias requeridas

    Devuelve exclusivamente un objeto JSON con esta estructura:

    {{
        "relevance_score": number between 1 and 10,
        "years_experience": total years of relevant experience,
        "key_achievements": list of 3 main achievements or responsibilities,
        "improvement_suggestions": list of 2 specific suggestions to enhance experience presentation
    }}

    Contenido del CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "education_analysis": """
    Actúa como un reclutador profesional. Analiza la formación académica del candidato en el siguiente CV.

    Evalúa:
    - Nivel educativo alcanzado
    - Relevancia de la formación para el puesto
    - Certificaciones o cursos complementarios
    - Calidad de la institución educativa

    Devuelve exclusivamente un objeto JSON con esta estructura:

    {{
        "education_level": "highest degree obtained",
        "relevance_score": number between 1 and 10,
        "institutions": list of educational institutions mentioned,
        "certifications": list of certifications or additional courses,
        "recommendations": list of 2 suggestions to improve education section
    }}

    Contenido del CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "skills_analysis": """
    Actúa como un reclutador profesional especializado en el puesto de {puesto}. Analiza las habilidades del candidato en el siguiente CV.

    Evalúa:
    - Habilidades técnicas relevantes para el puesto
    - Habilidades blandas demostradas
    - Nivel de dominio de cada habilidad
    - Gaps en habilidades requeridas

    Devuelve exclusivamente un objeto JSON con esta estructura:

    {{
        "technical_skills": list of technical skills found,
        "soft_skills": list of soft skills identified,
        "skill_gaps": list of missing skills for the position,
        "skill_level": "Basic/Intermediate/Advanced" based on overall skill presentation
    }}

    Contenido del CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "achievements_analysis": """
    Actúa como un reclutador profesional. Analiza los logros y resultados del candidato en el siguiente CV.

    Evalúa:
    - Logros cuantificables mencionados
    - Impacto de las contribuciones
    - Resultados específicos y medibles
    - Calidad de la presentación de logros

    Devuelve exclusivamente un objeto JSON con esta estructura:

    {{
        "quantifiable_achievements": list of achievements with numbers/percentages,
        "impact_level": "Low/Medium/High" based on achievement impact,
        "achievement_count": total number of achievements identified,
        "improvement_suggestions": list of 2 suggestions to better present achievements
    }}

    Contenido del CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "relevance": """
    Imagina que eres un revisor de currículums con experiencia en selección de personal. Tu tarea es revisar el CV de una persona que postula al siguiente cargo: **{puesto_postular}**.

    Tu objetivo es dar una **opinión profesional y cercana** sobre si la experiencia laboral de la persona está **vigente** y si **realmente aporta valor para el puesto al que postula**.

    Habla de tú a tú, como si dieras una recomendación directa al candidato. Usa un **solo párrafo, maximo 70 palabras**, en tono natural (sin parecer una IA ni usar lenguaje técnico innecesario) No saludes, que se vea natural. No quiero mensajes de aliento, no necesito mensajes de exclamacion. se un profesional.


    Evalúa:
    - Si la experiencia es reciente (últimos 10-15 años).
    - Si está alineada al cargo o al tipo de trabajo que se espera.
    - Si hay continuidad profesional o vacíos laborales importantes.
    - No comentes sobre estudios, habilidades o redacción.

    Ejemplos del tono esperado:
    - "Veo que tu experiencia reciente en atención al cliente encaja bien con lo que se busca en este puesto, aunque te recomiendo resaltar más logros concretos."
    - "Has trabajado hace tiempo en roles similares, pero sería ideal actualizar tu experiencia con algo más reciente para estar al día con lo que el mercado pide."
    - "Tuviste un rol interesante en logística hace unos años, pero hay un vacío importante desde entonces; te recomiendo explicar eso para evitar dudas."

    Texto del CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "impact_verbs": """
    Actúa como un reclutador profesional. Evalúa el uso de verbos de impacto en el siguiente currículum.

    Analiza:
    - Si el candidato usa verbos fuertes que transmiten logros, liderazgo o resultados (por ejemplo: lideré, optimicé, implementé).
    - Si los verbos son genéricos o poco potentes (como: ayudé, colaboré, realicé).
    - Si hay variedad o repetición.

    Devuelve un JSON con la siguiente estructura:

    {{
        "level": an integer from 1 to 10, where 10 represents excellent use of impact verbs.
        "comment": The tone of the suggestions should be exhortative, as if you were giving practical advice to the candidate. active verbs and oriented to results. In first person. a brief and clear professional observation, approximately 160 characters (no more than 180). Use a formal style, without emojis.
        "suggestions": a list of 3 specific suggestions to improve the verbs in the CV writing. Each suggestion must have a max of 25 words and explain clearly how to improve a generic or repeated verb, including a concrete example of replacement. The tone of the suggestions should be exhortative, as if you were giving practical advice to the candidate. active verbs and oriented to results.
    }}

    Do not include any text outside the JSON.

    Texto del CV:
    \"\"\"{contenido}\"\"\"
    """,
    
    "professional_profile": """
    Actúa como un experto en redacción de currículums. Analiza el contenido que te doy.


    Tu objetivo es evaluar la redacción del texto actual y sugerir una versión mejorada que sea más clara, profesional y alineada con estándares actuales. Usa como guía el siguiente enfoque de redacción (no lo copies literalmente):

    Debe empezar con: "Estudiante de "Número" ciclo de "Carrera" en la/el "Nombre de la Universidad"". Haz lo posible por ecnontrar esa informacion, en todo el texto. En caso no encuentres la informacino necesesaria indica algo como Estudiante de 'X' de la carrera 'Y' de la Universidad 'Z' como recomendacion. A partir de ahí, describe la identidad profesional de forma integral, combinando elementos personales como mentalidad, valores o trayectoria con intereses profesionales, fortalezas, experiencias relevantes o áreas de especialización. El objetivo es proyectar una imagen clara, auténtica y alineada con las metas profesionales del estudiante. Añade un toque personal que haga sentir al lector que conoce al candidato, pero manteniendo un tono profesional y directo. de acuerdo al puesto de {puesto}. en lo posible identifica la carrera y la universidad del candidato.

    No menciones para nada "X" "Y" "Z" no los menciones, tienes que si o si de todo el {contenido} encontrar la carrera, universidad.
    Devuelve solo un JSON con esta estructura:

    {{
    "current": "Texto actual del primer párrafo, sin encabezados ni contactos. Maximo unas 30 palabras",
    "recommended": "Texto recomendado, redactado de forma más clara y profesional, alineado con el enfoque sugerido. Maximo 40 palabras"
    }}

    Texto del perfil:
    \"\"\"{contenido}\"\"\"
    """,
    
    "position_adjustment": """
    Actúa como un reclutador experto en selección de personal para el rol de {puesto}. Evalúa el contenido del siguiente CV y clasifícalo en las siguientes categorías:

    - Habilidades de análisis
    - Resultados cuantificables
    - Habilidades blandas
    - Lenguaje técnico

    Para cada categoría proporciona:
    1. Un nivel: Bajo, Medio o Alto.
    2. Una acción concreta para mejorar. El tono de la accion  deben ser exhortativas, como si estuvieras dando consejos prácticos al candidato. No uses verbos en infinitivo que termine en ar er ir, dime ordenes, hablame de tu a tu. Si es posible, sugiere reemplazos específicos en el formato: "cambia #X# por #Y#", Maximo 30 palabras.

    Devuelve exclusivamente un objeto JSON con el siguiente formato:

    {{
        "analysis_skills": {{
            "level": "",
            "action": ""
        }},
        "quantifiable_results": {{
            "level": "",
            "action": ""
        }},
        "soft_skills": {{
            "level": "",
            "action": ""
        }},
        "technical_language": {{
            "level": "",
            "action": ""
        }}
    }}

    Todo en base al siguiente contenido del CV:
    \"\"\"{contenido}\"\"\"
    """
}

# Prompts para secciones específicas
SECTION_ANALYSIS_PROMPTS = {
    "work_experience": """
    Brinda sugerencias personalizadas de mejora por sección del CV, orientadas al rol de {puesto}.

    En esta parte, cubre lo siguiente:

    - En "Company" indica el nombre de la empresa tal como aparece en el CV. Identifícalo bien por favor. No confundir con el rol.
    - En "Current" incluye el texto completo de la experiencia laboral tal como figura en el CV.
    - En "Recommended" proporciona una versión mejorada del texto de experiencia laboral, aplicando el siguiente formato:

        Logro profesional + Elemento de descripción de trabajo + Cómo contribuyó a la empresa + % o cifra específica (si aplica).

        Además:
        - Inicia con un verbo de acción fuerte.
        - Alinea el contenido con las funciones o competencias clave para el rol de {puesto}.
        - Usa el contenido original como base, no inventes logros no mencionados.
        - Mejora redacción, impacto y claridad, sin agregar información no contenida en el texto original.

    Devuélveme exclusivamente un JSON con el siguiente formato, sin ningún tipo de encabezado, explicación, texto adicional o marcas como --json:

    [
    {{
        "Company": "Company name",
        "Current": "Textual representation as it appears in the CV. The job title and its description.",
        "Recommended": "Enhanced text applying the indicated format and oriented to the position of {puesto}. Mention results, whether they are integers or percentages, but you must mention the results, it was improved in so much"
    }}
    ]

    If there is more than one experience, include more objects in the array.  
    If there is no work experience, return a JSON with a single object indicating clearly that no work experience was found.  
    Do not include education, contact details or headers.  
    All information must be based solely on the information provided below:

    \"\"\"{contenido}\"\"\"
    """,
    
    "skills_tools": """
    Actúa como un experto en reclutamiento y redacción de currículums (CVs), con experiencia en múltiples industrias y perfiles profesionales.

    Analiza el siguiente contenido extraído de un CV:

    \"\"\"{contenido}\"\"\"

    El puesto objetivo del candidato es: **{puesto}**

    Tu tarea es:
    1. Identificar la sección relacionada con habilidades técnicas, herramientas, conocimientos técnicos o específicos del perfil (ej. software, metodologías, idiomas, maquinaria, plataformas, etc.).
    2. Evaluar si esta sección está bien redactada, clara, agrupada correctamente y alineada con el perfil profesional del puesto objetivo (**{puesto}**).
    3. Brindar un conjunto de recomendaciones útiles para mejorar esa sección con el fin de hacerla más atractiva y profesional para un reclutador en ese campo.

    Las recomendaciones debe incluir:
    - Primero iniciara asi CV ACTUAL y aqui colocaras una parte maximo 25 palabras de lo que se considera en el cv
    - Segundo iniciara RECOMMENDATIONS:  y  Pondras Las herramientos como debe ir Por ejemplo: "Informatica (Herramientas) (Nivel) solo es un ejemplo tu analizalo bien" 
    El tono de las recomendaciones deben ser exhortativas, como si estuvieras dando consejos prácticos al candidato. no usar verbos infinitivos mas si, orientados a resultados.

    Tu respuesta debe ser exclusivamente en formato JSON, con la siguiente estructura:

    {{
    "recommendations": [
        "CV ACTUAL: Aqui debes poner una parte del cv donde se menciona las habilidades y herramientas **{contenido}**,
        "RECOMMENDATIONS: Aqui debes darme recomendaciones para el puesto de {puesto}.",
    ]
    }}

    """,
    
    "education": """
    Analiza el siguiente CV y enfócate exclusivamente en la sección de educación o formación académica.

    Genera un array de recomendaciones generales en formato JSON. Estas recomendaciones deben:

    - Ser útiles y aplicables para mejorar la presentación y claridad de la formación académica.
    - Cada recomendación debe tener como minimo 20 palabras. El tono de las recomendaciones deben ser exhortativas, como si estuvieras dando consejos prácticos al candidato. no usar verbos infinitivos mas si, orientados a resultados. Haz recomendaciones puntuales y específicas, segun el puesto.
    - No inventes información no presente en el CV. Enfocado al puesto de {puesto}. 
    - Si no hay una sección de educación/formación académica en el CV, incluye una única recomendación indicando que dicha sección no fue encontrada. no usar verbos infinitivos mas si, orientados a resultados
    - Solo dame 4 recomendaciones
    Analiza este contenido:

    \"\"\"{contenido}\"\"\"

    Devuelve solo el JSON con este formato:

    {{
        "recommendations": [
            "Recomendación 1...",
            "Recomendación 2...",
            "Recomendación 3...",
            "Recomendación 4..."
        ]
    }}
    """,
    
    "volunteering": """
    Analiza el siguiente CV y detecta si hay una sección de voluntariado.
    Sino encuentras la sección de voluntariado, responde con un JSON indicando que no se encontró. SE MUY ESPECIFICO Y NO INVENTES INFORMACIÓN. NI LA CONFUNDAS CON EXPERIENCIA LABORAL. SE LITERALMENTE ESPECIFICO CON "VOLUNTARIADO".

    Si existe, por cada experiencia encontrada devuelve:

    - "Organization": nombre de la institución u organización.
    - "Current": texto original tal como aparece en el CV.
    - "Recommended": versión mejorada del texto, manteniendo la experiencia pero:
        - Iniciando con un verbo de acción potente.
        - Destacando logros, impacto o habilidades desarrolladas.
        - Enfocando el texto en competencias alineadas al rol de {puesto}.
        - Sin inventar contenido no presente en el CV.

    Si **no se encuentra** una sección de voluntariado, responde igualmente con un JSON en este formato:
    [
    {{
        "Organization": null,
        "Current": null,
        "Recommended": "No volunteering section found in the CV."
    }}
    ]

    Todo el análisis se basa únicamente en el contenido proporcionado a continuación:

    \"\"\"{contenido}\"\"\"

    Do not include text outside the JSON.
    """
}

# Prompts para análisis avanzado
ADVANCED_ANALYSIS_PROMPTS = {
    "formatting_language": """
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. 
    Por favor, proporciona un análisis detallado sobre el formato y lenguaje del CV, evaluando lo siguiente:

    1. Claridad del CV: ¿Es fácil de leer y entender? ¿La información está organizada de manera clara?
    2. Profesionalismo: ¿El CV tiene un aspecto profesional? ¿La tipografía y el diseño son adecuados?
    3. Errores gramaticales y ortográficos: ¿Cuántos errores gramaticales y ortográficos hay en el CV?
    4. Uso de verbos de acción: ¿Se utilizan verbos de acción en las descripciones de las experiencias laborales? ¿Son adecuados para resaltar logros?

    Formato de salida: 
    {{
        "formattingAndLanguage": {{
            "clarity": "string_clarity_evaluation",
            "professionalism": "string_professionalism_evaluation",
            "grammarSpellingErrorsCount": "number_error_count",
            "actionVerbsUsed": "boolean"
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """,
    
    "keywords": """
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. 
    Por favor, extrae las palabras clave relevantes para el puesto en cuestión y las habilidades generales mencionadas en el CV. 

    Primero, identifica las palabras clave relacionadas con el puesto de {puesto}, estas pueden ser habilidades técnicas, habilidades blandas o certificaciones que son relevantes para el rol. Luego, clasifica las palabras clave en las siguientes categorías:

    1. **Palabras clave encontradas**: Las palabras clave relacionadas con el puesto que aparecen en el CV.
    2. **Palabras clave faltantes**: Las palabras clave que son esenciales para el puesto pero no aparecen en el CV.
    3. **Palabras clave de habilidades generales encontradas**: Las habilidades generales que son valiosas para el rol (por ejemplo: comunicación, trabajo en equipo, etc.).

    Formato de salida: 
    {{
        "keywordAnalysis": {{
            "jobKeywordsFound": ["keyword_1", "keyword_2"],
            "jobKeywordsMissing": ["missing_keyword_1"],
            "generalSkillsKeywordsFound": ["general_skill_1"]
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """,
    
    "ats_compliance": """
    Eres un reclutador profesional con experiencia en el uso de sistemas de seguimiento de candidatos (ATS). A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. 
    Por favor, evalúa el cumplimiento del CV con respecto a los criterios comunes de un sistema ATS. 

    Tu tarea es realizar lo siguiente:

    1. **Puntaje de Cumplimiento ATS (de 0 a 100)**: Evalúa el grado de cumplimiento del CV con los criterios comunes de los sistemas ATS, como el uso de palabras clave, la legibilidad, el formato, y la estructura.
    2. **Problemas encontrados**: Proporciona una lista de los problemas comunes detectados en el CV en relación con el cumplimiento de los estándares ATS. Algunos problemas pueden incluir:
        - Uso insuficiente de palabras clave relacionadas con el puesto.
        - Formato inapropiado o no compatible con el ATS.
        - Mala organización de la información.
        - Información irrelevante o mal estructurada.
        - Falta de secciones claves como experiencia, habilidades, educación.
    3. **Recomendaciones para mejorar el cumplimiento ATS**: Brinda sugerencias sobre cómo mejorar el CV para cumplir mejor con los requisitos de un sistema ATS. Las recomendaciones deben ser prácticas y concretas.

    Formato de salida: 
    {{
        "atsCompliance": {{
            "score": "number_ats_score_0_100",
            "issues": ["ats_issue_1", "ats_issue_2"],
            "recommendations": ["ats_suggestion_1"]
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """,
    
    "skills": """
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. 
    Por favor, extrae las habilidades técnicas, habilidades blandas e idiomas mencionados en el CV. 

    Proporciona los datos de la siguiente manera, asegurándote de que cada sección esté bien organizada:

    - Habilidades Técnicas: [Lista de habilidades técnicas]
    - Habilidades Blandas: [Lista de habilidades blandas]
    - Idiomas: [Lista de idiomas con niveles de dominio]

    Ejemplo de formato correcto:

    {{
        "skills": {{
            "technical": [
                "Python",
                "JavaScript"
            ],
            "soft": [
                "Communication",
                "Teamwork"
            ],
            "languages": [
                "English (Advanced)",
                "Spanish (Native)"
            ]
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """,
    
    "education_extraction": """
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. Por favor, extrae la información relacionada con la educación. Para cada título educativo, proporciona la siguiente información de manera estructurada en JSON:

    - Grado: El título académico obtenido por el candidato (por ejemplo, Licenciatura en Ingeniería de Sistemas).
    - Institución: El nombre de la institución educativa en la que el candidato obtuvo su título.
    - Año de graduación: El año de graduación o la fecha en la que el candidato completó sus estudios.

    Formato JSON:
    {{
        "education": [
            {{
                "degree": "Degree obtained",
                "institution": "Educational institution",
                "graduationYear": "Graduation year"
            }}
        ]
    }}

    Contenido del CV a evaluar:
    {contenido}
    """,
    
    "common_errors": """
    Eres un reclutador profesional. A continuación, analiza el siguiente currículum vitae para identificar los errores más comunes que se presentan en este documento. Los errores pueden incluir:
    - Errores de formato
    - Errores ortográficos
    - Secciones mal estructuradas
    - Información innecesaria o faltante
    - Uso incorrecto de la tipografía o la organización visual

    Por favor, lista todos los errores comunes que encuentres en el CV y devuélvelos como una lista de errores. Cada error debe estar separado por guiones (-). No agregues información adicional.

    {contenido}
    """,
    
    "strengths": """
    Eres un reclutador profesional. A continuación, analiza el siguiente currículum vitae para identificar las fortalezas más comunes que se presentan en este documento. Los errores pueden incluir:
   
    Por favor, lista todos las fortalezas comunes que encuentres en el CV y devuélvelos como una lista de errorfortalezases. Cada fortalezas debe estar separado por guiones (-). No agregues información adicional.

    {contenido}
    """
}
