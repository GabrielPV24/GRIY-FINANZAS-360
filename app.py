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

st.markdown(
    """
    <style>
      .stApp {background:linear-gradient(180deg,#07140f 0%,#0b1a23 48%,#08121a 100%);color:#eef7f2}
      .block-container {padding-top:1.1rem;max-width:1180px}
      .griy-head {display:flex;align-items:center;gap:16px;margin:4px 0 16px}
      .griy-logo {width:76px;height:76px;border-radius:22px;background:linear-gradient(145deg,#0f8a4b,#063d29);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900;letter-spacing:1.5px;color:white;box-shadow:0 12px 28px rgba(15,138,75,.28);border:1px solid rgba(255,255,255,.14)}
      .griy-title {font-size:34px;font-weight:900;line-height:1;margin:0}
      .griy-sub {color:#a9c8b8;margin-top:6px;font-size:14px;letter-spacing:.10em}
      .pill {display:inline-block;padding:7px 12px;border-radius:999px;background:#102c23;border:1px solid #1f5d43;color:#c9f1dc;margin:4px 6px 4px 0;font-size:13px;font-weight:700}
      .card {background:rgba(17,34,42,.92);border:1px solid #25424d;border-radius:18px;padding:18px;margin:10px 0;box-shadow:0 8px 22px rgba(0,0,0,.12)}
      .event {background:linear-gradient(135deg,rgba(16,95,61,.45),rgba(15,44,58,.78));border:1px solid #287256;border-left:6px solid #35c77a;border-radius:16px;padding:16px 18px;margin:12px 0}
      .warning-card {background:rgba(103,43,22,.38);border:1px solid #8b5a2b;border-left:6px solid #e7a84b;border-radius:16px;padding:16px 18px;margin:12px 0}
      .tiny {color:#9fb4bd;font-size:13px}
      .choice-help {color:#bdd2c6;font-size:14px;margin-top:-4px;margin-bottom:8px}
      .round-badge {display:inline-block;padding:6px 11px;border-radius:10px;background:#154b37;color:#dcffeb;font-weight:800}
      div[data-testid="stMetric"] {background:rgba(14,31,39,.96);border:1px solid #264650;padding:12px;border-radius:15px}
      .stButton>button {border-radius:12px;font-weight:800}
      footer {visibility:hidden}
    </style>
    """,
    unsafe_allow_html=True,
)


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


def init_state():
    defaults = {
        "role": None,
        "room_code": "",
        "admin_pin": "",
        "player_token": "",
        "player_name": "",
        "last_result": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def logout():
    for k in ["role", "room_code", "admin_pin", "player_token", "player_name", "last_result"]:
        st.session_state[k] = None if k == "role" else ""
    st.rerun()


def header():
    st.markdown(
        """
        <div class='griy-head'>
          <div class='griy-logo'>GRIY</div>
          <div>
            <div class='griy-title'>GRIY · Reto Petrolero</div>
            <div class='griy-sub'>FINANZAS 360 · SIMULADOR PARA CLASE</div>
            <div style='margin-top:8px'>
              <span class='pill'>🛢️ Operación</span>
              <span class='pill'>🏭 Maquinaria</span>
              <span class='pill'>💳 Financiamiento</span>
              <span class='pill'>🛡️ Seguridad</span>
              <span class='pill'>🚨 Huachicol</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Caso académico independiente inspirado en una empresa petrolera mexicana. Las cantidades y efectos del juego son supuestos didácticos.")


def simple_round_text(n):
    return {
        1: ("📦 Operación de planta", "La planta necesita consumibles e insumos para trabajar bien este mes."),
        2: ("🏭 ¿Compramos una máquina nueva?", "Puedes invertir en equipo nuevo. Cuesta hoy, pero puede ayudar a producir mejor después."),
        3: ("🏦 ¿Pedimos dinero prestado?", "Hay opción de pedir un préstamo. Tendrás más efectivo, pero también más deuda e intereses."),
        4: ("🚨 Alerta de huachicol", "Existe riesgo de robo de hidrocarburos. Puedes gastar en vigilancia y monitoreo para reducir el impacto dentro del juego."),
        5: ("⛽ Demanda alta de combustible", "El mercado está comprando más. Puedes aprovechar la demanda para operar con mayor intensidad."),
    }.get(int(n or 0), ("Reto GRIY", "Administra tu empresa."))


def explain_result(round_no, choices, new_state):
    profit = money(new_state.get("profit"))
    cash = money(new_state.get("cash"))
    score = fnum(new_state.get("score"))
    if round_no == 1:
        lead = "Compraste consumibles para operar con mayor intensidad." if choices["consumibles"] == "Sí" else "Decidiste ahorrar y operar de forma limitada."
    elif round_no == 2:
        lead = "Compraste maquinaria: es una inversión que aumenta tus activos." if choices["maquina"] == "Sí" else "Conservaste el efectivo y no compraste maquinaria."
    elif round_no == 3:
        lead = "Pediste financiamiento: subió tu efectivo, pero también tu deuda." if choices["prestamo"] == "Sí" else "No pediste financiamiento y evitaste aumentar la deuda."
    elif round_no == 4:
        lead = "Invertiste en vigilancia y monitoreo para reducir el impacto del huachicol." if choices["seguridad"] == "Sí" else "No invertiste en seguridad y asumiste un mayor riesgo de pérdida."
    else:
        lead = "Aprovechaste la alta demanda y operaste más fuerte." if choices["demanda"] == "Sí" else "Fuiste conservador y mantuviste una operación moderada."
    return f"{lead}  |  Efectivo: {cash}  ·  Ganancia acumulada: {profit}  ·  Puntos: {score:.0f}"


def payload_for_round(round_no, choices):
    operations = capex = controls = debt_payment = financing = 0
    if round_no == 1:
        operations = 2_500_000 if choices["consumibles"] == "Sí" else 900_000
    elif round_no == 2:
        capex = 2_500_000 if choices["maquina"] == "Sí" else 0
        operations = 1_800_000 if choices["operacion"] == "Operación normal" else 900_000
    elif round_no == 3:
        financing = 3_000_000 if choices["prestamo"] == "Sí" else 0
        operations = 1_700_000 if choices["operar"] == "Sí" else 900_000
    elif round_no == 4:
        controls = 1_800_000 if choices["seguridad"] == "Sí" else 0
        operations = 1_600_000 if choices["seguir"] == "Sí" else 800_000
    elif round_no == 5:
        operations = 3_600_000 if choices["demanda"] == "Sí" else 1_500_000
        debt_payment = 1_000_000 if choices["pagar"] == "Sí" else 0
    return {
        "p_operations": operations,
        "p_capex": capex,
        "p_controls": controls,
        "p_debt_payment": debt_payment,
        "p_financing": financing,
    }


init_state()
header()

with st.sidebar:
    st.markdown("## 🛢️ GRIY")
    st.write("**Reto Petrolero**")
    st.caption("Toma decisiones sencillas y observa cómo cambian las finanzas de la empresa.")
    st.divider()
    st.markdown("**Traducción rápida**")
    st.write("🏭 Máquina nueva = inversión (CAPEX)")
    st.write("📦 Consumibles / seguridad = gasto de operación (OPEX)")
    st.write("💧 Liquidez = capacidad de pagar y seguir operando")
    st.write("💳 Deuda = dinero que la empresa debe")
    st.divider()
    if st.session_state.role:
        st.write(f"Modo: **{st.session_state.role.title()}**")
        if st.session_state.room_code:
            st.code(st.session_state.room_code)
        if st.button("Salir / volver al inicio", use_container_width=True):
            logout()


if not st.session_state.role:
    st.markdown("## ¿Cómo quieres entrar?")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 👤 Participante")
        st.write("Solo necesitas el código de la sala y tu nombre.")
        if st.button("Entrar como participante", use_container_width=True, type="primary"):
            st.session_state.role = "participante"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🧑‍🏫 Administrador")
        st.write("Crea la sala, inicia el juego, cambia de ronda y ve el ranking.")
        if st.button("Entrar como administrador", use_container_width=True):
            st.session_state.role = "administrador"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


if st.session_state.role == "participante":
    if not st.session_state.player_token:
        st.markdown("## Entrar al Reto GRIY")
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
        st.error(str(e))
        st.stop()

    st.markdown(f"## 👷 {p['name']} · tu empresa")
    st.caption(f"Sala {p['room_code']} · Ronda {p['current_round']} de {p['max_rounds']}")

    a, b, c, d = st.columns(4)
    a.metric("💵 Dinero disponible", money(p["cash"]))
    b.metric("📈 Ganancia acumulada", money(p["profit"]))
    c.metric("💳 Deuda total", money(p["debt"]))
    d.metric("⭐ Puntos", f"{fnum(p['score']):.0f}")
    e, f, g, h = st.columns(4)
    e.metric("🏭 Maquinaria y equipo", money(p["fixed_assets"]))
    f.metric("🛡️ Seguridad acumulada", money(p["control_investment"]))
    g.metric("🚨 Pérdida por huachicol", money(p["illicit_losses"]))
    h.metric("🏆 Lugar actual", f"#{p['rank']}")

    with st.expander("¿Qué significan estos números?", expanded=False):
        st.write("**Dinero disponible:** lo que tienes en caja para pagar decisiones.")
        st.write("**Ganancia:** lo que queda después de costos, gastos e intereses del juego.")
        st.write("**Deuda:** préstamos y obligaciones pendientes.")
        st.write("**Maquinaria y equipo:** activos que permanecen en la empresa.")
        st.write("**Seguridad:** dinero acumulado en vigilancia y control.")

    if st.session_state.last_result:
        st.success("✅ " + st.session_state.last_result)

    status = p["room_status"]
    if status == "waiting":
        st.info("La empresa está lista. Espera a que el administrador inicie el reto.")
        if st.button("🔄 Revisar si ya empezó"):
            st.rerun()
        st.stop()
    if status == "paused":
        st.warning("La partida está pausada por el administrador.")
        if st.button("🔄 Revisar estado"):
            st.rerun()
        st.stop()
    if status == "finished":
        st.success("🏁 El reto terminó.")
        if int(p["rank"] or 999) == 1:
            st.balloons()
            st.markdown("# 🏆 ¡Ganaste el Reto GRIY!")
        else:
            st.markdown(f"### Terminaste en la posición #{p['rank']}")
        st.stop()

    round_no = int(p["current_round"] or 0)
    title, desc = simple_round_text(round_no)
    st.markdown(f"<div class='event'><span class='round-badge'>RONDA {round_no}</span><h3>{title}</h3><div>{desc}</div></div>", unsafe_allow_html=True)

    if p["submitted"]:
        st.success("Tu decisión ya quedó guardada. Espera a que el administrador pase a la siguiente ronda.")
        if st.button("🔄 Actualizar"):
            st.rerun()
        st.stop()

    st.markdown("### Elige qué harías")

    if round_no == 1:
        st.write("La planta necesita materiales pequeños de uso diario: lubricantes, sellos, filtros y otros consumibles.")
        st.markdown("<div class='choice-help'>Comprar ayuda a operar más; no comprar conserva efectivo, pero limita la operación.</div>", unsafe_allow_html=True)
        consumibles = st.radio("¿Comprar los consumibles necesarios?", ["Sí", "No"], horizontal=True, key="r1c")
        choices = {"consumibles": consumibles}

    elif round_no == 2:
        st.write("Aparece la oportunidad de comprar una máquina nueva para modernizar parte de la planta.")
        maquina = st.radio("¿Comprar la máquina nueva?", ["Sí", "No"], horizontal=True, key="r2m")
        operacion = st.radio("Mientras tanto, ¿cómo operas este mes?", ["Operación normal", "Ahorrar dinero"], horizontal=True, key="r2o")
        st.caption("Comprar la máquina es una inversión: no se considera un gasto operativo inmediato dentro del juego.")
        choices = {"maquina": maquina, "operacion": operacion}

    elif round_no == 3:
        st.write("Hay poco margen de maniobra y el banco ofrece un préstamo.")
        prestamo = st.radio("¿Pedir el préstamo?", ["Sí", "No"], horizontal=True, key="r3p")
        operar = st.radio("¿Mantener la operación del mes?", ["Sí", "No"], horizontal=True, key="r3o")
        st.caption("Un préstamo aumenta el dinero disponible, pero también la deuda y los intereses.")
        choices = {"prestamo": prestamo, "operar": operar}

    elif round_no == 4:
        st.markdown("<div class='warning-card'><b>🚨 Se detecta riesgo de huachicol.</b><br>Una toma clandestina puede provocar pérdida de producto y dinero.</div>", unsafe_allow_html=True)
        seguridad = st.radio("¿Invertir en vigilancia, monitoreo y control?", ["Sí", "No"], horizontal=True, key="r4s")
        seguir = st.radio("¿Seguir operando este mes?", ["Sí", "No"], horizontal=True, key="r4o")
        st.caption("En este simulador, la inversión en controles reduce el impacto del evento. Es un supuesto didáctico, no un porcentaje real.")
        choices = {"seguridad": seguridad, "seguir": seguir}

    else:
        st.write("Sube la demanda de combustible. Puedes producir y vender más, pero también puedes aprovechar para bajar deuda.")
        demanda = st.radio("¿Aprovechar la alta demanda?", ["Sí", "No"], horizontal=True, key="r5d")
        pagar = st.radio("¿Pagar una parte de la deuda?", ["Sí", "No"], horizontal=True, key="r5p")
        choices = {"demanda": demanda, "pagar": pagar}

    if st.button("✅ Confirmar mi decisión", type="primary", use_container_width=True):
        try:
            payload = payload_for_round(round_no, choices)
            new_state = rpc("griy_submit_decision", {"p_player_token": st.session_state.player_token, **payload})
            st.session_state.last_result = explain_result(round_no, choices, new_state)
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(str(e))


if st.session_state.role == "administrador":
    if not st.session_state.room_code:
        st.markdown("## 🧑‍🏫 Panel del administrador")
        t1, t2 = st.tabs(["Crear nueva partida", "Abrir partida existente"])
        with t1:
            with st.form("create_room"):
                title = st.text_input("Nombre de la actividad", value="GRIY · Reto Petrolero")
                pin = st.text_input("Crea un PIN de administrador", type="password", help="Usa de 4 a 12 dígitos.")
                max_players = st.number_input("Máximo de alumnos", min_value=1, max_value=60, value=30, step=1)
                make = st.form_submit_button("Crear sala", type="primary", use_container_width=True)
            if make:
                try:
                    data = rpc("griy_create_room", {"p_admin_pin": pin, "p_title": title, "p_max_players": int(max_players)})
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
                    rpc("griy_admin_state", {"p_code": code, "p_pin": pin2})
                    st.session_state.room_code = code
                    st.session_state.admin_pin = pin2
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.stop()

    try:
        state = rpc("griy_admin_state", {"p_code": st.session_state.room_code, "p_pin": st.session_state.admin_pin})
        room = state["room"]
        agg = state["aggregate"]
        players = state["players"]
    except Exception as e:
        st.error(str(e))
        st.stop()

    st.markdown("## 🧑‍🏫 Control de la partida")
    st.markdown(f"<div class='card'><div class='tiny'>CÓDIGO PARA LOS ALUMNOS</div><h1 style='margin:4px 0'>{room['code']}</h1><div>Comparte el mismo enlace de GRIY y este código.</div></div>", unsafe_allow_html=True)

    current = int(room["current_round"] or 0)
    if current > 0:
        rt, rd = simple_round_text(current)
        st.markdown(f"<div class='event'><span class='round-badge'>RONDA {current} DE {room['max_rounds']}</span><h3>{rt}</h3><div>{rd}</div></div>", unsafe_allow_html=True)

    a,b,c,d = st.columns(4)
    a.metric("👥 Alumnos", f"{agg['player_count']} / {room['max_players']}")
    b.metric("✅ Ya decidieron", f"{agg['submitted']}")
    c.metric("⭐ Puntos promedio", f"{fnum(agg['avg_score']):.0f}")
    d.metric("💵 Ganancia promedio", money(agg["avg_profit"]))

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if room["status"] == "waiting" and st.button("▶️ Iniciar reto", use_container_width=True, type="primary"):
            try:
                rpc("griy_admin_start", {"p_code": room["code"], "p_pin": st.session_state.admin_pin})
                st.rerun()
            except Exception as e:
                st.error(str(e))
    with c2:
        if room["status"] in ["running", "paused"]:
            label = "⏸️ Pausar" if room["status"] == "running" else "▶️ Reanudar"
            if st.button(label, use_container_width=True):
                try:
                    rpc("griy_admin_pause_toggle", {"p_code": room["code"], "p_pin": st.session_state.admin_pin})
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with c3:
        if room["status"] in ["running", "paused"] and st.button("⏭️ Cerrar ronda / siguiente", use_container_width=True):
            try:
                rpc("griy_admin_advance", {"p_code": room["code"], "p_pin": st.session_state.admin_pin})
                st.rerun()
            except Exception as e:
                st.error(str(e))
    with c4:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()

    if room["status"] == "waiting":
        st.info("Espera a que entren los alumnos. Cuando estén listos, pulsa **Iniciar reto**.")
    elif room["status"] == "finished":
        st.success("🏁 La partida terminó. Abajo está el podio final.")

    st.markdown("### 📊 Seguimiento del grupo")
    if players:
        df = pd.DataFrame(players)
        keep = [c for c in ["name","score","profit","cash","liquidity","debt","submitted"] if c in df.columns]
        df = df[keep].rename(columns={
            "name":"Alumno","score":"Puntos","profit":"Ganancia","cash":"Efectivo",
            "liquidity":"Liquidez","debt":"Deuda","submitted":"Ya respondió"
        })
        for col in ["Puntos","Ganancia","Efectivo","Liquidez","Deuda"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        st.dataframe(df, use_container_width=True, hide_index=True)

        if room["status"] == "finished" and "Puntos" in df.columns:
            podium = df.sort_values(["Puntos","Ganancia"], ascending=[False,False]).head(3).reset_index(drop=True)
            st.markdown("## 🏆 Podio GRIY")
            medals = ["🥇","🥈","🥉"]
            cols = st.columns(min(3, len(podium)))
            for i, row in podium.iterrows():
                with cols[i]:
                    st.markdown(f"<div class='card' style='text-align:center'><div style='font-size:46px'>{medals[i]}</div><h3>{row['Alumno']}</h3><div style='font-size:25px;font-weight:900'>{row['Puntos']:.0f} pts</div></div>", unsafe_allow_html=True)
            st.balloons()
    else:
        st.info("Todavía no entra ningún participante.")

    st.divider()
    st.caption("Proyecto académico GRIY. No es un sitio oficial ni está afiliado a Petróleos Mexicanos.")
