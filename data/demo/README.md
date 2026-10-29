# Qué es real y qué es simulado en la demo

Decirlo así en el pitch y en las preguntas del jurado. En pantalla, cada cifra lleva su etiqueta **real**, **estimado** o **simulado**.

| Pieza | Estado hoy | Cómo se vuelve real |
|---|---|---|
| Mapa base, rutas a pie | **Real** (Mapbox, si hay token; si no, línea recta con aviso) | Ya lo es |
| Alta por nota de voz en Telegram | **Real** (OpenAI transcribe y extrae la ficha; con `DEMO_MODE=1`, respuestas grabadas) | Ya lo es |
| Regla anti-cadenas (4 filtros) | **Real** (código) sobre negocios simulados | Correrla sobre la descarga del DENUE |
| Negocios (520, forma del DENUE) | **Simulado** | DENUE de INEGI |
| Hexágonos: población, actividad con tarjeta, impulso | **Simulado** / **estimado** sobre simulados | Censo 2020 + CNBV BDIF por alcaldía |
| Dinero por alcaldía (CNBV) | **Simulado** | CNBV, Bases de Datos de Inclusión Financiera |
| Tianguis y mercados (60) | **Simulado**, salvo los que el equipo de campo deje en `data/campo/tianguis_verificados.csv` (**real**) | Datos abiertos de SEDECO + verificación en campo |
| Diccionario de artículos (332) | Construido a mano | Ampliar a ≥ 2,000 y evaluar |
| Historia de la plataforma (7 días de búsquedas, rutas, "compré aquí") | **Simulado**: `plataforma_simulada.json`, `demo_data: true` | Uso real del piloto |
| Programas (Mercomuna, DiMo, CoDi) | **Real** (existen); "Puntos de barrio" es **propuesta** | — |

## Archivos

- `plataforma_simulada.json`: `uv run python scripts/generar_historia.py` (determinista).
- Doña Lupe para la demo: `app/services/demo.py` (`DONA_LUPE`, a ~100 m de la sede para que entre a la ruta de Karla).
- Prueba de los 6 pasos sin red: `DEMO_MODE=1 uv run pytest -q app/tests/test_demo.py`.
