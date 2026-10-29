import json
import mimetypes
import os
import sys
import time
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv(Path(__file__).parent.parent / ".env")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

PAUSA_ENTRE_FOTOS = 13
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
  "secciones_no_leidas": ["nombre de secciones visibles que no pudiste leer"],
  "platillos": [
    {{
      "nombre": "texto tal como aparece, con la variante si aplica",
      "tipo": "platillo|bebida|postre",
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
- Si una línea del menú agrupa varias variantes (rellenos, tipos, salsas, sabores, tipos de cerveza o de jugo), crea UNA entrada por cada variante, con nombre "Platillo base - variante", y evalúa cada una por separado.
- Incluye TODAS las secciones visibles del menú. Si una sección no se puede leer, anótala en "secciones_no_leidas" en lugar de omitirla en silencio.
- Clasifica cada entrada: "bebida" (café, té, jugos, licuados, refrescos, cervezas, vinos, cocteles), "postre" (postres, pan dulce, galletas, pasteles) y "platillo" (todo lo demás, incluidas entradas y guarniciones que se piden solas).
- NO incluyas extras ni modificadores: complementos con costo adicional, tamaños, tipos de leche, endulzantes, toppings o "agrega X". No son entradas independientes del menú.
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
                    response_mime_type="application/json",
                    temperature=0.2,
                    max_output_tokens=16000,
                ),
            )
            return json.loads(resp.text)
        except errors.APIError as e:
            if e.code == 429 and "PerDay" in str(e):
                print("   Cuota DIARIA agotada para este modelo. No tiene caso reintentar ahora.")
                raise SystemExit(1)
            if e.code in (429, 503) and intento < MAX_REINTENTOS - 1:
                espera = ESPERAS[intento]
                print(f"   Error {e.code}, reintento {intento + 1}/{MAX_REINTENTOS - 1} en {espera}s...")
                time.sleep(espera)
            else:
                raise
        except json.JSONDecodeError:
            print("   El JSON llegó incompleto (menú muy largo). Anótalo como falla de salida truncada.")
            raise


def main():
    carpeta = Path(__file__).parent / "menus"
    salida = Path(__file__).parent / "results_v2"
    salida.mkdir(exist_ok=True)
    pedidas = set(sys.argv[1:])
    fotos = [p for p in carpeta.iterdir()
             if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
             and (not pedidas or p.name in pedidas)]
    if not fotos:
        print("No hay fotos que procesar (revisa nombres y carpeta spike/menus/)")
        return
    print(f"Modelo: {MODEL}")
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
        data["_modelo"] = MODEL
        destino.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        items = data.get("platillos", [])
        tipos = Counter(p.get("tipo") for p in items)
        compat = Counter(p.get("compatibilidad") for p in items)
        print(f"Legible: {data.get('legible')} | Calidad: {data.get('calidad_imagen')} | Total: {len(items)}")
        print(f"   Tipos: platillo {tipos['platillo']}, bebida {tipos['bebida']}, postre {tipos['postre']}")
        print(f"   Compatibilidad: alta {compat['alta']}, media {compat['media']}, baja {compat['baja']}")
        if data.get("secciones_no_leidas"):
            print("   Secciones no leídas:", data["secciones_no_leidas"])
        time.sleep(PAUSA_ENTRE_FOTOS)
    print("\n=== RESUMEN ===")
    print("Fallidas:", fallidas if fallidas else "ninguna")


if __name__ == "__main__":
    main()