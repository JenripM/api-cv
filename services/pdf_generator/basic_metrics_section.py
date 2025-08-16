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
    # Asegurarse de que 'pages' sea una cadena
    paginas = str(datos_cv.get('pagination', {}).get('pages', 'Pages not available'))
    comentarioPagination = datos_cv.get('pagination', {}).get('comment', 'Comment not available')
    
    errores = str(datos_cv.get('spelling', {}).get('errors', 'Errors not available'))
    erroresPagination = datos_cv.get('spelling', {}).get('comment', 'Comment not available')
    detalles_errores = datos_cv.get('spelling', {}).get('error_details', [])

    margen_horizontal = 50
    espacio_entre_divs = 20
    alto_div = 160

    sombra_expand = 8
    sombra_offset_x = 2
    sombra_offset_y = -2
    sombra_alpha = 0.12

    ancho_disponible = ancho - 2 * margen_horizontal - espacio_entre_divs
    ancho_div = ancho_disponible / 2

    x_div1 = margen_horizontal
    x_div2 = margen_horizontal + ancho_div + espacio_entre_divs
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

    # Justificación del texto del comentarioPagination
    c.setFillColor(black)
    c.setFont("Poppins-Regular", 9)
    texto_1 = comentarioPagination

    palabras = texto_1.split()
    lineas = []
    linea_actual = ""
    max_ancho = ancho_div - 40

    for palabra in palabras:
        prueba_linea = linea_actual + (" " if linea_actual else "") + palabra
        if c.stringWidth(prueba_linea, "Helvetica", 10) <= max_ancho:
            linea_actual = prueba_linea
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)

    y_texto = y_div + alto_div - 70
    for linea in lineas:
        ancho_linea = c.stringWidth(linea, "Helvetica", 10)
        x_texto = x_div1 + (ancho_div - ancho_linea) / 2
        c.drawString(x_texto, y_texto, linea)
        y_texto -= 14

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

    # Justificación del texto de erroresPagination
    c.setFillColor(black)
    c.setFont("Poppins-Regular", 9)
    texto_2 = erroresPagination

    palabras = texto_2.split()
    lineas = []
    linea_actual = ""
    max_ancho = ancho_div - 40

    for palabra in palabras:
        prueba_linea = linea_actual + (" " if linea_actual else "") + palabra
        if c.stringWidth(prueba_linea, "Helvetica", 10) <= max_ancho:
            linea_actual = prueba_linea
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)

    y_texto = y_div + alto_div - 70
    for linea in lineas:
        ancho_linea = c.stringWidth(linea, "Helvetica", 10)
        x_texto = x_div2 + (ancho_div - ancho_linea) / 2
        c.drawString(x_texto, y_texto, linea)
        y_texto -= 14

    # Mostrar los detalles de los errores con justificación
    estilo_errores = ParagraphStyle(
        name="ErroresJustificados",
        fontName="Poppins-Regular",
        fontSize=8,
        leading=10,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )

    # Crear un único párrafo con los detalles de los errores separados por comas
    if detalles_errores is not None:
        errores_completos = ", ".join([f"{error['original']} → {error['suggestion']}" for error in detalles_errores])
    else:
        errores_completos = "No errors found."    
    par_errores_completos = Paragraph(errores_completos, estilo_errores)

    # Obtener el tamaño del párrafo
    w_error, h_error = par_errores_completos.wrap(ancho_div - 40, alto_div)

    # Dibujar el párrafo completo en la página
    par_errores_completos.drawOn(c, x_div2 + 20, y_texto - h_error)

    # Actualizar la posición Y para los siguientes elementos
    y_texto -= h_error + 5  # Espacio entre los errores

    return alto_div
