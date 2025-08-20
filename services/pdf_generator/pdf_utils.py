import math
import numpy as np
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from math import cos, sin, pi
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import mm
import requests

# Definir colores específicos
white = Color(1, 1, 1)
black = Color(0, 0, 0)
grey = Color(0.5, 0.5, 0.5)
green = HexColor('#0c846c')
red = Color(1, 0, 0)
orange = Color(1, 0.5, 0)
yellow = Color(1, 1, 0)

# Registrar fuentes
pdfmetrics.registerFont(TTFont('Poppins-Regular', './fonts/Poppins-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Poppins-Bold', './fonts/Poppins-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Poppins-SemiBold', './fonts/Poppins-SemiBold.ttf'))
pdfmetrics.registerFont(TTFont('Poppins-Italic', './fonts/Poppins-Italic.ttf'))

def dibujar_velocimetro(c, centro_x, centro_y, radio, valor):
    """
    Dibuja un velocímetro semicírculo (tipo 7.8/10) en un canvas de ReportLab.

    :param c: canvas de ReportLab
    :param centro_x: coordenada x del centro del velocímetro
    :param centro_y: coordenada y del centro del velocímetro
    :param radio: radio del semicírculo
    :param valor: valor entre 0 y 10
    """
    # Aseguramos que el valor esté en rango
    valor = max(0, min(10, valor))

    # Determinar color según valor
    if valor <= 3:
        color_arco = red
    elif valor < 7:
        color_arco = orange
    else:
        color_arco = green

    # Parámetros del ángulo
    angulo_total = 180  # grados
    angulo_inicio = 180  # desde la izquierda
    angulo_valor = angulo_total * (valor / 10)

    # Estilo de línea
    c.setLineWidth(15)

    # 1. Arco de fondo gris claro
    c.setStrokeColorRGB(0.9, 0.9, 0.95)
    c.arc(centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio,
          startAng=angulo_inicio, extent=-angulo_total)

    # 2. Arco coloreado según valor
    c.setStrokeColor(color_arco)
    c.arc(centro_x - radio, centro_y - radio, centro_x + radio, centro_y + radio,
          startAng=angulo_inicio, extent=-angulo_valor)

    # 3. Círculo al final del arco
    angulo_final = angulo_inicio - angulo_valor
    angulo_final_rad = np.radians(angulo_final)
    punto_x = centro_x + radio * cos(angulo_final_rad)
    punto_y = centro_y + radio * sin(angulo_final_rad)
    c.setFillColor(color_arco)
    c.circle(punto_x, punto_y, 8, fill=1)

    # 4. Texto central del valor
    c.setFont("Poppins-Bold", 18)
    c.setFillColor(black)
    c.drawCentredString(centro_x, centro_y + 10, f"{valor:.1f}/10")

    # 5. Texto secundario
    c.setFont("Poppins-Regular", 10)
    c.setFillColor(grey)
    c.drawCentredString(centro_x, centro_y - 5, "Puntaje General")


def wrap_text(text, max_width, canvas, font_name, font_size):
    """Divide un texto en líneas para que no exceda max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def descargar_imagen(url: str, ruta_local: str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(ruta_local, "wb") as f:
            f.write(response.content)
        # print("Imagen descargada correctamente.")
    else:
        print(f"Error al descargar la imagen: {response.status_code}")
