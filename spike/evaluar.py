"""Evaluación del spike de menús."""

import csv
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
COLUMNAS = ["nombre", "tipo", "compatibilidad", "puntaje", "marca", "tipo_ok", "compat_ok", "nota", "razon"]


def rutas(args):
    ronda = args[args.index("--ronda") + 1] if "--ronda" in args else "v2"
    if ronda == "v2":
        return BASE / "results_v2", BASE / "evaluacion"
    return BASE / f"results_{ronda}", BASE / f"evaluacion_{ronda}"


def limpiar(txt):
    t = (txt or "").strip().lower()
    for a, b in (("ó", "o"), ("í", "i"), ("á", "a"), ("é", "e"), ("ú", "u"), ("ü", "u")):
        t = t.replace(a, b)
    return t


def norm(nombre):
    return re.sub(r"[^a-z0-9]+", " ", limpiar(nombre)).strip()


def leer_csv(ruta):
    texto = ruta.read_text(encoding="utf-8-sig")
    lineas = texto.splitlines()
    delim = ";" if lineas and lineas[0].count(";") > lineas[0].count(",") else ","
    return list(csv.DictReader(lineas, delimiter=delim))


def generar(args):
    RES, EVAL = rutas(args)
    forzar = "--forzar" in args
    previo = Path(BASE / args[args.index("--previo") + 1]) if "--previo" in args else None
    if not RES.exists():
        print(f"No existe {RES.name}/. Corre primero el spike.")
        return
    EVAL.mkdir(exist_ok=True)
    for js in sorted(RES.glob("*.json")):
        destino = EVAL / f"{js.stem}.csv"
        if destino.exists() and not forzar:
            print(f"(ya existe, no se toca: {destino.name})")
            continue
        data = json.loads(js.read_text(encoding="utf-8"))
        items = data.get("platillos", [])
        prev_map, prev_falto = {}, []
        if previo and (previo / f"{js.stem}.csv").exists():
            for fila in leer_csv(previo / f"{js.stem}.csv"):
                m = limpiar(fila.get("marca"))
                if m in ("ok", "x"):
                    prev_map[norm(fila.get("nombre"))] = fila
                elif m == "falto":
                    prev_falto.append(fila)
        filas, arrastradas, nuevas = [], 0, 0
        for p in items:
            base = [p.get("nombre", ""), p.get("tipo", ""), p.get("compatibilidad", ""), p.get("puntaje", "")]
            razon = p.get("razon", "")
            if previo:
                ant = prev_map.get(norm(p.get("nombre")))
                if ant:
                    tipo_ok = ant.get("tipo_ok", "") if limpiar(ant.get("tipo")) == limpiar(p.get("tipo")) else ""
                    comp_ok = ant.get("compat_ok", "") if limpiar(ant.get("compatibilidad")) == limpiar(p.get("compatibilidad")) else ""
                    filas.append(base + [ant.get("marca", "ok"), tipo_ok, comp_ok, ant.get("nota", ""), razon])
                    arrastradas += 1
                else:
                    filas.append(base + ["revisar", "", "", "", razon])
                    nuevas += 1
            else:
                filas.append(base + ["ok", "", "", "", razon])
        if previo:
            nombres_nuevos = {norm(p.get("nombre")) for p in items}
            for f in prev_falto:
                if norm(f.get("nombre")) not in nombres_nuevos:
                    filas.append([f.get("nombre", ""), "", "", "", "falto", "", "", "arrastrado: verifica que siga sin detectarse", ""])
        with destino.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(COLUMNAS)
            w.writerows(filas)
        extra = f" | arrastradas {arrastradas}, por revisar {nuevas}" if previo else ""
        print(f"Creado: {destino.name} ({len(items)} filas{extra})")
    print("\nSiguiente paso: abre cada CSV, compáralo con la foto y corrige la columna 'marca'.")


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "n/a"


def calcular(args):
    RES, EVAL = rutas(args)
    archivos = [a for a in sorted(EVAL.glob("*.csv")) if a.stem != "resumen"] if EVAL.exists() else []
    if not archivos:
        print(f"No hay CSV en {EVAL.name}/. Corre primero: python evaluar.py generar")
        return
    filas_res = []
    tot = {"ok": 0, "x": 0, "falto": 0}
    tipo_s = tipo_n = comp_s = comp_n = errata = 0
    for a in archivos:
        c = {"ok": 0, "x": 0, "falto": 0}
        pend = 0
        for fila in leer_csv(a):
            m = limpiar(fila.get("marca"))
            if m == "revisar":
                pend += 1
                continue
            if m not in c:
                if (fila.get("nombre") or "").strip():
                    print(f"  Aviso: {a.name} -> '{fila.get('nombre')}' tiene marca '{fila.get('marca')}' (usa ok, x o falto)")
                continue
            c[m] += 1
            if m == "ok":
                t = limpiar(fila.get("tipo_ok"))
                tipo_s += t in ("s", "si")
                tipo_n += t in ("n", "no")
                k = limpiar(fila.get("compat_ok"))
                comp_s += k in ("s", "si")
                comp_n += k in ("n", "no")
            if limpiar(fila.get("nota")).startswith("errata"):
                errata += 1
        det, real = c["ok"] + c["x"], c["ok"] + c["falto"]
        modelo = ""
        jf = RES / f"{a.stem}.json"
        if jf.exists():
            modelo = json.loads(jf.read_text(encoding="utf-8")).get("_modelo", "")
        filas_res.append({
            "menu": a.stem, "modelo": modelo, "reales": real, "detectados": det, "pend": pend,
            "correctos": c["ok"], "inventados": c["x"], "faltantes": c["falto"],
            "precision": pct(c["ok"], det), "cobertura": pct(c["ok"], real),
            "_p": c["ok"] / det if det else None, "_r": c["ok"] / real if real else None,
        })
        for k in tot:
            tot[k] += c[k]

    print(f"\n{'Menú':<12}{'Reales':>7}{'Detec.':>7}{'OK':>5}{'X':>4}{'Falt.':>6}{'Pend.':>6}{'Precisión':>11}{'Cobertura':>11}  Modelo")
    for r in filas_res:
        print(f"{r['menu']:<12}{r['reales']:>7}{r['detectados']:>7}{r['correctos']:>5}{r['inventados']:>4}"
              f"{r['faltantes']:>6}{r['pend']:>6}{r['precision']:>11}{r['cobertura']:>11}  {r['modelo']}")
    if any(r["pend"] for r in filas_res):
        print("\n  ATENCIÓN: hay filas 'revisar' sin resolver; los porcentajes de esos menús NO son finales.")

    ps = [r["_p"] for r in filas_res if r["_p"] is not None]
    rs = [r["_r"] for r in filas_res if r["_r"] is not None]
    det_t, real_t = tot["ok"] + tot["x"], tot["ok"] + tot["falto"]
    print("\n=== GLOBAL ===")
    print(f"Menús evaluados: {len(filas_res)}")
    print(f"Promedio por menú  -> Precisión {100 * sum(ps) / len(ps):.1f}% | Cobertura {100 * sum(rs) / len(rs):.1f}%")
    print(f"Suma de platillos  -> Precisión {pct(tot['ok'], det_t)} | Cobertura {pct(tot['ok'], real_t)}  (OK {tot['ok']}, X {tot['x']}, faltantes {tot['falto']})")
    print(f"Errores de lectura (nota 'errata'): {errata}")
    print(f"Tipo correcto (platillo/bebida/postre): {pct(tipo_s, tipo_s + tipo_n)} de {tipo_s + tipo_n} revisados")
    print(f"Compatibilidad razonable: {pct(comp_s, comp_s + comp_n)} de {comp_s + comp_n} revisados")

    out = EVAL / "resumen.csv"
    campos = ("menu", "modelo", "reales", "detectados", "correctos", "inventados", "faltantes", "precision", "cobertura")
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(campos)
        for r in filas_res:
            w.writerow([r[k] for k in campos])
    print(f"\nGuardado: {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("generar", "calcular"):
        print(__doc__)
    elif sys.argv[1] == "generar":
        generar(sys.argv)
    else:
        calcular(sys.argv)