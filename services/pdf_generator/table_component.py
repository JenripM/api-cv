from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.utils import ImageReader


class EvaluationTable:
    """
    Componente reutilizable para tablas de evaluación con estado y sugerencias.
    Usado en secciones como "Ajuste al puesto" y "Formato y optimización".
    """
    
    def __init__(self, canvas, width, height, y_start, data, config=None):
        """
        Inicializa el componente de tabla de evaluación.
        
        Args:
            canvas: Canvas de ReportLab
            width: Ancho total disponible
            height: Alto total disponible
            y_start: Posición Y inicial
            data: Lista de tuplas (elemento, estado, sugerencia, color_estado)
            config: Configuración opcional del componente
        """
        self.c = canvas
        self.width = width
        self.height = height
        self.y_start = y_start
        self.data = data
        
        # Configuración por defecto
        self.config = {
            'title': 'Evaluación',
            'show_background': True,
            'background_image': None,
            'background_color': None,
            'container_style': {
                'margin_horizontal': 30,
                'padding_internal': 20,
                'shadow_offset': 5,
                'border_radius': 15,
                'shadow_alpha': 0.15
            },
            'header_style': {
                'font_family': 'Poppins-SemiBold',
                'font_size': 10,
                'color': HexColor("#A9A9A9"),
                'line_color': HexColor("#B0B0B0"),
                'line_width': 0.7
            },
            'column_config': {
                'element_width': 0.2,      # 20% del ancho
                'status_width': 0.2,       # 20% del ancho
                'suggestion_width': 0.6    # 60% del ancho
            },
            'row_style': {
                'font_family': 'Poppins-Regular',
                'font_size': 9,
                'line_height': 12,
                'status_circle_radius': 5,
                'status_text_offset': 10,
                'row_spacing': 20,
                'separator_line_width': 0.5
            },
            'suggestion_style': {
                'font_family': 'Poppins-Regular',
                'font_size': 8,
                'leading': 10,
                'alignment': TA_JUSTIFY
            }
        }
        
        # Actualizar configuración con valores personalizados
        if config:
            self._update_config(config)
    
    def _update_config(self, custom_config):
        """Actualiza la configuración con valores personalizados."""
        for key, value in custom_config.items():
            if key in self.config:
                if isinstance(value, dict) and isinstance(self.config[key], dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value
    
    def _calculate_dimensions(self):
        """Calcula las dimensiones del contenedor y columnas."""
        container = self.config['container_style']
        
        # Dimensiones del contenedor
        self.container_width = self.width - 2 * container['margin_horizontal'] - 2 * container['padding_internal']
        self.container_x = container['margin_horizontal'] + container['padding_internal']
        
        # Calcular altura dinámica basada en el contenido
        self.container_height = self._calculate_content_height()
        self.container_y = self.y_start - self.container_height + container['padding_internal']
        
        # Posiciones de las columnas
        col_config = self.config['column_config']
        self.col1_x = self.container_x + 10  # Margen interno
        self.col2_x = self.container_x + self.container_width * col_config['element_width']
        self.col3_x = self.container_x + self.container_width * (col_config['element_width'] + col_config['status_width'])
        
        # Anchos de las columnas
        self.col1_width = self.container_width * col_config['element_width'] - 10
        self.col2_width = self.container_width * col_config['status_width'] - 10
        self.col3_width = self.container_width * col_config['suggestion_width'] - 10
    
    def _calculate_content_height(self):
        """Calcula la altura necesaria para el contenido."""
        # Altura base para título y cabecera
        base_height = 60  # Título + cabecera + línea + padding
        
        # Altura para las filas de datos
        row_height = 0
        for item in self.data:
            element, status, suggestion, color = item
            
            # Altura del elemento (puede tener múltiples líneas)
            element_lines = element.split('\n')
            element_height = len(element_lines) * self.config['row_style']['line_height']
            
            # Altura de la sugerencia (usando Paragraph para calcular)
            temp_style = ParagraphStyle(
                name="TempSuggestion",
                fontName=self.config['suggestion_style']['font_family'],
                fontSize=self.config['suggestion_style']['font_size'],
                leading=self.config['suggestion_style']['leading'],
                alignment=self.config['suggestion_style']['alignment']
            )
            
            par_suggestion = Paragraph(suggestion or "", temp_style)
            suggestion_width = self.width * self.config['column_config']['suggestion_width'] - 20
            w_sug, h_sug = par_suggestion.wrap(suggestion_width, 1000)
            
            # Altura máxima de la fila
            row_height += max(element_height, h_sug) + self.config['row_style']['row_spacing']
        
        return max(200, base_height + row_height + 40)  # Altura mínima de 200
    
    def _draw_background(self):
        """Dibuja el fondo del contenedor."""
        container = self.config['container_style']
        
        # Fondo con imagen si está configurado
        if self.config['show_background'] and self.config['background_image']:
            imagen_fondo = ImageReader(self.config['background_image'])
            self.c.drawImage(imagen_fondo, 0, self.y_start - self.container_height, 
                           width=self.width, height=self.container_height)
        
        # Sombra
        self.c.setFillColorRGB(0, 0, 0, alpha=container['shadow_alpha'])
        self.c.roundRect(
            self.container_x + container['shadow_offset'],
            self.container_y - container['shadow_offset'],
            self.container_width,
            self.container_height,
            radius=container['border_radius'],
            fill=1, stroke=0
        )
        
        # Contenedor principal
        if self.config['background_color']:
            self.c.setFillColor(self.config['background_color'])
        else:
            self.c.setFillColor(Color(1, 1, 1))  # Blanco
        
        self.c.roundRect(
            self.container_x,
            self.container_y,
            self.container_width,
            self.container_height,
            radius=container['border_radius'],
            fill=1, stroke=0
        )
    
    def _draw_header(self):
        """Dibuja la cabecera de la tabla."""
        header_style = self.config['header_style']
        
        # Posición de la cabecera
        y_header = self.container_y + self.container_height - 20
        
        # Configurar estilo
        self.c.setFont(header_style['font_family'], header_style['font_size'])
        self.c.setFillColor(header_style['color'])
        
        # Dibujar títulos de columnas
        self.c.drawString(self.col1_x, y_header, "Elemento")
        
        # Centrar "Estado" en su columna
        status_text = "Estado"
        status_width = self.c.stringWidth(status_text, header_style['font_family'], header_style['font_size'])
        status_x = self.col2_x + (self.col2_width - status_width) / 2
        self.c.drawString(status_x, y_header, status_text)
        
        self.c.drawString(self.col3_x, y_header, "Sugerencia")
        
        # Línea separadora
        self.c.setStrokeColor(header_style['line_color'])
        self.c.setLineWidth(header_style['line_width'])
        self.c.line(self.col1_x, y_header - 5, 
                   self.container_x + self.container_width - 10, y_header - 5)
        
        return y_header - 25  # Retorna la posición Y para la primera fila
    
    def _draw_rows(self, y_start):
        """Dibuja las filas de datos."""
        row_style = self.config['row_style']
        suggestion_style = self.config['suggestion_style']
        
        # Configurar estilo de filas
        self.c.setFont(row_style['font_family'], row_style['font_size'])
        
        # Crear estilo para sugerencias
        par_style = ParagraphStyle(
            name="SuggestionStyle",
            fontName=suggestion_style['font_family'],
            fontSize=suggestion_style['font_size'],
            leading=suggestion_style['leading'],
            alignment=suggestion_style['alignment'],
            spaceBefore=0,
            spaceAfter=0
        )
        
        y_current = y_start
        
        for i, (element, status, suggestion, color) in enumerate(self.data):
            # Dibujar elemento
            y_element = y_current
            self.c.setFillColor(Color(0, 0, 0))  # Negro
            
            for line in element.split('\n'):
                self.c.drawString(self.col1_x, y_element, line)
                y_element -= row_style['line_height']
            
            # Dibujar círculo de estado
            self.c.setFillColor(color)
            circle_x = self.col2_x + (self.col2_width - 10) / 2
            self.c.circle(circle_x, y_current - 5, row_style['status_circle_radius'], fill=1, stroke=0)
            
            # Dibujar texto de estado
            self.c.setFillColor(Color(0, 0, 0))  # Negro
            self.c.drawString(circle_x + row_style['status_text_offset'], 
                            y_current - 10, str(status))
            
            # Dibujar sugerencia
            par_suggestion = Paragraph(suggestion or "", par_style)
            w_sug, h_sug = par_suggestion.wrap(self.col3_width, self.container_height)
            par_suggestion.drawOn(self.c, self.col3_x, y_current - h_sug + 4)
            
            # Calcular posición para la siguiente fila
            next_y = min(y_element, y_current - h_sug) - row_style['row_spacing']
            
            # Línea separadora (excepto para la última fila)
            if i < len(self.data) - 1:
                self.c.setStrokeColor(self.config['header_style']['line_color'])
                self.c.setLineWidth(row_style['separator_line_width'])
                self.c.line(self.col1_x, next_y + row_style['row_spacing'], 
                           self.container_x + self.container_width - 10, next_y + row_style['row_spacing'])
            
            y_current = next_y
        
        return y_current
    
    def render(self):
        """
        Renderiza la tabla completa.
        
        Returns:
            float: Altura total ocupada por la tabla
        """
        # Calcular dimensiones
        self._calculate_dimensions()
        
        # Dibujar fondo
        self._draw_background()
        
        # Dibujar cabecera
        y_first_row = self._draw_header()
        
        # Dibujar filas
        self._draw_rows(y_first_row)
        
        return self.container_height


def create_evaluation_table(canvas, width, height, y_start, data, title=None, 
                          background_image=None, custom_config=None, title_spacing=0):
    """
    Función helper para crear una tabla de evaluación.
    
    Args:
        canvas: Canvas de ReportLab
        width: Ancho total disponible
        height: Alto total disponible
        y_start: Posición Y inicial
        data: Lista de tuplas (elemento, estado, sugerencia, color_estado)
        title: Título opcional de la sección
        background_image: Ruta opcional a imagen de fondo
        custom_config: Configuración personalizada opcional
        title_spacing: Espacio adicional para el título (en puntos)
    
    Returns:
        float: Altura total ocupada
    """
    # Configuración base
    config = {
        'title': title,
        'background_image': background_image,
        'show_background': bool(background_image)
    }
    
    # Actualizar con configuración personalizada
    if custom_config:
        config.update(custom_config)
    
    # Ajustar posición Y para respetar el espaciado del título
    adjusted_y_start = y_start - title_spacing
    
    # Crear y renderizar tabla
    table = EvaluationTable(canvas, width, height, adjusted_y_start, data, config)
    return table.render()
