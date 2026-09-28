import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="GRIY | Reto Petrolero", page_icon="🛢️", layout="wide")

SUPABASE_URL = "https://xhizwsiitcvjnafmpplf.supabase.co"
SUPABASE_KEY = "sb_publishable_yLYAPUcEBf5X2ZV6BEfy0w_NPzf58zx"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

ROUNDS = {
    1: {
        "emoji": "🧰", "title": "Arranque de la planta", "tag": "CONSUMIBLES",
        "bg": "linear-gradient(135deg,#f59e0b 0%,#ef4444 48%,#7c2d12 100%)",
        "scenario": "La planta comienza el periodo y necesita lubricantes, filtros, sellos y otros consumibles para operar.",
        "question": "¿Cómo vas a abastecer los consumibles?",
        "options": [
            {"title":"Comprar solo lo indispensable","desc":"Operas con cautela y conservas más efectivo.","concept":"OPEX y control de efectivo","payload":(1200000,0,0,0,0),"result":"Elegiste una operación austera: cuidaste caja, pero limitaste la actividad de la planta."},
            {"title":"Comprar inventario completo","desc":"Gastas más ahora para operar con mayor intensidad.","concept":"OPEX y costo de operación","payload":(2500000,0,0,0,0),"result":"Aseguraste insumos suficientes para operar fuerte; sacrificaste efectivo a cambio de mayor actividad."},
            {"title":"Comprar más y financiar parte","desc":"Aseguras inventario sin usar todo tu efectivo, pero aumenta la deuda.","concept":"OPEX + financiamiento","payload":(3200000,0,0,0,1500000),"result":"Protegiste la operación usando financiamiento: ganaste margen de maniobra, pero asumiste nueva deuda."},
        ],
    },
    2: {
        "emoji": "🔧", "title": "Una bomba empieza a vibrar", "tag": "MANTENIMIENTO",
        "bg": "linear-gradient(135deg,#38bdf8 0%,#2563eb 52%,#172554 100%)",
        "scenario": "Mantenimiento detecta vibración anormal en una bomba importante. Todavía funciona, pero puede empeorar.",
        "question": "¿Qué haces con la bomba?",
        "options": [
            {"title":"Mantenimiento preventivo ahora","desc":"Bajas un poco la operación y gastas en prevención.","concept":"OPEX preventivo","payload":(1500000,0,800000,0,0),"result":"Atendiste la bomba antes de una falla mayor. Tuviste un gasto preventivo y una operación más controlada."},
            {"title":"Seguir operando y posponer","desc":"Produces más hoy, pero no fortaleces prevención.","concept":"Riesgo operativo","payload":(2100000,0,0,0,0),"result":"Priorizaste producción inmediata. Conservaste recursos de mantenimiento, pero asumiste más riesgo operativo."},
            {"title":"Reacondicionar el conjunto completo","desc":"Haces una intervención mayor y mejoras activos.","concept":"CAPEX + mantenimiento","payload":(1000000,1500000,800000,0,0),"result":"Hiciste una intervención profunda: gastaste más hoy, pero fortaleciste la capacidad física de la empresa."},
        ],
    },
    3: {
        "emoji": "🏭", "title": "Oferta de una máquina nueva", "tag": "INVERSIÓN",
        "bg": "linear-gradient(135deg,#a855f7 0%,#7c3aed 46%,#312e81 100%)",
        "scenario": "Un proveedor ofrece equipo nuevo que puede modernizar parte de la planta y elevar la eficiencia futura.",
        "question": "¿Qué haces con la inversión?",
        "options": [
            {"title":"Comprar con efectivo","desc":"Desembolsas mucho hoy y aumentas tus activos.","concept":"CAPEX","payload":(1400000,3500000,0,0,0),"result":"Compraste la máquina con recursos propios. Bajó tu efectivo, pero aumentó tu activo fijo y tu capacidad futura."},
            {"title":"Comprar con apoyo de financiamiento","desc":"Modernizas sin vaciar la caja, pero tomas deuda.","concept":"CAPEX + deuda","payload":(1800000,2000000,0,0,2500000),"result":"Modernizaste usando deuda: preservaste más efectivo, pero ahora cargas un compromiso financiero adicional."},
            {"title":"No comprar y seguir con el equipo actual","desc":"Conservas efectivo y priorizas la operación presente.","concept":"Liquidez vs inversión","payload":(2000000,0,0,0,0),"result":"No invertiste en equipo nuevo. Protegiste tu caja, pero renunciaste a mejorar capacidad productiva en esta ronda."},
        ],
    },
    4: {
        "emoji": "📈", "title": "Suben los precios de insumos", "tag": "COSTOS",
        "bg": "linear-gradient(135deg,#fb7185 0%,#f97316 50%,#9a3412 100%)",
        "scenario": "Los proveedores anuncian un aumento de precios. Mantener el mismo nivel de producción será más exigente para la caja.",
        "question": "¿Cómo respondes al aumento de costos?",
        "options": [
            {"title":"Mantener producción alta","desc":"Aceptas un uso fuerte de efectivo para sostener ventas.","concept":"Costo variable","payload":(3500000,0,0,0,0),"result":"Defendiste el volumen de operación pese a los costos. Moviste más dinero y apostaste por sostener ingresos."},
            {"title":"Reducir producción temporalmente","desc":"Proteges liquidez y operas de forma moderada.","concept":"Liquidez","payload":(1500000,0,0,0,0),"result":"Bajaste el ritmo para proteger efectivo. Tu exposición al costo fue menor, pero también tu actividad comercial."},
            {"title":"Comprar fuerte usando crédito","desc":"Aseguras insumos y pides apoyo financiero.","concept":"Inventario + financiamiento","payload":(3000000,0,0,0,2000000),"result":"Cubres la necesidad de insumos con financiamiento. Mantienes operación, pero incrementas obligaciones futuras."},
        ],
    },
    5: {
        "emoji": "🏦", "title": "El banco ofrece crédito", "tag": "FINANCIAMIENTO",
        "bg": "linear-gradient(135deg,#4f46e5 0%,#0ea5e9 52%,#164e63 100%)",
        "scenario": "El banco ofrece una línea de crédito. Puede darte flexibilidad, pero cada peso prestado aumenta deuda e intereses.",
        "question": "¿Cuánto financiamiento tomas?",
        "options": [
            {"title":"Tomar un crédito grande","desc":"Tienes mucha caja para operar, con mayor deuda.","concept":"Deuda y gasto financiero","payload":(3000000,0,0,0,5000000),"result":"Tomaste un crédito grande. Ganaste capacidad inmediata de gasto, pero aumentaron deuda e intereses."},
            {"title":"Tomar un crédito moderado","desc":"Buscas equilibrio entre efectivo y deuda.","concept":"Estructura financiera","payload":(2200000,0,0,0,2000000),"result":"Elegiste financiamiento moderado. Mejoraste caja sin llevar la deuda al nivel de la opción agresiva."},
            {"title":"No pedir crédito","desc":"Operas únicamente con recursos disponibles.","concept":"Autofinanciamiento","payload":(1500000,0,0,0,0),"result":"Rechazaste el préstamo. Evitaste nueva deuda, pero tu capacidad de expansión inmediata fue menor."},
        ],
    },
    6: {
        "emoji": "👷", "title": "Capacitación del personal", "tag": "PERSONAL",
        "bg": "linear-gradient(135deg,#22c55e 0%,#14b8a6 52%,#115e59 100%)",
        "scenario": "Se detectan oportunidades de mejora en procedimientos operativos. Puedes invertir en capacitación o mantener el esquema actual.",
        "question": "¿Qué nivel de capacitación autorizas?",
        "options": [
            {"title":"Programa intensivo","desc":"Mayor gasto hoy para fortalecer prevención y operación.","concept":"OPEX y prevención","payload":(1400000,0,1500000,0,0),"result":"Hiciste una capacitación intensiva. Aumentó el gasto del periodo, pero fortaleciste prevención y control acumulados."},
            {"title":"Capacitación corta","desc":"Gasto moderado y menor interrupción de la operación.","concept":"OPEX","payload":(1800000,0,600000,0,0),"result":"Elegiste una capacitación breve: mantuviste más actividad con una inversión moderada en prevención."},
            {"title":"No capacitar este periodo","desc":"No gastas en formación y mantienes producción.","concept":"Ahorro de corto plazo","payload":(2100000,0,0,0,0),"result":"Evitaste el gasto de capacitación. Conservaste recursos hoy, pero no fortaleciste los controles de la empresa."},
        ],
    },
    7: {
        "emoji": "⏸️", "title": "¿Parar la planta para mantenimiento?", "tag": "PARO PROGRAMADO",
        "bg": "linear-gradient(135deg,#64748b 0%,#334155 48%,#f59e0b 100%)",
        "scenario": "Ingeniería propone un paro parcial para revisar equipos críticos. Parar cuesta producción; no parar mantiene ventas pero deja el riesgo.",
        "question": "¿Cuál es tu estrategia?",
        "options": [
            {"title":"Paro parcial preventivo","desc":"Reduces operación y gastas en mantenimiento.","concept":"Costo de oportunidad + OPEX","payload":(700000,0,1500000,0,0),"result":"Aceptaste un paro preventivo. Perdiste actividad inmediata, pero invertiste en reducir riesgo operacional."},
            {"title":"Seguir operando normalmente","desc":"No haces paro y priorizas producción.","concept":"Riesgo vs ingreso","payload":(2600000,0,0,0,0),"result":"Mantienes la planta trabajando. Generas más actividad hoy, pero sin el colchón preventivo de un paro programado."},
            {"title":"Cambiar un componente crítico","desc":"Haces una parada corta y conviertes parte del gasto en activo.","concept":"CAPEX + mantenimiento","payload":(1100000,2000000,500000,0,0),"result":"Aprovechaste la intervención para renovar un componente. Fue costoso, pero aumentó tu activo fijo."},
        ],
    },
    8: {
        "emoji": "🚨", "title": "Alerta de huachicol", "tag": "RIESGO ILÍCITO",
        "bg": "linear-gradient(135deg,#dc2626 0%,#991b1b 50%,#450a0a 100%)",
        "scenario": "Se detectan indicios de posible robo de hidrocarburos. En este juego, la inversión previa y actual en controles reduce el impacto del evento.",
        "question": "¿Cómo proteges la operación?",
        "options": [
            {"title":"Blindaje fuerte de vigilancia y monitoreo","desc":"Realizas un gasto importante en controles.","concept":"Control interno + OPEX","payload":(1500000,0,2500000,0,0),"result":"Reforzaste fuertemente controles. Tu gasto subió, pero llegaste mejor protegido al evento de huachicol."},
            {"title":"Refuerzo moderado","desc":"Buscas equilibrio entre costo y protección.","concept":"Gestión de riesgos","payload":(1800000,0,1200000,0,0),"result":"Aplicaste un refuerzo moderado. No gastaste tanto como en el blindaje total, pero redujiste parte de la exposición."},
            {"title":"No agregar controles","desc":"Conservas efectivo y asumes el riesgo del evento.","concept":"Riesgo financiero","payload":(2200000,0,0,0,0),"result":"Decidiste no gastar más en controles. Tu operación siguió con fuerza, pero quedaste más expuesto a la pérdida por huachicol."},
        ],
    },
    9: {
        "emoji": "⛽", "title": "Demanda alta de combustible", "tag": "VENTAS",
        "bg": "linear-gradient(135deg,#06b6d4 0%,#0284c7 50%,#1d4ed8 100%)",
        "scenario": "La demanda local aumenta. Hay oportunidad de vender más, pero producir más también exige más capital de trabajo.",
        "question": "¿Qué nivel de producción eliges?",
        "options": [
            {"title":"Aprovechar al máximo la demanda","desc":"Producción alta y uso fuerte de recursos.","concept":"Ingresos y capital de trabajo","payload":(5000000,0,0,0,0),"result":"Fuiste agresivo en ventas. Moviste mucho efectivo y aprovechaste el mercado al máximo."},
            {"title":"Aumentar producción con prudencia","desc":"Subes ventas sin llevar la operación al máximo.","concept":"Margen y liquidez","payload":(3300000,0,0,0,0),"result":"Aprovechaste la demanda de forma moderada. Buscaste crecimiento sin tensionar tanto la caja."},
            {"title":"Mantener una producción conservadora","desc":"Proteges efectivo aunque dejas ventas sobre la mesa.","concept":"Liquidez","payload":(1600000,0,0,0,0),"result":"Conservaste liquidez. La empresa quedó más cómoda de caja, pero no capturó toda la oportunidad de mercado."},
        ],
    },
    10: {
        "emoji": "🚚", "title": "Problema de logística", "tag": "DISTRIBUCIÓN",
        "bg": "linear-gradient(135deg,#f97316 0%,#eab308 52%,#854d0e 100%)",
        "scenario": "Un problema de transporte amenaza entregas. Debes decidir entre pagar una solución rápida, reorganizar o aceptar retrasos.",
        "question": "¿Cómo resuelves la logística?",
        "options": [
            {"title":"Contratar transporte de emergencia","desc":"Es caro, pero sostienes un nivel alto de operación.","concept":"OPEX logístico","payload":(2500000,0,800000,0,0),"result":"Pagaste una solución rápida. Protegiste entregas, aunque elevaste el gasto operativo del periodo."},
            {"title":"Reorganizar rutas con recursos propios","desc":"Mantienes actividad media sin gasto extraordinario fuerte.","concept":"Eficiencia operativa","payload":(2000000,0,300000,0,0),"result":"Reorganizaste la distribución. Tuviste un costo moderado y evitaste una respuesta de emergencia más cara."},
            {"title":"Aceptar retrasos y ahorrar","desc":"Gastas poco, pero reduces actividad comercial.","concept":"Costo de oportunidad","payload":(1000000,0,0,0,0),"result":"Preferiste ahorrar. La empresa conservó caja, pero trabajó con menor intensidad durante el problema logístico."},
        ],
    },
    11: {
        "emoji": "🏗️", "title": "Proyecto de infraestructura", "tag": "EXPANSIÓN",
        "bg": "linear-gradient(135deg,#0f766e 0%,#059669 48%,#ca8a04 100%)",
        "scenario": "Surge un proyecto para mejorar infraestructura. Puedes pagarlo, financiarlo o rechazarlo.",
        "question": "¿Cómo manejas el proyecto?",
        "options": [
            {"title":"Invertir con recursos propios","desc":"Usas efectivo y aumentas activos.","concept":"CAPEX","payload":(1500000,3500000,0,0,0),"result":"Financiaste la infraestructura con caja propia. Disminuyó efectivo, pero aumentó el patrimonio operativo de la empresa."},
            {"title":"Co-invertir con financiamiento","desc":"Haces la inversión y tomas deuda para no vaciar la caja.","concept":"CAPEX + financiamiento","payload":(1800000,3500000,0,0,2500000),"result":"Realizaste el proyecto con apoyo financiero. Conservaste más caja, pero elevaste la deuda."},
            {"title":"Rechazar el proyecto","desc":"No aumentas activos y mantienes recursos líquidos.","concept":"Liquidez vs crecimiento","payload":(2300000,0,0,0,0),"result":"No construiste infraestructura nueva. La empresa quedó más líquida, pero sin ese crecimiento de capacidad."},
        ],
    },
    12: {
        "emoji": "💰", "title": "¿Qué hacemos con el dinero?", "tag": "UTILIDADES",
        "bg": "linear-gradient(135deg,#7c3aed 0%,#db2777 48%,#831843 100%)",
        "scenario": "La empresa tiene que decidir qué priorizar: deuda, reinversión o conservar efectivo.",
        "question": "¿Dónde colocas los recursos?",
        "options": [
            {"title":"Pagar deuda","desc":"Disminuyes obligaciones y futuros intereses.","concept":"Desapalancamiento","payload":(1500000,0,0,3000000,0),"result":"Reduciste deuda. Tu caja bajó, pero mejoraste la estructura financiera y los compromisos futuros."},
            {"title":"Reinvertir en activos","desc":"Compras equipo y apuestas por capacidad futura.","concept":"CAPEX","payload":(1600000,3000000,0,0,0),"result":"Reinvertiste en activos. Sacrificaste liquidez inmediata para fortalecer la capacidad de largo plazo."},
            {"title":"Guardar efectivo","desc":"No haces inversión ni pago extraordinario.","concept":"Reserva de liquidez","payload":(1000000,0,0,0,0),"result":"Guardaste efectivo. La empresa quedó con mayor colchón de caja, aunque sin reducir deuda ni ampliar activos."},
        ],
    },
    13: {
        "emoji": "🔍", "title": "Auditoría de inventarios", "tag": "CONTROL INTERNO",
        "bg": "linear-gradient(135deg,#475569 0%,#0891b2 48%,#0e7490 100%)",
        "scenario": "Hay diferencias entre registros e inventario físico. Una revisión puede costar dinero, pero ayuda a detectar fugas y pérdidas.",
        "question": "¿Qué tan profunda será la auditoría?",
        "options": [
            {"title":"Auditoría completa","desc":"Revisas inventarios y controles con profundidad.","concept":"Control interno","payload":(1200000,0,2000000,0,0),"result":"Aplicaste una auditoría completa. Gastaste más, pero acumulaste una defensa mayor frente a diferencias y pérdidas."},
            {"title":"Revisión dirigida a áreas críticas","desc":"Gasto moderado y enfoque selectivo.","concept":"Control basado en riesgo","payload":(1800000,0,800000,0,0),"result":"Hiciste una revisión focalizada. Equilibraste continuidad operativa y gasto de control."},
            {"title":"No auditar por ahora","desc":"Mantienes producción y ahorras el costo de revisión.","concept":"Riesgo de control","payload":(2200000,0,0,0,0),"result":"Pospusiste la auditoría. Ahorraste recursos hoy, pero quedaste con menor protección ante diferencias de inventario."},
        ],
    },
    14: {
        "emoji": "🤝", "title": "Contrato extraordinario", "tag": "OPORTUNIDAD",
        "bg": "linear-gradient(135deg,#2563eb 0%,#10b981 52%,#047857 100%)",
        "scenario": "Llega un contrato grande de suministro. Puede impulsar ingresos, pero exige capacidad y efectivo para cumplir.",
        "question": "¿Aceptas el contrato?",
        "options": [
            {"title":"Aceptar el contrato completo","desc":"Operas casi al máximo para capturar la oportunidad.","concept":"Ventas y capital de trabajo","payload":(5500000,0,0,0,1500000),"result":"Aceptaste el contrato completo. Apostaste por un fuerte crecimiento de ventas y usaste apoyo financiero para sostenerlo."},
            {"title":"Aceptar solo una parte","desc":"Capturas parte del negocio con menor presión financiera.","concept":"Crecimiento moderado","payload":(3500000,0,0,0,0),"result":"Aceptaste parcialmente. Generaste actividad adicional sin llevar la operación al nivel máximo."},
            {"title":"Rechazar el contrato","desc":"Proteges liquidez y capacidad operativa.","concept":"Riesgo y liquidez","payload":(1400000,0,0,0,0),"result":"Rechazaste el contrato. La empresa evitó presión operativa, pero dejó pasar una oportunidad importante de ingresos."},
        ],
    },
    15: {
        "emoji": "🏁", "title": "Cierre del reto", "tag": "ESTRATEGIA FINAL",
        "bg": "linear-gradient(135deg,#16a34a 0%,#eab308 50%,#b45309 100%)",
        "scenario": "Es la última decisión. Ya no basta con vender: importa cómo terminas en efectivo, deuda, activos y control de riesgos.",
        "question": "¿Cuál será tu estrategia final?",
        "options": [
            {"title":"Cerrar con ventas agresivas","desc":"Maximizas operación y buscas utilidad final.","concept":"Rentabilidad","payload":(5800000,0,0,0,0),"result":"Cerraste de forma agresiva. Priorizaste actividad y ventas por encima de reducir deuda o reforzar controles."},
            {"title":"Cerrar de forma equilibrada","desc":"Operas fuerte, pagas parte de deuda y refuerzas control.","concept":"Balance financiero","payload":(3800000,0,500000,1500000,0),"result":"Elegiste equilibrio: combinaste ventas, reducción de deuda y prevención antes del cierre."},
            {"title":"Limpiar el balance","desc":"Operas menos y concentras recursos en bajar deuda.","concept":"Solvencia","payload":(2000000,0,0,3000000,0),"result":"Priorizaste sanear la deuda. Sacrificaste parte de la actividad final para cerrar con menos obligaciones."},
        ],
    },
}

DEFAULT_THEME = {
    "emoji":"🛢️","title":"GRIY · Reto Petrolero","tag":"FINANZAS 360",
    "bg":"linear-gradient(135deg,#0f766e 0%,#2563eb 48%,#7c3aed 100%)",
}

BASE_CSS = """
<style>
.block-container {padding-top:1.15rem;max-width:1180px}
.stApp {color:#fff}
.stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {color:#fff !important}
section[data-testid="stSidebar"] {background:rgba(5,15,25,.90)!important;border-right:1px solid rgba(255,255,255,.16)}
section[data-testid="stSidebar"] * {color:#fff!important}
.hero {position:relative;overflow:hidden;border-radius:28px;padding:26px 30px;margin-bottom:18px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);box-shadow:0 18px 45px rgba(0,0,0,.18);backdrop-filter:blur(14px)}
.hero-grid {display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center}
.griy-logo {display:inline-flex;width:78px;height:78px;border-radius:22px;background:#fff;color:#117a4b!important;align-items:center;justify-content:center;font-weight:950;font-size:23px;letter-spacing:1px;box-shadow:0 12px 35px rgba(0,0,0,.18)}
.hero-title {font-size:38px;font-weight:950;line-height:1.04;margin:12px 0 5px}.hero-sub{font-size:15px;color:#eff6ff!important}.hero-emoji{font-size:88px;filter:drop-shadow(0 12px 16px rgba(0,0,0,.18))}
.badge {display:inline-block;padding:7px 12px;margin:3px 6px 3px 0;border-radius:999px;background:rgba(0,0,0,.20);border:1px solid rgba(255,255,255,.28);font-weight:800;font-size:12px;letter-spacing:.05em}
.glass {background:rgba(8,18,28,.68);border:1px solid rgba(255,255,255,.22);border-radius:22px;padding:20px;margin:12px 0;box-shadow:0 12px 28px rgba(0,0,0,.12);backdrop-filter:blur(10px)}
.question {background:rgba(255,255,255,.93);color:#102030!important;border-radius:24px;padding:23px;margin:14px 0;box-shadow:0 16px 38px rgba(0,0,0,.16)}
.question * {color:#102030!important}.question .tag {display:inline-block;background:#0f766e;color:white!important;padding:6px 10px;border-radius:999px;font-weight:900;font-size:12px}.question h2{margin:10px 0 8px}.scenario{font-size:17px;line-height:1.5}.ask{font-size:20px;font-weight:900;margin-top:16px}
.option-card {min-height:176px;background:rgba(255,255,255,.94);border-radius:20px;padding:17px;border:2px solid rgba(255,255,255,.5);box-shadow:0 12px 24px rgba(0,0,0,.12);margin-bottom:8px}.option-card *{color:#172033!important}.option-letter{font-size:13px;font-weight:950;color:#0f766e!important;letter-spacing:.08em}.option-title{font-size:19px;font-weight:950;margin:7px 0}.option-desc{font-size:14px;line-height:1.4;color:#44515f!important}.concept{font-size:12px;margin-top:12px;color:#0f766e!important;font-weight:900}
div[data-testid="stMetric"] {background:rgba(6,18,28,.74);border:1px solid rgba(255,255,255,.20);padding:12px;border-radius:18px;backdrop-filter:blur(8px)}
div[data-testid="stMetric"] * {color:#fff!important}.stButton>button{border-radius:14px;font-weight:900;min-height:46px}.stProgress > div > div > div > div {background-color:#fde047!important}
.result {background:rgba(236,253,245,.96);border-left:7px solid #16a34a;border-radius:18px;padding:16px 18px;margin:12px 0}.result *{color:#123524!important}.note {font-size:13px;opacity:.90}.podium {background:rgba(255,255,255,.94);border-radius:22px;padding:18px;text-align:center;min-height:170px}.podium *{color:#172033!important}
@media(max-width:800px){.hero-title{font-size:29px}.hero-emoji{font-size:60px}.hero{padding:19px}.hero-grid{grid-template-columns:1fr auto}.griy-logo{width:62px;height:62px;font-size:19px}.option-card{min-height:auto}}
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)


def rpc(fn, payload):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/{fn}", headers=HEADERS, json=payload, timeout=18)
        if r.ok:
            return None if not r.text else r.json()
        try:
            body = r.json()
            msg = body.get("message") or body.get("hint") or r.text
        except Exception:
            msg = r.text
        raise RuntimeError(msg)
    except requests.RequestException as e:
        raise RuntimeError(f"No se pudo conectar con el servidor: {e}")


def money(x):
    x = float(x or 0)
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:,.2f} M"
    return f"${x:,.0f}"


def fnum(x):
    try:
        return float(x or 0)
    except Exception:
        return 0.0


def inject_theme(round_no=0):
    theme = ROUNDS.get(int(round_no or 0), DEFAULT_THEME)
    st.markdown(f"<style>.stApp{{background:{theme['bg']} fixed!important;background-size:cover!important}}</style>", unsafe_allow_html=True)


def header(round_no=0):
    t = ROUNDS.get(int(round_no or 0), DEFAULT_THEME)
    subtitle = "15 decisiones · finanzas · operación · riesgo · control"
    st.markdown(f"""
    <div class='hero'>
      <div class='hero-grid'>
        <div>
          <div style='display:flex;align-items:center;gap:14px'>
            <div class='griy-logo'>GRIY</div>
            <div><span class='badge'>RETO PETROLERO</span><span class='badge'>SIMULACIÓN ACADÉMICA</span></div>
          </div>
          <div class='hero-title'>{t['title'] if round_no else 'GRIY · Reto Petrolero'}</div>
          <div class='hero-sub'>{subtitle}</div>
        </div>
        <div class='hero-emoji'>{t['emoji']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def init_state():
    defaults = {
        "role": None,
        "room_code": "",
        "admin_pin": "",
        "player_token": "",
        "player_name": "",
        "last_result": "",
        "last_result_round": 0,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def logout():
    for k in ["role","room_code","admin_pin","player_token","player_name","last_result","last_result_round"]:
        st.session_state[k] = None if k == "role" else (0 if k == "last_result_round" else "")
    st.rerun()


def sidebar(round_no=0):
    with st.sidebar:
        st.markdown("## 🛢️ GRIY")
        st.write("**Reto Petrolero**")
        if round_no:
            st.progress(min(1.0, round_no / 15.0), text=f"Pregunta {round_no} de 15")
        st.divider()
        st.markdown("**Traducción rápida**")
        st.write("🏭 Máquina/infraestructura = **CAPEX**")
        st.write("🧰 Consumibles/mantenimiento = **OPEX**")
        st.write("💵 Efectivo = dinero disponible")
        st.write("💳 Deuda = obligaciones pendientes")
        st.write("🛡️ Prevención y control = protección ante riesgos")
        if st.session_state.room_code:
            st.divider()
            st.caption("Código de sala")
            st.code(st.session_state.room_code)
        if st.session_state.role and st.button("Salir / volver al inicio", use_container_width=True):
            logout()


def player_result_text(option, state):
    return (
        f"<b>{option['result']}</b><br><br>"
        f"Concepto financiero: <b>{option['concept']}</b><br>"
        f"Efectivo: <b>{money(state.get('cash'))}</b> · "
        f"Ganancia acumulada: <b>{money(state.get('profit'))}</b> · "
        f"Deuda: <b>{money(state.get('debt'))}</b> · "
        f"Puntos: <b>{fnum(state.get('score')):.0f}</b>"
    )


def submit_option(round_no, option):
    operations, capex, controls, debt_payment, financing = option["payload"]
    payload = {
        "p_player_token": st.session_state.player_token,
        "p_operations": operations,
        "p_capex": capex,
        "p_controls": controls,
        "p_debt_payment": debt_payment,
        "p_financing": financing,
    }
    new_state = rpc("griy_submit_decision", payload)
    st.session_state.last_result = player_result_text(option, new_state)
    st.session_state.last_result_round = round_no
    time.sleep(0.4)
    st.rerun()


def question_card(round_no):
    r = ROUNDS[round_no]
    st.markdown(f"""
    <div class='question'>
      <span class='tag'>PREGUNTA {round_no} DE 15 · {r['tag']}</span>
      <h2>{r['emoji']} {r['title']}</h2>
      <div class='scenario'>{r['scenario']}</div>
      <div class='ask'>{r['question']}</div>
    </div>
    """, unsafe_allow_html=True)


def option_grid(round_no):
    r = ROUNDS[round_no]
    cols = st.columns(3)
    letters = ["A", "B", "C"]
    for i, option in enumerate(r["options"]):
        with cols[i]:
            st.markdown(f"""
            <div class='option-card'>
              <div class='option-letter'>OPCIÓN {letters[i]}</div>
              <div class='option-title'>{option['title']}</div>
              <div class='option-desc'>{option['desc']}</div>
              <div class='concept'>{option['concept']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Elegir {letters[i]}", key=f"choice_{round_no}_{i}", use_container_width=True, type="primary" if i == 1 else "secondary"):
                try:
                    submit_option(round_no, option)
                except Exception as e:
                    st.error(str(e))


init_state()

if not st.session_state.role:
    inject_theme(0)
    header(0)
    sidebar(0)
    st.markdown("## ¿Cómo quieres entrar?")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='glass'><h2>👤 Participante</h2><p>Recibe un código de sala, administra tu empresa y toma 15 decisiones.</p></div>", unsafe_allow_html=True)
        if st.button("Entrar como participante", use_container_width=True, type="primary"):
            st.session_state.role = "participante"
            st.rerun()
    with c2:
        st.markdown("<div class='glass'><h2>🧑‍🏫 Administrador</h2><p>Crea la sala, controla el avance, observa resultados y muestra el podio final.</p></div>", unsafe_allow_html=True)
        if st.button("Entrar como administrador", use_container_width=True):
            st.session_state.role = "administrador"
            st.rerun()
    st.caption("Proyecto académico independiente. No es un sitio oficial ni está afiliado a Petróleos Mexicanos.")
    st.stop()


if st.session_state.role == "participante":
    if not st.session_state.player_token:
        inject_theme(0)
        header(0)
        sidebar(0)
        st.markdown("## Entrar al reto")
        with st.form("join"):
            code = st.text_input("Código de sala", placeholder="GRIY-1234").strip().upper()
            name = st.text_input("Tu nombre o apodo", max_chars=50).strip()
            ok = st.form_submit_button("Entrar a la empresa", type="primary", use_container_width=True)
        if ok:
            try:
                data = rpc("griy_join_room", {"p_code": code, "p_name": name})
                st.session_state.player_token = data["player_token"]
                st.session_state.player_name = data["name"]
                st.session_state.room_code = data["room_code"]
                st.rerun()
            except Exception as e:
                st.error(str(e))
        st.stop()

    try:
        p = rpc("griy_player_state", {"p_player_token": st.session_state.player_token})
    except Exception as e:
        inject_theme(0); header(0); sidebar(0); st.error(str(e)); st.stop()

    round_no = int(p.get("current_round") or 0)
    inject_theme(round_no)
    header(round_no)
    sidebar(round_no)

    st.markdown(f"### 👷 {p['name']} · tu empresa")
    st.progress(min(1.0, round_no / 15.0), text=f"Avance del reto: {round_no}/15")

    a,b,c,d = st.columns(4)
    a.metric("💵 Efectivo", money(p["cash"]))
    b.metric("📈 Ganancia", money(p["profit"]))
    c.metric("💳 Deuda", money(p["debt"]))
    d.metric("⭐ Puntos", f"{fnum(p['score']):.0f}")
    e,f,g,h = st.columns(4)
    e.metric("🏭 Activo fijo", money(p["fixed_assets"]))
    f.metric("🛡️ Prevención y control", money(p["control_investment"]))
    g.metric("🚨 Pérdidas ilícitas", money(p["illicit_losses"]))
    h.metric("🏆 Lugar", f"#{p['rank']}")

    if st.session_state.last_result and st.session_state.last_result_round == round_no:
        st.markdown(f"<div class='result'>{st.session_state.last_result}</div>", unsafe_allow_html=True)

    status = p["room_status"]
    if status == "waiting":
        st.info("La sala está lista. Espera a que el administrador inicie el reto.")
        if st.button("🔄 Revisar si ya empezó"): st.rerun()
        st.stop()
    if status == "paused":
        st.warning("La partida está pausada por el administrador.")
        if st.button("🔄 Revisar estado"): st.rerun()
        st.stop()
    if status == "finished":
        st.success("🏁 El reto terminó.")
        if int(p["rank"] or 999) == 1:
            st.balloons(); st.markdown("# 🏆 ¡Ganaste el Reto GRIY!")
        else:
            st.markdown(f"## Tu posición final: #{p['rank']}")
        st.stop()

    if p["submitted"]:
        st.info("✅ Tu decisión quedó registrada. Espera a que el administrador avance a la siguiente pregunta.")
        if st.button("🔄 Actualizar estado"): st.rerun()
        st.stop()

    if round_no not in ROUNDS:
        st.error("La pregunta actual no está configurada.")
        st.stop()

    question_card(round_no)
    option_grid(round_no)
    st.caption("Cada opción produce una combinación diferente de operación, inversión, controles, deuda o financiamiento. No hay una respuesta universalmente correcta: depende de cómo llegaste a esta ronda.")


if st.session_state.role == "administrador":
    if not st.session_state.room_code:
        inject_theme(0)
        header(0)
        sidebar(0)
        st.markdown("## 🧑‍🏫 Panel del administrador")
        t1,t2 = st.tabs(["Crear nueva partida","Abrir partida existente"])
        with t1:
            with st.form("create_room"):
                title = st.text_input("Nombre de la actividad", value="GRIY · Reto Petrolero")
                pin = st.text_input("PIN del administrador", type="password", help="De 4 a 12 dígitos.")
                max_players = st.number_input("Máximo de alumnos", min_value=1, max_value=60, value=30, step=1)
                make = st.form_submit_button("Crear sala de 15 preguntas", type="primary", use_container_width=True)
            if make:
                try:
                    data = rpc("griy_create_room", {"p_admin_pin":pin,"p_title":title,"p_max_players":int(max_players)})
                    st.session_state.room_code = data["code"]
                    st.session_state.admin_pin = pin
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        with t2:
            with st.form("open_room"):
                code = st.text_input("Código", placeholder="GRIY-1234").strip().upper()
                pin2 = st.text_input("PIN", type="password")
                open_it = st.form_submit_button("Abrir panel", use_container_width=True)
            if open_it:
                try:
                    rpc("griy_admin_state", {"p_code":code,"p_pin":pin2})
                    st.session_state.room_code = code
                    st.session_state.admin_pin = pin2
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.stop()

    try:
        state = rpc("griy_admin_state", {"p_code":st.session_state.room_code,"p_pin":st.session_state.admin_pin})
        room = state["room"]; agg = state["aggregate"]; players = state["players"]
    except Exception as e:
        inject_theme(0); header(0); sidebar(0); st.error(str(e)); st.stop()

    current = int(room.get("current_round") or 0)
    inject_theme(current)
    header(current)
    sidebar(current)

    st.markdown(f"<div class='glass'><div style='font-size:13px'>CÓDIGO PARA EL GRUPO</div><div style='font-size:42px;font-weight:950'>{room['code']}</div><div>Comparte el mismo enlace de GRIY y este código.</div></div>", unsafe_allow_html=True)

    if current in ROUNDS:
        r = ROUNDS[current]
        st.markdown(f"<div class='question'><span class='tag'>PREGUNTA {current} DE 15 · {r['tag']}</span><h2>{r['emoji']} {r['title']}</h2><div class='scenario'>{r['scenario']}</div><div class='ask'>{r['question']}</div></div>", unsafe_allow_html=True)

    a,b,c,d = st.columns(4)
    a.metric("👥 Alumnos", f"{agg['player_count']} / {room['max_players']}")
    b.metric("✅ Ya respondieron", f"{agg['submitted']}")
    c.metric("⭐ Puntos promedio", f"{fnum(agg['avg_score']):.0f}")
    d.metric("📈 Ganancia promedio", money(agg["avg_profit"]))

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if room["status"] == "waiting" and st.button("▶️ Iniciar reto", use_container_width=True, type="primary"):
            try:
                rpc("griy_admin_start", {"p_code":room["code"],"p_pin":st.session_state.admin_pin}); st.rerun()
            except Exception as e: st.error(str(e))
    with c2:
        if room["status"] in ["running","paused"]:
            label = "⏸️ Pausar" if room["status"] == "running" else "▶️ Reanudar"
            if st.button(label, use_container_width=True):
                try:
                    rpc("griy_admin_pause_toggle", {"p_code":room["code"],"p_pin":st.session_state.admin_pin}); st.rerun()
                except Exception as e: st.error(str(e))
    with c3:
        if room["status"] in ["running","paused"] and st.button("⏭️ Siguiente pregunta", use_container_width=True):
            try:
                rpc("griy_admin_advance", {"p_code":room["code"],"p_pin":st.session_state.admin_pin}); st.rerun()
            except Exception as e: st.error(str(e))
    with c4:
        if st.button("🔄 Actualizar", use_container_width=True): st.rerun()

    if room["status"] == "waiting":
        st.info("Espera a que entren los alumnos y después inicia el reto. Las salas nuevas tienen 15 preguntas.")
    elif room["status"] == "finished":
        st.success("🏁 El reto terminó. Ya puedes proyectar el podio final.")

    st.markdown("### 📊 Seguimiento del grupo")
    if players:
        df = pd.DataFrame(players)
        keep = [c for c in ["name","score","profit","cash","liquidity","debt","submitted"] if c in df.columns]
        df = df[keep].rename(columns={"name":"Alumno","score":"Puntos","profit":"Ganancia","cash":"Efectivo","liquidity":"Liquidez","debt":"Deuda","submitted":"Ya respondió"})
        for col in ["Puntos","Ganancia","Efectivo","Liquidez","Deuda"]:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce")
        st.dataframe(df, use_container_width=True, hide_index=True)

        if room["status"] == "finished" and "Puntos" in df.columns:
            podium = df.sort_values(["Puntos","Ganancia"], ascending=[False,False]).head(3).reset_index(drop=True)
            st.markdown("## 🏆 Podio GRIY")
            medals = ["🥇","🥈","🥉"]
            cols = st.columns(len(podium))
            for i,row in podium.iterrows():
                with cols[i]:
                    st.markdown(f"<div class='podium'><div style='font-size:52px'>{medals[i]}</div><h3>{row['Alumno']}</h3><div style='font-size:27px;font-weight:950'>{row['Puntos']:.0f} pts</div><div>{money(row['Ganancia'])} de ganancia</div></div>", unsafe_allow_html=True)
            st.balloons()
    else:
        st.info("Todavía no entra ningún participante.")

    st.caption("GRIY es una simulación académica independiente del sector petrolero mexicano. No es un sitio oficial ni está afiliado a Petróleos Mexicanos.")
