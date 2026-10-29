# Pendiente legal · priorización de repartidores y aviso de privacidad

> **Estado: POR VALIDAR CON ASESORÍA LEGAL.** Este documento describe lo que el equipo propone y las preguntas abiertas. No es un dictamen legal ni lo sustituye. Nada de esto debe operar con personas reales hasta tener el visto bueno.

Fuente de diseño: `IDEA-v2.md` §4.3 y §4.5.

## 1. Qué se propone

**Priorización, no exclusión.** Al ofrecer una ruta cuando hay más repartidores que rutas en una colonia, el orden es: prioridad (mayor primero), cercanía, antigüedad.

| Situación del repartidor | `prioridad` |
|---|---:|
| 18 a 30 años **y** estudiante | 2 |
| Cumple solo una de las dos | 1 |
| Ninguna | 0 |

- Nadie queda excluido por edad ni por no estudiar: todos ven y pueden tomar ofertas.
- Mayoría de edad: se pide ser **mayor de 18 años** para registrarse.
- La prioridad se calcula solo en el backend (`prioridad()` en `app/services/repartidor_dialogo.py`, rama `feat/co-009`). La interfaz y el bot nunca muestran la prioridad de otra persona, y la edad y el dato de estudiante no salen del backend.
- Se guarda `rango_edad` (`18-30` o `31+`), no la fecha de nacimiento.

## 2. Preguntas para la asesoría legal

1. ¿Puede darse preferencia por edad (18 a 30) y por ser estudiante, enmarcada como programa de empleo juvenil o acción afirmativa, sin que sea discriminación? Marco a revisar: Ley Federal para Prevenir y Eliminar la Discriminación y Ley Federal del Trabajo (pendiente confirmar los artículos aplicables).
2. ¿Cambia algo si la plataforma no es empleadora sino intermediaria? ¿Qué relación tienen los repartidores con el negocio y con colonIA?
3. ¿Hace falta una regla de transparencia (publicar el criterio de prioridad) aunque no se muestre la de cada persona?
4. ¿Qué documentos de identidad son válidos y cómo se conservan o borran? (Propuesta: INE, pasaporte o credencial escolar vigente.)
5. ¿Qué cambia si el repartidor es estudiante menor de 18? (Propuesta: no se acepta.)

## 3. Aviso de privacidad (borrador de contenido, texto por validar)

Marco a revisar: la ley de protección de datos personales en posesión de particulares vigente (pendiente confirmar el nombre y la versión aplicable).

| Dato | Para qué | Cómo se trata |
|---|---|---|
| Nombre para mostrar | Identificar al repartidor | Es lo que la persona decide que le llamen |
| Rango de edad y si estudia | Prioridad de ofertas | Solo backend; nunca se muestra a otras personas |
| Foto de identificación | Verificar identidad | No se publica ni se envía al frontend; se guarda fuera de git (`data/live/ids/`); se borra tras verificar; solo queda `id_verificada`, `tipo_id` y fecha |
| Alcaldía, colonias, transporte, disponibilidad | Asignar ofertas | Visible solo para el propio repartidor y para el sistema |
| Contacto por Telegram | Enviar el número de repartidor y el código de acceso | Se usa el `chat_id`; no se guarda número de teléfono |

Puntos que el aviso debe cubrir (por redactar): quién es el responsable, finalidades, derechos de acceso, rectificación, cancelación y oposición, transferencias (el texto de voz se envía a un proveedor de IA para transcribirse y extraer campos: **declararlo**), plazo de conservación y cómo revocar.

El bot muestra un aviso corto con botón **Acepto**; sin aceptar no continúa el alta (`IDEA-v2.md` §4.2).

## 4. Qué falta para cerrar

- [ ] Opinión legal por escrito sobre §2.
- [ ] Texto final del aviso de privacidad, corto (bot) y completo (web).
- [ ] Decisión de producto si la respuesta es negativa: quitar la prioridad y ordenar solo por cercanía y antigüedad (cambio de peso en `app/config.py`).
- [ ] Responsable de datos personales designado.

Mientras tanto, en la demo la prioridad existe como regla de código y los repartidores son `demo_data: true`.
