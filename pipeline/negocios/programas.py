"""Programas a los que puede entrar un negocio de barrio (vista Negocio). Se escribe en data/processed/programas.json.

estado: existe (programa público vigente), por_verificar (no se muestra como hecho), propuesta (idea de colonIA).
"""

FECHA = "2026-10-25"

PROGRAMAS = [
    {
        "id": "mercomuna",
        "nombre": "Mercomuna",
        "que_es": "Vales del Gobierno de la CDMX que las familias canjean en negocios de barrio afiliados.",
        "para_quien": "Tiendas, mercados y negocios de barrio de la CDMX que quieran recibir los vales.",
        "como_entrar": "Registrarse en el directorio oficial de comercios Mercomuna (requisitos de afiliación por confirmar).",
        "url_oficial": "https://comercios-mercomuna.cdmx.gob.mx/",
        "estado": "existe",
        "fecha_verificacion": FECHA,
    },
    {
        "id": "dimo",
        "nombre": "DiMo (Dinero Móvil, Banxico)",
        "que_es": "Transferencias con el número de celular, sin comisión, desde la app del banco.",
        "para_quien": "Cualquier negocio con cuenta bancaria; no necesita terminal.",
        "como_entrar": "Activar DiMo en la app de su banco y asociar su número de celular.",
        "url_oficial": "https://www.banxico.org.mx",
        "estado": "existe",
        "fecha_verificacion": FECHA,
    },
    {
        "id": "codi",
        "nombre": "CoDi (Cobro Digital, Banxico)",
        "que_es": "Cobro con código QR desde la app del banco, sin comisión.",
        "para_quien": "Negocios con cuenta bancaria que quieran cobrar con QR.",
        "como_entrar": "Activar CoDi en la app de su banco y generar su QR de cobro.",
        "url_oficial": "https://www.banxico.org.mx",
        "estado": "existe",
        "fecha_verificacion": FECHA,
    },
    {
        "id": "crece-mipyme",
        "nombre": "Crece tu Mipyme con pagos digitales",
        "que_es": "Apoyo para que micro y pequeños negocios empiecen a cobrar con medios digitales.",
        "para_quien": "Micro y pequeños negocios.",
        "como_entrar": "Por verificar: no se muestra al comerciante hasta confirmar que existe.",
        "url_oficial": None,
        "estado": "por_verificar",
        "fecha_verificacion": FECHA,
    },
    {
        "id": "puntos-de-barrio",
        "nombre": "Puntos de barrio",
        "que_es": "Propuesta de colonIA: puntos por comprar en negocios de barrio, inspirada en Onnuri (Corea) y PayPay (Japón).",
        "para_quien": "Vecinos y negocios de barrio de la red.",
        "como_entrar": "Es una propuesta para un piloto con SEDECO; todavía no existe.",
        "url_oficial": None,
        "estado": "propuesta",
        "fecha_verificacion": FECHA,
    },
]
