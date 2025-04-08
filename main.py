from fpdf import FPDF
from io import BytesIO
import requests
import tempfile  
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from fastapi import FastAPI, UploadFile, File
import openai
from pdf_reader import extract_text_from_pdf
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import altair as alt
import pandas as pd
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class PDF(FPDF):
    def header(self):
        image_url = "https://static.wixstatic.com/media/6ce38e_68ce9c2cf3f346a0a7a7bdee0a5ad2dd~mv2.png/v1/fill/w_202,h_44,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/MyWorkIn%20web.png"
        response = requests.get(image_url)
        
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name 

            image_width = 40
            image_height = 8 

            self.image(tmp_file_path, 10, 8, image_width, image_height)
        else:
            self.cell(0, 10, 'Imagen no encontrada', 0, 1, 'C')
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'workin2.com', 0, 1, 'R')  
        self.ln(5)  

    def add_bar_chart(self, title, score):
        temp_dir = tempfile.mkdtemp()

        fig, ax = plt.subplots(figsize=(6, 1))  
        ax.barh([0], [score], color='skyblue')
        ax.set_xlim(0, 100)  
        ax.set_yticks([]) 
        ax.set_xlabel('Puntuación')
        ax.set_title(title)
        
        chart_path = os.path.join(temp_dir, "chart.png")
        plt.savefig(chart_path, format='png', bbox_inches='tight')
        plt.close(fig)

        self.image(chart_path, x=10, w=180)
        self.ln(5) 


    def add_alignment_bar_chart(self, alignment_score):
        # Asegurarse de que la puntuación esté entre 0 y 100
        alignment_score = min(max(alignment_score, 0), 100)

        # Crear un DataFrame para Altair
        data = pd.DataFrame({
            'category': ['Alineación'],
            'score': [alignment_score]
        })

        # Crear el gráfico con Altair
        chart = alt.Chart(data).mark_bar(color='#8CBA80').encode(
            x=alt.X('score:Q', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(title='Porcentaje de Alineación')),
            y=alt.Y('category:N', axis=alt.Axis(title=''))
        ).properties(width=600, height=50)

        temp_dir = tempfile.mkdtemp()
        chart_path = os.path.join(temp_dir, "alignment_chart.png")
        chart.save(chart_path)

        # Insertar la imagen en el PDF
        self.image(chart_path, x=10, w=180)
        self.ln(5) 


def create_pdf(analysis_text: str,
                score: int,
                suitability_analysis: str,
                suitability_score: int,
                alignment_score: int,
                cv_approach_analysis: str,
                cv_improvement_suggestions: str,
                candidate_name: str,
                observations_and_opportunities: str, 
                elements_clave:str,
                cursos_ceritificaciones:str,
                formato_diseno_cv:str,
                areas_mejora:str,
                recomendaciones_especificas:str,
                puesto:str):
    pdf = PDF()
    pdf.add_page()

    pdf.add_font('Poppins-Regular', '', './fonts/Poppins-Regular.ttf', uni=True)
    pdf.add_font('Poppins-Bold', '', './fonts/Poppins-Bold.ttf', uni=True)

    pdf.ln(1)  
    pdf.set_font("Poppins-Bold", '', 16)
    pdf.set_text_color(3,70,123)  
    pdf.cell(0, 15, "INFORME DE REVISIÓN DE CV", 0, 1, 'C')  

    pdf.ln(1)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, f"{candidate_name}", 0, 1, 'I')  

    puesto = puesto.replace("_", " ")  
    pdf.set_font("Poppins-Regular", '', 12)  
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, f"{puesto}", 0, 1, 'I')


    pdf.ln(2) 
    pdf.set_draw_color(255, 165, 0)  
    pdf.set_line_width(0.5)  
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  
    
    
    pdf.ln(2) 
    pdf.set_font("Poppins-Bold", '', 14)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "SECCIÓN 1: RESUMEN DEL CANDIDATO", 0, 1, 'I') 

    pdf.set_text_color(0, 0, 0)  
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Poppins-Regular", size=12)

    pdf.multi_cell(0, 5, analysis_text)

    pdf.ln(10)
    pdf.set_font("Poppins-Bold", '', 14) 
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "SECCIÓN 2: ANÁLISIS DE ADECUACIÓN AL ROL", 0, 1, 'I')  

    pdf.ln(1)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Brechas frente al rol", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)  
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, suitability_analysis)  


    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Alineación con el puesto", 0, 1, 'I') 

    pdf.set_text_color(0, 0, 0)  
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Poppins-Regular", size=12)

    #pdf.multi_cell(0, 10, f"Porcentaje de alineación: {alignment_score}%")

    pdf.add_alignment_bar_chart(alignment_score)


    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Enfoque del CV", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, cv_approach_analysis) 



    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "SECCIÓN 3: SUGERENCIAS DE MEJORA POR SECCIÓN DEL CV", 0, 1, 'I')

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, cv_improvement_suggestions)  

    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "SECCIÓN 4: OBSERVACIONES Y OPORTUNIDADES DE MEJORA", 0, 1, 'I')


    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Fortalezas", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, observations_and_opportunities)

    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Áreas de mejora", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, areas_mejora) 


    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Recomendaciones especificas", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, recomendaciones_especificas) 





    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "SECCIÓN 5:  RECOMENDACIONES ADICIONALES", 0, 1, 'I')

    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Palabras clave para filtros ATS", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, elements_clave)

    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Cursos y certificaciones recomendados  ", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, cursos_ceritificaciones)

    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "Formato del CV ", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.multi_cell(0, 5, formato_diseno_cv)


    pdf.ln(10) 
    pdf.set_font("Poppins-Bold", '', 10) 
    pdf.set_text_color(3,70,123)  
    pdf.cell(0, 10, "Gracias Por Utilizar Los Servicios De MyWorkIn.", 0, 1, 'C')

    pdf.ln(1)  
    pdf.set_font("Poppins-Bold", '', 10)  
    pdf.set_text_color(255, 165, 0) 
    pdf.multi_cell(0, 10, "Para Mas Información, visiten en workin2.com o contactanos en diego@workin2.com", align='C')

    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1')) 
    pdf_output.seek(0)  

    return pdf_output


@app.get("/analizar-cv/")
async def analizar_cv(pdf_url: str, puesto_postular: str):
    response = requests.get(pdf_url)
    
    puesto = puesto_postular

    if response.status_code != 200:
        return {"error": "No se pudo descargar el archivo PDF."}
    
    pdf_content = BytesIO(response.content)

    contenido = extract_text_from_pdf(pdf_content)


    prompt6 = f"""
    Eres un reclutador profesional. Por favor, extrae el nombre completo del candidato que aparece en el CV para el puesto de {puesto}. El nombre debe ser identificado con precisión, considerando los posibles formatos y variaciones en la presentación de la información del candidato dentro del documento. 
    Solamente dame el nombre completo

    Ejemplo: (Solamente dame eso)
    Diego Rodríguez Franco​
    {contenido}
    """
    
    response6 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt6}],
        temperature=0.7,
        #max_tokens=50  
    )
    
    candidate_name = response6['choices'][0]['message']['content'].strip()



    prompt1 = f"""
    Eres un reclutador profesional. Analiza el siguiente currículum vitae para el puesto de {puesto}.
    Debes proporcionar el siguiente análisis detallado del CV:

    Genera un resumen claro, atractivo y profesional que destaque el potencial del candidato, alineando su perfil con habilidades transferibles, conocimientos, logros formativos y actitud, incluso si no tiene experiencia directa en el cargo. Asegúrate de cubrir:
    1. Título y formación profesional (ej. “Ingeniero industrial”).
    2. Experiencia relevante o transferible de acuerdo con la posición que busca.
    3. Habilidades duras y blandas destacadas.
    4. Alineación con el rol postulado.
    5. Valor agregado que puede aportar.

    Tiene que ser un resumen no tan largo, Un parrafo, Maximo 6 lineas
    {contenido}
    """

    prompt2 = f""" Todo relacionado a {puesto} quiero que identifiques brechas
        - Habilidades técnicas faltantes (ej. {puesto}).
        - Conocimientos específicos del sector (ej. banca).
        - Certificaciones o formación adicional necesaria.
        - Herramientas requeridas por el rol y nivel de dominio.
    2. Nivel de cada brecha: Alto / Medio / Bajo.
    3. Recomendaciones de mejora claras y accionables. las recomendaciones deben ir en cada brecha, no por separado

     Ejemplo: igual a este ejmplo debe ser: las recomendaciones deben ir en cada brecha
    - {puesto} (Alto): Requiere capacitación específica para mejorar. 
    - Conocimiento del sector bancario (Alto): Necesita inmersión en el sector. 
    - Herramientas de {puesto} (Medio): Mejorar el uso de herramientas específicas de {puesto} 
    - Certificaciones en {puesto} (Medio): Obtener certificaciones reconocidas.

    {contenido}
    """

    prompt3 = f"""
    Eres un reclutador profesional. Analiza el perfil del candidato para el puesto de {puesto}. Evalúa lo siguiente para determinar qué tan adecuado es el candidato para el puesto:

    - Experiencia laboral relevante.
    - Habilidades necesarias para el rol de {puesto}.
    - Capacitación y formación complementaria.
    - Actitudes y aptitudes generales relacionadas con el {puesto}.

    Luego, calcula un porcentaje de alineación, que debe ser un número entre 0 y 100, indicando el grado de adecuación entre el perfil del candidato y el puesto. 

    Por favor, responde con solo un número que represente el porcentaje de encaje.

    Por ejemplo: 89 

    Solo debe ser un numero
    {contenido}
    """


    response1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt1}],
        temperature=0.7,
       # max_tokens=100
    )
    analysis_text = response1['choices'][0]['message']['content']

    response2 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt2}],
        temperature=0.7,
        #max_tokens=150
    )
    suitability_analysis = response2['choices'][0]['message']['content']

    score_match = re.search(r'Puntuación final:\s*(\d+)', analysis_text)
    suitability_score_match = re.search(r'Porcentaje de encaje:\s*(\d+)', suitability_analysis)

    score = 0
    suitability_score = 0

    if score_match:
        score = int(score_match.group(1))
    
    if suitability_score_match:
        suitability_score = int(suitability_score_match.group(1))


    response3 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt3}],
        temperature=0.7,
        #max_tokens=100  
    )
    alignment_analysis = response3['choices'][0]['message']['content']

    alignment_score = 0
    try:
        # Asegurarse de que alignment_score sea un número entero
        alignment_score_str = response3['choices'][0]['message']['content'].strip().replace('%', '')
        alignment_score = int(alignment_score_str)  # Convertir a entero
    except (ValueError, IndexError) as e:
        print(f"Error al obtener la puntuación de alineación: {e}")

    prompt4 = f"""
    Enfoque del CV:
    Utilizando el porcentaje de encaje de {alignment_score}% para el puesto de {puesto}, genera un análisis sobre cómo el perfil del candidato se ajusta a este puesto. Considera lo siguiente:

    - Habilidades generales y específicas que tiene el candidato.
    - Áreas donde tiene una fuerte alineación con el puesto (por ejemplo, habilidades analíticas, gestión de proyectos).
    - Áreas donde el candidato tiene desajustes importantes (por ejemplo, falta de experiencia específica en {puesto}).

    El análisis debe ser un párrafo coherente, explicando cómo el porcentaje se traduce en la adecuación del candidato al puesto. Tiene que ser breve y entendible
    """

    response4 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt4}],
        temperature=0.7,
       # max_tokens=130
    )


    prompt5 = f"""
    SECCIÓN 3: SUGERENCIAS DE MEJORA POR SECCIÓN DEL CV

    Brinda sugerencias personalizadas de mejora por sección del CV, orientadas al rol de {puesto}. En esta parte, cubre lo siguiente:

    1. Experiencia Laboral:
        - Iniciar cada logro con un verbo de acción poderoso.
        - Incluir resultados cuantificables.
        - Alinear cada experiencia con el rol objetivo.
        - Brindar ejemplos con los verbos pero relacionados con el cv, no quiero que me des ejemplos tuyos, utiliza oraciones del cv y agrega el verbo, pero referente a la experiencia laboral
        Dame unos 3 ejemplos, tienen que ser concretos no solamente me des los verbos, si no la oracion completa

    2. Formación Académica:
        Debes verificar si tengo datos como:
        - Nombre de la universidad.
        - Carrera.
        - Especialización (si existe).
        - Mérito académico destacado (solo si es relevante).
        Si tengo esos datos debes darme que otra informacion de formacion academica puedo agregar

    3. Habilidades Técnicas:
            Debes brindarme Habilidades  Técnicas, en caso no tenga esta informacion: si tengo, ve que otra habilidad  puedes dar, pero no me pongas las que tengo

        - Nombre de la herramienta.
        - Nivel de dominio (Básico / Intermedio / Avanzado).
        - Relevancia con el rol.

    4. Certificaciones:
        - Sugerir certificaciones específicas que potencien el perfil.
        - Nombre de la certificación.
        - Institución que la emite (si hay).
        - Fecha de obtención.

    Por favor, asegúrate de proporcionar sugerencias específicas y prácticas para cada sección mencionada, basadas en el perfil del candidato y su adecuación al rol de {puesto}.
    No agregues asetericos, ni numerales
    {contenido}
    """

    response5 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt5}],
        temperature=0.7,
        #max_tokens=200 
    )
    cv_improvement_suggestions = response5['choices'][0]['message']['content']

    prompt7 = f"""
    Eres un reclutador profesional. Por favor, proporciona un análisis detallado. En este análisis, evalúa lo siguiente:

    Identifica las áreas en las que el candidato sobresale y tiene un fuerte desempeño. Esto puede incluir habilidades específicas, experiencia relevante, o logros notables que aportan valor al puesto. Dame en guiones, se breve y consiso

    Se breve y consiso, hazlo en guiones y se especifico

    Por favor, asegúrate de que cada sección esté claramente separada y de que las recomendaciones sean específicas y detalladas.

    No debe a ver subtitulos no les coloques numerales o astericos
    No pongas subtitulos, todo hazlo por guiones y de manera general

    {contenido}
    """

    response7 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt7}],
        temperature=0.7,
    )
    observations_and_opportunities = response7['choices'][0]['message']['content']


    prompt13 = f"""
    Eres un reclutador profesional. Por favor, proporciona un análisis detallado. En este análisis, evalúa lo siguiente:

    Señala las áreas donde el candidato puede mejorar para ser más adecuado para el puesto. Esto puede incluir habilidades faltantes, experiencia relevante o áreas en las que necesita formación adicional.

    Por favor, asegúrate de que cada sección esté claramente separada y de que las recomendaciones sean específicas y detalladas.

    Se breve y consiso, hazlo en guiones y se especifico

    No debe a ver subtitulos no les coloques numerales o astericos, sin asteriscos
    
    No pongas subtitulos, todo hazlo por guiones y de manera general

    No quiero Asteriscos, si el {puesto} es en ingles, tu mantiene el puesto tal como es pero la respuesta en español

    No quiero astericos, no me des subtitulos

    {contenido}
    """

    response13 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt13}],
        temperature=0.7,
    )
    areas_mejora = response13['choices'][0]['message']['content']





    prompt14 = f"""
    Eres un reclutador profesional. Por favor, proporciona un análisis detallado. En este análisis, evalúa lo siguiente:

    Proporciona sugerencias claras y accionables para cada área de mejora. Las recomendaciones deben ser prácticas y enfocadas en cómo el candidato puede mejorar para mejorar su idoneidad para el puesto.

    Por favor, asegúrate de que cada sección esté claramente separada y de que las recomendaciones sean específicas y detalladas.

    Se breve y consiso, hazlo en guiones y se especifico

    No debe a ver subtitulos no les coloques numerales o astericos, sin asteriscos, quiero por guiones, se claro
    
    No pongas subtitulos, todo hazlo por guiones y de manera general
    {contenido}
    """

    response14 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt14}],
        temperature=0.7,
    )
    recomendaciones_especificas = response14['choices'][0]['message']['content']




    cv_approach_analysis = response4['choices'][0]['message']['content']



    prompt8 = f"""
    Eres un reclutador profesional. Proporciona un conjunto de recomendaciones prácticas y estratégicas para optimizar el CV a nivel técnico y de contenido, considerando su compatibilidad con filtros ATS (Applicant Tracking Systems), posibles mejoras en formación profesional, y aspectos de formato y presentación general. Esta sección apunta a los ajustes finales que pueden marcar la diferencia entre ser descartado o avanzar en un proceso de selección.

        - Identificar palabras clave específicas del rol al que postula el candidato.
        - Usar términos que suelen estar en las descripciones de puestos, especialmente habilidades técnicas y blandas.
        - Asegurar que estas palabras clave estén integradas de forma natural en el CV, no en forma de lista.
        - Si no están, sugerir dónde y cómo integrarlas.
        Tiene que sacarlas de la posición que estoy buscando. Por ejemplo, si voy a una posición de {puesto}, quizas palabras clave sean SEO, SEM, REDES SOCIALES, ETC todo relacionado al {puesto}
        esas palabras variaran dependiendo el {puesto} al que estoy

        Proporciona filtros ATS, separados por guiones. Responde únicamente con los filtros ATS en el siguiente formato por guiones

     Tienes que darme asi las palabras, solo 5 palabras, Las palabras claves no deben ser del cv, si no del puesto que se busca

    {contenido}
    """


    response8 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt8}],
        temperature=0.7,
    )
    elements_clave = response8['choices'][0]['message']['content']


    prompt9 = f"""
    Sugerir cursos técnicos para cubrir brechas detectadas en el sector.
    - Recomendar certificaciones alineadas a las competencias clave del rol.
    - Añadir formación en habilidades blandas relevantes y diferenciadoras (ej. comunicación, gestión del tiempo, trabajo en equipo). 
    Ser específicos: nombre, plataforma o institución, y razón por la que son valiosos.
    {contenido}
    """

    response9 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt9}],
        temperature=0.7,
    )

    cursos_ceritificaciones = response9['choices'][0]['message']['content']


    prompt12 = f"""
     Eres un reclutador profesional. Evalúa si el CV cumple con los criterios mínimos de legibilidad y presentación profesional, basándote en el formato Harvard. Los criterios son los siguientes:

    1. 1 página: El CV debe ocupar solo una página. (Debes verificar que si tiene una pagina o mas)
    2. Buena jerarquía visual: Asegúrate de que la información esté organizada de manera clara, con títulos y subtítulos bien diferenciados. (Se directo)
    3. Tipografía clara: El CV debe usar una tipografía legible y profesional. (Se breve al indicar eso)
    4. Uso correcto de espacios: Los márgenes y el espaciado deben ser adecuados, sin saturar el documento.
    5. Estructura coherente: El CV debe seguir una estructura lógica, por ejemplo, con secciones bien definidas (formación, experiencia laboral, habilidades, etc.).

    Si el CV cumple con estos criterios, confirma que pasa los filtros ATS. Si no, indica que no cumple y proporciónale el siguiente enlace donde puede encontrar un formato adecuado: https://www.workin2.com/post/descarga-gratis-formatos-de-cv-para-estudiantes-y-practicantes.
    No agregues asetericos, ni numerales

    Tienes que verificar bien el documento, contar todo bien
    Ejemplo: Algo asi debe ser: si es que cumple: Tienes que indicar detalle por detalle
    El CV cumple con los criterios mínimos de legibilidad y presentación profesional en
    formato Harvard. 
    1. Cumple con tener una sola página.
    2. La jerarquía visual está bien definida con títulos y subtítulos diferenciados.
    3. La tipografía es clara y profesional.
    4. Los espacios y márgenes son adecuados, sin saturar el documento.
    5. Sigue una estructura coherente con secciones bien definidas (Experiencia,
    Voluntariado, Educación, Habilidades & Certificaciones, Logros destacados, Hobbies).
    Por lo tanto, este CV pasa los filtros ATS. ¡Buen trabajo!

    {contenido}
    """

    response12 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt12}],
        temperature=0.7,
    )

    formato_diseno_cv = response12['choices'][0]['message']['content']



    pdf_output = create_pdf(analysis_text,
                            score,
                            suitability_analysis,
                            suitability_score,
                            alignment_score,
                            cv_approach_analysis,
                            cv_improvement_suggestions,
                            candidate_name,
                            observations_and_opportunities,
                            elements_clave,
                            cursos_ceritificaciones,
                            formato_diseno_cv,
                            areas_mejora,
                            recomendaciones_especificas,
                            puesto)

    public_folder = './static/pdf_reports/'
    os.makedirs(public_folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Guardar el archivo PDF
    pdf_filename = f"{candidate_name.replace(' ', '-')}_{now}.pdf"
    pdf_filepath = os.path.join(public_folder, pdf_filename)

    with open(pdf_filepath, 'wb') as f:
        f.write(pdf_output.getvalue())

    # Devuelve la URL donde el PDF está disponible para ser accedido
    pdf_url = f"https://api-cv-myworkin.onrender.com/static/pdf_reports/{pdf_filename}"

    # Devuelves el enlace en formato JSON
    return JSONResponse(content={"pdf_url": pdf_url})



def extract_score_from_text(text):
    try:
        score = int(text.split(":")[1].strip().split()[0])
        return score
    except Exception as e:
        return 0



