   # ADR 0002: Configuración congelada del VLM para la medición final
   - Fecha: 2026-10-28
   - Modelo: gemini-3.8-flash
   - Prompt: spike/spike_menuV3.py (variable PROMPT)
   - Temperatura: 0.2 | MAX_SALIDA: 32000
   - Perfil de prueba: diabetes tipo 2, 4 criterios (ver PERFIL en el script)
   - Regla: no se modifica el prompt hasta terminar la medición de los 15 menús
   - Limitación conocida: variabilidad entre corridas en ~1 % de las entradas