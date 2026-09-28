import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="GRIY | Finanzas 360", page_icon="◆", layout="wide")

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
    .stApp {background: #0b1118; color: #e8eef7;}
    .block-container {padding-top: 1.1rem; max-width: 1200px;}
    .griy-wrap {display:flex;align-items:center;gap:14px;margin-bottom:8px;}
    .griy-logo {width:62px;height:62px;border-radius:16px;background:linear-gradient(135deg,#64748b,#0ea5e9);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:21px;color:white;letter-spacing:1px;box-shadow:0 8px 24px rgba(14,165,233,.25)}
    .griy-title {font-size:34px;font-weight:800;line-height:1;margin:0;}
    .griy-sub {color:#9fb1c7;margin-top:5px;font-size:14px;letter-spacing:.12em;}
    .card {background:#111a24;border:1px solid #223244;border-radius:16px;padding:18px;margin:8px 0;}
    .event {background:#0f2130;border-left:5px solid #38bdf8;border-radius:12px;padding:14px 16px;margin:10px 0;}
    .good {color:#86efac;font-weight:700}.bad {color:#fca5a5;font-weight:700}.muted{color:#94a3b8}
    div[data-testid="stMetric"] {background:#101923;border:1px solid #223244;padding:12px;border-radius:14px;}
    .stButton>button {border-radius:12px;font-weight:700;}
    </style>
    <div class="griy-wrap">
      <div class="griy-logo">GRIY</div>
      <div><div class="griy-title">GRIY</div><div class="griy-sub">FINANZAS 360 · RETO EMPRESARIAL</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)


def rpc(fn, payload):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/{fn}", headers=HEADERS, json=payload, timeout=15)
        if r.ok:
            if not r.text:
                return None
            return r.json()
        try:
            msg = r.json().get("message", r.text)
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


def init_state():
    defaults = {
        "role": None,
        "room_code": "",
        "admin_pin": "",
        "player_token": "",
        "player_name": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def logout():
    for k in ["role", "room_code", "admin_pin", "player_token", "player_name"]:
        st.session_state[k] = None if k == "role" else ""
    st.rerun()


init_state()

with st.sidebar:
    st.markdown("### GRIY · Finanzas 360")
    st.caption("Simulador competitivo de administración financiera")
    if st.session_state.role:
        st.write(f"Modo: **{st.session_state.role.title()}**")
        if st.session_state.room_code:
            st.code(st.session_state.room_code)
        if st.button("Salir", use_container_width=True):
            logout()
    st.divider()
    st.caption("Los efectos de controles y eventos son supuestos didácticos del juego. No representan porcentajes empíricos reales.")


if not st.session_state.role:
    st.markdown("## ¿Cómo quieres entrar?")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 👤 Participante")
        st.write("Entra con el código que muestra el administrador.")
        if st.button("Entrar como participante", use_container_width=True, type="primary"):
            st.session_state.role = "participante"
            st.rerun()
    with c2:
        st.markdown("### 👨‍🏫 Administrador")
        st.write("Crea una sala, controla rondas y observa el ranking.")
        if st.button("Entrar como administrador", use_container_width=True):
            st.session_state.role = "administrador"
            st.rerun()
    st.stop()


if st.session_state.role == "participante":
    if not st.session_state.player_token:
        st.markdown("## Entrar al Reto GRIY")
        with st.form("join"):
            code = st.text_input("Código de sala", placeholder="GRIY-1234").strip().upper()
            name = st.text_input("Tu nombre o apodo", max_chars=50).strip()
            ok = st.form_submit_button("Entrar a la sala", type="primary", use_container_width=True)
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

    st.markdown(f"## Hola, {p['name']}")
    st.caption(f"Sala {p['room_code']} · Ronda {p['current_round']} de {p['max_rounds']}")

    a,b,c,d = st.columns(4)
    a.metric("Efectivo", money(p["cash"]))
    b.metric("Utilidad acumulada", money(p["profit"]))
    c.metric("Liquidez", f"{float(p['liquidity'] or 0):.2f}x")
    d.metric("Puntos", f"{float(p['score'] or 0):.0f}")

    e,f,g,h = st.columns(4)
    e.metric("Deuda", money(p["debt"]))
    f.metric("Activo fijo", money(p["fixed_assets"]))
    g.metric("Controles", money(p["control_investment"]))
    h.metric("Posición actual", f"#{p['rank']}")

    status = p["room_status"]
    if status == "waiting":
        st.info("La sala está lista. Espera a que el administrador inicie el reto.")
        if st.button("Actualizar"):
            st.rerun()
        st.stop()
    if status == "paused":
        st.warning("La partida está pausada por el administrador.")
        if st.button("Actualizar"):
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

    st.markdown(
        f"<div class='event'><b>Ronda {p['current_round']}: {p.get('event_title') or 'Decisión financiera'}</b><br>{p.get('event_description') or ''}</div>",
        unsafe_allow_html=True,
    )

    if p["submitted"]:
        st.success("✅ Ya enviaste tu decisión. Espera a que el administrador cierre la ronda.")
        if st.button("Actualizar estado"):
            st.rerun()
        st.stop()

    st.markdown("### Decide cómo usar tus recursos")
    st.caption("Cada ronda permite una sola decisión. No necesitas gastar todo tu efectivo.")

    with st.form(f"decision_{p['current_round']}"):
        operations = st.slider("Operación / producción", 0, 6_000_000, 2_000_000, 250_000, format="$%d")
        capex = st.slider("CAPEX · maquinaria e instalaciones", 0, 4_000_000, 0, 250_000, format="$%d")
        controls = st.slider("OPEX de controles y prevención", 0, 3_000_000, 0, 250_000, format="$%d")
        debt_payment = st.slider("Pago de deuda", 0, 4_000_000, 0, 250_000, format="$%d")
        financing = st.slider("Nuevo financiamiento", 0, 5_000_000, 0, 250_000, format="$%d")
        total_use = operations + capex + controls + debt_payment
        available = float(p["cash"]) + financing
        st.write(f"Uso de efectivo: **{money(total_use)}** · Disponible con financiamiento: **{money(available)}**")
        submit = st.form_submit_button("Enviar decisión", type="primary", use_container_width=True)

    if submit:
        try:
            new_state = rpc("griy_submit_decision", {
                "p_player_token": st.session_state.player_token,
                "p_operations": operations,
                "p_capex": capex,
                "p_controls": controls,
                "p_debt_payment": debt_payment,
                "p_financing": financing,
            })
            st.success(f"Decisión registrada. Puntuación provisional: {float(new_state['score']):.0f}")
            time.sleep(0.8)
            st.rerun()
        except Exception as e:
            st.error(str(e))


if st.session_state.role == "administrador":
    if not st.session_state.room_code:
        st.markdown("## Panel del administrador")
        tab1, tab2 = st.tabs(["Crear nueva partida", "Abrir partida existente"])
        with tab1:
            st.write("Cada vez que quieras usar GRIY puedes crear una sala nueva sin cambiar el enlace de la aplicación.")
            with st.form("create_room"):
                title = st.text_input("Nombre de la actividad", value="Reto GRIY · Finanzas 360")
                max_players = st.number_input("Máximo de participantes", min_value=1, max_value=60, value=30)
                pin = st.text_input("Crea un PIN de administrador", type="password", help="De 4 a 12 dígitos. No lo compartas con el grupo.")
                create = st.form_submit_button("Crear sala", type="primary", use_container_width=True)
            if create:
                try:
                    data = rpc("griy_create_room", {"p_admin_pin": pin, "p_title": title, "p_max_players": int(max_players)})
                    st.session_state.room_code = data["code"]
                    st.session_state.admin_pin = pin
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        with tab2:
            with st.form("open_room"):
                code = st.text_input("Código", placeholder="GRIY-1234").upper().strip()
                pin2 = st.text_input("PIN", type="password")
                open_room = st.form_submit_button("Abrir panel", use_container_width=True)
            if open_room:
                try:
                    rpc("griy_admin_state", {"p_code": code, "p_pin": pin2})
                    st.session_state.room_code = code
                    st.session_state.admin_pin = pin2
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.stop()

    try:
        data = rpc("griy_admin_state", {"p_code": st.session_state.room_code, "p_pin": st.session_state.admin_pin})
    except Exception as e:
        st.error(str(e))
        st.stop()

    room = data["room"]
    agg = data["aggregate"]
    players = data["players"]

    st.markdown(f"## {room['title']}")
    st.markdown(f"### Código para el grupo: `{room['code']}`")
    st.caption("Comparte el mismo enlace de esta app. Los alumnos eligen Participante e ingresan este código.")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Participantes", f"{agg['player_count']} / {room['max_players']}")
    c2.metric("Ronda", f"{room['current_round']} / {room['max_rounds']}")
    c3.metric("Entregaron", agg['submitted'])
    c4.metric("Liquidez promedio", f"{float(agg['avg_liquidity'] or 0):.2f}x")

    c5,c6,c7 = st.columns(3)
    c5.metric("Utilidad promedio", money(agg['avg_profit']))
    c6.metric("Puntuación promedio", f"{float(agg['avg_score'] or 0):.0f}")
    c7.metric("Activos administrados", money(agg['total_managed_assets']))

    if room["current_round"]:
        st.markdown(
            f"<div class='event'><b>Evento actual: {room.get('event_title') or ''}</b><br>{room.get('event_description') or ''}</div>",
            unsafe_allow_html=True,
        )

    b1,b2,b3 = st.columns(3)
    if room["status"] == "waiting":
        if b1.button("▶️ Iniciar reto", type="primary", use_container_width=True):
            try:
                rpc("griy_admin_start", {"p_code": room["code"], "p_pin": st.session_state.admin_pin})
                st.rerun()
            except Exception as e:
                st.error(str(e))
    elif room["status"] in ["running", "paused"]:
        label = "▶️ Reanudar" if room["status"] == "paused" else "⏸️ Pausar"
        if b1.button(label, use_container_width=True):
            try:
                rpc("griy_admin_pause_toggle", {"p_code": room["code"], "p_pin": st.session_state.admin_pin})
                st.rerun()
            except Exception as e:
                st.error(str(e))
        adv_label = "🏁 Finalizar reto" if room["current_round"] >= room["max_rounds"] else "⏭️ Cerrar ronda y avanzar"
        if b2.button(adv_label, type="primary", use_container_width=True):
            try:
                rpc("griy_admin_advance", {"p_code": room["code"], "p_pin": st.session_state.admin_pin})
                st.rerun()
            except Exception as e:
                st.error(str(e))
    if b3.button("🔄 Actualizar panel", use_container_width=True):
        st.rerun()

    st.markdown("### Ranking")
    if players:
        df = pd.DataFrame(players)
        df.insert(0, "Posición", range(1, len(df)+1))
        df_show = df[["Posición","name","score","profit","cash","liquidity","debt","submitted"]].copy()
        df_show.columns = ["Posición","Participante","Puntos","Utilidad","Efectivo","Liquidez","Deuda","Entregó"]
        df_show["Puntos"] = df_show["Puntos"].astype(float).round(0)
        df_show["Utilidad"] = df_show["Utilidad"].map(money)
        df_show["Efectivo"] = df_show["Efectivo"].map(money)
        df_show["Liquidez"] = df_show["Liquidez"].astype(float).round(2)
        df_show["Deuda"] = df_show["Deuda"].map(money)
        st.dataframe(df_show, use_container_width=True, hide_index=True)

        if room["status"] == "finished":
            st.balloons()
            winner = players[0]
            st.markdown(f"# 🏆 Ganador: {winner['name']}")
            st.write(f"Puntuación final: **{float(winner['score']):.0f} puntos**")
    else:
        st.info("Aún no hay participantes conectados.")

    st.markdown("### Cómo se calcula el desempeño")
    st.write("La puntuación combina utilidad, liquidez, endeudamiento, capacidad productiva y manejo de riesgos. No gana simplemente quien conserve más efectivo.")
