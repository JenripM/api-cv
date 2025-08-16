import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from .header_section import seccion_encabezado
from .main_analysis_section import seccion_2
from .basic_metrics_section import seccion_3
from .remaining_sections import seccion_4, seccion_5, seccion_6, seccion_7, seccion_8, seccion_9, seccion_10, seccion_11, seccion_12, seccion_13
from .pdf_utils import descargar_imagen
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

# Ruta donde se guardarán los PDFs generados
CARPETA_PDFS = "output/analisis_pdfs/"

# Verificar si la carpeta existe, si no, crearla
if not os.path.exists(CARPETA_PDFS):
    os.makedirs(CARPETA_PDFS)

def generar_pdf_con_secciones(datos_cv, nombre_archivo, logo_path, ruta_logo2):
    """
    Genera el PDF completo ensamblando todas las secciones
    """
    try:
        ancho = 8.5 * inch
        alto = 60 * inch  # Tamaño carta

        c = canvas.Canvas(CARPETA_PDFS + nombre_archivo, pagesize=(ancho, alto))

        # Encabezado con la información básica
        try:
            seccion_encabezado(c, ancho, alto, logo_path)
        except Exception as e:
            print(f"Error al renderizar sección encabezado: {e}")
            raise e
        
        y_actual = alto - 80

        y_actual = alto - 40  
        espacio_entre_secciones = 20

        # Generar todas las secciones en orden
        try:
            altura = seccion_2(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 2 (análisis principal): {e}")
            raise e

        try:
            altura = seccion_3(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 3 (métricas básicas): {e}")
            raise e

        try:
            altura = seccion_4(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 4: {e}")
            raise e

        try:
            altura = seccion_5(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 5: {e}")
            raise e

        try:
            altura = seccion_6(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 6: {e}")
            raise e

        try:
            altura = seccion_7(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 7: {e}")
            raise e

        try:
            altura = seccion_8(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 8: {e}")
            raise e
        
        try:
            altura = seccion_9(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 9: {e}")
            raise e
        
        try:
            altura = seccion_10(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 10: {e}")
            raise e

        try:
            altura = seccion_11(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 11: {e}")
            raise e

        try:
            altura = seccion_12(c, ancho, alto, y_actual, datos_cv)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 12: {e}")
            raise e

        try:
            altura = seccion_13(c, ancho, alto, y_actual, logo_path)
            y_actual -= altura + espacio_entre_secciones
        except Exception as e:
            print(f"Error al renderizar sección 13: {e}")
            raise e

        # Guardar el PDF
        try:
            c.save()
        except Exception as e:
            print(f"Error al guardar PDF: {e}")
            raise e
            
        return f"/static/analisis_pdfs/{nombre_archivo}"
        
    except Exception as e:
        print(f"Error general en generar_pdf_con_secciones: {e}")
        raise e
