from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

# Definir colores específicos
white = Color(1, 1, 1)
black = Color(0, 0, 0)
grey = Color(0.5, 0.5, 0.5)
green = Color(0, 1, 0)
red = Color(1, 0, 0)
blue = Color(0, 0, 1)

def seccion_3(c, ancho, alto, y_inicio, datos_cv):
    """3. Sección de métricas básicas (páginas y ortografía)"""
    # Actualizar claves según el nuevo formato
    paginas = str(datos_cv.get('document_size_analysis', {}).get('total_pages', 'Pages not available'))
    comentarioPagination = datos_cv.get('document_size_analysis', {}).get('ai_feedback', 'Comment not available')
    
    errores = str(datos_cv.get('spelling_analysis', {}).get('spelling_errors', 'Errors not available'))
    erroresPagination = datos_cv.get('spelling_analysis', {}).get('ai_feedback', 'Comment not available')
    detalles_errores = datos_cv.get('spelling_analysis', {}).get('errors_found', [])

    margen_horizontal = 50
    espacio_entre_divs = 20
    # Altura mínima de las cards
    altura_minima_div = 160

    sombra_expand = 8
    sombra_offset_x = 2
    sombra_offset_y = -2
    sombra_alpha = 0.12

    ancho_disponible = ancho - 2 * margen_horizontal - espacio_entre_divs
    ancho_div = ancho_disponible / 2

    x_div1 = margen_horizontal
    x_div2 = margen_horizontal + ancho_div + espacio_entre_divs
    # Preparar estilos de párrafo con ajuste automático dentro del ancho disponible
    estilo_parrafo = ParagraphStyle(
        name="MetricParagraph",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
        textColor=black,
    )
    # Permitir quiebres por carácter para prevenir overflow con palabras muy largas
    # (ReportLab respeta 'wordWrap' en estilos de Paragraph)
    setattr(estilo_parrafo, 'wordWrap', 'CJK')

    # Crear párrafos y calcular alturas requeridas
    ancho_texto_div = ancho_div - 40
    parrafo_tamano = Paragraph(comentarioPagination, estilo_parrafo)
    _, alto_parrafo_tamano = parrafo_tamano.wrap(ancho_texto_div, alto)

    parrafo_errores = Paragraph(erroresPagination, estilo_parrafo)
    _, alto_parrafo_errores = parrafo_errores.wrap(ancho_texto_div, alto)

    # Cálculo dinámico de altura de cada card
    separacion_superior_contenido = 70  # espacio desde el borde superior de la card hasta el inicio del texto
    margen_inferior_contenido = 20

    alto_div_izq = max(altura_minima_div, separacion_superior_contenido + alto_parrafo_tamano + margen_inferior_contenido)
    alto_div_der = max(altura_minima_div, separacion_superior_contenido + alto_parrafo_errores + margen_inferior_contenido)

    alto_div = max(alto_div_izq, alto_div_der)

    y_div = y_inicio - alto_div

    # Sombra primer div
    c.setFillColorRGB(0, 0, 0, alpha=sombra_alpha)
    c.roundRect(
        x_div1 - sombra_expand / 2 + sombra_offset_x,
        y_div - sombra_expand / 2 + sombra_offset_y,
        ancho_div + sombra_expand,
        alto_div + sombra_expand,
        radius=15 + sombra_expand / 2,
        fill=1, stroke=0
    )

    # Sombra segundo div
    c.roundRect(
        x_div2 - sombra_expand / 2 + sombra_offset_x,
        y_div - sombra_expand / 2 + sombra_offset_y,
        ancho_div + sombra_expand,
        alto_div + sombra_expand,
        radius=15 + sombra_expand / 2,
        fill=1, stroke=0
    )

    # Div blancos sin borde encima
    c.setFillColor(white)
    c.roundRect(x_div1, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)
    c.roundRect(x_div2, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # Títulos superiores en gris claro
    c.setFillColor(grey)
    c.setFont("Poppins-SemiBold", 9)
    c.drawString(x_div1 + 20, y_div + alto_div - 15, "Tamaño")
    c.drawString(x_div2 + 20, y_div + alto_div - 15, "Ortografía")

    # Primer div: "paginas Pagina" con colores
    c.setFillColor(black)
    c.setFont("Poppins-Bold", 16)
    ancho_texto_1 = c.stringWidth(paginas, "Poppins-Bold", 16)
    ancho_texto_2 = c.stringWidth("  Página", "Poppins-Bold", 16)

    total_ancho = ancho_texto_1 + ancho_texto_2
    inicio_texto = x_div1 + (ancho_div - total_ancho) / 2

    c.drawString(inicio_texto, y_div + alto_div - 40, paginas)
    c.setFillColor(green)
    c.drawString(inicio_texto + ancho_texto_1, y_div + alto_div - 40, " Página")

    # Texto del comentario de tamaño (usa Paragraph para ajuste en el contenedor)
    c.setFillColor(black)
    c.setFont("Poppins-Regular", 9)
    x_texto_izq = x_div1 + 20
    y_top_izq = y_div + alto_div - separacion_superior_contenido
    parrafo_tamano.drawOn(c, x_texto_izq, y_top_izq - alto_parrafo_tamano)

    # Segundo div: "Errores" en rojo y texto
    c.setFillColor(black)
    c.setFont("Poppins-Bold", 16)
    ancho_texto_1 = c.stringWidth(errores, "Poppins-Bold", 16)
    ancho_texto_2 = c.stringWidth(" Errores", "Poppins-Bold", 16)

    total_ancho = ancho_texto_1 + ancho_texto_2
    inicio_texto = x_div2 + (ancho_div - total_ancho) / 2

    c.drawString(inicio_texto, y_div + alto_div - 40, errores)
    c.setFillColor(red)
    c.drawString(inicio_texto + ancho_texto_1, y_div + alto_div - 40, " Errores")

    # Texto del comentario de errores (usa Paragraph para ajuste en el contenedor)
    c.setFillColor(black)
    c.setFont("Poppins-Regular", 9)
    x_texto_der = x_div2 + 20
    y_top_der = y_div + alto_div - separacion_superior_contenido
    parrafo_errores.drawOn(c, x_texto_der, y_top_der - alto_parrafo_errores)

    
    return alto_div
