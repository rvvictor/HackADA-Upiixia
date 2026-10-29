# Ruta de maduración a 30 días

De un prototipo de hackathon a un piloto real en Coyoacán e Iztapalapa. Las metas son propuestas del equipo, **por validar** con los actores del piloto; ninguna es un resultado.

## Punto de partida (al 29-oct-2026)

- Funciona: alta de un negocio por nota de voz, mapa, ruta de compras a pie y modo `DEMO_MODE=1` sin red.
- Real: 1,367 tianguis, 329 mercados, 1,543 colonias, marginación y contaminación por colonia; negocios del DENUE en revisión.
- Simulado: población y negocios por hexágono, dinero CNBV, historial, repartidores, ofertas e incentivos.
- En curso: alta de repartidor por Telegram (CO-009), portal de repartidores, incentivos.

## Semana 1 · Cimientos legales y de datos

- Asesoría legal sobre la priorización por edad y estudiante y sobre el aviso de privacidad (`docs/legal/priorizacion.md`). **Sin esto no hay piloto con repartidores.**
- Sustituir lo simulado: población del Censo (INEGI) por hexágono y la base de inclusión financiera de la CNBV; integrar el DENUE.
- Definir con quién se hace el piloto: 1 o 2 colectivos locales y una alcaldía, en una colonia de Coyoacán y una de Iztapalapa.
- Medir la extracción por voz con grabaciones reales de comerciantes (acentos, ruido de tianguis).
- **Medible:** datos reales integrados y rotulados en `data/fuentes/`; lista de 20 voces de prueba con porcentaje de fichas correctas.

## Semana 2 · Piloto con comerciantes

- Alta presencial de 10 a 20 negocios en las dos colonias, con acompañamiento humano.
- Confirmar con cada uno su consentimiento de publicar y si su ubicación es exacta o aproximada.
- Corregir lo que falle: giros que no entiende, horarios, formas de pago.
- **Medible:** negocios dados de alta y confirmados; tiempo medio de alta; fichas que el comerciante corrigió.

## Semana 3 · Repartidores y verificación

- Alta de 5 a 10 repartidores por Telegram, con verificación de identidad hecha por una persona responsable (no simulada) y borrado de la foto tras verificar.
- Definir cómo se paga al repartidor (hoy fuera de alcance) y quién paga; probar con pedidos reales de bajo volumen.
- Regla de prioridad activa solo si el visto bueno legal está listo; si no, orden por cercanía y antigüedad.
- **Medible:** repartidores verificados; rutas ofrecidas, tomadas y completadas; tiempo de toma de una oferta.

## Semana 4 · Medición y decisión

- Pedidos de punta a punta: negocio publica, vecino pide, repartidor entrega.
- Encuesta corta a comerciantes, vecinos y repartidores (¿lo volverías a usar?).
- Revisar privacidad y seguridad antes de ampliar (`.uak/docs/SECURITY.md`, lista de lanzamiento).
- Decidir: ampliar a más colonias, ajustar o parar.
- **Medible:** ver tabla.

## Métricas de éxito propuestas (por validar)

| Métrica | Meta propuesta al día 30 | Cómo se mide |
|---|---|---|
| Negocios con ficha confirmada | 15 | Conteo en la plataforma |
| Fichas sin corrección del comerciante | 70 % o más | Altas sin cambio tras **Así queda** |
| Tiempo medio de alta | 3 minutos o menos | Marca de tiempo del bot |
| Repartidores verificados por una persona | 6 | Registro de verificación |
| Entregas completadas | 40 | Rutas con estado `completada` |
| Comerciantes que repetirían | 70 % o más | Encuesta |

Estas metas son nuestra propuesta de arranque, no una proyección con base en datos; se ajustan con lo aprendido en la semana 1.

## Riesgos y qué haríamos

| Riesgo | Respuesta |
|---|---|
| Asesoría legal tarda o dice que no a la priorización | Piloto sin prioridad por edad; orden por cercanía y antigüedad |
| Comerciantes no confían en dar su ubicación | Ubicación aproximada por defecto |
| La extracción por voz falla en tianguis ruidosos | Texto como alternativa; corrección con botones |
| Sin patrocinador de la bici | Incentivos menores o ninguno; la propuesta sigue marcada como propuesta |
| Nadie paga al repartidor | Empezar con repartidores del propio negocio (`IDEA-v2.md` §6) |
