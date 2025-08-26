from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from .pdf_utils import dibujar_velocimetro, wrap_text

# Definir colores específicos
white = Color(1, 1, 1)
black = Color(0, 0, 0)
grey = Color(0.5, 0.5, 0.5)
red = Color(1, 0, 0)
orange = Color(1, 0.5, 0)
green = HexColor('#008000')

def seccion_2(c, ancho, alto, y_inicio, datos_cv):
    """2. Sección de análisis principal con velocímetro"""
    
    # Actualizar claves según el nuevo formato
    analisis = datos_cv.get('main_analysis', {}).get('ai_feedback', 'Analysis not available')
    porcentaje = datos_cv.get('main_analysis', {}).get('score', 0)
    nombre = datos_cv.get('metadata', {}).get('candidate_name', 'name not available')
    puesto_postular = datos_cv.get('puesto_postular', 'puesto_postular no disponible')

    margen_horizontal = 30
    padding_interno = 20
    sombra_offset = 5

    # Cargar imagen
    imagen_fondo = ImageReader('./public/img/fondo.png')

    # Calcular altura dinámica basada en el contenido
    alto_minimo = 385  # altura mínima de la card
    alto_degradado = 250   # altura del fondo degradado
    
    # Calcular altura necesaria para el análisis
    estilo_analisis = ParagraphStyle(
        name="AnalisisJustificado",
        fontName="Poppins-Regular",
        fontSize=10,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceBefore=10,
        spaceAfter=5,
    )
    
    par_analisis = Paragraph(analisis, estilo_analisis)
    ancho_disponible = ancho - 2 * margen_horizontal - 2 * padding_interno
    w_analisis, h_analisis = par_analisis.wrap(ancho_disponible, 1000)  # altura máxima para calcular
    
    # Calcular altura total necesaria - RESPONSIVE
    altura_elementos_fijos = 300  # espacio para nombre, puesto, velocímetro, estado y separación
    altura_analisis_necesaria = h_analisis + 60  # altura del análisis + padding extra
    alto_rectangulo = max(alto_minimo, altura_elementos_fijos + altura_analisis_necesaria)
    
    # Ajustar altura del degradado si es necesario
    alto_degradado = max(alto_degradado, alto_rectangulo - 100)

    # Dibujar imagen de fondo con las dimensiones deseadas

    c.drawImage(imagen_fondo, 0, y_inicio - alto_degradado, width=ancho, height=alto_degradado)

    # 2. Dimensiones y posición del div con sombra y rectángulo blanco
    x_div = margen_horizontal + padding_interno
    y_div = y_inicio - alto_rectangulo + 20 + padding_interno
    ancho_div = ancho - 2 * margen_horizontal - 2 * padding_interno
    alto_div = alto_rectangulo - 20 - 2 * padding_interno

    # 3. Sombra (ligeramente desplazada)
    c.setFillColorRGB(0, 0, 0, alpha=0.15)
    c.roundRect(x_div + sombra_offset, y_div - sombra_offset,
                ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # 4. Rectángulo blanco redondeado (div principal)
    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # 5. Texto principal centrado dentro del rectángulo
    c.setFillColor(black)
    c.setFont("Poppins-Bold", 16)
    texto_principal = nombre
    texto_ancho = c.stringWidth(texto_principal, "Poppins-Regular", 16)
    text_x = x_div + (ancho_div - texto_ancho) / 2
    text_y = y_div + alto_div - 40
    c.drawString(text_x, text_y, texto_principal)

    # Texto secundario (puesto a postular ajustado)
    c.setFillColor(grey)
    c.setFont("Poppins-Regular", 10)

    # Usamos wrap_text para ajustar el puesto a postular en una línea o dividirlo
    lineas_secundarias = wrap_text(puesto_postular, ancho_div - 2 * padding_interno, c, "Poppins-Regular", 10)
    line_height = 14
    y_texto_secundario = text_y - 15

    # Dibujar las líneas de texto secundario ajustadas
    for i, linea in enumerate(lineas_secundarias):
        ancho_linea = c.stringWidth(linea, "Poppins-Regular", 10)
        x_linea = x_div + (ancho_div - ancho_linea) / 2
        y_linea = y_texto_secundario - i * line_height
        c.drawString(x_linea, y_linea, linea)

    # 6. Velocímetro dentro del div blanco
    centro_x = x_div + ancho_div / 2
    espacio_antes_velocimetro = 5
    centro_y = y_div + alto_div / 2 - espacio_antes_velocimetro
    radio = 80
    valor = porcentaje / 10  # Divide el porcentaje entre 10 para obtener el valor adecuado
    

    # Asumo que tienes la función dibujar_velocimetro definida en otro lado
    dibujar_velocimetro(c, centro_x, centro_y, radio, valor)

    espacio_despues_velocimetro = 30

    # Determinar palabra clave y color según valor
    if valor >= 7:
        palabra_estado = "EXCELENTE!"
        color_estado = green
    elif valor >= 5:
        palabra_estado = "BUENO!"
        color_estado = HexColor('#4CAF50')  # Verde claro
    elif valor >= 3:
        palabra_estado = "REGULAR!"
        color_estado = orange
    else:
        palabra_estado = "PESIMO!"
        color_estado = red

    texto_base = "Tu CV está "
    fuente = "Poppins-Bold"
    tamano_fuente = 14

    ancho_base = c.stringWidth(texto_base, fuente, tamano_fuente)
    ancho_estado = c.stringWidth(palabra_estado, fuente, tamano_fuente)
    ancho_total = ancho_base + ancho_estado

    text_x = x_div + (ancho_div - ancho_total) / 2
    text_y = centro_y - radio + espacio_despues_velocimetro

    c.setFont(fuente, tamano_fuente)
    c.setFillColor(black)
    c.drawString(text_x, text_y, texto_base)

    c.setFillColor(color_estado)
    c.drawString(text_x + ancho_base, text_y, palabra_estado)

    # 7. Análisis con altura dinámica - RESPONSIVE
    c.setFont("Poppins-Regular", 10)
    c.setFillColor(grey)

    # Calcular posición del análisis - RESPONSIVE: siempre debajo del texto "Tu CV está..."
    separacion_analisis = 40  # Separación fija entre el texto de estado y el análisis
    y_analisis_pos = text_y - separacion_analisis  # Posición relativa al texto de estado
    
    # Verificar que el análisis no se salga de la card
    if y_analisis_pos - h_analisis < y_div + padding_interno:
        # Si se sale, ajustar la posición para que quepa
        y_analisis_pos = y_div + padding_interno + h_analisis
    
    # Asegurar que el análisis se dibuje dentro de los límites de la card
    ancho_analisis_disponible = ancho_div - 2 * padding_interno
    x_analisis = x_div + padding_interno
    
    # Recrear el párrafo con el ancho correcto
    par_analisis_final = Paragraph(analisis, estilo_analisis)
    w_final, h_final = par_analisis_final.wrap(ancho_analisis_disponible, 1000)
    

    par_analisis_final.drawOn(c, x_analisis, y_analisis_pos - h_final)  # Ajustar posición final

    x_texto = margen_horizontal
    y_texto = y_inicio - 30
    c.setFont("Poppins-Regular", 12)
    c.setFillColor(black)
    altura_ocupada = alto_rectangulo + 20  # altura total usada por la sección
    
    return altura_ocupada
