"""
Carga dinámica de plantillas de reportes holísticos desde archivos JSON en assets/report_templates/.
Permite al usuario editar los textos de cada rayo en cualquier momento.
"""

import os
import json
import logging

TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "assets", "report_templates"))

COLOR_FILE_MAP = {
    "Rosa": "rosa.json",
    "Verde": "verde.json",
    "Rojo": "rojo.json",
    "Marrón": "marron.json",
    "Amarillo": "amarillo.json",
    "Violeta": "violeta.json",
    "Azul": "azul.json"
}

BIORHYTHM_TEMPLATE = {
    "analisis_general": (
        "Estimado/a {name}, la evaluación de tu Biorritmo revela la dinámica activa de tus cuatro cuerpos energéticos principales:\n\n"
        "- Físico ({fisico}%): Representa tu fuerza vital, resistencia corporal y energía motriz.\n"
        "- Emocional ({emocional}%): Marca la sensibilidad, el estado de ánimo y la receptividad afectiva.\n"
        "- Intelectual ({intelectual}%): Indica la lucidez mental, concentración y agilidad para resolver problemas.\n"
        "- Espiritual ({espiritual}%): Refleja tu conexión con la intuición, el propósito del alma y la armonía cósmica.\n\n"
        "La combinación de estos porcentajes demuestra cómo tus ciclos biológicos y energéticos se entrelazan en esta etapa de tu vida."
    ),
    "consejo_practico": (
        "Para mantener el equilibrio en tu rutina diaria, {name}:\n"
        "- Si tu ciclo Físico o Emocional se encuentra bajo, prioriza el descanso reparador y la alimentación consciente.\n"
        "- Aprovecha los picos altos en tu indicador Intelectual y Espiritual para tomar decisiones estratégicas, meditar e iniciar proyectos creativos.\n"
        "- Realiza pausas de respiración consciente cada 3 horas para recargar el Prana en tus centros sutiles."
    ),
    "terapia_recomendada": (
        "En nuestro Centro Holístico KUMEN te recomendamos una sesión combinada de Alineación de Chakras y Armonización Sonora con cuencos tibetanos.\n\n"
        "Esta terapia recalibra tus cuatro campos y sincroniza tus biorritmos individuales con las frecuencias armónicas de la naturaleza."
    )
}

def get_aura_template(color_name: str, client_name: str) -> dict:
    name = client_name.strip() if client_name and client_name.strip() else "Consultante"
    filename = COLOR_FILE_MAP.get(color_name, "azul.json")
    filepath = os.path.join(TEMPLATES_DIR, filename)
    
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"Error leyendo plantilla {filepath}: {e}")

    # Fallback si no se pudo cargar
    if not data:
        data = {
            "ui_text": f"Color {color_name} detectado en tu campo áurico.",
            "analisis_aurico": f"Hola {name}, tu lectura áurica muestra una vibración {color_name}.",
            "explicacion_metafisica": f"Desde la metafísica, el rayo {color_name} alinea tus centros sutiles.",
            "maestros_elementales": "Los guías espirituales y seres de luz acompañan tu camino.",
            "terapia_recomendada": "Te recomendamos una sesión de armonización en KUMEN."
        }

    return {
        "analisis_aurico": data.get("analisis_aurico", "").format(name=name),
        "explicacion_metafisica": data.get("explicacion_metafisica", "").format(name=name),
        "maestros_elementales": data.get("maestros_elementales", "").format(name=name),
        "terapia_recomendada": data.get("terapia_recomendada", "").format(name=name),
        "ui_text": data.get("ui_text", "").format(name=name)
    }

def get_biorhythm_template(client_name: str, fisico: int, emocional: int, intelectual: int, espiritual: int) -> dict:
    name = client_name.strip() if client_name and client_name.strip() else "Consultante"
    return {
        "analisis_general": BIORHYTHM_TEMPLATE["analisis_general"].format(
            name=name, fisico=fisico, emocional=emocional, intelectual=intelectual, espiritual=espiritual
        ),
        "consejo_practico": BIORHYTHM_TEMPLATE["consejo_practico"].format(name=name),
        "terapia_recomendada": BIORHYTHM_TEMPLATE["terapia_recomendada"].format(name=name)
    }
