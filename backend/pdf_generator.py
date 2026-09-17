import os
import uuid
import base64
from io import BytesIO
from PIL import Image
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "assets"))
os.makedirs(REPORTS_DIR, exist_ok=True)

class HolisticPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 11)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, 'KUMEN - Centro de Energía Holística', align='C')
        self.ln(12)

    def footer(self):
        self.set_y(-22)
        self.set_font('helvetica', 'I', 9)
        self.set_text_color(140, 140, 140)
        self.cell(0, 8, 'Contacto: +54 9 11 2272-9393 | Instagram: @KumenHolistico', align='C')
        self.ln(4)
        self.cell(0, 8, f'Página {self.page_no()}', align='C')

    def add_title_page(self, title, subtitle, client_name="", phone="", email=""):
        self.add_page()
        self.set_y(90)
        self.set_font('helvetica', 'B', 24)
        self.set_text_color(30, 30, 30)
        self.cell(0, 15, title, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('helvetica', 'I', 15)
        self.set_text_color(120, 80, 200)
        self.cell(0, 10, subtitle, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(15)
        
        if client_name:
            self.set_font('helvetica', 'B', 14)
            self.set_text_color(80, 80, 80)
            self.cell(0, 10, f'Consultante: {client_name}', align='C', new_x="LMARGIN", new_y="NEXT")
        if phone:
            self.set_font('helvetica', '', 11)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, f'Teléfono: {phone}', align='C', new_x="LMARGIN", new_y="NEXT")
            
        self.set_font('helvetica', '', 11)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f'Fecha de Emisión: {datetime.now().strftime("%d/%m/%Y")}', align='C')

def decode_image(b64_string):
    if b64_string.startswith('data:image'):
        b64_string = b64_string.split(',')[1]
    img_data = base64.b64decode(b64_string)
    img = Image.open(BytesIO(img_data))
    
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        bg = Image.new('RGB', img.size, (0, 0, 0))
        bg.paste(img, mask=img.split()[3])
        img = bg
    
    temp_path = os.path.join(REPORTS_DIR, f"temp_{uuid.uuid4().hex}.jpg")
    img.convert('RGB').save(temp_path, "JPEG", quality=90)
    return temp_path

def add_commercial_closing_page(pdf: FPDF):
    """Página de cierre comercial vistosa con terapias en Valentín Alsina"""
    pdf.add_page()
    
    zen_banner = os.path.join(ASSETS_DIR, "zen_banner.png")
    if os.path.exists(zen_banner):
        pdf.image(zen_banner, x=15, y=18, w=180, h=52)
        pdf.set_y(76)
    else:
        pdf.set_y(30)
        
    pdf.set_font('helvetica', 'B', 13)
    pdf.set_text_color(109, 40, 217)
    pdf.cell(0, 8, 'Veni a realizar estas terapias y otras a nuestro local de Valentin Alsina', align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 7, 'Alli podras conocer mas sobre:', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    therapies = [
        "Reiki",
        "Yoga",
        "Masajes Energeticos",
        "Ritos y sanaciones ancestrales",
        "BioDecodificacion",
        "Constelaciones Familiares",
        "Lectura de Registros Akashicos",
        "Sesiones de meditacion y liberacion almica",
        "Protocolo de Observacion Cuantica",
        "Tarot Angelico"
    ]
    
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(67, 56, 202)
    
    for t in therapies:
        pdf.cell(42)
        pdf.cell(0, 6, f"-  {t}", new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(6)
    
    pdf.set_fill_color(245, 243, 255)
    pdf.set_draw_color(167, 139, 250)
    pdf.rect(x=20, y=240, w=170, h=22, style='DF')
    
    pdf.set_y(242)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(109, 40, 217)
    pdf.cell(0, 6, 'Valentin Alsina, Lanus | WhatsApp / Turnos: +54 9 11 2272-9393', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', 'I', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, 'Instagram: @KumenHolistico', align='C')

def create_aura_pdf(name: str, phone_number: str, email: str, b64_image: str, ai_data: dict, session_id: str) -> str:
    pdf = HolisticPDF()
    
    # PÁGINA 1: Portada
    pdf.add_title_page("REPORTE DE CAMPO ÁURICO", "Análisis y Sanación Cuántica", client_name=name, phone=phone_number, email=email)
    
    img_path = ""
    if b64_image:
        try:
            img_path = decode_image(b64_image)
        except Exception as e:
            print(f"Error decoding image: {e}")

    # PÁGINA 2: Fotografía a la izquierda, título y primer texto a la derecha, continuación debajo
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 15)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, f'Fotografía Áurica de {name or "Consultante"}', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    full_text = ai_data.get("analisis_aurico", "")
    paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
    
    if img_path:
        with Image.open(img_path) as img:
            iw, ih = img.size
            pdf_img_h = 75 * (ih / iw)
            
        # 1. Foto a la izquierda: x=15, y=30, ancho=75mm
        pdf.image(img_path, x=15, y=30, w=75)
        
        # 2. Título y primer párrafo a la derecha: x=95, y=30, ancho=100mm
        pdf.set_xy(95, 30)
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(109, 40, 217)
        pdf.cell(100, 7, 'Interpretación Emocional', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_x(95)
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(30, 30, 30)
        
        first_para = paragraphs[0] if len(paragraphs) > 0 else full_text
        pdf.multi_cell(100, 5.2, first_para, new_x="LMARGIN", new_y="NEXT")
        
        # 3. Continuación debajo de la foto a ancho completo
        safe_y = max(30 + pdf_img_h + 5, pdf.get_y() + 4)
        if safe_y > 270: # Si se pasa del límite, salto de página
            pdf.add_page()
            safe_y = 30
        pdf.set_xy(15, safe_y)
        pdf.set_font('helvetica', '', 10)
        
        remaining_paras = paragraphs[1:] if len(paragraphs) > 1 else []
        for p in remaining_paras:
            pdf.multi_cell(0, 5.5, p, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
    else:
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(109, 40, 217)
        pdf.cell(0, 8, 'Interpretación Emocional', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(30, 30, 30)
        for p in paragraphs:
            pdf.multi_cell(0, 5.5, p, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

    # PÁGINA 3: Metafísica
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(124, 58, 237)
    pdf.cell(0, 10, 'Explicación desde la Metafísica Cuántica', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 7, ai_data.get("explicacion_metafisica", ""), new_x="LMARGIN", new_y="NEXT")

    # PÁGINA 4: Maestros y Elementales
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(124, 58, 237)
    pdf.cell(0, 10, 'Maestros, Arcángeles y Elementales Guías', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 7, ai_data.get("maestros_elementales", ""), new_x="LMARGIN", new_y="NEXT")

    # PÁGINA 5: Terapia Recomendada
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(124, 58, 237)
    pdf.cell(0, 10, 'Sugerencia de Terapias Holísticas (KUMEN)', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 7, ai_data.get("terapia_recomendada", ""), new_x="LMARGIN", new_y="NEXT")

    # PÁGINA 6: Cierre Comercial Vistoso
    add_commercial_closing_page(pdf)
    
    if img_path and os.path.exists(img_path):
        os.remove(img_path)
        
    filename = f"{phone_number or 'aura'}_{session_id}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    pdf.output(filepath)
    return filename

def generate_biorhythm_chart(birthdate_str: str, period: str) -> str:
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.now()
    
    if period == 'weekly':
        days = 7
        title = "Proyección Semanal (Próximos 7 días)"
        labels = [(today + timedelta(days=i)).strftime("%a %d") for i in range(days)]
    else:
        days = 30
        title = "Proyección Mensual (Próximos 30 días)"
        step = 5
        days_indices = list(range(0, 30, step))
        labels = [(today + timedelta(days=i)).strftime("%d/%m") for i in days_indices]

    def calc_day(dias_vividos, p):
        return ((math.sin(2 * math.pi * dias_vividos / p) + 1) / 2) * 100

    fis = []; emo = []; intel = []; esp = []
    indices = range(7) if period == 'weekly' else list(range(0, 30, 5))
    
    for idx in indices:
        dias_totales = (today - birthdate).days + idx
        fis.append(calc_day(dias_totales, 23))
        emo.append(calc_day(dias_totales, 28))
        intel.append(calc_day(dias_totales, 33))
        esp.append(calc_day(dias_totales, 53))
            
    fig, ax = plt.subplots(figsize=(8, 3.2))
    x = range(len(labels))
    width = 0.2
    
    ax.bar([pos - width*1.5 for pos in x], fis, width, label='Físico (Rojo)', color='#ef4444')
    ax.bar([pos - width*0.5 for pos in x], emo, width, label='Emocional (Verde)', color='#34d399')
    ax.bar([pos + width*0.5 for pos in x], intel, width, label='Intelectual (Amarillo)', color='#eab308')
    ax.bar([pos + width*1.5 for pos in x], esp, width, label='Espiritual (Violeta)', color='#a855f7')
    
    ax.set_ylabel('Energía (%)')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 110)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    chart_path = os.path.join(REPORTS_DIR, f"chart_{period}_{uuid.uuid4().hex}.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()
    return chart_path

def create_biorhythm_pdf(name: str, phone_number: str, email: str, b64_image: str, ai_data: dict, session_id: str, birthdate: str) -> str:
    pdf = HolisticPDF()
    
    # PÁGINA 1: Portada
    pdf.add_title_page("REPORTE DE BIORRITMO VITAL", "Ciclos Energéticos y Proyección Temporal", client_name=name, phone=phone_number, email=email)
    
    img_path = ""
    if b64_image:
        try: img_path = decode_image(b64_image)
        except: pass
        
    # PÁGINA 2: Fotografía a la izquierda, título y primer texto a la derecha, continuación debajo
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 15)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, f'Captura de Frecuencia Vital - {name or "Consultante"}', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    full_text = ai_data.get("analisis_general", "")
    paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
    
    if img_path:
        with Image.open(img_path) as img:
            iw, ih = img.size
            pdf_img_h = 75 * (ih / iw)
            
        # 1. Foto a la izquierda: x=15, y=30, ancho=75mm
        pdf.image(img_path, x=15, y=30, w=75)
        
        # 2. Título y primer texto a la derecha: x=95, y=30, ancho=100mm
        pdf.set_xy(95, 30)
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(109, 40, 217)
        pdf.cell(100, 7, 'Diagnóstico de Campos Energéticos:', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_x(95)
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(30, 30, 30)
        
        first_para = paragraphs[0] if len(paragraphs) > 0 else full_text
        pdf.multi_cell(100, 5.2, first_para, new_x="LMARGIN", new_y="NEXT")
        
        # 3. Continuación debajo de la foto a ancho completo
        safe_y = max(30 + pdf_img_h + 5, pdf.get_y() + 4)
        if safe_y > 270:
            pdf.add_page()
            safe_y = 30
        pdf.set_xy(15, safe_y)
        pdf.set_font('helvetica', '', 10)
        
        remaining_paras = paragraphs[1:] if len(paragraphs) > 1 else []
        for p in remaining_paras:
            pdf.multi_cell(0, 5.5, p, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
    else:
        pdf.set_font('helvetica', 'B', 13)
        pdf.set_text_color(109, 40, 217)
        pdf.cell(0, 8, 'Diagnóstico de Campos Energéticos:', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10)
        pdf.set_text_color(30, 30, 30)
        for p in paragraphs:
            pdf.multi_cell(0, 5.5, p, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

    # PÁGINA 3: Gráficos de Proyección Semanal y Mensual
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(124, 58, 237)
    pdf.cell(0, 10, 'Proyecciones Temporales de Biorritmo', new_x="LMARGIN", new_y="NEXT")
    
    weekly_chart = generate_biorhythm_chart(birthdate, 'weekly')
    monthly_chart = generate_biorhythm_chart(birthdate, 'monthly')
    
    pdf.image(weekly_chart, x=15, y=30, w=180)
    pdf.image(monthly_chart, x=15, y=140, w=180)
    
    # PÁGINA 4: Consejos y Terapias
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(124, 58, 237)
    pdf.cell(0, 10, 'Recomendaciones Prácticas y Holísticas', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, 'Consejos para el Día a Día:', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 6, ai_data.get("consejo_practico", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, 'Terapia Sugerida (KUMEN):', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 6, ai_data.get("terapia_recomendada", ""), new_x="LMARGIN", new_y="NEXT")
    
    # PÁGINA 5: Cierre Comercial Vistoso con Terapias en Valentín Alsina
    add_commercial_closing_page(pdf)
    
    if img_path and os.path.exists(img_path): os.remove(img_path)
    if weekly_chart and os.path.exists(weekly_chart): os.remove(weekly_chart)
    if monthly_chart and os.path.exists(monthly_chart): os.remove(monthly_chart)
        
    filename = f"{phone_number or 'biorhythm'}_{session_id}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    pdf.output(filepath)
    return filename
