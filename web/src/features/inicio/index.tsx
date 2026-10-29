import type { CSSProperties, ReactNode } from "react";
import {
  ArrowRightIcon,
  CheckCircleIcon,
  GraduationCapIcon,
  MapTrifoldIcon,
  StorefrontIcon,
  UsersThreeIcon,
  HouseIcon,
} from "@phosphor-icons/react";
import { Cifra } from "./Cifra";
import { RejillaHex } from "./Hexagonos";
import "./inicio.css";

export const route = "inicio";
export const label = "Inicio";
export const order = 0;

const DONA_LUPE = "alta-puesto-de-dona-lupe";

type Acento = { acc: string };
const ROSA: Acento = { acc: "var(--ci-rosa-luz)" };
const CEMPA: Acento = { acc: "var(--ci-cempasuchil)" };
const JADE: Acento = { acc: "var(--ci-jade-luz)" };
const ANIL: Acento = { acc: "#7f9be6" };

function Enlace({ href, children, className = "" }: { href: string; children: ReactNode; className?: string }) {
  return (
    <a href={href} className={className}>
      {children}
    </a>
  );
}

function Hero() {
  return (
    <section className="ci-hero" aria-labelledby="titulo-colonia">
      <div className="ci-hero-glow" aria-hidden="true" />
      <div className="ci-wrap ci-hero-grid">
        <div>
          <h1 id="titulo-colonia" className="ci-marca">
            colon<span className="ci-marca-ia">IA</span>
          </h1>
          <p className="ci-tagline">La red viva de la economía de barrio</p>
          <p className="ci-pitch">
            Mira dónde se mueve el dinero del barrio, arma tu ruta sin cadenas y aparece en la red con una nota de voz.
          </p>
          <div className="ci-ctas">
            <Enlace href="#/sedeco" className="ci-btn ci-btn-primario">
              Ver el mapa de SEDECO
              <ArrowRightIcon size={20} weight="bold" aria-hidden="true" />
            </Enlace>
            <Enlace href="#/usuario" className="ci-btn ci-btn-sec">
              Armar mi ruta
            </Enlace>
          </div>
        </div>

        <figure className="ci-hero-visual" style={{ margin: 0 }}>
          <RejillaHex />
          <figcaption className="ci-hero-etiqueta">
            <span className="ci-punto-vivo" aria-hidden="true" />
            Demo con datos simulados
          </figcaption>
        </figure>
      </div>
    </section>
  );
}

const CIFRAS = [
  {
    valor: 1367,
    decimales: 0,
    texto: "tianguis en la CDMX sin un mapa vivo donde aparezcan juntos",
    acento: CEMPA,
    fuente: (
      <>
        Fuente:{" "}
        <a href="https://www.chilango.com/noticias/crean-mapa-con-todos-los-tianguis-de-cdmx-ubicaciones-dias-y-horarios/" target="_blank" rel="noreferrer">
          Chilango, mapa de tianguis CDMX
        </a>
      </>
    ),
  },
  {
    valor: 6.7,
    decimales: 1,
    sufijo: "%",
    texto: "de los negocios vendió en línea (2023)",
    acento: ROSA,
    fuente: (
      <>
        Fuente:{" "}
        <a href="https://deet.trabajo.cdmx.gob.mx/storage/app/media/uploaded-files/b03-censos-economicos-012025docx.pdf" target="_blank" rel="noreferrer">
          STyFE CDMX con Censos Económicos 2024
        </a>
      </>
    ),
  },
  {
    valor: 42.8,
    decimales: 1,
    prefijo: "−",
    sufijo: "%",
    texto: "de caída en la facturación promedio de tienditas, 2017 a 2023 (nacional)",
    acento: JADE,
    fuente: (
      <>
        Fuente:{" "}
        <a href="https://elceo.com/negocios/tiendas-de-la-esquina-pierden-clientes-sus-ventas-cayeron-42-8-en-un-sexenio/" target="_blank" rel="noreferrer">
          El CEO con datos de ANPEC
        </a>
      </>
    ),
  },
];

function Problema() {
  return (
    <section className="ci-sec ci-sec-alt" aria-labelledby="titulo-problema">
      <div className="ci-wrap">
        <span className="ci-kicker">El problema</span>
        <h2 id="titulo-problema" className="ci-h2">
          La red del barrio existe en la calle, pero no en ningún mapa.
        </h2>
        <div className="ci-cifras">
          {CIFRAS.map((c) => (
            <article key={c.texto} className="ci-cifra-card" style={{ "--acc": c.acento.acc } as CSSProperties}>
              <p className="ci-cifra-num">
                <Cifra valor={c.valor} decimales={c.decimales} prefijo={c.prefijo} sufijo={c.sufijo} />
              </p>
              <p className="ci-cifra-txt">{c.texto}</p>
              <p className="ci-fuente">{c.fuente}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

/* Mini-ilustraciones SVG (sin imágenes): cada paso tiene la suya. */
function IluVer() {
  const celdas = [
    [40, 30, "#1f3b8c"], [70, 30, "#00a86b"], [100, 30, "#1f3b8c"], [55, 52, "#1f3b8c"],
    [85, 52, "#ffb703"], [115, 52, "#1f3b8c"], [40, 74, "#1f3b8c"], [70, 74, "#e6007e"], [100, 74, "#00a86b"],
  ] as const;
  return (
    <svg viewBox="0 0 240 120" className="ci-ilu" aria-hidden="true">
      {celdas.map(([x, y, c], i) => (
        <polygon
          key={i}
          points={hexPts(x, y, 15)}
          fill={c}
          fillOpacity={c === "#1f3b8c" ? 0.55 : 0.9}
        />
      ))}
      <circle cx="185" cy="60" r="22" fill="none" stroke="#ffb703" strokeWidth="2" strokeDasharray="4 5" />
      <text x="185" y="64" textAnchor="middle" fill="#ffb703" fontSize="12" fontWeight="700">falta</text>
    </svg>
  );
}

function IluRuta() {
  return (
    <svg viewBox="0 0 240 120" className="ci-ilu" aria-hidden="true">
      <path className="ci-ruta" d="M28 84 C 70 30, 110 100, 150 52 S 205 30, 214 40" fill="none" stroke="#ffb703" strokeWidth="3" strokeLinecap="round" />
      {[[28, 84], [96, 74], [150, 52], [214, 40]].map(([x, y], i) => (
        <g key={i}>
          <circle cx={x} cy={y} r="9" fill="#0b0f14" stroke="#00a86b" strokeWidth="3" />
        </g>
      ))}
      <text x="28" y="110" fill="#b9c2d0" fontSize="11">0 cadenas</text>
    </svg>
  );
}

function IluVoz() {
  const barras = [18, 34, 52, 26, 60, 40, 22, 48, 30];
  return (
    <svg viewBox="0 0 240 120" className="ci-ilu" aria-hidden="true">
      {barras.map((h, i) => (
        <rect
          key={i}
          className="ci-barra"
          x={36 + i * 20}
          y={60 - h / 2}
          width="10"
          height={h}
          rx="5"
          fill="#e6007e"
          style={{ animationDelay: `${i * 0.11}s` }}
        />
      ))}
    </svg>
  );
}

function hexPts(cx: number, cy: number, r: number) {
  return Array.from({ length: 6 }, (_, i) => {
    const a = (Math.PI / 3) * i + Math.PI / 6;
    return `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`;
  }).join(" ");
}

const PASOS = [
  {
    titulo: "SEDECO ve dónde falta comercio",
    texto: "El mapa muestra dónde se mueve el dinero y en qué zonas no hay negocios de barrio.",
    ilu: <IluVer />,
    href: "#/sedeco",
    cta: "Ver el mapa",
    acento: CEMPA,
  },
  {
    titulo: "La vecina arma su ruta sin cadenas",
    texto: "Escribe su lista del mandado y recibe una ruta a pie por tiendas de su colonia.",
    ilu: <IluRuta />,
    href: "#/usuario",
    cta: "Armar una ruta",
    acento: JADE,
  },
  {
    titulo: "Doña Lupe se suma con una nota de voz",
    texto: "Manda un audio por Telegram y su puesto aparece en el mapa, en las rutas y en su página.",
    ilu: <IluVoz />,
    href: `#/negocio/${DONA_LUPE}`,
    cta: "Ver su puesto",
    acento: ROSA,
  },
];

function Como() {
  return (
    <section className="ci-sec" aria-labelledby="titulo-como">
      <div className="ci-wrap">
        <span className="ci-kicker">Cómo funciona</span>
        <h2 id="titulo-como" className="ci-h2">
          Tres pasos: ver, comprar y sumarse.
        </h2>
        <ol className="ci-pasos">
          {PASOS.map((p) => (
            <li key={p.titulo} className="ci-paso" style={{ "--acc": p.acento.acc } as CSSProperties}>
              <div className="ci-paso-cabeza">
                <span className="ci-paso-num" aria-hidden="true" />
                <h3>{p.titulo}</h3>
              </div>
              {p.ilu}
              <p>{p.texto}</p>
              <a href={p.href} className="ci-paso-link">
                {p.cta}
                <ArrowRightIcon size={18} weight="bold" aria-hidden="true" />
              </a>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

const PARA_QUIEN = [
  { titulo: "SEDECO y alcaldías", texto: "Ven dónde se mueve el dinero y dónde falta comercio, por día y hora.", icono: <MapTrifoldIcon size={26} />, acento: CEMPA },
  { titulo: "Vecinas", texto: "Resuelven su lista del mandado a pie, en negocios de su colonia.", icono: <HouseIcon size={26} />, acento: JADE },
  { titulo: "Comerciantes de barrio", texto: "Aparecen en la red con una nota de voz, sin descargar nada.", icono: <StorefrontIcon size={26} />, acento: ROSA },
  { titulo: "Colectivos INJUVE", texto: "Mantienen los datos del barrio y lo llevan a la calle.", icono: <UsersThreeIcon size={26} />, acento: ANIL },
];

function ParaQuien() {
  return (
    <section className="ci-sec" aria-labelledby="titulo-para">
      <div className="ci-wrap">
        <span className="ci-kicker">Para quién</span>
        <h2 id="titulo-para" className="ci-h2">
          Para quien hace funcionar el barrio.
        </h2>
        <ul className="ci-quien">
          {PARA_QUIEN.map((p) => (
            <li key={p.titulo} style={{ "--acc": p.acento.acc } as CSSProperties}>
              <span style={{ color: p.acento.acc, display: "inline-flex", marginBottom: 12 }} aria-hidden="true">
                {p.icono}
              </span>
              <h3>{p.titulo}</h3>
              <p>{p.texto}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

const ALCALDIAS = 16;

function Escala() {
  return (
    <section className="ci-sec ci-sec-alt" aria-labelledby="titulo-escala">
      <div className="ci-wrap">
        <span className="ci-kicker">Cómo escala</span>
        <h2 id="titulo-escala" className="ci-h2">
          Lo que funciona en una colonia, sirve en las 16 alcaldías.
        </h2>
        <div className="ci-dos">
          <article className="ci-panel">
            <h3>Escala sin costo de instalación</h3>
            <ul className="ci-lista">
              <li>
                <CheckCircleIcon size={22} weight="fill" aria-hidden="true" />
                <span>
                  <b>16 alcaldías, un mismo mapa.</b> Cada alcaldía se suma con sus propios puestos y tianguis.
                </span>
              </li>
              <li>
                <CheckCircleIcon size={22} weight="fill" aria-hidden="true" />
                <span>
                  <b>Entra por Telegram.</b> Un comerciante da de alta su puesto con una nota de voz.
                </span>
              </li>
              <li>
                <CheckCircleIcon size={22} weight="fill" aria-hidden="true" />
                <span>
                  <b>Datos abiertos.</b> Se apoya en fuentes públicas como DENUE del INEGI y tianguis de SEDECO.
                </span>
              </li>
              <li>
                <CheckCircleIcon size={22} weight="fill" aria-hidden="true" />
                <span>
                  <b>Costo casi cero.</b> Sin app que descargar y sin licencias que pagar.
                </span>
              </li>
            </ul>
            <div className="ci-alcaldias" role="img" aria-label={`Las ${ALCALDIAS} alcaldías de la CDMX; dos encendidas en la demo`}>
              {Array.from({ length: ALCALDIAS }, (_, i) => (
                <span key={i} className={i === 4 || i === 9 ? "on" : undefined} aria-hidden="true">
                  {i + 1}
                </span>
              ))}
            </div>
            <p style={{ margin: "10px 0 0", color: "var(--ci-texto-2)", fontSize: "0.9rem" }}>
              Esquema simulado: las alcaldías encendidas son solo de demo.
            </p>
          </article>

          <article className="ci-panel">
            <h3>Triple hélice</h3>
            <p style={{ margin: 0, color: "var(--ci-texto-2)" }}>
              Gobierno, comercio y academia sostienen la misma red. Cada quien aporta lo que sabe hacer.
            </p>
            <div className="ci-helice">
              <div style={{ "--k": "#ffb703" } as CSSProperties}>
                <i aria-hidden="true" />
                <span>
                  <b>Gobierno</b>
                  <small>SEDECO publica el estándar abierto y usa el mapa para decidir.</small>
                </span>
              </div>
              <div style={{ "--k": "#00a86b" } as CSSProperties}>
                <i aria-hidden="true" />
                <span>
                  <b>Comercio</b>
                  <small>CANACOPE y los comerciantes de barrio suman sus puestos y su voz.</small>
                </span>
              </div>
              <div style={{ "--k": "#e6007e" } as CSSProperties}>
                <i aria-hidden="true" />
                <span>
                  <b>Academia</b>
                  <small>El IPN aporta investigación para medir qué cambia en el barrio.</small>
                </span>
              </div>
            </div>
            <p style={{ margin: "16px 0 0", fontSize: "0.9rem", color: "var(--ci-texto-2)", display: "flex", gap: 8, alignItems: "center" }}>
              <GraduationCapIcon size={18} aria-hidden="true" /> Propuesta, no compromiso firmado.
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}

function Cierre() {
  return (
    <section className="ci-cierre" aria-labelledby="titulo-cierre">
      <div className="ci-wrap">
        <h2 id="titulo-cierre">Pon tu barrio en el mapa.</h2>
        <p>Mira la red de SEDECO o arma tu ruta de hoy. Todo en la misma demo.</p>
        <div className="ci-ctas">
          <Enlace href="#/sedeco" className="ci-btn ci-btn-primario">
            Ver el mapa de SEDECO
            <ArrowRightIcon size={20} weight="bold" aria-hidden="true" />
          </Enlace>
          <Enlace href="#/usuario" className="ci-btn ci-btn-jade">
            Armar mi ruta
          </Enlace>
        </div>
      </div>
    </section>
  );
}

export default function Inicio() {
  return (
    <div className="ci">
      <Hero />
      <Problema />
      <Como />
      <ParaQuien />
      <Escala />
      <Cierre />
      <footer className="ci-pie">
        <div className="ci-wrap">
          <p>Hecho en el Chilangatón 2026 · datos de la demo simulados donde se indica</p>
        </div>
      </footer>
    </div>
  );
}
