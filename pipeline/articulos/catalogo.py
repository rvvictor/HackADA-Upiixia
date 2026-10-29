"""Artículos comunes en México por clase SCIAN, escritos a mano (sin LLM) con sinónimos chilangos.

Formato: "artículo|sinónimo|sinónimo". Un artículo puede estar en varias clases (pilas: abarrotes y ferretería).
"""

CATALOGO: dict[str, list[str]] = {
    "461110": [  # Abarrotes y misceláneas
        "arroz", "frijol|frijoles", "azucar", "sal", "aceite|aceite de cocina", "huevo|huevos|blanquillos",
        "atun|lata de atun", "sardina", "pasta|sopa de pasta|fideo|sopa de coditos", "harina", "cafe|cafe soluble",
        "galletas", "refresco|chesco", "agua|garrafon|agua embotellada", "jugo", "leche|leche en polvo",
        "papel higienico|papel de baño", "jabon|jabon de barra", "detergente|jabon en polvo", "cloro",
        "suavizante", "servilletas", "pilas|baterias", "focos|foco", "veladoras|veladora", "cerillos",
        "recarga|recarga de celular|tiempo aire", "chiles en lata|chiles jalapeños", "mayonesa", "salsa|salsa valentina",
        "sopa instantanea|maruchan", "cereal", "avena", "chocolate en polvo", "pan de caja|pan bimbo",
        "papitas|papas fritas|sabritas", "cacahuates", "chicles", "consome|consome en polvo", "pure de tomate",
        "gelatina", "rastrillo", "pasta de dientes", "shampoo|champu", "toallas femeninas", "pañales",
        "bolsas de basura", "fibra|fibra para trastes", "vasos desechables", "platos desechables",
    ],
    "461130": [  # Frutas y verduras
        "jitomate|tomate rojo|tomate", "tomate verde|tomatillo", "cebolla", "ajo", "papa|papas", "zanahoria",
        "calabaza|calabacita|calabacitas", "chayote", "nopal|nopales", "chile serrano|serrano", "chile jalapeño",
        "chile poblano", "cilantro", "perejil", "epazote", "lechuga", "pepino", "aguacate", "limon|limones",
        "naranja|naranjas", "platano|platanos", "manzana", "papaya", "piña", "sandia", "melon", "mango",
        "guayaba", "fresa|fresas", "uva", "jicama", "elote|elotes", "ejotes", "brocoli", "coliflor",
        "espinaca", "acelga", "betabel", "rabano", "champiñones|hongos", "tuna", "mamey", "pera", "durazno",
    ],
    "311830": ["tortillas|tortilla|kilo de tortillas", "masa|masa de maiz", "totopos", "tostadas", "tlacoyos"],
    "311812": [
        "bolillo|bolillos", "telera|teleras", "pan dulce", "concha|conchas", "cuernito", "dona|donas",
        "pan de muerto", "rosca", "orejas", "polvorones", "birote", "pastel", "empanadas",
    ],
    "461121": [
        "bistec|bisteces", "carne molida|molida", "carne para asar", "chuleta|chuletas", "costilla",
        "milanesa|milanesas", "chorizo", "cecina", "carne de res", "carne de cerdo|puerco", "longaniza", "pierna",
    ],
    "461122": ["pollo", "pechuga", "pierna y muslo", "alitas", "huacal", "pollo entero", "milanesa de pollo"],
    "461140": [
        "chiles secos|chile seco", "chile guajillo|guajillo", "chile ancho|ancho", "chile de arbol",
        "chile pasilla|pasilla", "chile chipotle", "chile morita", "chile mulato", "pepitas", "ajonjoli",
        "canela", "comino", "pimienta", "oregano", "clavo", "hoja de laurel|laurel", "frijol a granel",
        "lentejas", "garbanzo", "habas", "maiz pozolero", "arroz a granel", "chia", "flor de jamaica|jamaica",
        "tamarindo", "achiote", "mole|mole en pasta",
    ],
    "461150": [
        "queso|queso fresco", "queso oaxaca|quesillo", "queso panela|panela", "crema", "jamon", "salchicha|salchichas",
        "mantequilla", "yogur|yogurt", "requeson", "queso manchego", "chorizo de cremeria", "tocino", "leche bronca",
    ],
    "461160": ["dulces", "piñata|piñatas", "chocolates", "paletas", "obleas", "glaseado", "chispas de chocolate"],
    "463211": [
        "playera|playeras", "pantalon|pantalones", "sudadera", "chamarra", "calcetines", "ropa interior",
        "uniforme escolar|uniforme", "vestido", "falda", "pijama", "suéter|sueter", "camisa", "short|shorts",
        "ropa para niño|ropa de niño", "ropa de bebe", "gorra", "bufanda", "mallas",
    ],
    "463310": [
        "tenis|tenis para niño|tenis para niña", "zapatos|zapato", "zapatos escolares", "sandalias|huaraches",
        "botas", "pantuflas", "chanclas", "zapatos de vestir", "agujetas",
    ],
    "464111": [
        "paracetamol", "ibuprofeno", "alcohol", "algodon", "curitas|banditas", "gasas", "suero|suero oral",
        "medicina|medicinas", "termometro", "jarabe", "pastillas para la tos", "cubrebocas", "condones",
        "vitaminas", "pomada",
    ],
    "465311": [
        "cuaderno|cuadernos|libreta", "lapiz|lapices", "pluma|plumas|boligrafo", "colores", "pegamento|resistol",
        "tijeras", "hojas blancas", "cartulina", "copias|fotocopias", "impresiones", "regla", "goma|borrador",
        "sacapuntas", "mochila", "plastilina", "papel china", "papel crepe", "folder|folders", "marcadores|plumones",
        "forro|forros", "calculadora", "engrapadora", "cinta adhesiva|diurex",
    ],
    "467111": [
        "pilas|baterias", "focos|foco", "clavos", "tornillos", "pintura", "brocha", "cinta de aislar",
        "cable|cable electrico", "contacto|enchufe", "extension", "martillo", "desarmador", "pinzas", "candado",
        "llave de agua|llave", "manguera", "cemento", "pegamento para tubo", "tubo pvc", "lija", "silicon",
        "cerradura", "bisagras", "escoba", "trapeador", "cubeta", "jerga", "foco led", "apagador",
    ],
    "466410": [
        "funda de celular|funda", "cargador|cargador de celular", "cable usb", "audifonos", "mica|protector de pantalla",
        "memoria usb", "recarga|tiempo aire", "chip|chip telefonico", "bocina",
    ],
    "722514": [
        "tacos|taco", "tacos al pastor|pastor", "tacos de suadero|suadero", "tacos de canasta", "tortas|torta",
        "quesadillas|quesadilla", "gringas", "tacos de guisado", "tacos de carnitas|carnitas", "barbacoa",
        "tlayudas", "sopes", "huaraches de comida", "gorditas", "flautas", "pambazos", "tamales|tamal", "atole",
    ],
    "722519": [
        "comida corrida", "menu del dia", "caldo de pollo|caldo", "sopa de fideo", "pozole", "enchiladas",
        "chilaquiles", "mole con pollo", "arroz con huevo", "guisado|guisados", "agua de sabor|agua fresca",
        "desayuno", "chiles rellenos", "pancita|menudo", "consome de barbacoa",
    ],
    "811430": ["reparacion de zapatos|arreglo de zapatos", "tapas para zapato|tapas", "suelas", "boleado|bolear zapatos"],
    "812110": [
        "corte de cabello|corte de pelo|corte", "tinte|pintar el cabello", "peinado", "uñas|manicure",
        "pedicure", "barba|arreglo de barba", "depilacion", "alaciado", "permanente", "rayos|luces",
    ],
    "811211": [
        "reparacion de celular|arreglo de celular", "cambio de pantalla", "cambio de bateria", "liberar celular",
        "reparacion de tablet", "reparacion de computadora", "reparacion de television",
    ],
}

CATEGORIA_UI = {
    "461110": "Abarrotes", "461130": "Frutas y verduras", "311830": "Tortillería", "311812": "Panadería",
    "461121": "Carnicería", "461122": "Pollería", "461140": "Chiles y semillas", "461150": "Cremería",
    "461160": "Dulcería", "463211": "Ropa", "463310": "Calzado", "464111": "Farmacia", "465311": "Papelería",
    "467111": "Ferretería", "466410": "Celulares", "722514": "Taquería", "722519": "Fonda",
    "811430": "Reparación de calzado", "812110": "Estética", "811211": "Reparación de celulares",
}
