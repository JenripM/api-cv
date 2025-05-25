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
import json
import hashlib
from datetime import datetime
import time
from fastapi.middleware.cors import CORSMiddleware       # ← NUEVO

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # permite todos los dominios
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],       # cualquier cabecera
)

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

def safe_json_load(data):
    try:
        # Intentamos cargar el JSON
        return json.loads(data)
    except json.JSONDecodeError:
        # Si ocurre un error, retornamos None o el valor que prefieras
        return None
        
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
                puesto:str,
                formacion_academica:str,
                habilidades_tecnicas:str,
                certificaciones:str,
                cv_rating:str):
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
    # Primero, agregamos el nombre del candidato (a la izquierda)
    pdf.cell(70, 10, f"{candidate_name}", 0, 0, 'L')  # Alineado a la izquierda
    pdf.ln(10)  
    # Luego, agregamos el puesto (en el centro)
    puesto = puesto.replace('_', ' ')
    pdf.cell(70, 10, f"{puesto}", 0, 0, 'I')  # Alineado al centro

    pdf.set_font("Poppins-Bold", '', 15)  # Cambiamos el tamaño de la fuente a 20 para el cv_rating

    circle_radius = 20
    circle_x = 180  
    circle_y = pdf.get_y() + 5 
    pdf.set_line_width(1)
    # Dibuja el círculo
    pdf.set_draw_color(2, 69, 121)  
    pdf.set_fill_color(0, 0, 0)  
    pdf.ellipse(circle_x - circle_radius, circle_y - circle_radius, 2 * circle_radius, 2 * circle_radius)

    pdf.set_font("Poppins-Bold", '', 25)  

    pdf.set_text_color(2, 69, 121)  
    cv_rating_text = f"{cv_rating} / 10"  
    pdf.text(circle_x - 10, circle_y + 4, cv_rating_text)  

    pdf.set_font("Poppins-Bold", '', 12)  

    pdf.ln(32) 
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


    #pdf.ln(2)  
   # pdf.set_font("Poppins-Bold", '', 12)
    #pdf.set_text_color(0, 0, 0)  
    #pdf.cell(0, 15, "Enfoque del CV", 0, 1, 'I') 

    #pdf.set_font("Poppins-Regular", '', 12)
    #pdf.set_text_color(0, 0, 0)  
   # pdf.multi_cell(0, 5, cv_approach_analysis) 



    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "SECCIÓN 3: SUGERENCIAS DE MEJORA POR SECCIÓN DEL CV", 0, 1, 'I')

    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "1. Experiencia Laboral", 0, 1, 'I') 

    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  
    
    suggestions_data = json.loads(cv_improvement_suggestions)


    
    # Ahora puedes manipularlo como una lista de diccionarios
    for item in suggestions_data:
        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "Empresa:", 0, 1, 'I') 
        pdf.ln(0)  
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f"{item['Empresa']}")

        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "CV Actual:", 0, 1, 'I') 
        pdf.ln(0)  
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f" {item['Actual']}")

        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "Resultado Medible:", 0, 1, 'I')
        pdf.ln(0)   
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f"{item['Evaluación']}")

        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "Sugerencia:", 0, 1, 'I') 
        pdf.ln(0)  
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f"{item['Sugerencia']}")
        pdf.ln(5)  


    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "2. Formación Academica", 0, 1, 'I') 


    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  


    suggestions_data2 = json.loads(formacion_academica)


    for item in suggestions_data2:
        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "CV Actual:", 0, 1, 'I') 
        pdf.ln(0)  
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f" {item['Actual']}")

        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "Evaluación:", 0, 1, 'I')
        pdf.ln(0)   
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f"{item['Evaluación']}")

        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "Sugerencia:", 0, 1, 'I') 
        pdf.ln(0)  
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f"{item['Sugerencia']}")
        pdf.ln(5)  

    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "3. Habilidades", 0, 1, 'I') 


    pdf.set_font("Poppins-Regular", '', 12)
    pdf.set_text_color(0, 0, 0)  



    suggestions_data3 = json.loads(habilidades_tecnicas)


    for item in suggestions_data3:
        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "CV Actual:", 0, 1, 'I') 
        pdf.ln(0)  
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f" {item['Actual']}")

        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "Evaluación:", 0, 1, 'I')
        pdf.ln(0)   
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f"{item['Evaluación']}")

        pdf.set_font("Poppins-Bold", '', 12)
        pdf.cell(0, 15, "Sugerencia:", 0, 1, 'I') 
        pdf.ln(0)  
        pdf.set_font("Poppins-Regular", '', 12)
        pdf.multi_cell(0, 5, f"{item['Sugerencia']}")
        pdf.ln(5)  


   # pdf.ln(2)  
   # pdf.set_text_color(0, 0, 0)  
   # pdf.set_font("Poppins-Bold", '', 12)
   # pdf.set_text_color(0, 0, 0)  
   # pdf.cell(0, 15, "4. Certificaciones", 0, 1, 'I') 

   # pdf.set_font("Poppins-Regular", '', 12)
   # pdf.set_text_color(0, 0, 0)  
   # pdf.multi_cell(0, 5, certificaciones)


   # pdf.ln(2)  
    #pdf.set_font("Poppins-Bold", '', 12)
   # pdf.set_text_color(0, 0, 0)  
   # pdf.cell(0, 15, "SECCIÓN 4: OBSERVACIONES Y OPORTUNIDADES DE MEJORA", 0, 1, 'I')


    #pdf.ln(2)  
    #pdf.set_font("Poppins-Bold", '', 12)
    #pdf.set_text_color(0, 0, 0)  
    #pdf.cell(0, 15, "Fortalezas", 0, 1, 'I') 

    #pdf.set_font("Poppins-Regular", '', 12)
    #pdf.set_text_color(0, 0, 0)  
    #pdf.multi_cell(0, 5, observations_and_opportunities)

    #pdf.ln(2)  
    #pdf.set_font("Poppins-Bold", '', 12)
    #pdf.set_text_color(0, 0, 0)  
    #pdf.cell(0, 15, "Áreas de mejora", 0, 1, 'I') 

    #pdf.set_font("Poppins-Regular", '', 12)
    #pdf.set_text_color(0, 0, 0)  
    #pdf.multi_cell(0, 5, areas_mejora) 


    #pdf.ln(2)  
    #pdf.set_font("Poppins-Bold", '', 12)
    #pdf.set_text_color(0, 0, 0)  
    #pdf.cell(0, 15, "Recomendaciones especificas", 0, 1, 'I') 

    #pdf.set_font("Poppins-Regular", '', 12)
    #pdf.set_text_color(0, 0, 0)  
    #pdf.multi_cell(0, 5, recomendaciones_especificas) 





    pdf.ln(2)  
    pdf.set_font("Poppins-Bold", '', 12)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(0, 15, "SECCIÓN 4:  RECOMENDACIONES ADICIONALES", 0, 1, 'I')

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
    start_time = time.time()
    end_time = time.time()
    processing_time_ms = int((end_time - start_time) * 1000)  # Convertir a milisegundos
    analysis_datetime = datetime.now().isoformat()  # "YYYY-MM-DDTHH:MM:SS"

    original_pdf = pdf_url
    response = requests.get(pdf_url)
    
    puesto = puesto_postular

    if response.status_code != 200:
        return {"error": "No se pudo descargar el archivo PDF."}
    
    pdf_content = BytesIO(response.content)

    contenido = extract_text_from_pdf(pdf_content)

    email = extract_email(contenido)


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

    Tiene que ser un resumen no tan largo, Un parrafo, Maximo 5 lineas
    {contenido}
    """

    prompt2 = f"""

    Compáralo con los requisitos habituales para el rol de {puesto}, e identifica las principales 
    brechas lo que se espera para desempeñarse con éxito en ese cargo. 
    Clasifica las brechas en las siguientes categorías: 
    Habilidades técnicas      Todo en relación con el {puesto}
    Conocimientos del sector o industria      Todo en relación con el {puesto}
    Certificaciones o formación clave      Todo en relación con el {puesto}
    Herramientas, plataformas o tecnologías     Todo en relación con el {puesto}

    Para cada brecha, proporciona:     
    Una descripción clara y específica. 
    Una recomendación concreta, práctica y de aplicación inmediata o a corto plazo. 

    Formato de salida (una línea por brecha, un comentario por categoría): 

    Habilidad técnica: [nombre] - [Descripción].  
    Recomendación: [acción concreta].  

    Conocimiento sectorial: [nombre] - [Descripción].  
    Recomendación: [acción concreta].  

    Certificación/formación: [nombre] - [Descripción].  
    Recomendación: [acción concreta].  

    Herramienta/tecnología: [nombre] - [Descripción].  
    Recomendación: [acción concreta].  

    Sé breve, profesional y enfocado en el {puesto}.
    Cada punto debe estar separado en líneas distintas para claridad.

    Todo en relación con el {puesto}
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


    prompt_error_analysis = f"""
    Eres un reclutador profesional. A continuación, analiza el siguiente currículum vitae para identificar los errores más comunes que se presentan en este documento. Los errores pueden incluir:
    - Errores de formato
    - Errores ortográficos
    - Secciones mal estructuradas
    - Información innecesaria o faltante
    - Uso incorrecto de la tipografía o la organización visual

    Por favor, lista todos los errores comunes que encuentres en el CV y devuélvelos como una lista de errores. Cada error debe estar separado por guiones (-). No agregues información adicional.

    {contenido}
    """

    response_error_analysis = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_error_analysis}],
        temperature=0.7,
    )

    errores_comunes = response_error_analysis['choices'][0]['message']['content'].strip()


    prompt_fortaleza = f"""
    Eres un reclutador profesional. A continuación, analiza el siguiente currículum vitae para identificar las fortalezas más comunes que se presentan en este documento. Los errores pueden incluir:
   
    Por favor, lista todos las fortalezas comunes que encuentres en el CV y devuélvelos como una lista de errorfortalezases. Cada fortalezas debe estar separado por guiones (-). No agregues información adicional.

    {contenido}
    """

    respon_fortaleza = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_fortaleza}],
        temperature=0.7,
    )

    fortalezas = respon_fortaleza['choices'][0]['message']['content'].strip()


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
    Brinda sugerencias personalizadas de mejora por sección del CV, orientadas al rol de {puesto}. En esta parte, cubre lo siguiente:

    En la parte de "Actual" indicaras todo lo de experiencia laboral, igual que en el cv {contenido}
    En la parte de "Evaluacion" indicaras como Si presenta un resultado cuantificable o No presenta resultado cuantificable
    En la parte de "Sugerencia" debes darme la correccion segun la parte "Actual":
        - Iniciar cada logro con un verbo de acción poderoso.
        - Incluir resultados cuantificables.
        - Alinear cada experiencia con el rol objetivo.
        - Brindar ejemplos con los verbos pero relacionados con el cv, no quiero que me des ejemplos tuyos, utiliza oraciones del cv y agrega el verbo, pero referente a la experiencia laboral.

      
    Devuelme como ese JSON, en formato correcto
    Cada punto que hagas, hazle un salto de línea, o sea que no esté todo pegado. Osea en  Cada Corchete Separado
    Solo es de la formación Laboral. TODO LO QUE ANALIZAS ES RESPECTO AL CV, NO ME AGREGUES COSAS QUE NO SON

    Todo en relacion con el {puesto}

    Devuélveme solo en formato JSON, con la siguiente estructura exacta (asegúrate de que el formato sea correcto):

       [{{
            "Empresa":,
            "Actual": ,
            "Evaluación": ,
            "Sugerencia": 
        }}
        {{
            "Empresa":,
            "Actual": ,
            "Evaluación": ,
            "Sugerencia": 
        }}]
      
    """


    while True:
        response5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt5}],
            temperature=0.7,
            #max_tokens=200 
        )
        cv_improvement_suggestions = response5['choices'][0]['message']['content']

        suggestions_data = safe_json_load(cv_improvement_suggestions)
        if suggestions_data is not None:
            break


    prompt20 = f"""

    Brinda sugerencias personalizadas de mejora por sección del CV, orientadas al rol de {puesto}. En esta parte, cubre lo siguiente:
    Formación académica: 

    En la parte de "Actual" indicaras todo lo de experiencia academica, igual que en el cv {contenido}, Solo Menciona Grado Academico - Profesion o Estudio

    En la parte de "Evaluacion" indicaras Correcto o Incorrecto

    En la parte de "Sugerencia" debes darme la correccion segun la parte "Actual":
        - Si falta alguno de estos elementos, indica específicamente qué falta., Si falta algo en "Evaluacion" seria incorrecto 
        - Si hay información adicional (como materias, cursos, proyectos, etc.), indica concretamente 
        qué sobra y que debe eliminarlo. 
        - Si no figura el orden de mérito y pudiera tenerlo, sugiere que lo agregue si corresponde 
        (importante). Evita decir que indique lo de promedio.
        - Si no necesita sugerencia, es decir todo esta correcto, solo indicar Esta bien
        - Indicar en caso no se mencione el estudio, o carrera estudiada o profesion, Si no menciona en "Evaluacion" seria incorrecto 

    Devuélveme solo en formato JSON, con la siguiente estructura exacta (asegúrate de que el formato sea correcto):
       [{{
            "Actual": ,
            "Evaluación": ,
            "Sugerencia": 
        }}
        {{
            "Actual": ,
            "Evaluación": ,
            "Sugerencia": 
        }}]
        Devuelme como ese JSON, en formato correcto
        Cada punto que hagas, hazle un salto de línea, o sea que no esté todo pegado. Osea en  Cada Corchete Separado
        Solo es de la formación academica., TODO LO QUE ANALIZAS ES RESPECTO AL CV, NO ME AGREGUES COSAS QUE NO SON
        {contenido}
    """

    while True:
        response20 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt20}],
            temperature=0.7,
            #max_tokens=200 
        )
        formacion_academica = response20['choices'][0]['message']['content']

        suggestions_data2 = safe_json_load(formacion_academica)
        if suggestions_data2 is not None:
            break




    prompt21 = f"""

    Brinda sugerencias personalizadas de mejora por sección del CV, orientadas al rol de {puesto}. En esta parte, cubre lo siguiente:

        Habilidades: 
        ● Verifica que las habilidades estén agrupadas por tipo (por ejemplo: Programación, 
        Herramientas, Software). 
        ● Verifica que cada habilidad tenga un nivel de dominio indicado (por ejemplo: Básico, 
        Intermedio, Avanzado). 
        ● El formato debe ser corrido por agrupación, como en este ejemplo: 
        Programación: Python (Avanzado), C++ (Básico) 
        Formato de salida: 
        CV Actual: [Texto original de la sección de habilidades] 
        Evaluación: [Correcto / Falta nivel / Falta agrupación / Faltan ambos] 
        Sugerencia: [Versión sugerida con habilidades agrupadas y nivel de dominio en formato 
        correcto, Si No hay sugerencias, indicar que todo esta bien] 
        Contenido del CV a evaluar: 
        No Agregues Simbolos o Guiones o Astericos en los Subtitulos
        Cada punto que hagas, hazle un salto de linea, osea que no este todo pegado
        Todo en relacion con el {puesto}

        Devuélveme solo en formato JSON, con la siguiente estructura exacta (asegúrate de que el formato sea correcto):
        [{{
                "Actual": ,
                "Evaluación": ,
                "Sugerencia": 
            }}
            {{
                "Actual": ,
                "Evaluación": ,
                "Sugerencia": 
            }}]
        Devuelme como ese JSON, en formato correcto

        Cada punto que hagas, hazle un salto de línea, o sea que no esté todo pegado. Osea en  Cada Corchete Separado
        Solo es de la Habilidades., TODO LO QUE ANALIZAS ES RESPECTO AL CV, NO ME AGREGUES COSAS QUE NO SON
    {contenido}
    """

    while True:
        response21 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt21}],
            temperature=0.7,
            #max_tokens=200 
        )
        habilidades_tecnicas = response21['choices'][0]['message']['content']

        suggestions_data3 = safe_json_load(habilidades_tecnicas)
        if suggestions_data3 is not None:
            break

    prompt22 = f"""

    Brinda sugerencias personalizadas de mejora por sección del CV, orientadas al rol de {puesto}. En esta parte, cubre lo siguiente:

        - Sugerir certificaciones específicas que potencien el perfil.
        - Nombre de la certificación.
        - Institución que la emite (si hay).
        - Fecha de obtención.

    Por favor, asegúrate de proporcionar sugerencias específicas y prácticas para cada sección mencionada, basadas en el perfil del candidato y su adecuación al rol de {puesto}.
    No agregues asetericos, ni numerales
        Cada punto que hagas, hazle un salto de linea, osea que no este todo pegado, TODO LO QUE ANALIZAS ES RESPECTO AL CV, NO ME AGREGUES COSAS QUE NO SON

    {contenido}
    """

    response22 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt22}],
        temperature=0.7,
        #max_tokens=200 
    )
    certificaciones = response22['choices'][0]['message']['content']



    prompt7 = f"""
    Eres un reclutador profesional. Por favor, proporciona un análisis detallado. En este análisis, evalúa lo siguiente:

    Identifica las áreas en las que el candidato sobresale y tiene un fuerte desempeño. Esto puede incluir habilidades específicas, experiencia relevante, o logros notables que aportan valor al puesto. Dame en guiones, se breve y consiso

    Se breve y consiso, hazlo en guiones y se especifico

    Por favor, asegúrate de que cada sección esté claramente separada y de que las recomendaciones sean específicas y detalladas.

    No debe a ver subtitulos no les coloques numerales o astericos
    No pongas subtitulos, todo hazlo por guiones y de manera general
    Cada punto que hagas, hazle un salto de linea, osea que no este todo pegado

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
    Cada punto que hagas, hazle un salto de linea, osea que no este todo pegado

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

    Se breve y consiso

    No debe a ver subtitulos no les coloques numerales o astericos, sin asteriscos, quiero por guiones, se claro
    
    No pongas subtitulos, todo hazlo por guiones y de manera general
        Cada punto que hagas, hazle un salto de linea, osea que no este todo pegado

    No me pongas asteriscos o lineas o simbolos a los subtitutlos
    Ejemplo: **Formación Académica:**, eso no quiero quita los asteriscos, sin asteriscos ni otro simbolos
    Solo debe ser Formacion Academica, no le agregues asteriscos
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
    Identifica 5 palabras clave segun el {puesto}
    relevantes para ese rol, que suelen aparecer en descripciones de empleo similares. Estas 
    deben incluir habilidades técnicas o blandas clave para el puesto. 

    Solo utiliza referencias propias del rol de {puesto}. 
     
    NO CURSOS TEC, Se estricto al momento de dar las palabras clave todo en relacion con el {puesto}, evita mencionar cosas relacionadas con "Experiencia en..."
    Las palabras claves son relacionadas con el {puesto}
    Formato de salida:
    - Palabra clave 1: Indica en que parte del CV incluirlo,  y un ejemplo de como incluirlo  debes crearlo tu, no con informacion del CV, logro, el ejemplo debe incluir resultados cuantificables agrega algun valor cuantificable, ya sea tasas %, enteros, si es que tiene, Por ejemplo:
    - Palabra clave 2: Indica en que parte del CV incluirlo,  y un ejemplo de como incluirlo  debes crearlo tu, no con informacion del CV, logro, el ejemplo debe incluir  resultados cuantificables agrega algun valor cuantificable, ya sea tasas %, enteros, si es que tiene Por ejemplo:
    - Palabra clave 3: Indica en que parte del CV incluirlo,  y un ejemplo de como incluirlo  debes crearlo tu, no con informacion del CV, logro, el ejemplo debe incluir  resultados cuantificables agrega algun valor cuantificable, ya sea tasas %, enteros, si es que tiene Por ejemplo:
    - Palabra clave 4: Indica en que parte del CV incluirlo,  y un ejemplo de como incluirlo  debes crearlo tu, no con informacion del CV, logro, el ejemplo debe incluir  resultados cuantificables agrega algun valor cuantificable, ya sea tasas %, enteros,si es que tiene Por ejemplo:
    - Palabra clave5: Indica en que parte del CV incluirlo,  y un ejemplo de como incluirlo  debes crearlo tu ,no con informacion del CV, logro,  el ejemplo debe incluir resultados cuantificables agrega algun valor cuantificable, ya sea tasas %, enteros, si es que tiene Por ejemplo:

    Recuerda la palabra clave damelo normal, sin agregar guiones, segun el formato de salida
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
    No agregues asteriscos
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


    prompt_analysis_cv = f"""
    Eres un reclutador profesional con experiencia en selección de talento junior. Tu tarea es 
    analizar el siguiente documento y otorgar una calificación numérica del 1 al 10, basada 
    exclusivamente en qué tan bien se ajusta el perfil al puesto de {puesto}. 
    Evalúa los siguientes criterios: 
    ● Experiencia relevante para el rol 
    ● Habilidades técnicas alineadas al puesto 
    ● Habilidades blandas adecuadas al entorno 
    ● Formación académica y certificaciones 
    ● Presentación, claridad y estructura del CV 
    ● Conocimiento aplicable al puesto 
    Condición especial: Si el candidato cumple adecuadamente en al menos dos de estos seis 
    criterios, el puntaje mínimo será 5, incluso si no hay coincidencia total con el puesto. 
    Condición adicional: Si el documento no es un currículum o no contiene información 
    personal y profesional de un candidato, responde automáticamente con 0/10. 
    Importante: Este análisis aplica a talento junior. No penalices fuertemente la falta de 
    experiencia laboral formal. Evalúa con enfoque en potencial, habilidades y nivel de 
    alineación. 
    Contenido del documento a evaluar: 
    {contenido} 
    Solo responde con un número en formato Numero. No incluyas ninguna explicación, 
    comentario ni texto adicional. 
    
    {contenido}
    """

    response_analysis_cv = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_analysis_cv}],
        temperature=0.7,
    )

    response_text = response_analysis_cv['choices'][0]['message']['content'].strip()


    prompt_experience = f"""
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. Por favor, extrae la información relacionada con la experiencia laboral. Para cada experiencia laboral, proporciona la siguiente información de manera estructurada en JSON:

    - Puesto: El título o nombre del puesto ocupado.
    - Empresa: El nombre de la empresa en la que el candidato ha trabajado.
    - Duración: El periodo de tiempo en el que trabajó en la empresa (por ejemplo, enero 2020 - diciembre 2022).
    - Descripción: Las responsabilidades y logros alcanzados en el puesto (debe ser una descripción concisa, resaltando los logros).

    Formato JSON:
    {{
        "workExperience": [
            {{
                "role": "Puesto",
                "company": "Empresa",
                "duration": "Periodo",
                "description": "Descripción de responsabilidades y logros"
            }}
        ]
    }}

    Contenido del CV a evaluar:
    {contenido}
    """

    response_experience = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_experience}],
        temperature=0.7,
    )

    # Extrae la experiencia laboral desde la respuesta
    work_experience = response_experience['choices'][0]['message']['content']

    # Asegúrate de que la respuesta esté en formato JSON válido
    work_experience_data = safe_json_load(work_experience)

    # Si no se pudo parsear correctamente, podrías intentar nuevamente o manejar el error
    if work_experience_data is None:
        return await analizar_cv(pdf_url, puesto_postular)

    # Extraer la experiencia laboral del JSON
    work_experience = work_experience_data.get("workExperience", [])

    # Ahora puedes hacer algo con el JSON válido que contiene la experiencia laboral



    prompt_education = f"""
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. Por favor, extrae la información relacionada con la educación. Para cada título educativo, proporciona la siguiente información de manera estructurada en JSON:

    - Grado: El título académico obtenido por el candidato (por ejemplo, Licenciatura en Ingeniería de Sistemas).
    - Institución: El nombre de la institución educativa en la que el candidato obtuvo su título.
    - Año de graduación: El año de graduación o la fecha en la que el candidato completó sus estudios.

    Formato JSON:
    {{
        "education": [
            {{
                "degree": "Título obtenido",
                "institution": "Institución educativa",
                "graduationYear": "Año de graduación"
            }}
        ]
    }}

    Contenido del CV a evaluar:
    {contenido}
    """

    response_education = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_education}],
        temperature=0.7,
    )

    # Extrae la información de educación desde la respuesta
    education_data = response_education['choices'][0]['message']['content']

    # Asegúrate de que la respuesta esté en formato JSON válido
    education_data_json = safe_json_load(education_data)

    # Si no se pudo parsear correctamente, podrías intentar nuevamente o manejar el error
    if education_data_json is None:
        return await analizar_cv(pdf_url, puesto_postular)

    # Extraer la educación del JSON
    education = education_data_json.get("education", [])

    # Ahora puedes hacer algo con el JSON válido que contiene la información de la educación


    prompt_feedback_summary = f"""
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

    response_feedback_summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_feedback_summary}],
        temperature=0.7,
        # max_tokens=150  # Puedes ajustar los tokens si necesitas una respuesta más larga o más corta
    )

    feedback_summary = response_feedback_summary['choices'][0]['message']['content'].strip()

    raw_text = contenido  # Aquí, 'contenido' ya es el texto completo del CV extraído

    prompt_skills = f"""
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
                "Comunicación",
                "Trabajo en equipo"
            ],
            "languages": [
                "Inglés (Avanzado)",
                "Español (Nativo)"
            ]
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """

    response_skills = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_skills}],
        temperature=0.7,
    )
    
    skills = process_skills_response(response_skills['choices'][0]['message']['content'])



    prompt_formatting = f"""
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. 
    Por favor, proporciona un análisis detallado sobre el formato y lenguaje del CV, evaluando lo siguiente:

    1. Claridad del CV: ¿Es fácil de leer y entender? ¿La información está organizada de manera clara?
    2. Profesionalismo: ¿El CV tiene un aspecto profesional? ¿La tipografía y el diseño son adecuados?
    3. Errores gramaticales y ortográficos: ¿Cuántos errores gramaticales y ortográficos hay en el CV?
    4. Uso de verbos de acción: ¿Se utilizan verbos de acción en las descripciones de las experiencias laborales? ¿Son adecuados para resaltar logros?

    Formato de salida: 
    {{
        "formattingAndLanguage": {{
            "clarity": "string_evaluacion_claridad",
            "professionalism": "string_evaluacion_profesionalismo",
            "grammarSpellingErrorsCount": "number_cantidad_errores",
            "actionVerbsUsed": "boolean"
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """

    response_formatting = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_formatting}],
        temperature=0.7,
    )
    formatting = process_formatting_response(response_formatting['choices'][0]['message']['content'])


    prompt_keywords = f"""
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. 
    Por favor, extrae las palabras clave relevantes para el puesto en cuestión y las habilidades generales mencionadas en el CV. 

    Primero, identifica las palabras clave relacionadas con el puesto de {puesto}, estas pueden ser habilidades técnicas, habilidades blandas o certificaciones que son relevantes para el rol. Luego, clasifica las palabras clave en las siguientes categorías:

    1. **Palabras clave encontradas**: Las palabras clave relacionadas con el puesto que aparecen en el CV.
    2. **Palabras clave faltantes**: Las palabras clave que son esenciales para el puesto pero no aparecen en el CV.
    3. **Palabras clave de habilidades generales encontradas**: Las habilidades generales que son valiosas para el rol (por ejemplo: comunicación, trabajo en equipo, etc.).

    Formato de salida: 
    {{
        "keywordAnalysis": {{
            "jobKeywordsFound": ["palabra_clave_1", "palabra_clave_2"],
            "jobKeywordsMissing": ["palabra_clave_faltante_1"],
            "generalSkillsKeywordsFound": ["habilidad_general_1"]
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """

    response_keywords = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": prompt_keywords}],
    temperature=0.7,
    )

    keywords = process_keywords_response(response_keywords['choices'][0]['message']['content'])


    prompt_ats_compliance = f"""
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
            "score": "number_puntaje_ats_0_100",
            "issues": ["problema_ats_1", "problema_ats_2"],
            "recommendations": ["sugerencia_ats_1"]
        }}
    }}

    Contenido del CV a evaluar:
    {contenido}
    """

    response_ats_compliance = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_ats_compliance}],
        temperature=0.7,
    )

    ats_compliance = process_ats_response(response_ats_compliance['choices'][0]['message']['content'])


    prompt_strengths = f"""
    Eres un reclutador profesional. A continuación, se muestra el contenido del CV de un candidato para el puesto de {puesto}. 
    Por favor, identifica las fortalezas clave del candidato, basándote en sus habilidades, experiencias, logros y cualidades que puedan ser relevantes para el puesto.

    Por favor, proporciona las fortalezas de manera clara y concreta, considerando lo siguiente:

    1. **Habilidades clave**: Identifica las habilidades que el candidato domina y que son valiosas para el puesto.
    2. **Experiencia destacada**: Menciona la experiencia laboral relevante que resalta en el CV.
    3. **Logros notables**: Identifica cualquier logro que sea impresionante o demuestre un impacto significativo.
    4. **Cualidades personales**: Si se mencionan cualidades que aportan al puesto, inclúyelas como fortalezas.

    Formato de salida:
    {{
        "strengths": ["fortaleza_identificada_1", "fortaleza_identificada_2"]
    }}

    Contenido del CV a evaluar:
    {contenido}
    """

    response_strengths = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt_strengths}],
        temperature=0.7,
    )




    match = re.search(r'\b([1-9]|10)\b', response_text)
    if match:
        cv_rating = int(match.group(1))
    else:
        cv_rating = 5  


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
                            puesto,
                            formacion_academica,
                            habilidades_tecnicas,
                            certificaciones,
                            cv_rating)

    public_folder = './static/pdf_reports/'
    os.makedirs(public_folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    pdf_filename = f"{candidate_name.replace(' ', '-')}_{now}.pdf"
    pdf_filepath = os.path.join(public_folder, pdf_filename)

    with open(pdf_filepath, 'wb') as f:
        f.write(pdf_output.getvalue())

    pdf_url = f"https://myworkin-cv.onrender.com/static/pdf_reports/{pdf_filename}"


    phone = extract_phone(contenido)
    linkedin = extract_linkedin(contenido)
    address = extract_address(contenido)

    return JSONResponse(content={
        "status": "success", 
        "message": "CV procesado y análisis guardado exitosamente.",
        "analysis_id": generate_analysis_id(candidate_name),
        "extractedData": {
            "cvAnalysisId": generate_analysis_id(candidate_name),
            "userId": generate_user_id(candidate_name),
            "jobPositionApplied": puesto, 
            "cvOriginalFileUrl": original_pdf,
            "analysisDateTime": analysis_datetime,  # Aquí agregamos la fecha y hora
            "processingTimeMs": processing_time_ms,  # Aq
            "extractedData": { 
                "candidateName": candidate_name,
                "contactInfo": {
                    "email": email if email else "No disponible",  # Aquí agregamos el email extraído
                    "phone": phone,
                    "linkedin": linkedin,
                    "address": address
                },
                "professionalSummary": analysis_text,
                "workExperience": work_experience,

                "education": education,
                "skills": skills["skills"],
                "rawText": raw_text,
            },
            "analysisResults": { 
                "pdf_url": pdf_url,
                "overallScore": f"{cv_rating}/10",
                "atsCompliance": ats_compliance["atsCompliance"],
                "strengths": fortalezas,
                "areasForImprovement": errores_comunes, 
                "keywordAnalysis": keywords["keywordAnalysis"],
                "formattingAndLanguage": formatting["formattingAndLanguage"],
                "feedbackSummary": feedback_summary  # Aquí agregamos el feedback summary
            }
        },
    })


@app.get("/backup-static/")
async def backup_static():
    static_folder = "static"
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Añadir archivo al zip con ruta relativa
                arcname = os.path.relpath(file_path, static_folder)
                zip_file.write(file_path, arcname=arcname)

    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=static_backup.zip"})



def process_keywords_response(response):
    # Intentar extraer la respuesta en formato JSON
    keywords_data = safe_json_load(response)

    # Si la respuesta no tiene el formato correcto, crear una estructura predeterminada
    if keywords_data is None or "keywordAnalysis" not in keywords_data:
        keywords_data = {
            "keywordAnalysis": {
                "jobKeywordsFound": [],
                "jobKeywordsMissing": [],
                "generalSkillsKeywordsFound": []
            }
        }

    # Asegurarse de que todas las claves estén presentes
    keywords_data["keywordAnalysis"].setdefault("jobKeywordsFound", [])
    keywords_data["keywordAnalysis"].setdefault("jobKeywordsMissing", [])
    keywords_data["keywordAnalysis"].setdefault("generalSkillsKeywordsFound", [])

    return keywords_data


def extract_score_from_text(text):
    try:
        score = int(text.split(":")[1].strip().split()[0])
        return score
    except Exception as e:
        return 0

def process_ats_response(response):
    # Intentar extraer la respuesta en formato JSON
    ats_data = safe_json_load(response)

    # Si la respuesta no tiene el formato correcto, crear una estructura predeterminada
    if ats_data is None or "atsCompliance" not in ats_data:
        ats_data = {
            "atsCompliance": {
                "score": 0,
                "issues": [],
                "recommendations": []
            }
        }

    # Asegurarse de que todas las claves estén presentes
    ats_data["atsCompliance"].setdefault("score", 0)
    ats_data["atsCompliance"].setdefault("issues", [])
    ats_data["atsCompliance"].setdefault("recommendations", [])

    return ats_data


def process_formatting_response(response):
    # Intentar extraer la respuesta en formato JSON
    formatting_data = safe_json_load(response)

    # Si la respuesta no tiene el formato correcto, crear una estructura predeterminada
    if formatting_data is None or "formattingAndLanguage" not in formatting_data:
        formatting_data = {
            "formattingAndLanguage": {
                "clarity": "No disponible",
                "professionalism": "No disponible",
                "grammarSpellingErrorsCount": 0,
                "actionVerbsUsed": False
            }
        }

    # Asegurarse de que todas las claves estén presentes
    formatting_data["formattingAndLanguage"].setdefault("clarity", "No disponible")
    formatting_data["formattingAndLanguage"].setdefault("professionalism", "No disponible")
    formatting_data["formattingAndLanguage"].setdefault("grammarSpellingErrorsCount", 0)
    formatting_data["formattingAndLanguage"].setdefault("actionVerbsUsed", False)

    return formatting_data

def process_skills_response(response):
    # Intenta extraer la respuesta en formato JSON
    skills_data = safe_json_load(response)

    # Si la respuesta no tiene el formato correcto, ajustarlo
    if skills_data is None or "skills" not in skills_data:
        # Crear un objeto vacío para asegurar la estructura
        skills_data = {
            "skills": {
                "technical": [],
                "soft": [],
                "languages": []
            }
        }

    # Asegurarte de que las secciones estén presentes, aunque sean listas vacías
    skills_data["skills"].setdefault("technical", [])
    skills_data["skills"].setdefault("soft", [])
    skills_data["skills"].setdefault("languages", [])

    return skills_data


def generate_analysis_id(candidate_name):
    # Extrae iniciales del nombre
    initials = ''.join([word[0] for word in candidate_name.split() if word]).upper()

    # Fecha y hora actual
    now = datetime.now().strftime('%Y%m%d%H%M%S')

    # Hash corto basado en nombre y timestamp
    hash_short = hashlib.md5((candidate_name + now).encode()).hexdigest()[:6]

    # ID único
    return f"{initials}-{now}-{hash_short}"

def generate_user_id(candidate_name):
    normalized_name = candidate_name.lower().replace(" ", "")
    hash_short = hashlib.md5(normalized_name.encode()).hexdigest()[:8]
    return f"user_{hash_short}"

def extract_email(text):
    # Expresión regular para identificar un correo electrónico
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Buscar el correo electrónico en el texto
    email_match = re.search(email_pattern, text)
    
    if email_match:
        return email_match.group(0)  # Devuelve el primer email encontrado
    else:
        return None  # Si no se encuentra ningún correo




def extract_phone(text):
    # Expresión regular para buscar un número de teléfono (ejemplo: (555) 555-5555 o 555-555-5555)
    phone_pattern = r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        return phone_match.group(0)  # Devuelve el primer teléfono encontrado
    else:
        return "No disponible"

def extract_linkedin(text):
    # Expresión regular para buscar un enlace de LinkedIn (por ejemplo: https://www.linkedin.com/in/usuario/)
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+'
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        return linkedin_match.group(0)  # Devuelve el primer enlace de LinkedIn encontrado
    else:
        return "No disponible"

def extract_address(text):
    # Expresión regular para buscar una dirección (básica, puede necesitar ajustes dependiendo del formato)
    address_pattern = r'(?:Calle|Av\.|Avenida|Pje\.)\s?[a-zA-Z0-9\s,.-]+'
    address_match = re.search(address_pattern, text)
    if address_match:
        return address_match.group(0)  # Devuelve la primera dirección encontrada
    else:
        return "No disponible"