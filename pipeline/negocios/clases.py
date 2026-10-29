"""Clases SCIAN del comercio y servicios de barrio que usa la demo.

Claves SCIAN 2018 tomadas como referencia; antes de usar el DENUE real hay que confirmarlas en el catálogo de INEGI
(IDEA.md A.5: ningún agente escribe claves de memoria para datos reales; aquí alimentan datos simulados).
"""

CLASES: dict[str, str] = {
    "461110": "Abarrotes, ultramarinos y misceláneas",
    "461121": "Carnicería",
    "461122": "Pollería",
    "461130": "Frutas y verduras frescas",
    "461140": "Semillas, granos, especias y chiles secos",
    "461150": "Lácteos y embutidos (cremería)",
    "461160": "Dulces y materias primas para repostería",
    "311812": "Panadería tradicional",
    "311830": "Tortillería y molino de nixtamal",
    "463211": "Ropa",
    "463310": "Calzado",
    "464111": "Farmacia",
    "465311": "Papelería",
    "467111": "Ferretería y tlapalería",
    "466410": "Celulares y accesorios",
    "722514": "Taquería",
    "722519": "Fonda y cocina económica",
    "811430": "Reparación de calzado",
    "812110": "Estética y peluquería",
    "811211": "Reparación de celulares y electrónicos",
    "462111": "Supermercado",
    "462112": "Minisúper y tienda de conveniencia",
    "462210": "Tienda departamental",
}
