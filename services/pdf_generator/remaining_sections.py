from reportlab.lib.colors import Color, HexColor

from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.utils import ImageReader
from .pdf_utils import wrap_text
from .table_component import create_evaluation_table


# Definir colores específicos
white = Color(1, 1, 1)
black = Color(0, 0, 0)
grey = Color(0.5, 0.5, 0.5)
green = HexColor('#14b48b')
red = Color(1, 0, 0)
blue = Color(0, 0, 1)
lightgrey = Color(0.9, 0.9, 0.9)
whitesmoke = Color(0.96, 0.96, 0.96)

def seccion_4(c, ancho, alto, y_inicio, datos_cv):
    """4. Sección de nombre de archivo"""
    # Actualizar claves según el nuevo formato
    archivo = datos_cv.get('filename_analysis', {}).get('filename', 'File not available')
    comentario = datos_cv.get('filename_analysis', {}).get('ai_feedback', 'Comment not available')

    margen_horizontal = 50
    margen_interno = 15
    alto_div = 130

    sombra_expand = 8
    sombra_offset_x = 2
    sombra_offset_y = -2
    sombra_alpha = 0.12

    ancho_div = ancho - 2 * margen_horizontal
    x_div = margen_horizontal
    y_div = y_inicio - alto_div

    # Sombra
    c.setFillColorRGB(0, 0, 0, alpha=sombra_alpha)
    c.roundRect(
        x_div - sombra_expand / 2 + sombra_offset_x,
        y_div - sombra_expand / 2 + sombra_offset_y,
        ancho_div + sombra_expand,
        alto_div + sombra_expand,
        radius=15 + sombra_expand / 2,
        fill=1, stroke=0
    )

    # Div blanco principal
    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # Título "Nombre"
    c.setFillColor(grey)
    c.setFont("Poppins-SemiBold", 9)
    x_nombre = x_div + margen_interno
    y_nombre = y_div + alto_div - 20
    c.drawString(x_nombre, y_nombre, "Nombre")

    # Nombre de archivo
    c.setFillColor(HexColor("#007bb6"))
    c.setFont("Poppins-Bold", 14)
    x_titulo = x_div + margen_interno
    y_titulo = y_nombre - 25
    c.drawString(x_titulo, y_titulo, archivo)

    # Comentario justificado
    estilo_coment = ParagraphStyle(
        name="ComentarioJustificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )
    ancho_com = ancho_div - 2 * margen_interno
    x_com = x_div + margen_interno

    par_com = Paragraph(comentario, estilo_coment)
    w_com, h_com = par_com.wrapOn(c, ancho_com, alto_div)
    par_com.drawOn(c, x_com, y_titulo - h_com - 5)

    return alto_div

def seccion_5(c, ancho, alto, y_inicio, datos_cv):
    """5. Sección de elementos indispensables"""
    # Actualizar claves según el nuevo formato
    observacion = datos_cv.get('essential_elements', {}).get('ai_feedback', 'general_comment not available')
    margen_horizontal = 50
    ancho_div = ancho - 2 * margen_horizontal
    x_div = margen_horizontal
    
    # Calcular altura dinámicamente
    evaluacion = datos_cv.get('essential_elements', {}).get('evaluation', [])
    
    # Altura base para título y cabecera - más responsive con mejor padding
    altura_base = 45  # Aumentado de 30 a 45pt para más padding superior
    
    # Altura para las filas de evaluación - más compacto
    altura_tabla = len(evaluacion) * 16  # Reducido de 18 a 16pt por fila
    
    # Calcular altura para la observación
    estilo_obs = ParagraphStyle(
        name="Justificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceAfter=0,
        spaceBefore=0,
    )
    
    x_obs = x_div + 290
    ancho_obs = ancho_div - (x_obs - x_div) - 15
    par_obs = Paragraph(observacion, estilo_obs)
    w_obs, h_obs = par_obs.wrap(ancho_obs, 1000)  # Altura máxima para calcular
    
    # Altura total del div - con padding inferior responsive
    padding_inferior = max(15, h_obs * 0.1)  # 15pt mínimo o 10% de la altura de la observación
    alto_div = max(100, altura_base + altura_tabla + h_obs + padding_inferior)
    
    y_div = y_inicio - alto_div

    sombra_expand = 6
    sombra_offset_x = 2
    sombra_offset_y = -2
    sombra_alpha = 0.12

    # Dibujar sombra
    c.setFillColorRGB(0, 0, 0, alpha=sombra_alpha)
    c.roundRect(
        x_div - sombra_expand / 2 + sombra_offset_x,
        y_div - sombra_expand / 2 + sombra_offset_y,
        ancho_div + sombra_expand,
        alto_div + sombra_expand,
        radius=12 + sombra_expand / 2,
        fill=1, stroke=0
    )

    # Div blanco principal
    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div, radius=12, fill=1, stroke=0)

    # Título "Indispensable" - con más padding superior
    c.setFillColor(grey)
    c.setFont("Poppins-SemiBold", 9)
    c.drawString(x_div + 10, y_div + alto_div - 20, "Indispensable")

    # Posición inicial de la tabla - ajustado para nueva altura base
    y_tabla_inicio = y_div + alto_div - 40

    # Cabecera de la tabla
    c.setFont("Poppins-SemiBold", 7)
    columnas = [x_div + 10, x_div + 100, x_div + 160, x_div + 220]
    c.setFillColor(black)
    c.drawString(columnas[0], y_tabla_inicio, "Elemento")
    c.drawString(columnas[1], y_tabla_inicio, "¿Existe?")
    c.drawString(columnas[2], y_tabla_inicio, "¿Bien")
    c.drawString(columnas[2], y_tabla_inicio - 12, "posicionado?")
    c.drawString(columnas[3], y_tabla_inicio, "¿Fácil de")
    c.drawString(columnas[3], y_tabla_inicio - 12, "distinguir?")

    # Línea bajo la cabecera
    c.setStrokeColor(HexColor("#B0B0B0"))
    c.setLineWidth(0.7)
    c.line(columnas[0], y_tabla_inicio - 18, columnas[3] + 30, y_tabla_inicio - 18)

    # Filas de datos
    y_filas = [y_tabla_inicio - 28 - 16 * i for i in range(len(evaluacion))]

    c.setFont("Helvetica", 8)
    check = "✔"
    x_check_1 = columnas[1] + 5
    x_check_2 = columnas[2] + 5
    x_check_3 = columnas[3] + 5

    for i, item in enumerate(evaluacion):
        y = y_filas[i]
        # Elemento
        c.setFillColor(black)
        c.drawString(columnas[0], y, item["element"])

        # ¿Existe?
        if item.get("exists", False):
            c.setFillColor(green)
            c.drawString(x_check_1, y, check)
        else:
            c.setFillColor(red)
            c.drawString(x_check_1, y, "X")

        # ¿Bien posicionado?
        if item.get("well_positioned", False):
            c.setFillColor(green)
            c.drawString(x_check_2, y, check)
        else:
            c.setFillColor(red)
            c.drawString(x_check_2, y, "X")

        # ¿Fácil de distinguir?
        if item.get("easily_distinguishable", False):
            c.setFillColor(green)
            c.drawString(x_check_3, y, check)
        else:
            c.setFillColor(red)
            c.drawString(x_check_3, y, "X")

        # Línea separadora
        c.setStrokeColor(HexColor("#B0B0B0"))
        c.setLineWidth(0.5)
        c.line(columnas[0], y - 4, columnas[3] + 30, y - 4)

    # Título y Observación justificada - con mejor padding inferior
    x_obs = x_div + 290
    y_obs_title = y_div + alto_div - 15  # Aumentado de 8 a 15pt para más padding superior
    ancho_obs = ancho_div - (x_obs - x_div) - 15

    c.setFont("Poppins-Bold", 9)
    c.setFillColor(red)
    c.drawString(x_obs, y_obs_title, "Observación:")

    par_obs.drawOn(c, x_obs, y_obs_title - h_obs - 8)  # Aumentado de 4 a 8pt para más espacio

    return alto_div



def seccion_6(c, ancho, alto, y_inicio, datos_cv):
    """6. Sección de palabras clave y sugerencias de keywords"""
    # Actualizar claves según el nuevo formato
    keywords_data = datos_cv.get('keywords_analysis', {})
    found_keywords = keywords_data.get('found_keywords', [])
    missing_keywords = keywords_data.get('missing_keywords', [])
    keywords_suggestion = keywords_data.get('ai_feedback', 'No hay sugerencias de keywords disponibles')
    
    # Solo mostrar keywords encontradas en la card de palabras clave
    all_keywords = []
    for keyword in found_keywords:
        all_keywords.append({"word": keyword, "found": True})

    margen_horizontal = 50
    espacio_entre_divs = 20

    sombra_expand = 8
    sombra_offset_x = 2
    sombra_offset_y = -2
    sombra_alpha = 0.12

    ancho_disponible = ancho - 2 * margen_horizontal - espacio_entre_divs
    ancho_div = ancho_disponible / 2

    x_div1 = margen_horizontal
    x_div2 = margen_horizontal + ancho_div + espacio_entre_divs
    
    # Calcular altura dinámicamente para cada card
    
    # Card 1: Palabras Clave
    altura_card1 = calcular_altura_keywords(c, all_keywords, ancho_div)
    
    # Card 2: Sugerencias
    altura_card2 = calcular_altura_sugerencias(c, keywords_suggestion, missing_keywords, ancho_div)
    
    # Usar la altura máxima de ambas cards
    alto_div = max(180, max(altura_card1, altura_card2))
    
    y_div = y_inicio - alto_div

    # Dibujar sombras
    c.setFillColorRGB(0, 0, 0, alpha=sombra_alpha)
    for x_div in (x_div1, x_div2):
        c.roundRect(
            x_div - sombra_expand/2 + sombra_offset_x,
            y_div - sombra_expand/2 + sombra_offset_y,
            ancho_div + sombra_expand,
            alto_div + sombra_expand,
            radius=15 + sombra_expand/2,
            fill=1, stroke=0
        )

    # Dibujar divs blancos
    c.setFillColor(white)
    c.roundRect(x_div1, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)
    c.roundRect(x_div2, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # Primer div: Palabras Clave
    c.setFillColor(grey)
    c.setFont("Poppins-Bold", 10)
    c.drawString(x_div1 + 15, y_div + alto_div - 25, "Palabras Clave")

    # Configuración de burbujas
    c.setFont("Poppins-Bold", 9)
    espacio_x = 15
    espacio_y = 8
    radio_burbuja = 14
    color_burbuja = HexColor("#007bb6")
    color_texto = white

    x_actual = x_div1 + 15
    y_actual = y_div + alto_div - 50

    for keyword_data in all_keywords:
        palabra = keyword_data["word"]
        
        ancho_palabra = c.stringWidth(palabra, "Poppins-Bold", 9)
        ancho_burbuja = ancho_palabra + 16
        
        if x_actual + ancho_burbuja > x_div1 + ancho_div - 15:
            x_actual = x_div1 + 15
            y_actual -= radio_burbuja * 2 + espacio_y
        
        c.setFillColor(color_burbuja)
        c.roundRect(x_actual, y_actual - radio_burbuja, ancho_burbuja, radio_burbuja*2, radius=radio_burbuja, fill=1, stroke=0)
        c.setFillColor(color_texto)
        c.drawString(x_actual + 8, y_actual - radio_burbuja/2 + 3, palabra)
        x_actual += ancho_burbuja + espacio_x

    # Segundo div: Sugerencias de Keywords
    c.setFillColor(grey)
    c.setFont("Poppins-Bold", 10)
    c.drawString(x_div2 + 15, y_div + alto_div - 25, "Sugerencias de Keywords")

    # Contenido de la sugerencia principal
    estilo_sug = ParagraphStyle(
        name="SugerenciaKeywords",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )

    ancho_sug = ancho_div - 30
    x_sug = x_div2 + 15
    y_sug = y_div + alto_div - 25 - 18

    # Dibujar la sugerencia principal
    par_sug = Paragraph(keywords_suggestion, estilo_sug)
    w_sug, h_sug = par_sug.wrap(ancho_sug, alto_div)
    par_sug.drawOn(c, x_sug, y_sug - h_sug)

    # Dibujar keywords faltantes como badges grises pequeños
    if missing_keywords:
        # Subtítulo para keywords faltantes
        y_faltantes = y_sug - h_sug - 25
        c.setFillColor(HexColor("#666666"))
        c.setFont("Poppins-Bold", 8)
        c.drawString(x_sug, y_faltantes, "Keywords faltantes:")

        # Configuración de badges pequeños
        c.setFont("Poppins-Bold", 7)
        espacio_x_peq = 8
        espacio_y_peq = 6
        radio_burbuja_peq = 8
        color_burbuja_faltante = HexColor("#9E9E9E")
        color_texto_peq = white

        x_actual_peq = x_sug
        y_actual_peq = y_faltantes - 15

        for keyword in missing_keywords:
            ancho_palabra_peq = c.stringWidth(keyword, "Poppins-Bold", 7)
            ancho_burbuja_peq = ancho_palabra_peq + 12
            
            if x_actual_peq + ancho_burbuja_peq > x_div2 + ancho_div - 15:
                x_actual_peq = x_sug
                y_actual_peq -= radio_burbuja_peq * 2 + espacio_y_peq
            
            c.setFillColor(color_burbuja_faltante)
            c.roundRect(x_actual_peq, y_actual_peq - radio_burbuja_peq, ancho_burbuja_peq, radio_burbuja_peq*2, radius=radio_burbuja_peq, fill=1, stroke=0)
            c.setFillColor(color_texto_peq)
            c.drawString(x_actual_peq + 6, y_actual_peq - radio_burbuja_peq/2 + 2, keyword)
            x_actual_peq += ancho_burbuja_peq + espacio_x_peq

    return alto_div

def calcular_altura_keywords(c, all_keywords, ancho_div):
    """Calcula la altura necesaria para mostrar las keywords"""
    if not all_keywords:
        return 80  # Altura mínima
    
    # Configuración de burbujas
    espacio_x = 15
    espacio_y = 8
    radio_burbuja = 14
    
    x_actual = 15
    y_actual = 25  # Altura del título
    filas = 1
    
    for keyword_data in all_keywords:
        palabra = keyword_data["word"]
        ancho_palabra = c.stringWidth(palabra, "Poppins-Bold", 9)
        ancho_burbuja = ancho_palabra + 16
        
        if x_actual + ancho_burbuja > ancho_div - 15:
            x_actual = 15
            y_actual -= radio_burbuja * 2 + espacio_y
            filas += 1
        
        x_actual += ancho_burbuja + espacio_x
    
    return max(80, 25 + filas * (radio_burbuja * 2 + espacio_y) + 20)

def calcular_altura_sugerencias(c, keywords_suggestion, missing_keywords, ancho_div):
    """Calcula la altura necesaria para mostrar las sugerencias"""
    altura_base = 25  # Título
    
    # Altura para la sugerencia principal
    estilo_sug = ParagraphStyle(
        name="SugerenciaKeywords",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )
    
    ancho_sug = ancho_div - 30
    par_sug = Paragraph(keywords_suggestion, estilo_sug)
    w_sug, h_sug = par_sug.wrap(ancho_sug, 1000)
    
    altura_total = altura_base + h_sug + 20
    
    # Altura para keywords faltantes
    if missing_keywords:
        altura_total += 25  # Subtítulo
        
        espacio_x_peq = 8
        espacio_y_peq = 6
        radio_burbuja_peq = 8
        
        x_actual_peq = 0
        y_actual_peq = 0
        filas_faltantes = 1
        
        for keyword in missing_keywords:
            ancho_palabra_peq = c.stringWidth(keyword, "Poppins-Bold", 7)
            ancho_burbuja_peq = ancho_palabra_peq + 12
            
            if x_actual_peq + ancho_burbuja_peq > ancho_div - 30:
                x_actual_peq = 0
                y_actual_peq -= radio_burbuja_peq * 2 + espacio_y_peq
                filas_faltantes += 1
            
            x_actual_peq += ancho_burbuja_peq + espacio_x_peq
        
        altura_total += filas_faltantes * (radio_burbuja_peq * 2 + espacio_y_peq) + 20
    
    return max(80, altura_total)

def seccion_7(c, ancho, alto, y_inicio, datos_cv):
    # Actualizar claves según el nuevo formato
    impact_verbs_data = datos_cv.get('impact_verbs_analysis', {})
    nivel = impact_verbs_data.get('score', 5)  # Ahora es directamente un número
    sugerencias = impact_verbs_data.get('ai_feedbacks', ['No hay sugerencias disponibles'])
    
    # Asegurar que el nivel esté entre 1 y 10
    nivel = max(1, min(10, nivel))

    margen_horizontal = 50
    alto_div          = 330
    sombra_expand     = 8
    sombra_offset_x   = 2
    sombra_offset_y   = -2
    sombra_alpha      = 0.12

    ancho_div = ancho - 2 * margen_horizontal
    x_div     = margen_horizontal
    y_div     = y_inicio - alto_div

    # Sombra y fondo
    c.setFillColorRGB(0, 0, 0, alpha=sombra_alpha)
    c.roundRect(
        x_div - sombra_expand/2 + sombra_offset_x,
        y_div - sombra_expand/2 + sombra_offset_y,
        ancho_div + sombra_expand,
        alto_div + sombra_expand,
        radius=15 + sombra_expand/2,
        fill=1, stroke=0
    )
    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # Título
    c.setFillColor(grey)
    c.setFont("Poppins-SemiBold", 9)
    c.drawString(x_div + 10, y_div + alto_div - 14, "Verbos de impacto")

    # Barra de impacto
    barra_x      = x_div + 40
    barra_y      = y_div + alto_div - 70
    barra_width  = ancho_div - 80
    barra_height = 20
    n_segments   = 10
    seg_w        = barra_width / n_segments

    colores_segmentos = [
        Color(1,0,0), Color(1,0.3,0), Color(1,0.5,0),
        Color(1,0.7,0), Color(1,0.9,0), Color(0.9,1,0),
        Color(0.7,1,0), Color(0.4,1,0), Color(0.2,1,0),
        Color(0,1,0)
    ]
    for i in range(n_segments):
        c.setFillColor(colores_segmentos[i] if i < nivel else lightgrey)
        c.rect(barra_x + i*seg_w, barra_y, seg_w, barra_height, stroke=0, fill=1)

    # Numeración
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    for i in range(n_segments+1):
        c.drawString(barra_x + i*seg_w - 3, barra_y + barra_height + 5, str(i+1))

    # Flecha indicador
    flecha_x = barra_x + (nivel - 0.5) * seg_w
    flecha_y = barra_y - 12
    p = c.beginPath()
    p.moveTo(flecha_x, flecha_y)
    p.lineTo(flecha_x - 7, flecha_y - 15)
    p.lineTo(flecha_x + 7, flecha_y - 15)
    p.close()
    c.setFillColor(red)
    c.drawPath(p, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(flecha_x, flecha_y - 23, "Tu nivel")

    # Sugerencias con fondo ajustado
    estilo_sug = ParagraphStyle(
        name="SugerenciaJustificada",
        fontName="Helvetica",
        fontSize=9,
        leading=10,
        alignment=TA_JUSTIFY
    )
    padding_x      = 10
    padding_y      = 5
    icon_r         = 7
    text_off       = icon_r*3 + 5
    adv_y          = barra_y - 60  # Ajustado sin h_com
    bg_width       = ancho_div - 2 * padding_x - 20  # espacio extra 20 pts

    for sugerencia in sugerencias:
        par_sug = Paragraph(sugerencia, estilo_sug)
        wrap_w, wrap_h = par_sug.wrap(bg_width - text_off - padding_x, alto_div)
        # bg position and size
        bg_x = x_div + padding_x
        bg_y = adv_y - wrap_h - padding_y
        bg_h = wrap_h + 2 * padding_y
        c.setFillColor(whitesmoke)
        c.roundRect(bg_x, bg_y, bg_width, bg_h, radius=10, fill=1, stroke=0)
        # bullet icon
        icon_x = bg_x + padding_x
        icon_y = bg_y + bg_h - padding_y - icon_r
        c.setFillColor(white)
        c.setStrokeColor(red)
        c.setLineWidth(2)
        c.circle(icon_x, icon_y, icon_r, fill=1, stroke=1)
        c.setFillColor(red)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(icon_x, icon_y - 5, "!")
        # draw text
        par_sug.drawOn(c, bg_x + text_off, bg_y + padding_y)
        # next block
        adv_y = bg_y - 20

    return alto_div + 20

# SECCION 8 - JUSTIFICADO
def seccion_8(c, ancho, alto, y_inicio, datos_cv):
    # Actualizar claves según el nuevo formato
    executive_summary = datos_cv.get('executive_summary_analysis', {})
    actual = executive_summary.get('current', '')
    recomendado = executive_summary.get('recommended', '')
    
    # Manejar casos donde los campos están vacíos
    if not actual or actual.strip() == '':
        actual = 'Resumen ejecutivo no incluido en el CV'
    if not recomendado or recomendado.strip() == '':
        recomendado = 'Recomendación no disponible'

    # Título
    c.setFont("Poppins-Bold", 14)
    c.setFillColor(HexColor("#028BBF"))
    c.drawString(50, y_inicio, "Resumen Ejecutivo")

    # Posicionar encabezados
    y = y_inicio - 30
    c.setFont("Poppins-SemiBold", 10)
    c.setFillColor(HexColor("#A9A9A9"))
    c.drawString(50, y, "Texto Actual")
    c.drawString(ancho / 2 + 10, y, "Texto recomendado")

    # Línea separatoria
    y_linea = y - 3
    c.setLineWidth(1)
    c.setStrokeColor(black)
    c.line(45, y_linea, ancho - 45, y_linea)

    # Preparar estilo justificado para ambos textos
    estilo_col = ParagraphStyle(
        name="ColJustificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )
    # Permitir corte por carácter para evitar overflow con palabras largas
    setattr(estilo_col, 'wordWrap', 'CJK')

    # Columnas
    ancho_columna = (ancho / 2) - 60  # deja 50px margen + 10px separación
    x_actual = 50
    x_reco = ancho / 2 + 10
    # Altura disponible para el texto (no limitamos para medir correctamente)
    alto_disponible = alto  # usar alto total para medir

    # Crear párrafos
    par_actual = Paragraph(actual, estilo_col)
    par_reco = Paragraph(recomendado, estilo_col)

    # Envolver y dibujar "Texto Actual"
    w_act, h_act = par_actual.wrap(ancho_columna, alto_disponible)
    par_actual.drawOn(c, x_actual, y - h_act - 5)  # 5pt debajo de la línea

    # Envolver y dibujar "Texto recomendado"
    w_rec, h_rec = par_reco.wrap(ancho_columna, alto_disponible)
    par_reco.drawOn(c, x_reco, y - h_rec - 5)

    # Altura dinámica: título (30) + línea (5) + altura mayor de columnas + margen inferior
    altura_contenido = 30 + 5 + max(h_act, h_rec) + 15
    alto_seccion = max(145, altura_contenido)

    return alto_seccion

def seccion_9(c, ancho, alto, y_inicio, datos_cv):
    """9. Sección de ajuste al puesto usando el componente reutilizable"""
    
    # Colores para estados
    green = HexColor("#28A745")
    yellow = HexColor("#FFC107")
    red = HexColor("#DC3545")
    
    # Título de la sección
    c.setFont("Poppins-Bold", 14)
    c.setFillColor(HexColor("#028BBF"))
    c.drawString(50, y_inicio, "Ajuste al puesto")
    
    # Preparar datos - usar role_fit_analysis según el nuevo formato
    role_fit = datos_cv.get('role_fit_analysis', {})
    if role_fit:
        # Crear mapeo basado en la información de role_fit_analysis disponible
        analysis_skills = role_fit.get('analysis_skills', {})
        quantifiable_results = role_fit.get('quantifiable_results', {})
        
        ajuste = {
            'analysis_skills': {
                'level': analysis_skills.get('level', 'Medio'),
                'action': analysis_skills.get('ai_feedback', 'Revisar sugerencias de mejora en el análisis.')
            },
            'quantifiable_results': {
                'level': quantifiable_results.get('level', 'Medio'),
                'action': quantifiable_results.get('ai_feedback', 'Añadir métricas cuantificables por proyecto según las sugerencias de mejora.')
            },
            'soft_skills': {
                'level': 'Alto',
                'action': 'Las habilidades blandas están bien representadas en el CV.'
            },
            'technical_language': {
                'level': 'Alto',
                'action': 'El lenguaje técnico es apropiado para el puesto.'
            }
        }
    else:
        ajuste = {}
    
    # Mapear en español
    mapping = {
        'analysis_skills': 'Herramientas de Medición',
        'quantifiable_results': 'Resultados Cuantificables',
        'soft_skills': 'Habilidades Blandas',
        'technical_language': 'Lenguaje Técnico',
    }
    
    # Preparar datos para el componente
    data = []
    for clave, etiqueta in mapping.items():
        entry = ajuste.get(clave, {})
        nivel = entry.get('level', 'N/E')
        accion = entry.get('action', '')
        color_estado = (
            green if nivel.lower() == 'alto' else
            yellow if nivel.lower() == 'medio' else
            red if nivel.lower() == 'bajo' else
            black
        )
        data.append((etiqueta, nivel, accion, color_estado))
    
    # Configuración personalizada para esta sección
    custom_config = {
        'container_style': {
            'margin_horizontal': 20,
            'padding_internal': 20,
            'shadow_offset': 5,
            'border_radius': 15,
            'shadow_alpha': 0.15
        },
        'column_config': {
            'element_width': 0.2,      # 20% del ancho
            'status_width': 0.2,       # 20% del ancho
            'suggestion_width': 0.6    # 60% del ancho
        },
        'header_style': {
            'font_family': 'Poppins-SemiBold',
            'font_size': 10,
            'color': HexColor("#A9A9A9"),
            'line_color': HexColor("#B0B0B0"),
            'line_width': 0.7
        }
    }
    
    # Crear tabla usando el componente reutilizable
    table_height = create_evaluation_table(
        canvas=c,
        width=ancho,
        height=alto,
        y_start=y_inicio - 40,  # Espacio para el título
        data=data,
        custom_config=custom_config
    )
    
    return table_height + 60  # Incluir espacio del título

def seccion_10(c, ancho, alto, y_inicio, datos_cv):
    margen_horizontal = 30
    padding_interno = 20
    sombra_offset = 5
    desplazamiento_bajar_div = 30  # Baja el div blanco 30 pts

    # Actualizar claves según el nuevo formato
    experiencias = datos_cv.get('work_experience_analysis', [])

    # Estilo justificado para "Texto Recomendado"
    estilo_reco = ParagraphStyle(
        name="RecoJustificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )

    # Estilo justificado para "Texto Actual"
    estilo_act = ParagraphStyle(
        name="ActJustificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=5,
    )

    # Cálculo dinámico del alto total basado en el contenido
    alto_rectangulo = 100  # Valor base para el rectángulo
    for exp in experiencias:
        # Empresa con wrap
        empresa = exp.get('company', '')
        max_width_emp = ancho * 0.2 - 10
        lineas_empresa = wrap_text(empresa, max_width_emp, c, "Poppins-Regular", 9)
        
        # Texto Actual con wrap
        texto_actual = exp.get('current', '')
        max_width_act = ancho * 0.35 - 10
        lineas_actual = wrap_text(texto_actual, max_width_act, c, "Poppins-Regular", 9)
        
        # Texto Recomendado justificado via Paragraph
        texto_recomendado = exp.get('recommended', '')
        ancho_reco = ancho * 0.4 - 10
        par_reco = Paragraph(texto_recomendado, estilo_reco)
        w_reco, h_reco = par_reco.wrap(ancho_reco, alto)
        
        # Ajustar el alto total del rectángulo según el contenido
        alto_rectangulo += max(len(lineas_empresa), len(lineas_actual), int(h_reco / 12)) * 12 + 40  # Agregamos 20 por espaciado entre filas

    # Definición del alto del fondo degradado
    alto_degradado = alto_rectangulo - 60  # Añadir un margen adicional para el fondo

    # Fondo degradado
    imagen_fondo = ImageReader('./public/img/fondo.png')
    c.drawImage(imagen_fondo, 0, y_inicio - alto_degradado, width=ancho, height=alto_degradado)

    # Título
    c.setFont("Poppins-Bold", 18)
    c.setFillColor(white)
    titulo = "Experiencia Laboral"
    ancho_titulo = c.stringWidth(titulo, "Poppins-Bold", 18)
    x_titulo = margen_horizontal + (ancho - 2 * margen_horizontal - ancho_titulo) / 2
    y_titulo = y_inicio - 40
    c.drawString(x_titulo, y_titulo, titulo)

    # Div blanco con sombra
    y_div = y_inicio - alto_rectangulo + 20 + padding_interno - desplazamiento_bajar_div - 20
    x_div = margen_horizontal + padding_interno
    ancho_div = ancho - 2 * margen_horizontal - 2 * padding_interno
    alto_div = alto_rectangulo - 20 - 2 * padding_interno

    # Sombra
    c.setFillColorRGB(0, 0, 0, alpha=0.15)
    c.roundRect(x_div + sombra_offset, y_div - sombra_offset, ancho_div, alto_div, radius=15, fill=1, stroke=0)
    # Div blanco
    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # Cabeceras
    padding_top_div = 20
    y = y_div + alto_div - padding_top_div
    c.setFont("Poppins-SemiBold", 10)
    c.setFillColor(HexColor("#A9A9A9"))
    margen_col1 = x_div + 10
    margen_col2 = x_div + ancho_div * 0.2
    margen_col3 = x_div + ancho_div * 0.6
    c.drawString(margen_col1, y, "Empresa")
    c.drawString(margen_col2, y, "Texto Actual")
    c.drawString(margen_col3, y, "Texto Recomendado")

    gris_linea = HexColor("#B0B0B0")
    c.setStrokeColor(gris_linea)
    c.setLineWidth(0.7)
    c.line(margen_col1, y - 5, x_div + ancho_div - 10, y - 5)

    # Cuerpo de la tabla
    c.setFont("Poppins-Regular", 9)
    y -= 25

    for i, exp in enumerate(experiencias):
        empresa = exp.get('company', '')
        texto_actual = exp.get('current', '')
        texto_recomendado = exp.get('recommended', '')

        # Empresa con wrap
        max_width_emp = ancho_div * 0.2 - 10
        lineas_empresa = wrap_text(empresa, max_width_emp, c, "Poppins-Regular", 9)
        y_emp = y
        c.setFillColor(black)
        for linea in lineas_empresa:
            c.drawString(margen_col1, y_emp, linea)
            y_emp -= 12

        # Texto Actual con justificación via Paragraph
        ancho_act = ancho_div * 0.35 - 10
        par_act = Paragraph(texto_actual, estilo_act)
        w_act, h_act = par_act.wrap(ancho_act, alto_div)
        y_act_start = y + 15
        par_act.drawOn(c, margen_col2, y_act_start - h_act)

        # Texto Recomendado justificado via Paragraph
        ancho_reco = ancho_div * 0.4 - 10
        par_reco = Paragraph(texto_recomendado, estilo_reco)
        w_reco, h_reco = par_reco.wrap(ancho_reco, alto_div)
        y_reco_start = y + 15
        par_reco.drawOn(c, margen_col3, y_reco_start - h_reco)

        # Ajustar y para siguiente fila
        siguiente_y = min(y_emp, y_act_start - h_act, y_reco_start - h_reco) - 20

        # Agregar espacio antes de la línea
        siguiente_y -= 10  # Puedes ajustar este valor a la cantidad de espacio que desees

        # Línea separadora
        if i < len(experiencias) - 1:
            c.setStrokeColor(gris_linea)
            c.setLineWidth(0.5)
            c.line(margen_col1, siguiente_y + 20, x_div + ancho_div - 10, siguiente_y + 20)

        y = siguiente_y

    altura_ocupada = alto_rectangulo + desplazamiento_bajar_div + 20
    return altura_ocupada

def seccion_11(c, ancho, alto, y_inicio, datos_cv):
    margen_izq = 50
    margen_der = 100          # Aumento del margen derecho
    espacio_columna = 20      # Separación extra entre bloques
    y = y_inicio
    azul_titulo = HexColor("#028BBF")

    # Estilo justificado para columnas de Voluntariado/Educación
    estilo_just = ParagraphStyle(
        name="Justificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )

    # -------------------------------------------------------------------
    # Habilidades y Herramientas (Columna 1)
    # -------------------------------------------------------------------
    c.setFont("Poppins-Bold", 14)
    c.setFillColor(azul_titulo)
    c.drawString(margen_izq, y, "Habilidades y Herramientas")

    # Ajuste para comenzar la lista de habilidades y herramientas
    y_hh = y - 40
    c.setFont("Poppins-Regular", 9)
    # Actualizar claves según el nuevo formato
    skills_tools_data = datos_cv.get('skills_tools_analysis', {})
    habilidades = skills_tools_data  # Usar todo el objeto, no solo ai_feedback
    max_width_hh = ancho - margen_izq - margen_der  # Usamos todo el ancho disponible
    
    # Formatear habilidades de manera estructurada
    if isinstance(habilidades, dict):
        # Si es un diccionario con la nueva estructura
        current_skills = habilidades.get('current_skills', '')
        ai_feedback = habilidades.get('ai_feedback', '')
        
        # Mostrar habilidades actuales con subtítulo
        if current_skills:
            # Subtítulo "Habilidades Actuales"
            c.setFont("Poppins-Bold", 11)
            c.setFillColor(HexColor("#3a3a3a"))
            c.drawString(margen_izq, y_hh, "Habilidades Actuales:")
            y_hh -= 18
            
            # Contenido de las habilidades actuales
            c.setFont("Poppins-Regular", 9)
            c.setFillColor(HexColor("#2c2c2c"))  # Gris oscuro para distinguir del título
            lineas = wrap_text(current_skills, max_width_hh, c, "Poppins-Regular", 9)
            for linea in lineas:
                c.drawString(margen_izq, y_hh, linea)
                y_hh -= 12
            y_hh -= 20  # espacio extra después del contenido
        
        # Mostrar AI feedback con subtítulo
        if ai_feedback:
            # Subtítulo "Recomendaciones"
            c.setFont("Poppins-Bold", 11)
            c.setFillColor(HexColor("#3a3a3a"))
            c.drawString(margen_izq, y_hh, "Recomendaciones:")
            y_hh -= 18
            
            # Contenido de las recomendaciones
            c.setFont("Poppins-Regular", 9)
            c.setFillColor(HexColor("#2c2c2c"))  # Gris oscuro para distinguir del título
            lineas = wrap_text(ai_feedback, max_width_hh, c, "Poppins-Regular", 9)
            for linea in lineas:
                c.drawString(margen_izq, y_hh, linea)
                y_hh -= 12
            y_hh -= 15  # espacio extra después del contenido
    elif isinstance(habilidades, list):
        cv_actual_content = ""
        recommendations_content = ""
        
        # Separar el contenido en CV actual y recomendaciones
        for habilidad in habilidades:
            if isinstance(habilidad, str):
                texto_habilidad = habilidad.strip()
                
                if texto_habilidad.startswith("CV ACTUAL:"):
                    cv_actual_content = texto_habilidad.replace("CV ACTUAL:", "").strip()
                elif texto_habilidad.startswith("RECOMMENDATIONS:"):
                    recommendations_content = texto_habilidad.replace("RECOMMENDATIONS:", "").strip()
        
        # Mostrar CV Actual con subtítulo
        if cv_actual_content:
            # Subtítulo "Habilidades Actuales"
            c.setFont("Poppins-Bold", 11)
            c.setFillColor(HexColor("#3a3a3a"))
            c.drawString(margen_izq, y_hh, "Habilidades Actuales:")
            y_hh -= 18
            
            # Contenido de las habilidades actuales
            c.setFont("Poppins-Regular", 9)
            c.setFillColor(HexColor("#2c2c2c"))  # Gris oscuro para distinguir del título
            lineas = wrap_text(cv_actual_content, max_width_hh, c, "Poppins-Regular", 9)
            for linea in lineas:
                c.drawString(margen_izq, y_hh, linea)
                y_hh -= 12
            y_hh -= 20  # espacio extra después del contenido
        
        # Mostrar Recomendaciones con subtítulo
        if recommendations_content:
            # Subtítulo "Recomendaciones"
            c.setFont("Poppins-Bold", 11)
            c.setFillColor(HexColor("#3a3a3a"))
            c.drawString(margen_izq, y_hh, "Recomendaciones:")
            y_hh -= 18
            
            # Contenido de las recomendaciones
            c.setFont("Poppins-Regular", 9)
            c.setFillColor(HexColor("#2c2c2c"))  # Gris oscuro para distinguir del título
            lineas = wrap_text(recommendations_content, max_width_hh, c, "Poppins-Regular", 9)
            for linea in lineas:
                c.drawString(margen_izq, y_hh, linea)
                y_hh -= 12
            y_hh -= 15  # espacio extra después del contenido
    else:
        # Si es otro tipo, convertirlo a string
        texto = str(habilidades)
        c.drawString(margen_izq, y_hh, "•")
        lineas = wrap_text(texto, max_width_hh - 20, c, "Poppins-Regular", 9)
        for linea in lineas:
            c.drawString(margen_izq + 15, y_hh, linea)
            y_hh -= 12
        y_hh -= 8

    # -------------------------------------------------------------------
    # Separación entre Habilidades y Herramientas y Educación (en la misma fila)
    # -------------------------------------------------------------------
    y_hh -= 30  # Espacio entre secciones para no sobreponerse
    c.setFont("Poppins-Bold", 14)
    c.setFillColor(azul_titulo)
    c.drawString(margen_izq, y_hh, "Educación")

    # Ajuste para Educación
    y_educ = y_hh - 30  # Reducido de 40 a 30 para eliminar el subtítulo confuso
    
    c.setFont("Poppins-Regular", 9)
    estudios = datos_cv.get('education_analysis', [])
    max_width_edu = ancho - margen_izq - margen_der  # Usamos todo el ancho disponible
    
    # Formatear educación de manera estructurada
    if isinstance(estudios, list):
        for estudio in estudios:
            if isinstance(estudio, dict):
                # Extraer datos del diccionario
                degree = estudio.get('degree', 'No especificado')
                institution = estudio.get('institution', 'No especificada')
                graduation_year = estudio.get('date', 'No especificado')
                ai_feedback = estudio.get('ai_feedback', '')
                
                # Formatear el título del grado
                c.setFont("Poppins-Bold", 11)
                c.setFillColor(HexColor("#007bb6"))  # Azul para el título
                lineas_degree = wrap_text(degree, max_width_edu, c, "Poppins-Bold", 11)
                for linea in lineas_degree:
                    c.drawString(margen_izq, y_educ, linea)
                    y_educ -= 15
                
                # Formatear la institución
                c.setFont("Poppins-SemiBold", 10)
                c.setFillColor(black)
                lineas_institution = wrap_text(institution, max_width_edu, c, "Poppins-SemiBold", 10)
                for linea in lineas_institution:
                    c.drawString(margen_izq, y_educ, linea)
                    y_educ -= 13
                
                # Formatear el año de graduación
                c.setFont("Poppins-Regular", 9)
                c.setFillColor(grey)
                c.drawString(margen_izq, y_educ, graduation_year)
                y_educ -= 15
                
                # Mostrar ai_feedback si está disponible (como recomendación)
                if ai_feedback:
                    c.setFont("Poppins-Regular", 8)
                    c.setFillColor(HexColor("#666666"))
                    c.setFont("Poppins-SemiBold", 8)
                    c.drawString(margen_izq, y_educ, "Recomendación:")
                    y_educ -= 12
                    c.setFont("Poppins-Regular", 8)
                    lineas_feedback = wrap_text(ai_feedback, max_width_edu, c, "Poppins-Regular", 8)
                    for linea in lineas_feedback:
                        c.drawString(margen_izq, y_educ, linea)
                        y_educ -= 10
                
                # Espacio entre estudios
                y_educ -= 15
            else:
                # Si no es un diccionario, mostrar como texto simple
                texto = str(estudio)
                lineas = wrap_text(texto, max_width_edu, c, "Poppins-Regular", 8)
                for linea in lineas:
                    c.drawString(margen_izq, y_educ, linea)
                    y_educ -= 12
                y_educ -= 15
    elif isinstance(estudios, dict):
        # Si es un solo diccionario, formatearlo
        degree = estudios.get('degree', 'No especificado')
        institution = estudios.get('institution', 'No especificada')
        graduation_year = estudios.get('date', 'No especificado')
        ai_feedback = estudios.get('ai_feedback', '')
        
        c.setFont("Poppins-Bold", 11)
        c.setFillColor(HexColor("#007bb6"))
        lineas_degree = wrap_text(degree, max_width_edu, c, "Poppins-Bold", 11)
        for linea in lineas_degree:
            c.drawString(margen_izq, y_educ, linea)
            y_educ -= 15
        
        c.setFont("Poppins-SemiBold", 10)
        c.setFillColor(black)
        lineas_institution = wrap_text(institution, max_width_edu, c, "Poppins-SemiBold", 10)
        for linea in lineas_institution:
            c.drawString(margen_izq, y_educ, linea)
            y_educ -= 13
        
        c.setFont("Poppins-Regular", 9)
        c.setFillColor(grey)
        c.drawString(margen_izq, y_educ, graduation_year)
        y_educ -= 15
        
        # Mostrar ai_feedback si está disponible (como recomendación)
        if ai_feedback:
            c.setFont("Poppins-Regular", 8)
            c.setFillColor(HexColor("#666666"))
            c.setFont("Poppins-SemiBold", 8)
            c.drawString(margen_izq, y_educ, "Recomendación:")
            y_educ -= 12
            c.setFont("Poppins-Regular", 8)
            lineas_feedback = wrap_text(ai_feedback, max_width_edu, c, "Poppins-Regular", 8)
            for linea in lineas_feedback:
                c.drawString(margen_izq, y_educ, linea)
                y_educ -= 10

    # -------------------------------------------------------------------
    # Voluntariado
    # -------------------------------------------------------------------
    c.setFont("Poppins-Bold", 14)
    c.setFillColor(azul_titulo)

    # Agregar más separación antes de la sección de Voluntariado
    y_vol = y_educ - 50  # He aumentado la separación de 30 a 50
    c.drawString(margen_izq, y_vol, "Voluntariado")

    y_vol -= 40  # Ajuste adicional para que la parte de "Voluntariado" no se solape
    c.setFont("Poppins-SemiBold", 10)
    c.setFillColor(black)
    c.drawString(margen_izq, y_vol, "Organización")
    c.drawString(margen_izq + 100, y_vol, "Texto Actual")
    c.drawString(margen_izq + 300, y_vol, "Texto Recomendado")

    y_vol -= 20
    c.setStrokeColor(HexColor("#B0B0B0"))
    c.setLineWidth(0.7)
    c.line(margen_izq, y_vol, ancho - margen_der, y_vol)
    y_vol -= 20

    voluntariado = datos_cv.get('volunteering_analysis', [])
    for item in voluntariado:
        org = item.get("organization", "No disponible") or "No disponible"
        actual = item.get("current", "No disponible") or "No disponible"
        reco = item.get("recommended", "No disponible") or "No disponible"

        # Organización
        y_org = y_vol
        for linea in wrap_text(org, 90, c, "Poppins-Regular", 9):
            c.drawString(margen_izq, y_org, linea)
            y_org -= 12

        # Texto Actual
        par_act = Paragraph(actual, estilo_just)
        ancho_act = 180
        w_act, h_act = par_act.wrap(ancho_act, alto)
        par_act.drawOn(c, margen_izq + 100, y_vol - h_act + 5)

        # Texto Recomendado
        par_reco = Paragraph(reco, estilo_just)
        ancho_reco = ancho - (margen_izq + 300) - margen_der
        w_rec, h_rec = par_reco.wrap(ancho_reco, alto)
        par_reco.drawOn(c, margen_izq + 300, y_vol - h_rec + 5)

        # Ajuste de la altura (alineación de las sugerencias)
        max_h = max(h_act, h_rec)
        y_vol = y_vol - max_h - 20  # Ajustamos la altura de la siguiente línea
        if item is not voluntariado[-1]:
            c.setStrokeColor(HexColor("#B0B0B0"))
            c.setLineWidth(0.5)
            c.line(margen_izq, y_vol + 15, ancho - margen_der, y_vol + 15)

    altura_ocupada = y_inicio - y_vol
    return altura_ocupada - 20

# SECCION 12 - JUSTIFICADO
def seccion_12(c, ancho, alto, y_inicio, datos_cv):
    """12. Sección de formato y optimización usando el componente reutilizable"""
    
    # Alturas y márgenes
    alto_degradado = 250
    margen_horizontal = 30
    
    # Fondo degradado
    imagen_fondo = ImageReader('./public/img/fondo2.png')
    c.drawImage(imagen_fondo, 0, y_inicio - alto_degradado,
                width=ancho, height=alto_degradado)

    # Título encima del degradado
    titulo = "Formato y optimización"
    c.setFont("Poppins-Bold", 18)
    c.setFillColor(white)
    ancho_tit = c.stringWidth(titulo, "Poppins-Bold", 18)
    x_tit = margen_horizontal + (ancho - 2*margen_horizontal - ancho_tit)/2
    c.drawString(x_tit, y_inicio - 40, titulo)

    # Colores para estados
    green = HexColor("#28A745")
    yellow = HexColor("#FFC107")
    red = HexColor("#DC3545")
    
    # Datos dinámicos
    ajuste = datos_cv.get('format_optimization', {})
    
    # Mapear en español
    mapping = {
        'length': 'Longitud',
        'photo': 'Foto',
        'keywords': 'Palabras Clave',
    }
    
    # Preparar datos para el componente
    data = []
    for key, label in mapping.items():
        ent = ajuste.get(key, {})
        estado = ent.get('status', 'N/E')
        sugerencia = ent.get('ai_feedback', '')
        
        # Handle different data types for status
        if isinstance(estado, str):
            nivel = estado.lower()
            if nivel == 'alto':
                color = green
            elif nivel == 'medio':
                color = yellow
            elif nivel == 'bajo':
                color = red
            else:
                color = black
        else:
            color = black
            
        data.append((label, estado, sugerencia, color))
    
    # Configuración personalizada para esta sección
    custom_config = {
        'container_style': {
            'margin_horizontal': 30,
            'padding_internal': 20,
            'shadow_offset': 5,
            'border_radius': 15,
            'shadow_alpha': 0.15
        },
        'column_config': {
            'element_width': 0.2,      # 20% del ancho
            'status_width': 0.2,       # 20% del ancho
            'suggestion_width': 0.6    # 60% del ancho
        },
        'header_style': {
            'font_family': 'Poppins-SemiBold',
            'font_size': 10,
            'color': HexColor("#A9A9A9"),
            'line_color': HexColor("#B0B0B0"),
            'line_width': 0.7
        }
    }
    
    # Crear tabla usando el componente reutilizable
    # Ajustar la posición para que no tape el título
    table_height = create_evaluation_table(
        canvas=c,
        width=ancho,
        height=alto,
        y_start=y_inicio - 40,  # Posición base
        data=data,
        custom_config=custom_config,
        title_spacing=40  # Espacio adicional para el título
    )
    
    return table_height + 40  # Incluir espacio del título

def seccion_13(c, ancho, alto, y_inicio, logo_path): 
    # Calcular las dimensiones de la imagen
    imagen = ImageReader(logo_path)
    imagen_width = 120  # Puedes ajustar el tamaño de la imagen según sea necesario
    imagen_height = 26  # Ajusta la altura de la imagen también

    # Calcular la posición centrada para la imagen
    x_imagen = (ancho - imagen_width) / 2
    y_imagen = y_inicio - imagen_height - 20  # Ajustar un poco hacia abajo

    # Dibujar la imagen centrada en la sección
    c.drawImage(imagen, x_imagen, y_imagen, width=imagen_width, height=imagen_height, mask='auto')

    # Definir la altura ocupada en la sección
    altura_ocupada = imagen_height - 10  # Incluir el espacio para la imagen y un poco de margen

    return altura_ocupada -20

def seccion_14(c, ancho, alto, y_inicio, datos_cv):
    """14. Sección de cumplimiento ATS - Completamente responsive"""
    # Obtener datos de ATS compliance
    ats_data = datos_cv.get('ats_compliance', {})
    score = ats_data.get('score', 0)
    issues = ats_data.get('issues', [])
    ai_feedbacks = ats_data.get('ai_feedbacks', [])
    
    # Determinar el estado basado en el score
    if score >= 71:
        estado = "Alto"
        color_estado = HexColor("#28A745")
    elif score >= 41:
        estado = "Medio"
        color_estado = HexColor("#FFC107")
    else:
        estado = "Bajo"
        color_estado = HexColor("#DC3545")

    margen_horizontal = 50
    ancho_div = ancho - 2 * margen_horizontal
    x_div = margen_horizontal
    
    # Calcular altura dinámicamente
    altura_base = 50  # Título + score + estado
    
    # Calcular altura para issues
    altura_issues = 0
    if issues:
        altura_issues = 20  # Título "Problemas encontrados:"
        for issue in issues:
            # Calcular altura del texto con wrap
            estilo_issue = ParagraphStyle(
                name="IssueStyle",
                fontName="Poppins-Regular",
                fontSize=9,
                leading=11,
                alignment=TA_LEFT,
                spaceBefore=0,
                spaceAfter=0,
            )
            par_issue = Paragraph(f"• {issue}", estilo_issue)
            w_issue, h_issue = par_issue.wrap(ancho_div - 30, 1000)
            altura_issues += h_issue + 5
        altura_issues += 25  # Más espacio extra después de issues para separar secciones
    
    # Calcular altura para feedbacks
    altura_feedbacks = 0
    if ai_feedbacks:
        altura_feedbacks = 20  # Título "Recomendaciones:"
        for feedback in ai_feedbacks:
            estilo_feedback = ParagraphStyle(
                name="FeedbackStyle",
                fontName="Poppins-Regular",
                fontSize=9,
                leading=11,
                alignment=TA_JUSTIFY,
                spaceBefore=0,
                spaceAfter=0,
            )
            par_feedback = Paragraph(f"• {feedback}", estilo_feedback)  # Añadido bullet point
            w_feedback, h_feedback = par_feedback.wrap(ancho_div - 30, 1000)  # Ajustado margen para bullet
            altura_feedbacks += h_feedback + 8
        altura_feedbacks += 10  # Espacio extra después de feedbacks
    
    # Altura total del div
    alto_div = max(120, altura_base + altura_issues + altura_feedbacks + 20)
    y_div = y_inicio - alto_div

    sombra_expand = 8
    sombra_offset_x = 2
    sombra_offset_y = -2
    sombra_alpha = 0.12

    # Sombra
    c.setFillColorRGB(0, 0, 0, alpha=sombra_alpha)
    c.roundRect(
        x_div - sombra_expand / 2 + sombra_offset_x,
        y_div - sombra_expand / 2 + sombra_offset_y,
        ancho_div + sombra_expand,
        alto_div + sombra_expand,
        radius=15 + sombra_expand / 2,
        fill=1, stroke=0
    )

    # Div blanco principal
    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # Título
    c.setFillColor(grey)
    c.setFont("Poppins-SemiBold", 9)
    c.drawString(x_div + 10, y_div + alto_div - 14, "Cumplimiento ATS")

    # Score y estado
    c.setFillColor(black)
    c.setFont("Poppins-Bold", 16)
    score_text = f"{score}/100"
    ancho_score = c.stringWidth(score_text, "Poppins-Bold", 16)
    x_score = x_div + (ancho_div - ancho_score) / 2
    c.drawString(x_score, y_div + alto_div - 40, score_text)

    # Estado con color
    c.setFillColor(color_estado)
    c.setFont("Poppins-Bold", 14)
    ancho_estado = c.stringWidth(estado, "Poppins-Bold", 14)
    x_estado = x_div + (ancho_div - ancho_estado) / 2
    c.drawString(x_estado, y_div + alto_div - 60, estado)

    # Posición inicial para contenido dinámico
    y_contenido = y_div + alto_div - 80

    # Issues si existen
    if issues:
        c.setFillColor(black)
        c.setFont("Poppins-Bold", 10)
        c.drawString(x_div + 10, y_contenido, "Problemas encontrados:")
        y_contenido -= 20
        
        for issue in issues:
            estilo_issue = ParagraphStyle(
                name="IssueStyle",
                fontName="Poppins-Regular",
                fontSize=9,
                leading=11,
                alignment=TA_LEFT,
                spaceBefore=0,
                spaceAfter=0,
            )
            par_issue = Paragraph(f"• {issue}", estilo_issue)
            w_issue, h_issue = par_issue.wrap(ancho_div - 30, 1000)
            par_issue.drawOn(c, x_div + 10, y_contenido - h_issue)
            y_contenido -= h_issue + 5
        y_contenido -= 20  # Más espacio extra después de issues para separar secciones

    # AI Feedbacks
    if ai_feedbacks:
        c.setFillColor(black)
        c.setFont("Poppins-Bold", 10)
        c.drawString(x_div + 10, y_contenido, "Recomendaciones:")
        y_contenido -= 20
        
        for feedback in ai_feedbacks:
            estilo_feedback = ParagraphStyle(
                name="FeedbackStyle",
                fontName="Poppins-Regular",
                fontSize=9,
                leading=11,
                alignment=TA_LEFT,  # Cambiado de TA_JUSTIFY a TA_LEFT para consistencia
                spaceBefore=0,
                spaceAfter=0,
            )
            par_feedback = Paragraph(f"• {feedback}", estilo_feedback)  # Añadido bullet point
            w_feedback, h_feedback = par_feedback.wrap(ancho_div - 30, 1000)  # Ajustado margen para bullet
            par_feedback.drawOn(c, x_div + 10, y_contenido - h_feedback)
            y_contenido -= h_feedback + 8

    return alto_div