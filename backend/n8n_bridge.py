import logging
import math
import random
from datetime import datetime
from backend.templates import get_aura_template, get_biorhythm_template
from backend.pdf_generator import create_aura_pdf, create_biorhythm_pdf
from backend.excel_logger import log_scan_to_excel

# Map to color names
color_names = {
    "#ec4899": "Rosa",
    "#34d399": "Verde",
    "#ef4444": "Rojo",
    "#451a03": "Marrón",
    "#fef08a": "Amarillo",
    "#a855f7": "Violeta",
    "#3b82f6": "Azul"
}

SAHUMERIO_OPTIONS = [
    {
        "name": "Sahumerio 7 Arcángeles",
        "type": "Edición Holística Especial",
        "image": "assets/sh_7ArcangelesFrente - Editado.png"
    },
    {
        "name": "Sahumerio 7 Chakras",
        "type": "Alineación y Purificación",
        "image": "assets/sh_7chacrasFrente - Editado.png"
    },
    {
        "name": "Sahumerio 7 Rayos",
        "type": "Transmutación Energética",
        "image": "assets/sh_7rayosF - Editado.png"
    }
]

def get_aura_recommendations(name: str, phone_number: str, email: str, color_hex: str, image_b64: str, session_id: str):
    try:
        color_name = color_names.get(color_hex, "Azul")
        
        # Obtener informe predefinido offline
        ai_data = get_aura_template(color_name, name)
        ui_analysis = ai_data.get("ui_text", "")

        # Generar PDF localmente
        pdf_filename = create_aura_pdf(name, phone_number, email, image_b64, ai_data, session_id)

        # Seleccionar 1 sahumerio al azar de los 3 disponibles en assets
        selected_sahumerio = random.choice(SAHUMERIO_OPTIONS)

        # Registrar en Excel automáticamente
        log_scan_to_excel(
            servicio="Escáner de Aura",
            nombre=name,
            telefono=phone_number,
            email=email,
            resultado=f"Aura {color_name} ({color_hex})",
            pdf_filename=pdf_filename
        )

        return {
            "success": True,
            "analysis": ui_analysis,
            "pdf_filename": pdf_filename,
            "recommended_products": [selected_sahumerio],
            "phone_target": phone_number
        }
    except Exception as e:
        logging.error(f"Error en recomendación Aura: {e}")
        return {"success": False, "error": str(e)}

def get_biorhythm_analysis(name: str, phone_number: str, email: str, birthdate_str: str, period: str, image_b64: str, session_id: str):
    try:
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
        today = datetime.now()
        
        def calc_day(dias_vividos, p):
            return ((math.sin(2 * math.pi * dias_vividos / p) + 1) / 2) * 100

        # Para el cálculo del día actual
        dias_totales = (today - birthdate).days
        fisico = int(calc_day(dias_totales, 23))
        emocional = int(calc_day(dias_totales, 28))
        intelectual = int(calc_day(dias_totales, 33))
        espiritual = int(calc_day(dias_totales, 53))
        
        ai_data = get_biorhythm_template(name, fisico, emocional, intelectual, espiritual)
        
        pdf_filename = create_biorhythm_pdf(name, phone_number, email, image_b64, ai_data, session_id, birthdate_str)
            
        selected_sahumerio = random.choice(SAHUMERIO_OPTIONS)

        # Registrar en Excel automáticamente
        log_scan_to_excel(
            servicio="Biorritmo Vital",
            nombre=name,
            telefono=phone_number,
            email=email,
            resultado=f"Físico {fisico}% | Emocional {emocional}% | Intelectual {intelectual}% | Espiritual {espiritual}%",
            pdf_filename=pdf_filename
        )

        return {
            "success": True,
            "fisico": fisico,
            "emocional": emocional,
            "intelectual": intelectual,
            "espiritual": espiritual,
            "frase": f"Tu energía del día: Físico {fisico}%, Emocional {emocional}%, Intelectual {intelectual}%, Espiritual {espiritual}%.",
            "pdf_filename": pdf_filename,
            "recommended_products": [selected_sahumerio],
            "phone_target": phone_number
        }
    except Exception as e:
        logging.error(f"Error biorritmo: {e}")
        return {"success": False, "error": str(e)}
