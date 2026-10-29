# Ficha: mercados públicos (real)

- **Archivo:** `data/raw/diccionario_tianguis.csv` (el nombre dice "tianguis" pero contiene mercados públicos). Sitio exacto: por confirmar.
- **Salida:** `data/processed/mercados.json` (329 filas) y las mismas filas dentro de `tianguis_abierto.json` con `tipo: "mercado"`. Cada fila: `tipo_dato: "real"`, `fuente`, `fecha_consulta: "2026-10-25"`.
- **Columnas de origen:** mercado, numero, locales, direccion, colonia_mercado, alcaldia_mercado, tipo, superficie_m2, anio_inauguracion, giro, detalle, forma, niveles, tamaño, protegido, longitud, latitud (en ese orden: longitud primero).
- **Por alcaldía:** Gustavo A. Madero 50, Venustiano Carranza 43, Cuauhtémoc 39, Coyoacán 24, Tlalpan 20, Azcapotzalco 19, Iztapalapa 19, Tláhuac 19, Miguel Hidalgo 18, Iztacalco 16, Álvaro Obregón 16, Benito Juárez 16, Xochimilco 11, Milpa Alta 9, Cuajimalpa 5, Magdalena Contreras 5. Sin descartes.
- **Calidad:** sin mojibake detectado; `NA` -> null.
- **Horario por defecto:** la fuente no trae días ni horario. Para cumplir el esquema se pone `dias` = todos, 07:00-18:00 y `horario_por_defecto: true`. No es un horario real: no usarlo como dato de apertura en la UI.
- **Sigue simulado / vacío:** productos, formas de pago, Mercomuna, verificación.
