import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

st.set_page_config(
    page_title="Monitor de Sensor",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Source+Sans+3:wght@300;400;600&family=Source+Code+Pro&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}

.stApp {
    background-color: #f7f6f3;
}

[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: none !important;
}
[data-testid="stSidebar"] label {
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    color: #888888 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background-color: #1c1c1c !important;
    border: 1px solid #333333 !important;
    border-radius: 4px !important;
    color: #eeeeee !important;
    font-family: 'Source Code Pro', monospace !important;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stNumberInput input:focus {
    border-color: #666666 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] div {
    color: #aaaaaa !important;
}
[data-testid="stSidebar"] strong {
    color: #dddddd !important;
}

.page-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #aaaaaa;
    margin-bottom: 8px;
}
.page-title {
    font-family: 'Merriweather', serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #111111;
    line-height: 1.15;
    margin-bottom: 6px;
}
.page-sub {
    font-size: 0.95rem;
    color: #777777;
    font-weight: 300;
    margin-bottom: 28px;
    line-height: 1.6;
}
.page-rule {
    border: none;
    border-top: 2px solid #111111;
    margin: 16px 0 24px 0;
}

.info-card {
    background: #ffffff;
    border: 1px solid #e0ddd8;
    border-radius: 6px;
    padding: 16px 20px;
    display: flex;
    gap: 24px;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.info-chip { display: flex; flex-direction: column; gap: 2px; }
.info-chip-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #aaaaaa;
}
.info-chip-value {
    font-size: 0.88rem;
    font-weight: 600;
    color: #222222;
}
.dot-live {
    width: 9px; height: 9px; border-radius: 50%;
    background: #333333;
    box-shadow: 0 0 0 3px rgba(50,50,50,0.15);
    animation: breathe 2.5s ease-in-out infinite;
    flex-shrink: 0;
}
.dot-idle {
    width: 9px; height: 9px; border-radius: 50%;
    background: #cccccc; flex-shrink: 0;
}
@keyframes breathe {
    0%, 100% { box-shadow: 0 0 0 3px rgba(50,50,50,0.12); }
    50%       { box-shadow: 0 0 0 6px rgba(50,50,50,0.05); }
}

.stButton > button {
    background-color: #111111 !important;
    color: #f7f6f3 !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    padding: 12px 28px !important;
    transition: background-color 0.2s !important;
}
.stButton > button:hover {
    background-color: #2a2a2a !important;
}
.stButton > button:active {
    background-color: #000000 !important;
}

[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e0ddd8 !important;
    border-radius: 6px !important;
    padding: 20px !important;
    text-align: center !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Source Code Pro', monospace !important;
    font-size: 0.62rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #aaaaaa !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Merriweather', serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #111111 !important;
}

.stSuccess > div {
    background-color: #f5f5f2 !important;
    border: 1px solid #cccccc !important;
    border-left: 3px solid #333333 !important;
    border-radius: 4px !important;
    color: #333333 !important;
    font-size: 0.88rem !important;
}
.stError > div {
    background-color: #f7f5f5 !important;
    border: 1px solid #d0c8c8 !important;
    border-left: 3px solid #666666 !important;
    border-radius: 4px !important;
    color: #444444 !important;
    font-size: 0.88rem !important;
}
.stWarning > div {
    background-color: #f6f5f2 !important;
    border: 1px solid #d0cdc8 !important;
    border-left: 3px solid #888888 !important;
    border-radius: 4px !important;
    color: #555555 !important;
    font-size: 0.88rem !important;
}
.stInfo > div {
    background-color: #f5f4f1 !important;
    border: 1px solid #d8d5cf !important;
    border-left: 3px solid #aaaaaa !important;
    border-radius: 4px !important;
    color: #555555 !important;
    font-size: 0.88rem !important;
}

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e0ddd8 !important;
    border-radius: 4px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #333333 !important;
    font-size: 0.88rem !important;
}

.section-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #aaaaaa;
    margin: 24px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label::after {
    content: '';
    flex: 1;
    border-top: 1px solid #e0ddd8;
}

.timestamp-tag {
    display: inline-block;
    background: #f0ede8;
    color: #666666;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.7rem;
    padding: 4px 12px;
    border-radius: 3px;
    margin-top: 14px;
    border: 1px solid #d8d5cf;
}

.broker-pill {
    background: #1c1c1c;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 7px 11px;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.72rem;
    color: #888888;
    margin-bottom: 5px;
}

hr { border: none !important; border-top: 1px solid #e0ddd8 !important; margin: 20px 0 !important; }
.stSpinner > div { border-top-color: #333333 !important; }
.stJson { border-radius: 4px !important; border: 1px solid #e0ddd8 !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #f7f6f3; }
::-webkit-scrollbar-thumb { background: #cccccc; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #999999; }
</style>
""", unsafe_allow_html=True)

# ── State ──────────────────────────────────────────────────────────────────────
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'connected' not in st.session_state:
    st.session_state.connected = False

# ── MQTT ───────────────────────────────────────────────────────────────────────
def get_mqtt_message(broker, port, topic, client_id):
    message_received = {"received": False, "payload": None}
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except Exception:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        client.loop_stop()
        client.disconnect()
        return message_received["payload"]
    except Exception as e:
        return {"error": str(e)}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="padding:8px 0 20px 0;">
  <div style="font-family:'Merriweather',serif; font-size:1rem; font-weight:700; color:#eeeeee; margin-bottom:4px;">Sensor Monitor</div>
  <div style="font-family:'Source Code Pro',monospace; font-size:0.65rem; color:#555555; letter-spacing:0.1em;">MQTT · Tiempo real</div>
</div>
""", unsafe_allow_html=True)

    broker    = st.text_input('Broker', value='broker.mqttdashboard.com')
    port      = st.number_input('Puerto', value=1883, min_value=1, max_value=65535)
    topic     = st.text_input('Tópico', value='Sensor/THP2')
    client_id = st.text_input('ID del cliente', value='streamlit_client')

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Source Code Pro\',monospace; font-size:0.6rem; letter-spacing:0.18em; text-transform:uppercase; color:#555555; margin-bottom:10px;">Brokers de prueba</div>', unsafe_allow_html=True)
    for b in ['broker.mqttdashboard.com', 'test.mosquitto.org', 'broker.hivemq.com']:
        st.markdown(f'<div class="broker-pill">› {b}</div>', unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-label">Monitor MQTT</div>', unsafe_allow_html=True)
st.markdown('<div class="page-title">Monitor de Sensor</div>', unsafe_allow_html=True)
st.markdown('<hr class="page-rule">', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Lee y visualiza datos de cualquier sensor MQTT al instante.</div>', unsafe_allow_html=True)

# ── Status card ────────────────────────────────────────────────────────────────
dot = '<div class="dot-live"></div>' if st.session_state.connected else '<div class="dot-idle"></div>'
ts  = st.session_state.last_update or "Sin lecturas aún"
st.markdown(f"""
<div class="info-card">
  {dot}
  <div class="info-chip">
    <span class="info-chip-label">Broker</span>
    <span class="info-chip-value">{broker}</span>
  </div>
  <div class="info-chip">
    <span class="info-chip-label">Tópico</span>
    <span class="info-chip-value">{topic}</span>
  </div>
  <div class="info-chip">
    <span class="info-chip-label">Puerto</span>
    <span class="info-chip-value">{int(port)}</span>
  </div>
  <div class="info-chip" style="margin-left:auto;">
    <span class="info-chip-label">Última lectura</span>
    <span class="info-chip-value">{ts}</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("¿Cómo funciona?"):
    st.markdown("""
1. **Configura** el broker y el tópico en el menú lateral
2. **Presiona** el botón para conectarte y recibir datos
3. Los valores del sensor aparecen como tarjetas
4. Espera hasta **5 segundos** para que llegue el mensaje
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ── Button ─────────────────────────────────────────────────────────────────────
if st.button("Obtener datos del sensor", use_container_width=True):
    with st.spinner("Conectando al broker..."):
        data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = data
        st.session_state.last_update = time.strftime('%d/%m/%Y — %H:%M:%S')
        st.session_state.connected = not (isinstance(data, dict) and 'error' in data)
    st.rerun()

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.sensor_data:
    st.markdown('<hr>', unsafe_allow_html=True)
    data = st.session_state.sensor_data

    if isinstance(data, dict) and 'error' in data:
        st.error(f"No se pudo conectar: {data['error']}")
        st.markdown("Verifica que el broker esté activo y el puerto sea correcto.")
    else:
        st.success("Datos recibidos correctamente.")
        st.markdown('<div class="section-label">Valores del sensor</div>', unsafe_allow_html=True)

        if isinstance(data, dict):
            cols = st.columns(max(len(data), 1))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key, value=value)

            st.markdown(f'<div class="timestamp-tag">Última lectura: {st.session_state.last_update}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("Ver JSON completo"):
                st.json(data)
        else:
            st.code(data, language=None)
