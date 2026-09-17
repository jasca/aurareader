import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Configuración de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.5-flash",
  generation_config=generation_config,
)

def generate_aura_report(color_name: str) -> dict:
    prompt = f"""
    Eres un Maestro Holístico, Sanador Cuántico y Guía Espiritual con más de 20 años de experiencia.
    Un paciente acaba de realizarse un profundo escaneo de su campo áurico en tu centro holístico, y el color dominante detectado es: {color_name}.
    Necesito que generes un informe extenso, muy detallado, empático y profundamente sanador. 
    ESTRICTAMENTE devuelve un objeto JSON válido con las siguientes 4 claves. Cada valor debe contener MÍNIMO 120 palabras y estar redactado en múltiples párrafos:
    {{
        "analisis_aurico": "Explicación profunda de qué significa este color a nivel de campo áurico, estado emocional actual y vibración energética. (Mínimo 120 palabras)",
        "explicacion_metafisica": "Análisis metafísico avanzado, detallando la conexión cósmica, los chakras involucrados y el flujo de energía vital (prana o chi). (Mínimo 120 palabras)",
        "maestros_elementales": "Desarrollo sobre los guías espirituales, Maestros Ascendidos, Arcángeles o seres de luz que custodian este rayo/frecuencia, y consejos para invocarlos. (Mínimo 120 palabras)",
        "terapia_recomendada": "Recomendaciones específicas y justificadas de terapias holísticas (ej. Sahumos con hierbas específicas, sesiones de Reiki, meditación guiada, gemoterapia) que ayudarán a la persona a transmutar o potenciar esta energía. (Mínimo 120 palabras)"
    }}
    Redacta en segunda persona, con un tono místico, cálido, contenedor y altamente profesional. No uses formato markdown alrededor del JSON, devuelve el raw JSON object.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error generando reporte de Aura con LLM: {e}")
        return {
            "analisis_aurico": f"Tu aura muestra una energía predominante {color_name}. Esto indica una etapa de transformación.",
            "explicacion_metafisica": "Desde la metafísica, tu campo áurico está recibiendo influencias de cambios profundos.",
            "maestros_elementales": "Los guías espirituales asociados a esta frecuencia están acompañándote.",
            "terapia_recomendada": "Te recomendamos una sesión de Reiki o Sahumo de limpieza profunda en nuestro centro."
        }

def generate_biorhythm_report(fisico: int, emocional: int, intelectual: int, espiritual: int, periodo: str) -> dict:
    prompt = f"""
    Eres un Maestro Holístico y experto en lectura de Biorritmos y ciclos vitales cósmicos.
    Un paciente ha completado su análisis de Biorritmo para el periodo: {periodo} (que indica si la proyección es para hoy, la semana o el mes).
    Sus niveles actuales de energía son: Físico {fisico}%, Emocional {emocional}%, Intelectual {intelectual}%, Espiritual {espiritual}%.
    Necesito que generes un informe de diagnóstico extenso y empático en un JSON válido con estas 3 claves (mínimo 100 palabras por clave):
    {{
        "analisis_general": "Una evaluación profunda de cómo estas cuatro energías están interactuando en su vida en este preciso instante, explicando las tensiones o armonías entre sus cuerpos. (Mínimo 100 palabras)",
        "consejo_practico": "Consejos espirituales y prácticos aplicables en el día a día para equilibrar las energías en déficit o aprovechar al máximo las energías en abundancia. (Mínimo 100 palabras)",
        "terapia_recomendada": "Sugerencias de terapias holísticas específicas (Reiki, alineación de chakras, meditación, aromaterapia) ofrecidas en el centro para alcanzar la plenitud. (Mínimo 100 palabras)"
    }}
    Redacta en segunda persona, con un tono motivador, espiritual, místico y profesional. No uses markdown, devuelve sólo JSON.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error generando reporte de Biorritmo con LLM: {e}")
        return {
            "analisis_general": f"Tus niveles promedio son: Físico {fisico}%, Emocional {emocional}%, Intelectual {intelectual}%, Espiritual {espiritual}%.",
            "consejo_practico": "Te sugerimos descansar si tus niveles físicos son bajos, o meditar si tus emociones fluctúan.",
            "terapia_recomendada": "Una armonización energética te ayudará a equilibrar todos tus cuerpos."
        }
