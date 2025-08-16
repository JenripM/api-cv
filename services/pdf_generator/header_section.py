from reportlab.lib.colors import black

def seccion_encabezado(c, ancho, alto, logo_path):
    """1. Encabezado con logo y título"""
    logo_width = 120
    logo_height = 26
    c.drawImage(logo_path, 20, alto - 35, width=logo_width, height=logo_height, mask='auto')

    texto = "Informe de revisión de CV"
    c.setFont("Poppins-Bold", 14)
    texto_ancho = c.stringWidth(texto, "Poppins-Bold", 14)
    x_texto = ancho - 25 - texto_ancho
    y_texto = alto - 27
    c.drawString(x_texto, y_texto, texto)
