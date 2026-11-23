# worklog/WL-1795414572-crismmolina-1-CO-028-hack.6xpFd3.md · CO-028

## Live summary
- Done: Claim created; implementation pending
- Decision: Own branch and worktree
- Why: Parallel work without touching the main checkout
- Failing: No validation run yet
- Commands: `bash -c 'test -s web/DESIGN.md && ls web/public/design-lock/screens/*-1280.png && npm --prefix web run build && bash .uak/bin/uak lint'`
- Next: `/uak-design-lock`, con un humano presente para elegir

## History
- 1795414572 | CLAIMED | crismmolina-1 | claim; next: `/uak-design-lock`, con un humano presente para elegir
- 1795415767 | CLAIMED | crismmolina-1 | pending decision CO-028-1795415767; option: Direction C · Maqueta viva; Why: cris eligió la C viendo las capturas de la ronda 2 (A, B, C): toda la app con el lenguaje de la maqueta (bloques blancos, cobalto donde falta comercio, pines rosa)
- 1795416239 | CLAIMED | crismmolina-1 | pending decision CO-028-1795416239; option: Paleta rosa mexicano y sin etiquetas real/simulado en pantalla; Why: cris (chat, 2026-11-23): quitar todo lo que dice simulado y datos reales, y usar la paleta rosa. Se apagan los chips con MOSTRAR_TIPO_DATO=false en Etiqueta; tipo_dato y fuente siguen en la API. Choca con C3 y criterios de CO-030/032/034/036, que piden etiqueta visible
