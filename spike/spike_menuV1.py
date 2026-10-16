import json
import mimetypes
import os
import time
from collections import Counter
from pathlib import Path
 
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
 
load_dotenv(Path(__file__).parent.parent / ".env")
 
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
 
PAUSA_ENTRE_FOTOS = 13      # nivel gratuito: 20 solicitudes al día, aprox 5 por minuto
MAX_REINTENTOS = 5
ESPERAS = [15, 30, 60, 90, 120] 
 
PERFIL = {
    "tipo_diabetes": "tipo 2",
    "criterios": [
        "bajo en carbohidratos refinados",
        "evitar bebidas azucaradas",
        "preferir proteína magra y verduras",
        "limitar frituras",
    ],
}
 
PROMPT = f"""Eres un asistente que ayuda a una persona con criterios alimentarios a leer menús de restaurante.
Analiza la imagen del menú y responde SOLO con JSON válido con esta estructura:
 
{{
  "legible": true/false,
  "calidad_imagen": "buena|regular|mala",
  "platillos": [
    {{
      "nombre": "texto tal como aparece",
      "descripcion": "texto del menú o null",
      "precio": "texto o null",
      "ingredientes_probables": ["..."],
      "compatibilidad": "alta|media|baja",
      "razon": "una frase breve basada SOLO en el texto del menú",
      "confianza": 0.0 a 1.0
    }}
  ]
}}
 
Perfil del usuario: {json.dumps(PERFIL, ensure_ascii=False)}
 
Reglas:
- Usa solo lo que está escrito en el menú. No inventes platillos ni ingredientes.
- Si algo es ilegible, bájale la confianza o no lo incluyas.
- No des consejos médicos, no calcules dosis, no diagnostiques.
- Evalúa compatibilidad únicamente contra los criterios del perfil.
"""
 
 
def analizar(ruta: Path) -> dict:
    mime = mimetypes.guess_type(ruta)[0] or "image/jpeg"
    img = types.Part.from_bytes(data=ruta.read_bytes(), mime_type=mime)
    for intento in range(MAX_REINTENTOS):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=[img, PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.2
                ),
            )
            return json.loads(resp.text)
        except errors.APIError as e:
            if e.code == 429 and "PerDay" in str(e):
                print("   Cuota DIARIA agotada. No tiene caso reintentar ahora.")
                raise SystemExit(1)
            if e.code in (429, 503) and intento < MAX_REINTENTOS - 1:
                espera = ESPERAS[intento]
                print(f"   Error {e.code}, reintento {intento + 1}/{MAX_REINTENTOS - 1} en {espera}s...")
                time.sleep(espera)
            else:
                raise
 
 
def main():
    carpeta = Path(__file__).parent / "menus"
    salida = Path(__file__).parent / "results"
    salida.mkdir(exist_ok=True)
    fotos = [p for p in carpeta.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    if not fotos:
        print("No hay fotos en spike/menus/")
        return
    fallidas = []
    for foto in sorted(fotos):
        destino = salida / f"{foto.stem}.json"
        if destino.exists():
            print(f"(omitida, ya procesada: {foto.name})")
            continue
        print(f"\n== {foto.name} ==")
        try:
            data = analizar(foto)
        except Exception as e:
            print("ERROR FINAL:", e)
            fallidas.append(foto.name)
            continue
        destino.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        platillos = data.get("platillos", [])
        conteo = Counter(p.get("compatibilidad") for p in platillos)
        print(f"Legible: {data.get('legible')} | Calidad: {data.get('calidad_imagen')} | "
              f"Platillos: {len(platillos)} (alta {conteo['alta']}, media {conteo['media']}, baja {conteo['baja']})")
        time.sleep(PAUSA_ENTRE_FOTOS)
    print("\n=== RESUMEN ===")
    print("Fallidas:", fallidas if fallidas else "ninguna")
 
if __name__ == "__main__":
    main()
 