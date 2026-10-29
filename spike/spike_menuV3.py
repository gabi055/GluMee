"""Spike v3: prompt para congelar y usar en la medición final."""
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
MAX_SALIDA = int(os.getenv("MAX_SALIDA", "32000"))

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
Analiza la imagen del menú y responde SOLO con JSON válido, sin campos adicionales, con esta estructura:

{{
  "legible": true/false,
  "calidad_imagen": "buena|regular|mala",
  "secciones_no_leidas": ["secciones visibles que no pudiste leer"],
  "platillos": [
    {{
      "nombre": "texto tal como aparece, con la variante si aplica",
      "tipo": "platillo|bebida|postre",
      "descripcion": "texto del menú, máximo 10 palabras, o null",
      "precio": "texto o null",
      "compatibilidad": "alta|media|baja",
      "puntaje": 0 a 100,
      "razon": "máximo 15 palabras"
    }}
  ]
}}

Perfil del usuario: {json.dumps(PERFIL, ensure_ascii=False)}

Reglas:
- Usa solo lo que está escrito en el menú. No inventes platillos.
- Si tu razón depende de algo que NO está escrito en el menú (por ejemplo, suponer que algo es frito), empieza la razón con "Se supone:".
- Cuando una línea del menú ofrece varias opciones (separadas por comas, por "o", por "/" o entre paréntesis: sabores, salsas, rellenos, tipos de proteína, tipos de jugo, refresco o cerveza), crea UNA entrada por cada opción, con nombre "Producto - opción". Ejemplo: "Chilaquiles: rojos, verdes o salsa Jalisco" son 3 entradas: "Chilaquiles - rojos", "Chilaquiles - verdes", "Chilaquiles - salsa Jalisco". Excepción: si el menú dice que el cliente arma el producto con ingredientes a elegir, usa una sola entrada.
- Incluye TODAS las secciones visibles. Si una no se puede leer, anótala en "secciones_no_leidas" en lugar de omitirla.
- Clasifica cada entrada: "bebida" (café, té, jugos, licuados, refrescos, cervezas, vinos, cocteles), "postre" (postres, pan dulce, galletas, pasteles) y "platillo" (todo lo demás, incluidas entradas y guarniciones que se piden solas).
- NO incluyas extras ni modificadores: complementos con costo adicional, tamaños, tipos de leche como cambio de otra bebida, endulzantes, toppings o "agrega X".
- Puntaje: 0 = nada compatible con los criterios, 100 = totalmente compatible. Usa todo el rango: si dos entradas difieren en algo relevante (tipo de pan, fritura, carbohidrato refinado, azúcar), sus puntajes deben diferir. "alta" = 70 o más, "media" = 40 a 69, "baja" = menos de 40.
- No des consejos médicos, no calcules dosis, no diagnostiques.
"""


def analizar(ruta: Path, salida: Path) -> dict:
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
                    max_output_tokens=MAX_SALIDA,
                ),
            )
        except errors.APIError as e:
            if e.code == 429 and "PerDay" in str(e):
                print("   Cuota DIARIA agotada para este modelo. No tiene caso reintentar ahora.")
                raise SystemExit(1)
            if e.code in (429, 503) and intento < MAX_REINTENTOS - 1:
                espera = ESPERAS[intento]
                print(f"   Error {e.code}, reintento {intento + 1}/{MAX_REINTENTOS - 1} en {espera}s...")
                time.sleep(espera)
                continue
            raise
        texto = resp.text or ""
        try:
            motivo = str(resp.candidates[0].finish_reason)
        except Exception:
            motivo = "desconocido"
        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            parcial = salida / f"{ruta.stem}.truncado.txt"
            parcial.write_text(texto, encoding="utf-8")
            if "MAX_TOKENS" in motivo:
                print(f"   Se alcanzó el límite de tokens de salida ({MAX_SALIDA}). Sube MAX_SALIDA o divide la foto.")
            else:
                print(f"   JSON inválido (motivo de fin: {motivo}).")
            print(f"   Texto parcial guardado en {parcial.name}")
            raise


def main():
    carpeta = Path(__file__).parent / "menus"
    salida = Path(__file__).parent / "results_v3"
    salida.mkdir(exist_ok=True)
    pedidas = set(sys.argv[1:])
    fotos = [p for p in carpeta.iterdir()
             if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
             and (not pedidas or p.name in pedidas)]
    if not fotos:
        print("No hay fotos que procesar (revisa nombres y carpeta spike/menus/)")
        return
    print(f"Modelo: {MODEL} | MAX_SALIDA: {MAX_SALIDA}")
    fallidas = []
    for foto in sorted(fotos):
        destino = salida / f"{foto.stem}.json"
        if destino.exists():
            print(f"(omitida, ya procesada: {foto.name})")
            continue
        print(f"\n== {foto.name} ==")
        try:
            data = analizar(foto, salida)
        except Exception as e:
            print("ERROR FINAL:", e)
            fallidas.append(foto.name)
            continue
        data["_modelo"] = MODEL
        destino.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        items = data.get("platillos", [])
        tipos = Counter(p.get("tipo") for p in items)
        compat = Counter(p.get("compatibilidad") for p in items)
        pts = [p["puntaje"] for p in items if isinstance(p.get("puntaje"), (int, float))]
        print(f"Legible: {data.get('legible')} | Calidad: {data.get('calidad_imagen')} | Total: {len(items)}")
        print(f"   Tipos: platillo {tipos['platillo']}, bebida {tipos['bebida']}, postre {tipos['postre']}")
        print(f"   Compatibilidad: alta {compat['alta']}, media {compat['media']}, baja {compat['baja']}")
        if pts:
            print(f"   Puntaje: mín {min(pts)}, máx {max(pts)}, promedio {sum(pts) / len(pts):.0f}")
        if data.get("secciones_no_leidas"):
            print("   Secciones no leídas:", data["secciones_no_leidas"])
        time.sleep(PAUSA_ENTRE_FOTOS)
    print("\n=== RESUMEN ===")
    print("Fallidas:", fallidas if fallidas else "ninguna")


if __name__ == "__main__":
    main()