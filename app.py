import time
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="GRIY | Aventura Petrolera", page_icon="🎮", layout="wide")

SUPABASE_URL = "https://xhizwsiitcvjnafmpplf.supabase.co"
SUPABASE_KEY = "sb_publishable_yLYAPUcEBf5X2ZV6BEfy0w_NPzf58zx"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# Cada misión mantiene conceptos financieros reales, pero con lenguaje sencillo.
MISSIONS = {
1:{"emoji":"🧰","title":"¡La planta despierta!","color":"#ff9f1c","bg":"linear-gradient(135deg,#ff9f1c,#ff4d6d)","scene":"Necesitamos filtros, lubricantes y sellos para arrancar.","ask":"¿Qué compras?","tip":"Gastar en cosas del día a día es OPEX.","opts":[("🟢 Solo lo necesario","Ahorras dinero, pero trabajas más lento.",(1200000,0,0,0,0)),("🔵 Todo el paquete","Gastas más y la planta puede trabajar mejor.",(2500000,0,0,0,0)),("🟣 Paquete grande con crédito","Tienes más insumos, pero aparece deuda.",(3200000,0,0,0,1500000))]},
2:{"emoji":"🔧","title":"¡La bomba tiembla!","color":"#00b4d8","bg":"linear-gradient(135deg,#00b4d8,#4361ee)","scene":"Una bomba importante está vibrando raro.","ask":"¿Qué haces?","tip":"Mantenimiento preventivo puede evitar problemas mayores.","opts":[("🛠️ Repararla ahora","Pagas mantenimiento y reduces riesgo.",(1500000,0,800000,0,0)),("🏃 Seguir trabajando","Produces hoy, pero tomas más riesgo.",(2100000,0,0,0,0)),("⚙️ Renovar el equipo","Gastás más, pero mejoras tus activos.",(1000000,1500000,800000,0,0))]},
3:{"emoji":"🏭","title":"¡Máquina nueva!","color":"#9b5de5","bg":"linear-gradient(135deg,#9b5de5,#5a189a)","scene":"Te ofrecen una máquina moderna para mejorar la planta.","ask":"¿La compras?","tip":"Comprar equipo que dura años es CAPEX.","opts":[("💵 Sí, con efectivo","Baja tu caja, sube tu activo fijo.",(1400000,3500000,0,0,0)),("🏦 Sí, con financiamiento","Conservas caja, pero sube la deuda.",(1800000,2000000,0,0,2500000)),("🙅 No por ahora","Proteges efectivo, pero no mejoras capacidad.",(2000000,0,0,0,0))]},
4:{"emoji":"📈","title":"¡Todo subió de precio!","color":"#ff595e","bg":"linear-gradient(135deg,#ff595e,#ff924c)","scene":"Los proveedores subieron los precios de los insumos.","ask":"¿Cómo reaccionas?","tip":"Más producción también puede significar más costo.","opts":[("🔥 Seguir a toda máquina","Mantienes ventas, pero gastas mucho.",(3500000,0,0,0,0)),("🐢 Bajar el ritmo","Proteges dinero y produces menos.",(1500000,0,0,0,0)),("💳 Comprar con crédito","Mantienes insumos y aumenta la deuda.",(3000000,0,0,0,2000000))]},
5:{"emoji":"🏦","title":"¡El banco llama!","color":"#4361ee","bg":"linear-gradient(135deg,#4361ee,#00b4d8)","scene":"El banco te ofrece dinero prestado para crecer.","ask":"¿Cuánto pides?","tip":"Un préstamo ayuda hoy, pero genera deuda e intereses.","opts":[("🚀 Crédito grande","Mucho efectivo, mucha deuda.",(3000000,0,0,0,5000000)),("⚖️ Crédito moderado","Buscas equilibrio.",(2200000,0,0,0,2000000)),("✋ Nada","No aumenta la deuda, pero tienes menos recursos.",(1500000,0,0,0,0))]},
6:{"emoji":"👷","title":"¡Entrenamiento del equipo!","color":"#2ec4b6","bg":"linear-gradient(135deg,#2ec4b6,#06d6a0)","scene":"Tu personal puede aprender mejores formas de trabajar.","ask":"¿Cuánto inviertes en capacitación?","tip":"Capacitar cuesta hoy, pero fortalece la operación y el control.","opts":[("🎓 Curso intensivo","Más gasto y más prevención.",(1400000,0,1500000,0,0)),("📘 Curso corto","Gasto moderado.",(1800000,0,600000,0,0)),("⏭️ Lo dejamos para después","Ahorras hoy, sin reforzar controles.",(2100000,0,0,0,0))]},
7:{"emoji":"⏸️","title":"¡Paro de planta!","color":"#6c757d","bg":"linear-gradient(135deg,#6c757d,#ffb703)","scene":"Ingeniería quiere parar un rato para revisar equipos.","ask":"¿Qué eliges?","tip":"Parar reduce producción, pero puede bajar riesgos.","opts":[("🛑 Paro preventivo","Menos producción, más mantenimiento.",(700000,0,1500000,0,0)),("▶️ Seguir normal","Más producción, menos prevención.",(2600000,0,0,0,0)),("🔩 Cambiar una pieza clave","Inviertes en equipo y mantenimiento.",(1100000,2000000,500000,0,0))]},
8:{"emoji":"🚨","title":"¡Alerta de huachicol!","color":"#d90429","bg":"linear-gradient(135deg,#d90429,#6a040f)","scene":"Hay riesgo de robo de hidrocarburos.","ask":"¿Cómo proteges la empresa?","tip":"En este juego, más controles reducen el impacto del robo.","opts":[("🛡️ Blindaje fuerte","Gastás más en vigilancia y control.",(1500000,0,2500000,0,0)),("👀 Refuerzo moderado","Protección intermedia.",(1800000,0,1200000,0,0)),("💸 No gastar en seguridad","Conservas caja, pero tomas más riesgo.",(2200000,0,0,0,0))]},
9:{"emoji":"⛽","title":"¡Todos quieren combustible!","color":"#00bbf9","bg":"linear-gradient(135deg,#00bbf9,#3a86ff)","scene":"La demanda sube y puedes vender mucho más.","ask":"¿Cuánto produces?","tip":"Vender más puede dar ingresos, pero exige dinero para operar.","opts":[("🚀 Producción máxima","Apuestas fuerte por ventas.",(5000000,0,0,0,0)),("⚖️ Producción media","Crecimiento con prudencia.",(3300000,0,0,0,0)),("🐢 Producción baja","Proteges efectivo.",(1600000,0,0,0,0))]},
10:{"emoji":"🚚","title":"¡Los camiones no llegan!","color":"#fb8500","bg":"linear-gradient(135deg,#fb8500,#ffb703)","scene":"Un problema de transporte amenaza las entregas.","ask":"¿Cómo lo arreglas?","tip":"La logística también cuesta dinero.","opts":[("🚚 Transporte de emergencia","Caro, pero mantienes entregas.",(2500000,0,800000,0,0)),("🗺️ Reorganizar rutas","Costo moderado.",(2000000,0,300000,0,0)),("⌛ Aceptar retrasos","Ahorras, pero vendes menos.",(1000000,0,0,0,0))]},
11:{"emoji":"🏗️","title":"¡Proyecto nuevo!","color":"#06d6a0","bg":"linear-gradient(135deg,#06d6a0,#ffd166)","scene":"Puedes mejorar infraestructura de la empresa.","ask":"¿Cómo pagas el proyecto?","tip":"Infraestructura nueva suele ser CAPEX.","opts":[("💵 Con dinero propio","Baja efectivo, suben activos.",(1500000,3500000,0,0,0)),("🏦 Con financiamiento","Haces el proyecto y sube la deuda.",(1800000,3500000,0,0,2500000)),("🙅 No hacerlo","Conservas efectivo.",(2300000,0,0,0,0))]},
12:{"emoji":"💰","title":"¡Hay dinero en caja!","color":"#f15bb5","bg":"linear-gradient(135deg,#f15bb5,#9b5de5)","scene":"Tienes que decidir qué hacer con los recursos disponibles.","ask":"¿A dónde va el dinero?","tip":"No siempre gastar más es mejor.","opts":[("💳 Pagar deuda","Bajan tus obligaciones.",(1500000,0,0,3000000,0)),("🏭 Reinvertir","Compras activos para el futuro.",(1600000,3000000,0,0,0)),("🐷 Guardar efectivo","Aumentas tu colchón de dinero.",(1000000,0,0,0,0))]},
13:{"emoji":"🔍","title":"¡Algo no cuadra!","color":"#577590","bg":"linear-gradient(135deg,#577590,#00b4d8)","scene":"El inventario físico no coincide con los registros.","ask":"¿Qué revisión haces?","tip":"Los controles internos ayudan a detectar pérdidas.","opts":[("🕵️ Auditoría completa","Más costo y más control.",(1200000,0,2000000,0,0)),("🎯 Revisar solo áreas críticas","Costo moderado.",(1800000,0,800000,0,0)),("🙈 No revisar todavía","Ahorras hoy, asumes más riesgo.",(2200000,0,0,0,0))]},
14:{"emoji":"🤝","title":"¡Contrato gigante!","color":"#3a86ff","bg":"linear-gradient(135deg,#3a86ff,#06d6a0)","scene":"Un cliente quiere comprar una gran cantidad de producto.","ask":"¿Aceptas el trato?","tip":"Más ventas pueden exigir más efectivo y capacidad.","opts":[("🏆 Aceptar todo","Apuesta grande y apoyo financiero.",(5500000,0,0,0,1500000)),("👍 Aceptar una parte","Crecimiento moderado.",(3500000,0,0,0,0)),("✋ Rechazarlo","Proteges recursos.",(1400000,0,0,0,0))]},
15:{"emoji":"🏁","title":"¡Gran final!","color":"#38b000","bg":"linear-gradient(135deg,#38b000,#ffd60a)","scene":"Es tu última decisión. ¡Hay que cerrar bien la empresa!","ask":"¿Cuál es tu jugada final?","tip":"El ganador equilibra ganancia, efectivo, deuda, activos y control.","opts":[("🔥 Vender a lo grande","Buscas máxima actividad.",(5800000,0,0,0,0)),("⚖️ Cierre equilibrado","Vendes, pagas deuda y refuerzas control.",(3800000,0,500000,1500000,0)),("🧹 Limpiar deudas","Produces menos y reduces obligaciones.",(2000000,0,0,3000000,0))]}
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&display=swap');
html,body,[class*='css'],.stApp{font-family:'Baloo 2',system-ui,sans-serif}.block-container{max-width:1180px;padding-top:1rem}.stApp{color:#fff}.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label{color:#fff!important}
section[data-testid='stSidebar']{background:rgba(34,32,64,.94)!important;border-right:4px solid rgba(255,255,255,.3)}section[data-testid='stSidebar'] *{color:#fff!important}
.game-head{background:rgba(255,255,255,.22);border:3px solid rgba(255,255,255,.45);border-radius:30px;padding:18px 22px;box-shadow:0 10px 0 rgba(0,0,0,.13),0 18px 40px rgba(0,0,0,.12);backdrop-filter:blur(10px);margin-bottom:14px}.brand{font-size:42px;font-weight:800;text-shadow:0 4px 0 rgba(0,0,0,.15)}.sub{font-size:17px;font-weight:700}.mascot{font-size:72px;animation:bounce 1.8s infinite}.bubble{background:white;color:#2b2d42!important;border-radius:20px;padding:12px 16px;font-weight:800;display:inline-block;box-shadow:0 7px 0 rgba(0,0,0,.12)}
@keyframes bounce{0%,100%{transform:translateY(0) rotate(-3deg)}50%{transform:translateY(-10px) rotate(3deg)}}@keyframes wiggle{0%,100%{transform:rotate(-1deg)}50%{transform:rotate(1deg)}}
.mission{background:#fff;color:#25324a!important;border-radius:28px;padding:22px;border:5px solid rgba(255,255,255,.7);box-shadow:0 12px 0 rgba(0,0,0,.13),0 22px 44px rgba(0,0,0,.14);margin:12px 0}.mission *{color:#25324a!important}.mission-title{font-size:34px;font-weight:800}.mission-scene{font-size:20px;line-height:1.35}.mission-ask{font-size:25px;font-weight:800;margin-top:13px}.tip{background:#fff3bf;border:3px dashed #ffb703;padding:10px 14px;border-radius:18px;font-weight:700;margin-top:12px}.mission-emoji{font-size:105px;text-align:center;animation:wiggle 2s infinite}
.choice{background:#fff;border-radius:24px;padding:16px;min-height:158px;box-shadow:0 9px 0 rgba(0,0,0,.12);border:4px solid #fff;margin-bottom:8px}.choice *{color:#25324a!important}.choice-title{font-size:21px;font-weight:800}.choice-desc{font-size:15px;color:#52606d!important}.stButton>button{font-family:'Baloo 2',sans-serif;font-weight:800;border-radius:18px;min-height:52px;font-size:17px;box-shadow:0 5px 0 rgba(0,0,0,.16);border:0}.stButton>button:hover{transform:translateY(-2px)}
div[data-testid='stMetric']{background:rgba(255,255,255,.92);border-radius:20px;padding:10px;border:4px solid rgba(255,255,255,.45);box-shadow:0 7px 0 rgba(0,0,0,.1)}div[data-testid='stMetric'] *{color:#25324a!important}.result{background:#d8f3dc;color:#1b4332!important;border:4px solid #52b788;border-radius:22px;padding:16px;font-size:17px;font-weight:700}.result *{color:#1b4332!important}.waiting{background:#fff3bf;color:#6c4d00!important;padding:16px;border-radius:20px;border:3px dashed #ffb703}.stars{font-size:29px;letter-spacing:3px}.podium{background:white;border-radius:26px;padding:18px;text-align:center;box-shadow:0 9px 0 rgba(0,0,0,.12)}.podium *{color:#25324a!important}
@media(max-width:800px){.brand{font-size:30px}.mascot{font-size:54px}.mission-title{font-size:27px}.mission-scene{font-size:17px}.mission-ask{font-size:21px}.mission-emoji{font-size:78px}.choice{min-height:auto}}
</style>
"""
st.markdown(CSS,unsafe_allow_html=True)


def rpc(fn,payload):
    try:
        r=requests.post(f"{SUPABASE_URL}/rest/v1/rpc/{fn}",headers=HEADERS,json=payload,timeout=18)
        if r.ok:return None if not r.text else r.json()
        try:msg=r.json().get("message",r.text)
        except Exception:msg=r.text
        raise RuntimeError(msg)
    except requests.RequestException as e:raise RuntimeError(f"No se pudo conectar: {e}")

def money(x):
    x=float(x or 0);return f"${x/1_000_000:,.1f} M" if abs(x)>=1_000_000 else f"${x:,.0f}"
def num(x):
    try:return float(x or 0)
    except:return 0.0

def stars(score):
    n=max(1,min(5,int(num(score)/200)+1));return "⭐"*n+"☆"*(5-n)

def theme(round_no=0):
    bg=MISSIONS.get(round_no,{"bg":"linear-gradient(135deg,#ff6b6b,#4d96ff,#6bcb77)"})["bg"]
    st.markdown(f"<style>.stApp{{background:{bg} fixed!important;background-size:cover!important}}</style>",unsafe_allow_html=True)

def header(round_no=0):
    title=MISSIONS.get(round_no,{}).get("title","GRIY · Aventura Petrolera")
    st.markdown(f"""<div class='game-head'><div style='display:flex;justify-content:space-between;align-items:center;gap:15px'><div><div class='brand'>🎮 GRIY</div><div class='sub'>AVENTURA PETROLERA · 15 MISIONES</div><div class='bubble'>💬 GriBot: {('¡Resuelve la misión antes de que se acabe el tiempo!' if round_no else '¡Administra la empresa y llega al podio!')}</div></div><div class='mascot'>🤖</div></div></div>""",unsafe_allow_html=True)

def timer(seconds_left,label="TIEMPO"):
    s=max(0,int(seconds_left or 0))
    components.html(f"""
    <div style='font-family:Arial;text-align:center;background:white;border-radius:24px;padding:10px 14px;box-shadow:0 8px 0 rgba(0,0,0,.12);border:4px solid #ffd166'>
      <div style='font-size:13px;font-weight:900;color:#555'>{label}</div>
      <div id='n' style='font-size:42px;font-weight:900;color:#e63946'>{s}</div>
      <div style='height:16px;background:#eee;border-radius:20px;overflow:hidden'><div id='bar' style='height:100%;width:{(s/25)*100:.1f}%;background:linear-gradient(90deg,#06d6a0,#ffd166,#ef476f);transition:width 1s linear'></div></div>
    </div>
    <script>
      let x={s}; let n=document.getElementById('n'); let b=document.getElementById('bar');
      let t=setInterval(()=>{{x=Math.max(0,x-1);n.innerText=x;b.style.width=(x/25*100)+'%';if(x<=5)n.style.color='#d90429';if(x===0){{clearInterval(t);n.innerText='⏰';}}}},1000);
    </script>""",height=115)

def sidebar(round_no=0):
    with st.sidebar:
        st.markdown("# 🤖 GriBot")
        st.write("Tu compañero de aventura")
        if round_no:st.progress(round_no/15,text=f"Misión {round_no}/15")
        st.divider();st.write("🏭 **CAPEX** = comprar cosas grandes que duran")
        st.write("🧰 **OPEX** = gastos del día a día")
        st.write("💵 **Efectivo** = dinero disponible")
        st.write("💳 **Deuda** = dinero que debes")
        if st.session_state.get("room_code"):st.code(st.session_state.room_code)
        if st.session_state.get("role") and st.button("🚪 Salir",use_container_width=True):
            for k in ["role","room_code","admin_pin","player_token","player_name","last_result","last_round"]:st.session_state[k]=None if k=="role" else ""
            st.rerun()

def mission_card(n):
    m=MISSIONS[n]
    c1,c2=st.columns([1,2])
    with c1:st.markdown(f"<div class='mission'><div class='mission-emoji'>{m['emoji']}</div></div>",unsafe_allow_html=True)
    with c2:st.markdown(f"<div class='mission'><div style='font-weight:800;color:{m['color']}!important'>MISIÓN {n} DE 15</div><div class='mission-title'>{m['title']}</div><div class='mission-scene'>{m['scene']}</div><div class='mission-ask'>{m['ask']}</div><div class='tip'>💡 GriBot explica: {m['tip']}</div></div>",unsafe_allow_html=True)

def choose_grid(n,token):
    m=MISSIONS[n];letters=["A","B","C"];cols=st.columns(3)
    for i,(title,desc,payload) in enumerate(m["opts"]):
        with cols[i]:
            st.markdown(f"<div class='choice'><div style='font-size:14px;font-weight:800;color:{m['color']}!important'>OPCIÓN {letters[i]}</div><div class='choice-title'>{title}</div><div class='choice-desc'>{desc}</div></div>",unsafe_allow_html=True)
            if st.button(f"✨ Elegir {letters[i]}",key=f"opt{n}_{i}",use_container_width=True,type="primary" if i==1 else "secondary"):
                o,c,ctrl,pay,fin=payload
                try:
                    ns=rpc("griy_submit_decision",{"p_player_token":token,"p_operations":o,"p_capex":c,"p_controls":ctrl,"p_debt_payment":pay,"p_financing":fin})
                    st.session_state.last_result=f"{title}. Ahora tienes {money(ns['cash'])} en efectivo, {money(ns['debt'])} de deuda y {num(ns['score']):.0f} puntos."
                    st.session_state.last_round=n
                    st.rerun()
                except Exception as e:st.error(str(e))

for k,v in {"role":None,"room_code":"","admin_pin":"","player_token":"","player_name":"","last_result":"","last_round":0}.items():st.session_state.setdefault(k,v)

if not st.session_state.role:
    theme();header();sidebar();st.markdown("## 🎯 Elige tu modo")
    a,b=st.columns(2)
    with a:
        st.markdown("<div class='mission'><div class='mission-emoji'>🧒</div><div class='mission-title'>Jugador</div><div class='mission-scene'>Entra con el código y completa las 15 misiones.</div></div>",unsafe_allow_html=True)
        if st.button("🎮 JUGAR",use_container_width=True,type="primary"):st.session_state.role="participante";st.rerun()
    with b:
        st.markdown("<div class='mission'><div class='mission-emoji'>🧑‍🏫</div><div class='mission-title'>Administrador</div><div class='mission-scene'>Crea la sala, controla las misiones y mira el ranking.</div></div>",unsafe_allow_html=True)
        if st.button("🕹️ CONTROLAR PARTIDA",use_container_width=True):st.session_state.role="administrador";st.rerun()
    st.stop()

if st.session_state.role=="participante":
    if not st.session_state.player_token:
        theme();header();sidebar()
        with st.form("join"):
            st.markdown("## 🚪 Entra a la aventura")
            code=st.text_input("Código de sala",placeholder="GRIY-1234").strip().upper();name=st.text_input("Tu nombre o apodo").strip();go=st.form_submit_button("🚀 ENTRAR",type="primary",use_container_width=True)
        if go:
            try:
                d=rpc("griy_join_room",{"p_code":code,"p_name":name});st.session_state.player_token=d["player_token"];st.session_state.player_name=d["name"];st.session_state.room_code=d["room_code"];st.rerun()
            except Exception as e:st.error(str(e))
        st.stop()
    try:p=rpc("griy_player_state",{"p_player_token":st.session_state.player_token})
    except Exception as e:theme();header();sidebar();st.error(str(e));st.stop()
    n=int(p.get("current_round") or 0);theme(n);header(n);sidebar(n)
    st.markdown(f"## 👋 ¡Hola, {p['name']}!")
    x1,x2,x3,x4=st.columns(4);x1.metric("💵 Dinero",money(p['cash']));x2.metric("🏆 Puntos",f"{num(p['score']):.0f}");x3.metric("📍 Lugar",f"#{p['rank']}");x4.metric("💳 Deuda",money(p['debt']))
    st.markdown(f"<div class='stars'>{stars(p['score'])}</div>",unsafe_allow_html=True)
    if p['room_status']=='waiting':st.markdown("<div class='waiting'>⏳ GriBot dice: espera a que el administrador empiece.</div>",unsafe_allow_html=True);st.button("🔄 Revisar") and st.rerun();st.stop()
    if p['room_status']=='paused':st.warning("⏸️ El juego está pausado.");st.stop()
    if p['room_status']=='finished':
        st.balloons();st.markdown(f"# 🏁 ¡Terminaste!\n## Quedaste en el lugar #{p['rank']}");st.stop()
    if st.session_state.last_result and st.session_state.last_round==n:st.markdown(f"<div class='result'>🎉 {st.session_state.last_result}</div>",unsafe_allow_html=True)
    if p['submitted']:st.success("✅ ¡Misión completada! Espera a la siguiente.");st.button("🔄 Actualizar") and st.rerun();st.stop()
    mission_card(n)
    if p.get('expired'):
        st.error("⏰ ¡Se acabó el tiempo! Espera la siguiente misión.");st.stop()
    timer(p.get('seconds_left',25),"⏱️ RESPONDE RÁPIDO")
    choose_grid(n,st.session_state.player_token)

if st.session_state.role=="administrador":
    if not st.session_state.room_code:
        theme();header();sidebar();a,b=st.tabs(["➕ Nueva partida","🔓 Abrir partida"])
        with a:
            with st.form("new"):
                title=st.text_input("Nombre",value="GRIY · Aventura Petrolera");pin=st.text_input("PIN",type="password");mx=st.number_input("Jugadores",1,60,30);go=st.form_submit_button("🎉 CREAR PARTIDA",type="primary",use_container_width=True)
            if go:
                try:d=rpc("griy_create_room",{"p_admin_pin":pin,"p_title":title,"p_max_players":int(mx)});st.session_state.room_code=d['code'];st.session_state.admin_pin=pin;st.rerun()
                except Exception as e:st.error(str(e))
        with b:
            with st.form("open"):
                code=st.text_input("Código").strip().upper();pin2=st.text_input("PIN",type="password");go2=st.form_submit_button("ABRIR")
            if go2:
                try:rpc("griy_admin_state",{"p_code":code,"p_pin":pin2});st.session_state.room_code=code;st.session_state.admin_pin=pin2;st.rerun()
                except Exception as e:st.error(str(e))
        st.stop()
    try:s=rpc("griy_admin_state",{"p_code":st.session_state.room_code,"p_pin":st.session_state.admin_pin});room=s['room'];agg=s['aggregate'];players=s['players']
    except Exception as e:theme();header();sidebar();st.error(str(e));st.stop()
    n=int(room.get('current_round') or 0);theme(n);header(n);sidebar(n)
    st.markdown(f"<div class='game-head'><div style='font-size:18px;font-weight:800'>📣 CÓDIGO PARA ENTRAR</div><div style='font-size:48px;font-weight:800'>{room['code']}</div></div>",unsafe_allow_html=True)
    if n in MISSIONS:mission_card(n);timer(room.get('seconds_left',25),"⏱️ TIEMPO DE LA MISIÓN")
    a,b,c,d=st.columns(4);a.metric("👥 Jugadores",f"{agg['player_count']} / {room['max_players']}");b.metric("✅ Respondieron",agg['submitted']);c.metric("🏆 Puntos promedio",f"{num(agg['avg_score']):.0f}");d.metric("📈 Ganancia promedio",money(agg['avg_profit']))
    q1,q2,q3,q4=st.columns(4)
    with q1:
        if room['status']=='waiting' and st.button("🚀 INICIAR",use_container_width=True,type="primary"):
            try:rpc("griy_admin_start",{"p_code":room['code'],"p_pin":st.session_state.admin_pin});st.rerun()
            except Exception as e:st.error(str(e))
    with q2:
        if room['status'] in ['running','paused']:
            label="⏸️ PAUSAR" if room['status']=='running' else "▶️ REANUDAR"
            if st.button(label,use_container_width=True):
                try:rpc("griy_admin_pause_toggle",{"p_code":room['code'],"p_pin":st.session_state.admin_pin});st.rerun()
                except Exception as e:st.error(str(e))
    with q3:
        if room['status'] in ['running','paused'] and st.button("⏭️ SIGUIENTE MISIÓN",use_container_width=True):
            try:rpc("griy_admin_advance",{"p_code":room['code'],"p_pin":st.session_state.admin_pin});st.rerun()
            except Exception as e:st.error(str(e))
    with q4:
        if st.button("🔄 ACTUALIZAR",use_container_width=True):st.rerun()
    if players:
        df=pd.DataFrame(players);cols=[c for c in ['name','score','profit','cash','debt','submitted'] if c in df.columns];df=df[cols].rename(columns={'name':'Jugador','score':'Puntos','profit':'Ganancia','cash':'Dinero','debt':'Deuda','submitted':'Listo'})
        st.dataframe(df,use_container_width=True,hide_index=True)
        if room['status']=='finished':
            st.balloons();st.markdown("# 🏆 PODIO GRIY");pod=df.sort_values(['Puntos','Ganancia'],ascending=False).head(3).reset_index(drop=True);med=['🥇','🥈','🥉'];pc=st.columns(len(pod))
            for i,row in pod.iterrows():
                with pc[i]:st.markdown(f"<div class='podium'><div style='font-size:55px'>{med[i]}</div><h2>{row['Jugador']}</h2><div style='font-size:28px;font-weight:800'>{row['Puntos']:.0f} pts</div></div>",unsafe_allow_html=True)
    else:st.info("Todavía no entra nadie.")

st.caption("GRIY es una simulación académica independiente. No es un sitio oficial ni está afiliado a Petróleos Mexicanos.")
