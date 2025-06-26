from fpdf import FPDF
from datetime import datetime
import os

class PDFReport(FPDF):
    def header(self):
        # Mapeo de meses en español
        meses = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        
        # Logo IPN (izquierda)
        self.image('public/ipn.png', x=10, y=8, w=30)
        
        # Logo ESCOM (derecha)
        self.image('public/escom.png', x=170, y=8, w=30)
        
        # Encabezado institucional
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Instituto Politécnico Nacional', 0, 1, 'C')
        self.cell(0, 10, 'ESCUELA SUPERIOR DE CÓMPUTO', 0, 1, 'C')
        self.ln(5)
        
        # Fecha en español
        hoy = datetime.now()
        self.set_font('Arial', '', 10)
        fecha_espanol = f"Ciudad de México a {hoy.day} de {meses[hoy.month]} de {hoy.year}"
        self.cell(0, 10, fecha_espanol, 0, 1, 'C')
        
        # Título del reporte
        self.set_font('Arial', 'B', 16)
        self.cell(0, 15, 'REPORTE DE ANÁLISIS MUSICAL', 0, 1, 'C')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

def generate_pdf_report(original_filename: str, instrument: str, frequency: float):
    pdf = PDFReport()
    pdf.add_page()
    
    # Imagen del instrumento detectado
    instrument_image = f'public/{instrument.lower()}.png'
    if os.path.exists(instrument_image):
        pdf.image(instrument_image, x=150, y=60, w=50)
    
    # Información del análisis
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Archivo analizado: {original_filename}', 0, 1)
    pdf.cell(0, 10, f'Instrumento detectado: {instrument.capitalize()}', 0, 1)
    pdf.cell(0, 10, f'Frecuencia fundamental: {frequency:.2f} Hz', 0, 1)  # Mostramos frecuencia
    pdf.ln(15)
    
    # Datos técnicos
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'Sistema de análisis desarrollado por Torres Abonce Luis Miguel', 0, 1, 'C')
    
    # Guardar PDF
    output_dir = 'pdf_reports'
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'reporte_{original_filename}.pdf')
    pdf.output(pdf_path)
    
    return pdf_path