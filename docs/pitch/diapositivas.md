# Diapositivas · Pulso Barrial (6)

Regla: cada cifra lleva su fuente (de `IDEA.md` §10, verificadas el 25-oct-2026). Lo simulado se dice simulado. Ninguna cifra de esta presentación viene del LLM.

---

## 1 · El problema (C1, C2)

**La red de negocios del barrio ya existe en la calle, pero no en un mapa.**

- **1,367 tianguis** en la CDMX: Iztapalapa 362, Gustavo A. Madero 206 y Coyoacán 136. Fuente: [Chilango, mapa de tianguis CDMX](https://www.chilango.com/noticias/crean-mapa-con-todos-los-tianguis-de-cdmx-ubicaciones-dias-y-horarios/)
- **30.6%** de los negocios usó internet y solo **6.7%** vendió en línea (2023). Fuente: [STyFE CDMX con datos de Censos Económicos 2024](https://deet.trabajo.cdmx.gob.mx/storage/app/media/uploaded-files/b03-censos-economicos-012025docx.pdf)
- La facturación promedio de las tienditas cayó **42.8%** entre 2017 y 2023 (dato nacional). Fuente: [El CEO con datos de ANPEC](https://elceo.com/negocios/tiendas-de-la-esquina-pierden-clientes-sus-ventas-cayeron-42-8-en-un-sexenio/)
- **339 mercados públicos**, con unos 7 millones de clientes por semana. Fuente: presentación de retos del Chilangatón 2026 (SEDECO, SECTEI, SAF)

Personas: Mtra. Rocío (JUD de Mercados y Tianguis), Karla (vecina de Coyoacán) y Doña Lupe (tianguista, 63 años). Son personas de la demo, no personas reales.

---

## 2 · Vista SEDECO: dónde se mueve el dinero y dónde falta barrio (C2, C3)

- Hexágonos 3D (H3, resolución 9) de Coyoacán e Iztapalapa. La altura es la actividad estimada de pago con tarjeta y el color es el índice de impulso.
- Interruptor **"Ver dato real"**: muestra el total por alcaldía de la base de inclusión financiera de la CNBV (transacciones en TPV por municipio; última actualización confirmada: 2023-2T). Fuente: [Reporte CNBV](https://www.gob.mx/cms/uploads/attachment/file/810711/ReporteTrimestralBDIF_202209.pdf) · [BBVA Research](https://www.bbvaresearch.com/publicaciones/mexico-en-2023-2t-99-de-adultos-en-municipios-con-punto-de-acceso-creditocaptacion/)
- **Aviso en pantalla:** en este prototipo, los hexágonos, la población, los negocios y los tianguis son **simulados** (`tipo_dato: "simulado"`), y el reparto por hexágono es **estimado**. Cada tarjeta lo dice.
- Barra de domingo a martes: los tianguis se apagan y aparecen los desiertos del día.
- Privacidad: SEDECO solo ve hexágonos agregados, y uno con menos de 3 negocios se pinta gris.
- Precedente: BBVA ya mapeó la CDMX con celdas hexagonales a partir de transacciones con tarjeta. Fuente: [BBVA Urban Discovery](https://www.bbva.com/es/innovacion/bbva-reordena-mapas-madrid-barcelona-mexico-ayuda-big-data/)

---

## 3 · Vista Usuario: ruta de compras de barrio (C3, C6)

- Karla escribe: "2 kilos de jitomate, tortillas, chiles secos, tenis para niño, pilas".
- Ruta a pie que pasa **solo por negocios de barrio**: **0 cadenas**, garantizado por 4 filtros deterministas y una prueba automática.
- Prioriza paradas en zonas con poco movimiento, y cada parada dice por qué fue elegida.
- Movilidad cero: todo en su colonia.
- Las cifras del chip (km, paradas) salen del cálculo sobre datos **simulados** del prototipo.

---

## 4 · Vista Negocio: alta por voz en vivo (C5, C6)

- Doña Lupe manda una nota de voz por Telegram y el bot le responde con su ficha para que la confirme. Al confirmar, el puesto aparece en el mapa, en las rutas y con su página web y su QR.
- Sin apps, sin formularios y sin trámites: pensado para adultos mayores y para el negocio en casa.
- **Escalera de barrio** voluntaria: visible → cobro digital → historial → crédito (como horizonte; hoy no se ofrece crédito).
- Programas a los que puede entrar: Mercomuna, con 700 mil apoyos en 2026 ([Chilango](https://www.chilango.com/noticias/vales-mercomuna-cdmx-entregara-700-mil-apoyos-2026/)) y más de 15 mil negocios que aceptan sus vales ([Posta](https://www.posta.com.mx/cdmx/vales-mercomuna-2026-la-lista-completa-de-tiendas-y-mercados-de-cdmx-donde-si-te-los-aceptan/vl2231918)).

---

## 5 · Implementación, costo y escala (C4, C7, C8)

- **Quién lo opera (C4):** colectivos juveniles de INJUVE verifican puestos con fecha de verificación; SEDECO publica el estándar abierto **Tianguis Abierto**; CANACOPE suma comerciantes. Es la triple hélice: gobierno, comercio y academia (IPN).
- **Por qué no se repite un fracaso (C4):** "Mi Mercado en Casa" (2022) arrancó en 2 mercados con meta de 40 ([Chilango](https://www.chilango.com/noticias/mi-mercado-en-casa-app-con-la-que-mercados-haran-envios-a-domicilio/)), y SEDECO derogó la digitalización de trámites de mercados tras el rechazo de los locatarios (2025, [DPL News](https://dplnews.com/?p=289857)). Pulso Barrial no pide descargar una app ni la liga a trámites.
- **Costo (C7):** cero para el comerciante (sin comisión, sin app). Para la ciudad, corre sobre Telegram, datos abiertos y herramientas gratuitas o de código abierto. El costo por usuario al mes **está por medirse en el piloto**: no presentamos una cifra que no tenemos.
- **Escala (C8):** las fuentes (CNBV, Censo 2020, SEDECO) cubren las 16 alcaldías, y el pipeline recibe la lista de alcaldías como parámetro. El piloto va de Coyoacán a Iztapalapa y después a toda la ciudad.
- **Evidencia internacional:** Singapur pasó de 2,300 a 7,800 etiquetas QR en centros de comida en poco más de un año ([MAS](https://www.mas.gov.sg/news/parliamentary-replies/2021/reply-to-parliamentary-question-on-e-payments-and-progress-on-the-roll-out-of-sgqr)). En Corea se usaron 3.95 billones de wones en vales Onnuri en un año, 65% de ellos en mercados tradicionales ([Korea JoongAng Daily](https://koreajoongangdaily.joins.com/korea/korea-revamps-onnuri-gift-certificates-to-attract-tourists-revive-local-markets/12900849)).
- **De hexágono estimado a real:** BBVA México y el Gobierno CDMX ya miden consumo con datos de terminales (jul-2026, [BBVA](https://www.bbva.com/es/mx/economia-y-finanzas/bbva-mexico-y-gobierno-cdmx-lanzan-plataforma-unica-que-midio-el-consumo-del-turismo-extranjero-durante-el-mundial/)). Con un convenio así, el hexágono se vuelve dato real.

---

## 6 · Cierre (C3)

**"Los demás le dan una app al comerciante. Nosotros le damos a la ciudad la red viva de su economía de barrio."**

Pulso Barrial · La red viva de la economía de barrio.
