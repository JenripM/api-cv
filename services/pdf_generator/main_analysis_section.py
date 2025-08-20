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
    analisis = datos_cv.get('main_analysis', {}).get('summary', 'Analysis not available')
    porcentaje = datos_cv.get('main_analysis', {}).get('score', 0)
    nombre = datos_cv.get('metadata', {}).get('candidate_name', 'name not available')
    puesto_postular = datos_cv.get('puesto_postular', 'puesto_postular no disponible')

    alto_degradado = 250   # altura menor para el fondo degradado
    alto_rectangulo = 385 # altura mayor para el rectángulo blanco

    margen_horizontal = 30
    padding_interno = 20
    sombra_offset = 5

    # Cargar imagen
    imagen_fondo = ImageReader('./public/img/fondo.png')

    # Dibujar imagen de fondo con las dimensiones deseadas
    c.drawImage(imagen_fondo, 0, y_inicio - alto_degradado, width=ancho, height=alto_degradado)

    # 2. Dimensiones y posición del div con sombra y rectángulo blanco (mayor altura)
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
    if valor < 4:
        palabra_estado = "desaprobado!"
        color_estado = red
    elif valor < 7:
        palabra_estado = "observado!"
        color_estado = orange
    else:
        palabra_estado = "aprobado!"
        color_estado = green

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

    # 7. Reemplazar texto adicional con el análisis
    c.setFont("Poppins-Regular", 10)
    c.setFillColor(grey)

    # Mantener la posición del análisis, pero justificar el texto
    estilo_analisis = ParagraphStyle(
        name="AnalisisJustificado",
        fontName="Poppins-Regular",
        fontSize=10,
        leading=12,
        alignment=TA_JUSTIFY,  # Justificar el texto
        spaceBefore=10,  # Espacio antes del análisis
        spaceAfter=5,
    )

    # Crear el párrafo con el análisis justificado
    par_analisis = Paragraph(analisis, estilo_analisis)
    w_analisis, h_analisis = par_analisis.wrap(ancho_div - 2 * padding_interno, alto_div)

    # Ajustar la posición para dibujarlo justo debajo del velocímetro
    # Considera el espacio ocupado por los elementos anteriores y ajusta la posición
    y_analisis_pos = text_y - 10 - espacio_despues_velocimetro - h_analisis  # Esto asegura que se ubique abajo

    par_analisis.drawOn(c, x_div + padding_interno, y_analisis_pos)

    x_texto = margen_horizontal
    y_texto = y_inicio - 30  # A
    c.setFont("Poppins-Regular", 12)
    c.setFillColor(black)
    altura_ocupada = 345 # altura total usada por la sección
    return altura_ocupada
