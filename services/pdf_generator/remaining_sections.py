from reportlab.lib.colors import Color, HexColor

from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from .pdf_utils import wrap_text


# Definir colores específicos
white = Color(1, 1, 1)
black = Color(0, 0, 0)
grey = Color(0.5, 0.5, 0.5)
green = Color(0, 1, 0)
red = Color(1, 0, 0)
blue = Color(0, 0, 1)
lightgrey = Color(0.9, 0.9, 0.9)
whitesmoke = Color(0.96, 0.96, 0.96)

def seccion_4(c, ancho, alto, y_inicio, datos_cv):
    """4. Sección de nombre de archivo"""
    archivo = datos_cv.get('filename', {}).get('file', 'File not available')
    comentario = datos_cv.get('filename', {}).get('comment', 'Comment not available')

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
    observacion = datos_cv.get('indispensable', {}).get('indispensable', {}).get('general_comment', 'general_comment not available')
    margen_horizontal = 50
    alto_div = 130
    ancho_div = ancho - 2 * margen_horizontal
    x_div = margen_horizontal
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

    # Título "Indispensable"
    c.setFillColor(grey)
    c.setFont("Poppins-SemiBold", 9)
    c.drawString(x_div + 10, y_div + alto_div - 14, "Indispensable")

    # Posición inicial de la tabla
    y_tabla_inicio = y_div + alto_div - 40

    # Cabecera de la tabla
    c.setFont("Poppins-SemiBold", 7)
    columnas = [x_div + 10, x_div + 100, x_div + 160, x_div + 220]
    c.setFillColor(black)
    c.drawString(columnas[0], y_tabla_inicio, "Elemento")
    c.drawString(columnas[1], y_tabla_inicio, "¿Existe?")
    c.drawString(columnas[2], y_tabla_inicio, "¿Bien")
    c.drawString(columnas[2], y_tabla_inicio - 13, "posicionado?")
    c.drawString(columnas[3], y_tabla_inicio, "¿Fácil de")
    c.drawString(columnas[3], y_tabla_inicio - 13, "distinguir?")

    # Línea bajo la cabecera
    c.setStrokeColor(HexColor("#B0B0B0"))
    c.setLineWidth(0.7)
    c.line(columnas[0], y_tabla_inicio - 20, columnas[3] + 30, y_tabla_inicio - 20)

    # Filas de datos
    evaluacion = datos_cv.get('indispensable', {}) \
    .get('indispensable', {}) \
    .get('evaluation', [])
    y_filas = [y_tabla_inicio - 30 - 15 * i for i in range(len(evaluacion))]

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
        c.line(columnas[0], y - 5, columnas[3] + 30, y - 5)

    # Título y Observación justificada
    x_obs = x_div + 290
    y_obs_title = y_div + alto_div - 25
    ancho_obs = ancho_div - (x_obs - x_div) - 15
    alto_obs = y_obs_title - (y_div + 10)

    c.setFont("Poppins-Bold", 9)
    c.setFillColor(red)
    c.drawString(x_obs, y_obs_title, "Observación:")

    estilo_obs = ParagraphStyle(
        name="Justificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceAfter=0,
        spaceBefore=0,
    )

    par_obs = Paragraph(observacion, estilo_obs)
    w_com, h_com = par_obs.wrap(ancho_obs, alto_obs)
    par_obs.drawOn(c, x_obs, y_obs_title - h_com - 4)

    return alto_div

# Continuar con las demás secciones...
def seccion_6(c, ancho, alto, y_inicio, datos_cv):
    """6. Sección de palabras repetidas y relevancia"""
    palabras_repetidas = [item['word'] for item in datos_cv.get('repeat_words', {}).get('repeated_words', [])]
    relevance = datos_cv.get('relevance', 'Relevancia no disponible')

    margen_horizontal = 50
    espacio_entre_divs = 20
    alto_div = 180

    sombra_expand = 8
    sombra_offset_x = 2
    sombra_offset_y = -2
    sombra_alpha = 0.12

    ancho_disponible = ancho - 2 * margen_horizontal - espacio_entre_divs
    ancho_div = ancho_disponible / 2

    x_div1 = margen_horizontal
    x_div2 = margen_horizontal + ancho_div + espacio_entre_divs
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

    # Primer div: Palabras repetidas
    c.setFillColor(grey)
    c.setFont("Poppins-Bold", 10)
    c.drawString(x_div1 + 15, y_div + alto_div - 25, "Palabras repetidas")

    c.setFont("Poppins-Bold", 9)
    espacio_x = 12
    espacio_y = 6
    radio_burbuja = 12
    color_burbuja = HexColor("#028BBF")
    color_texto = white

    x_actual = x_div1 + 15
    y_actual = y_div + alto_div - 50

    for palabra in palabras_repetidas:
        ancho_palabra = c.stringWidth(palabra, "Poppins-Bold", 9)
        ancho_burbuja = ancho_palabra + 10
        if x_actual + ancho_burbuja > x_div1 + ancho_div - 15:
            x_actual = x_div1 + 15
            y_actual -= radio_burbuja * 2 + espacio_y
        c.setFillColor(color_burbuja)
        c.roundRect(x_actual, y_actual - radio_burbuja, ancho_burbuja, radio_burbuja*2, radius=radio_burbuja, fill=1, stroke=0)
        c.setFillColor(color_texto)
        c.drawString(x_actual + 5, y_actual - radio_burbuja/2 + 3, palabra)
        x_actual += ancho_burbuja + espacio_x

    # Segundo div: Relevancia justificada
    c.setFillColor(grey)
    c.setFont("Poppins-Bold", 10)
    c.drawString(x_div2 + 15, y_div + alto_div - 25, "Relevancia")

    estilo_rel = ParagraphStyle(
        name="RelJustificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=10,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=0,
    )

    ancho_rel = ancho_div - 30
    x_rel = x_div2 + 15
    y_rel_top = y_div + alto_div - 25 - 14

    par_rel = Paragraph(relevance, estilo_rel)
    par_rel.wrapOn(c, ancho_rel, alto_div)
    par_rel.drawOn(c, x_rel, y_rel_top - par_rel.height)

    return alto_div

def seccion_7(c, ancho, alto, y_inicio, datos_cv):
    nivel       = datos_cv.get('impact_verbs', {}).get('level', 0)
    comentario  = datos_cv.get('impact_verbs', {}).get('comment', 'Comment not available')
    sugerencias = datos_cv.get('impact_verbs', {}).get('suggestions', ['suggestions not available'])

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

    # Comentario justificado
    estilo_com = ParagraphStyle(
        name="ComentarioJustificado",
        fontName="Poppins-Regular",
        fontSize=9,
        leading=11,
        alignment=TA_JUSTIFY
    )
    par_com = Paragraph(comentario, estilo_com)
    w_com, h_com = par_com.wrap(ancho_div - 40, barra_y - y_div - 40)
    par_com.drawOn(c, x_div + 20, barra_y - 40 - h_com)

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
    adv_x_start    = x_div + padding_x + 10
    adv_y          = barra_y - 60 - h_com - 20
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

    return alto_div +20

# SECCION 8 - JUSTIFICADO
def seccion_8(c, ancho, alto, y_inicio, datos_cv):
    actual = datos_cv.get('professional_profile', {}).get('current', 'Current not available')
    recomendado = datos_cv.get('professional_profile', {}).get('recommended', 'Recommended not available')

    # Título
    c.setFont("Poppins-Bold", 14)
    c.setFillColor(HexColor("#028BBF"))
    c.drawString(50, y_inicio, "Perfil Profesional")

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

    # Columnas
    ancho_columna = (ancho / 2) - 60  # deja 50px margen + 10px separación
    x_actual = 50
    x_reco = ancho / 2 + 10
    # Altura disponible para el texto (hasta  y - margen inferior)
    alto_disponible = y - 20  # 20pt margen inferior

    # Crear párrafos
    par_actual = Paragraph(actual, estilo_col)
    par_reco = Paragraph(recomendado, estilo_col)

    # Envolver y dibujar "Texto Actual"
    w_act, h_act = par_actual.wrap(ancho_columna, alto_disponible)
    par_actual.drawOn(c, x_actual, y - h_act - 5)  # 5pt debajo de la línea

    # Envolver y dibujar "Texto recomendado"
    w_rec, h_rec = par_reco.wrap(ancho_columna, alto_disponible)
    par_reco.drawOn(c, x_reco, y - h_rec - 5)

    return 145

def seccion_9(c, ancho, alto, y_inicio, datos_cv):
    # DEBUG: Logs para sección 9
    print("=== DEBUG SECCIÓN 9 ===")
    print(f"datos_cv keys disponibles: {list(datos_cv.keys())}")
    print(f"datos_cv completo: {datos_cv}")
    
    # Colores
    azul_titulo   = HexColor("#028BBF")
    gris_cabecera = HexColor("#A9A9A9")
    gris_linea    = HexColor("#B0B0B0")
    green         = HexColor("#28A745")
    yellow        = HexColor("#FFC107")
    red           = HexColor("#DC3545")

    # Título
    c.setFont("Poppins-Bold", 14)
    c.setFillColor(azul_titulo)
    c.drawString(50, y_inicio, "Ajuste al puesto")

    # Div contenedor
    alto_rect = 300
    marg_h     = 20
    pad        = 20
    x_div      = marg_h + pad
    y_div      = y_inicio - alto_rect + pad
    ancho_div  = ancho - 2 * marg_h - 2 * pad
    alto_div   = alto_rect - 2 * pad

    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div, radius=15, fill=1, stroke=0)

    # Cabeceras
    y = y_div + alto_div - 20
    c.setFont("Poppins-SemiBold", 10)
    c.setFillColor(gris_cabecera)

    col1 = x_div + 10
    col2 = x_div + ancho_div * 0.2
    col3 = x_div + ancho_div * 0.5  # reducido de 0.6 a 0.5

    c.drawString(col1, y, "Área")
    ajuste_cabecera_estado = 50  # Ajusta este valor para mover más o menos
    c.drawString(col2 + ajuste_cabecera_estado, y, "Estado")

    c.drawString(col3, y, "Acción recomendada")

    c.setStrokeColor(gris_linea)
    c.setLineWidth(0.7)
    c.line(col1, y - 5, x_div + ancho_div - 10, y - 5)

    # Preparar datos
    ajuste = datos_cv.get('position_adjustment', {})  # Cambiado de 'ajuste_puesto' a 'position_adjustment'
    print(f"DEBUG: ajuste = {ajuste}")
    print(f"DEBUG: tipo de ajuste = {type(ajuste)}")
    
    #Mapear en español
    mapping = {
        'analysis_skills':    'Herramientas de Medición',
        'quantifiable_results':  'Resultados Cuantificables',
        'soft_skills':        'Habilidades Blandas',
        'technical_language':           'Lenguaje Técnico',
    }
    data = []
    for clave, etiqueta in mapping.items():
        entry = ajuste.get(clave, {})
        print(f"DEBUG: clave '{clave}' -> entry = {entry}")
        nivel = entry.get('level', 'N/E')
        accion = entry.get('action', '')
        print(f"DEBUG: nivel = '{nivel}', accion = '{accion}'")
        color_estado = (
            green if nivel.lower() == 'alto' else
            yellow if nivel.lower() == 'medio' else
            red if nivel.lower() == 'bajo' else
            black
        )
        data.append((etiqueta, nivel, accion, color_estado))
    
    print(f"DEBUG: data final = {data}")

    # Estilo justificado
    estilo_accion = ParagraphStyle(
        name="AccionJustificado",
        fontName="Poppins-Regular",
        fontSize=8,
        leading=10,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )

    # Dibujar filas
    c.setFont("Poppins-Regular", 9)
    y -= 25
    max_w_accion = x_div + ancho_div - col3 - 10  # ajustado al nuevo col3

    print(f"DEBUG: Número de elementos a dibujar: {len(data)}")
    for i, (area, estado, accion, color_estado) in enumerate(data):
        print(f"DEBUG: Dibujando elemento {i+1}: area='{area}', estado='{estado}', accion='{accion}'")
        # Área
        y_text = y
        c.setFillColor(black)
        for line in area.split('\n'):
            c.drawString(col1, y_text, line)
            y_text -= 12

        # Estado
        c.setFillColor(color_estado)
        x_circ = col2 + (ancho_div * 0.2 - 10) / 2
        c.circle(x_circ, y - 5, 5, fill=1, stroke=0)
        c.setFillColor(black)
        c.drawString(x_circ + 10, y - 10, estado)

        # Acción recomendada justificada
        par_acc = Paragraph(accion or "", estilo_accion)
        w_acc, h_acc = par_acc.wrap(max_w_accion, alto_div)
        par_acc.drawOn(c, col3, y - h_acc + 4)

        # Ajuste del siguiente y
        siguiente_y = min(y_text, y - h_acc) - 20
        if i < len(data) - 1:
            c.setStrokeColor(gris_linea)
            c.setLineWidth(0.5)
            c.line(col1, siguiente_y + 20, x_div + ancho_div - 10, siguiente_y + 20)
        y = siguiente_y

    print("DEBUG: Sección 9 completada exitosamente")
    return alto_rect -20

def seccion_10(c, ancho, alto, y_inicio, datos_cv):
    margen_horizontal = 30
    padding_interno = 20
    sombra_offset = 5
    desplazamiento_bajar_div = 30  # Baja el div blanco 30 pts

    # Datos de contenido
    experiencias = datos_cv.get('work_experience', [])

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
        empresa = exp.get('Company', '')
        max_width_emp = ancho * 0.2 - 10
        lineas_empresa = wrap_text(empresa, max_width_emp, c, "Poppins-Regular", 9)
        
        # Texto Actual con wrap
        texto_actual = exp.get('Current', '')
        max_width_act = ancho * 0.35 - 10
        lineas_actual = wrap_text(texto_actual, max_width_act, c, "Poppins-Regular", 9)
        
        # Texto Recomendado justificado via Paragraph
        texto_recomendado = exp.get('Recommended', '')
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
        empresa = exp.get('Company', '')
        texto_actual = exp.get('Current', '')
        texto_recomendado = exp.get('Recommended', '')

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
    c.drawString(margen_izq, y, "Habilidades y")
    c.drawString(margen_izq, y - 16, "Herramientas")

    # Ajuste para comenzar la lista de habilidades y herramientas
    y_hh = y - 40
    c.setFont("Poppins-Bold", 9)
    c.setFillColor(black)
    c.drawString(margen_izq, y_hh, "Organízalas así:")

    c.setFont("Poppins-Regular", 9)
    habilidades = datos_cv.get('skills_tools', [])
    max_width_hh = ancho - margen_izq - margen_der  # Usamos todo el ancho disponible
    y_hh -= 20
    
    # Formatear habilidades de manera estructurada
    if isinstance(habilidades, list):
        for habilidad in habilidades:
            if isinstance(habilidad, str):
                texto_habilidad = habilidad.strip()
                
                if texto_habilidad.startswith("CV ACTUAL:"):
                    # Subtítulo "CV Actual"
                    c.setFont("Poppins-Bold", 11)
                    c.setFillColor(HexColor("#007bb6"))
                    c.drawString(margen_izq, y_hh, "CV Actual:")
                    y_hh -= 18
                    
                    # Contenido del CV actual
                    contenido = texto_habilidad.replace("CV ACTUAL:", "").strip()
                    c.setFont("Poppins-Regular", 9)
                    c.setFillColor(black)
                    lineas = wrap_text(contenido, max_width_hh, c, "Poppins-Regular", 9)
                    for linea in lineas:
                        c.drawString(margen_izq, y_hh, linea)
                        y_hh -= 12
                    y_hh -= 15  # espacio extra después del contenido
                    
                elif texto_habilidad.startswith("RECOMMENDATIONS:"):
                    # Subtítulo "Recomendaciones"
                    c.setFont("Poppins-Bold", 11)
                    c.setFillColor(HexColor("#007bb6"))
                    c.drawString(margen_izq, y_hh, "Recomendaciones:")
                    y_hh -= 18
                    
                    # Contenido de las recomendaciones
                    contenido = texto_habilidad.replace("RECOMMENDATIONS:", "").strip()
                    c.setFont("Poppins-Regular", 9)
                    c.setFillColor(black)
                    lineas = wrap_text(contenido, max_width_hh, c, "Poppins-Regular", 9)
                    for linea in lineas:
                        c.drawString(margen_izq, y_hh, linea)
                        y_hh -= 12
                    y_hh -= 15  # espacio extra después del contenido
                    
                else:
                    # Si es otra habilidad normal
                    c.setFont("Poppins-Regular", 9)
                    c.setFillColor(black)
                    c.drawString(margen_izq, y_hh, "•")
                    lineas = wrap_text(texto_habilidad, max_width_hh - 20, c, "Poppins-Regular", 9)
                    for i, linea in enumerate(lineas):
                        if i == 0:
                            c.drawString(margen_izq + 15, y_hh, linea)
                        else:
                            c.drawString(margen_izq + 25, y_hh, linea)  # Indentación para líneas adicionales
                        y_hh -= 12
                    y_hh -= 8  # espacio entre ítems
            elif isinstance(habilidad, dict):
                # Si es un diccionario, extraer el texto relevante
                texto = str(habilidad)
                c.drawString(margen_izq, y_hh, "•")
                lineas = wrap_text(texto, max_width_hh - 20, c, "Poppins-Regular", 9)
                for linea in lineas:
                    c.drawString(margen_izq + 15, y_hh, linea)
                    y_hh -= 12
                y_hh -= 8
    elif isinstance(habilidades, dict):
        # Si es un diccionario, convertirlo a string
        texto = str(habilidades)
        c.drawString(margen_izq, y_hh, "•")
        lineas = wrap_text(texto, max_width_hh - 20, c, "Poppins-Regular", 9)
        for linea in lineas:
            c.drawString(margen_izq + 15, y_hh, linea)
            y_hh -= 12
        y_hh -= 8
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
    y_educ = y_hh - 40
    c.setFont("Poppins-Bold", 9)
    c.setFillColor(black)
    c.drawString(margen_izq, y_educ, "Incluye tus estudios y proyectos destacados:")
    
    c.setFont("Poppins-Regular", 9)
    estudios = datos_cv.get('education', [])
    max_width_edu = ancho - margen_izq - margen_der  # Usamos todo el ancho disponible
    y_educ -= 20
    
    # Formatear educación de manera estructurada
    if isinstance(estudios, list):
        for estudio in estudios:
            if isinstance(estudio, dict):
                # Extraer datos del diccionario
                degree = estudio.get('degree', 'No especificado')
                institution = estudio.get('institution', 'No especificada')
                graduation_year = estudio.get('graduationYear', 'No especificado')
                
                # Formatear el título del grado
                c.setFont("Poppins-Bold", 10)
                c.setFillColor(HexColor("#007bb6"))  # Azul para el título
                lineas_degree = wrap_text(degree, max_width_edu, c, "Poppins-Bold", 10)
                for linea in lineas_degree:
                    c.drawString(margen_izq, y_educ, linea)
                    y_educ -= 14
                
                # Formatear la institución
                c.setFont("Poppins-SemiBold", 9)
                c.setFillColor(black)
                lineas_institution = wrap_text(institution, max_width_edu, c, "Poppins-SemiBold", 9)
                for linea in lineas_institution:
                    c.drawString(margen_izq, y_educ, linea)
                    y_educ -= 12
                
                # Formatear el año de graduación
                c.setFont("Poppins-Regular", 8)
                c.setFillColor(grey)
                c.drawString(margen_izq, y_educ, graduation_year)
                y_educ -= 15
                
                # Espacio entre estudios
                y_educ -= 10
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
        graduation_year = estudios.get('graduationYear', 'No especificado')
        
        c.setFont("Poppins-Bold", 10)
        c.setFillColor(HexColor("#007bb6"))
        lineas_degree = wrap_text(degree, max_width_edu, c, "Poppins-Bold", 10)
        for linea in lineas_degree:
            c.drawString(margen_izq, y_educ, linea)
            y_educ -= 14
        
        c.setFont("Poppins-SemiBold", 9)
        c.setFillColor(black)
        lineas_institution = wrap_text(institution, max_width_edu, c, "Poppins-SemiBold", 9)
        for linea in lineas_institution:
            c.drawString(margen_izq, y_educ, linea)
            y_educ -= 12
        
        c.setFont("Poppins-Regular", 8)
        c.setFillColor(grey)
        c.drawString(margen_izq, y_educ, graduation_year)
        y_educ -= 15
    else:
        # Si es otro tipo, mostrar como texto simple
        texto = str(estudios)
        lineas = wrap_text(texto, max_width_edu, c, "Poppins-Regular", 8)
        for linea in lineas:
            c.drawString(margen_izq, y_educ, linea)
            y_educ -= 12
        y_educ -= 15

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

    voluntariado = datos_cv.get('volunteering', [])
    for item in voluntariado:
        org = item.get("Organization", "No disponible") or "No disponible"
        actual = item.get("Current", "No disponible") or "No disponible"
        reco = item.get("Recommended", "No disponible") or "No disponible"

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
    # DEBUG: Logs para sección 12
    print("=== DEBUG SECCIÓN 12 ===")
    print(f"datos_cv keys disponibles: {list(datos_cv.keys())}")
    print(f"datos_cv completo: {datos_cv}")
    
    # Alturas y márgenes
    alto_degradado    = 250
    alto_rectangulo   = 300
    margen_horizontal = 30
    padding_interno   = 20
    sombra_offset     = 5
    bajar_div         = 30

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

    # Coordenadas del div blanco
    y_div     = y_inicio - alto_rectangulo + padding_interno - bajar_div
    x_div     = margen_horizontal + padding_interno
    ancho_div = ancho - 2*margen_horizontal - 2*padding_interno
    alto_div  = alto_rectangulo - 2*padding_interno - 20

    # Sombra y fondo blanco
    c.setFillColorRGB(0,0,0, alpha=0.15)
    c.roundRect(x_div + sombra_offset, y_div - sombra_offset,
                ancho_div, alto_div, radius=15, fill=1, stroke=0)
    c.setFillColor(white)
    c.roundRect(x_div, y_div, ancho_div, alto_div,
                radius=15, fill=1, stroke=0)

    # Cabeceras
    padding_top = 20
    margen_int  = 10
    y = y_div + alto_div - padding_top

    c.setFont("Poppins-SemiBold", 10)
    c.setFillColor(HexColor("#A9A9A9"))

    col1 = x_div + margen_int
    col2 = x_div + ancho_div * 0.2 + margen_int
    # Ahora col3 al 48% para acercar más
    col3 = x_div + ancho_div * 0.48 + margen_int

    # Centrar "Estado"
    cabe_est = "Estado"
    w_est = c.stringWidth(cabe_est, "Poppins-SemiBold", 10)
    x_est = col2 + (ancho_div * 0.2 - w_est)/2

    c.drawString(col1, y, "Elemento")
    c.drawString(x_est, y, cabe_est)
    c.drawString(col3, y, "Sugerencia")

    gris = HexColor("#B0B0B0")
    c.setStrokeColor(gris)
    c.setLineWidth(0.7)
    c.line(col1, y-5, x_div + ancho_div - margen_int, y-5)

    # Estilo justificado para "Sugerencia"
    estilo_sug = ParagraphStyle(
        name="SugJustificado",
        fontName="Poppins-Regular",
        fontSize=8,
        leading=10,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=0,
    )

    # Datos dinámicos
    ajuste = datos_cv.get('format_optimization', {})
    print(f"DEBUG: ajuste = {ajuste}")
    print(f"DEBUG: tipo de ajuste = {type(ajuste)}")
    
    #Mapear en español
    mapping = {
        'length':          'Longitud',
        'photo':              'Foto',
        'keywords':    'Palabras Clave',
        'impact_verbs': 'Verbos de Impacto',
    }
    green  = HexColor("#28A745")
    yellow = HexColor("#FFC107")
    red    = HexColor("#DC3545")

    data = []
    for key, label in mapping.items():
        ent = ajuste.get(key, {})
        print(f"DEBUG: clave '{key}' -> ent = {ent}")
        estado     = ent.get('state', 'N/E')
        sugerencia = ent.get('suggestion', '')
        print(f"DEBUG: estado = '{estado}', sugerencia = '{sugerencia}'")
        nivel = estado.lower()
        if nivel == 'alto':
            color = green
        elif nivel == 'medio':
            color = yellow
        elif nivel == 'bajo':
            color = red
        else:
            color = black
        data.append((label, estado, sugerencia, color))
    
    print(f"DEBUG: data final = {data}")

    # Dibujar filas
    c.setFont("Poppins-Regular", 9)
    y -= 25
    # max_w_sug es el espacio restante tras col3
    max_w_sug = x_div + ancho_div - col3 - margen_int

    print(f"DEBUG: Número de elementos a dibujar: {len(data)}")
    for i, (elem, est, sug, col) in enumerate(data):
        print(f"DEBUG: Dibujando elemento {i+1}: elem='{elem}', est='{est}', sug='{sug}'")
        # Elemento
        y_text = y
        for ln in elem.split('\n'):
            c.setFillColor(black)
            c.drawString(col1, y_text, ln)
            y_text -= 12

        # Círculo y texto de estado
        c.setFillColor(col)
        x_c = col2 + (ancho_div * 0.2 - 10)/2
        c.circle(x_c, y - 5, 5, fill=1, stroke=0)
        c.setFillColor(black)
        c.drawString(x_c + 10, y - 10, est)

        # Sugerencia justificada
        par_sug = Paragraph(sug or "", estilo_sug)
        w_sug, h_sug = par_sug.wrap(max_w_sug, alto_div)
        par_sug.drawOn(c, col3, y - h_sug + 4)

        # Preparar y de la siguiente fila
        y = min(y_text, y - h_sug) - 20
        if i < len(data) - 1:
            c.setStrokeColor(gris)
            c.setLineWidth(0.5)
            c.line(col1, y + 20, x_div + ancho_div - margen_int, y + 20)

    print("DEBUG: Sección 12 completada exitosamente")
    return alto_rectangulo +20

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