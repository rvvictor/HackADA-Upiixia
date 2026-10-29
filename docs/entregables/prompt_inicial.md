# Prompt inicial del sistema de IA

colonIA usa el modelo de lenguaje para una sola cosa: **convertir lo que dice una persona (texto o nota de voz transcrita) en campos estructurados**. Nunca para calcular cifras, rutas o prioridades (ver `flujo_ia.md`).

Todos los prompts de abajo están copiados del código. Si cambias el código, cambia aquí.

## Reglas comunes a todos los prompts

- Los modelos se fijan solo en `app/config.py`: `OPENAI_MODEL` (por defecto `gpt-5.6-terra`), `OPENAI_FALLBACK_MODEL` (`gpt-5-mini`) y `OPENAI_TRANSCRIBE_MODEL` (`gpt-transcribe`, con `whisper-1` de respaldo en `transcribir`). Los IDs exactos siguen **por validar** con la cuenta del equipo.
- **Salida estructurada**: la llamada usa `responses.parse(..., text_format=<modelo Pydantic>)`; la salida se vuelve a validar con Pydantic.
- Si no valida, se reintenta una vez con el mismo modelo, luego con el modelo de respaldo, y al final se usa la **respuesta grabada** (`app/bot/fixtures/`) o las reglas locales. Un fallo del modelo nunca tumba el alta.
- Sin `OPENAI_API_KEY` o con `DEMO_MODE=1` no se llama a ningún modelo (`usar_respaldo()`).
- El modelo elige de **listas cerradas** (claves SCIAN, enums de transporte, alcaldías). Si responde algo fuera de la lista, el código lo corrige (`clase_scian` inválida pasa a `999999`, "Otro").

## 1. Ficha del negocio (nota de voz o texto del comerciante)

Archivo: `app/services/altas.py` · constante `PROMPT_FICHA` · función `extraer_ficha(texto)`. Estado: **en `main`**.

Mensaje de sistema (el marcador `{giros}` se llena con la lista cerrada `GIROS`, "clave (nombre)", de la que el modelo debe elegir):

```text
Eres un asistente que llena la ficha de un puesto o negocio de barrio de la Ciudad de México a partir de lo que dice su dueña o dueño. Usa solo lo que se dice; no inventes precios ni horarios. Días: 0 = lunes … 6 = domingo; si dice 'fines de semana' son [5, 6]. Horas en formato HH:MM de 24 h ('de 7 a 3' = 07:00 a 15:00). formas_pago solo de: efectivo, transferencia, dimo, codi, tarjeta (efectivo siempre). clase_scian debe ser una de estas claves: {giros}. Si no dice nombre del negocio, usa 'Puesto de <nombre de la persona>'. telefono solo si lo dicta para su ficha.
```

Mensaje de usuario: la transcripción tal cual.

Esquema de salida (`Ficha`, Pydantic): `nombre`, `giro`, `clase_scian`, `productos[{nombre, precio, unidad}]`, `dias` (0 a 6), `abre`, `cierra` (HH:MM), `formas_pago`, `acepta_mercomuna`, `telefono`.

Después del modelo, código determinista: valida `clase_scian` contra `GIROS`, rellena `giro` con el nombre de la lista, ordena y filtra `dias`. El comerciante confirma con el botón **Así queda** antes de publicar (`confirmado`).

Ejemplo de entrada: la transcripción grabada de Doña Lupe (`app/bot/fixtures/dona_lupe_transcripcion.txt`); ejemplo de salida grabada: `app/bot/fixtures/dona_lupe_ficha.json`.

## 2. Alta del repartidor (texto o voz, un campo por mensaje)

Archivo: `app/services/repartidor_dialogo.py` · función `_llm(modelo, instruccion, texto)`. Estado: **en la rama `feat/co-009`** (CO-009, en revisión; aún no está en `main`).

Mensaje de sistema, común a todos los pasos (`instruccion` cambia por paso):

```text
Extrae SOLO el campo pedido de lo que dijo la persona. No inventes nada; si no está claro, deja null. {instruccion}
```

| Paso | `instruccion` | Esquema de salida |
|---|---|---|
| nombre | Campo: el nombre con el que quiere que le llamen. | `NombreOut` (`nombre`, 2 a 40 caracteres) |
| edad | Campo: edad en años cumplidos (si dio año de nacimiento, calcula con 2026). | `EdadOut` (`edad` o null) |
| estudia | Campo: ¿estudia actualmente? | `SiNoOut` (`valor`: true, false o null) |
| alcaldía | Campo: alcaldía de la CDMX. | `AlcaldiaOut` (`alcaldia` o null) |
| colonias | Campo: colonias que dijo (máximo 3). | `ColoniasOut` (hasta 3 nombres) |
| transporte | Campo: medio de transporte para repartir. | `TransporteOut` (enum: bici, bici_electrica, a_pie, scooter_electrico, moto, auto) |
| disponibilidad | Campos: días (entre_semana, fin_de_semana, todos) y franja (manana, tarde, noche) que dijo. | `DisponibilidadOut` |

Cada paso tiene una **regla local de respaldo** (`_regla_nombre`, `_regla_edad`, `_regla_transporte`, etc.) que se usa si el modelo no está disponible o devuelve null. Después, código determinista: la alcaldía y las colonias se emparejan contra el catálogo real, y `prioridad(rango_edad, estudiante)` se calcula solo en el backend; la edad exacta no se guarda, solo `rango_edad` (`18-30` o `31+`).

## 3. Artículo de la lista del mandado → giro (vecino)

Archivo: `app/services/articulos.py` · función de clasificación dentro de `interpretar`. Estado: **en `main`**. Solo se llama si el artículo no está en el diccionario (332 artículos, a mano) ni empata por similitud (RapidFuzz).

```text
Clasifica un artículo de compra de México en una clase SCIAN de la lista. Responde 'ninguna' si no corresponde a ninguna.
```

Salida con esquema JSON estricto: `{"clase": <una de las clases dadas o "ninguna">}`. Si falla o no está en la lista, el artículo va a `sin_resultado` y la interfaz lo dice.

## 4. Lo que NO tiene prompt

- **Descripción de la página del negocio** (`app/services/negocio.py::descripcion`): es una plantilla fija con datos de la ficha. No usa modelo.
- **Ruta de compras, prioridad de repartidores, puntajes, cifras del mapa**: código determinista.
- **Foto del pizarrón o del puesto**: no implementada; no hay prompt.
- **Identidad del repartidor**: la verificación de la foto de identificación es simulada en la demo (`verificar_id`: en demo se da por buena y se borra la imagen; fuera de demo la revisa una persona); no la hace un modelo.

## Qué se pasa al modelo y qué no

Se envía solo el texto de la persona y la lista cerrada de opciones. No se envían cifras del mapa, datos de otras personas, la foto de identificación ni la prioridad.
