import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

st.set_page_config(
    page_title="Sensor en Vivo",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: linear-gradient(160deg, #f0f4ff 0%, #faf5ff 50%, #f0fff8 100%);
    min-height: 100vh;
}

[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid #ede8f5 !important;
    box-shadow: 4px 0 24px rgba(120,80,200,0.06) !important;
}
[data-testid="stSidebar"] label {
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    color: #7c6faa !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    border-radius: 12px !important;
    border: 2px solid #ede8f5 !important;
    background: #faf8ff !important;
    color: #3a2f5e !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 14px !important;
    font-size: 0.9rem !important;
}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stNumberInput input:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 4px rgba(167,139,250,0.15) !important;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: white;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 20px;
    margin-bottom: 12px;
}
.hero-title {
    font-family: 'Nunito', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 50%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 8px;
}
.hero-sub {
    font-size: 1rem;
    color: #9ca3af;
    font-weight: 400;
    margin-bottom: 28px;
}

.info-card {
    background: white;
    border-radius: 20px;
    padding: 18px 22px;
    border: 1px solid #ede8f5;
    box-shadow: 0 4px 20px rgba(120,80,200,0.06);
    display: flex;
    gap: 20px;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.info-chip { display: flex; flex-direction: column; gap: 2px; }
.info-chip-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #c4b5fd; }
.info-chip-value { font-size: 0.9rem; font-weight: 600; color: #4c1d95; }
.dot-live {
    width: 10px; height: 10px; border-radius: 50%;
    background: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.2);
    animation: breathe 2s ease-in-out infinite; flex-shrink: 0;
}
.dot-idle { width: 10px; height: 10px; border-radius: 50%; background: #d1d5db; flex-shrink: 0; }
@keyframes breathe {
    0%, 100% { box-shadow: 0 0 0 3px rgba(16,185,129,0.2); }
    50% { box-shadow: 0 0 0 6px rgba(16,185,129,0.08); }
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 16px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 14px 28px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

[data-testid="stMetric"] {
    background: white !important;
    border-radius: 20px !important;
    padding: 24px !important;
    border: 1px solid #ede8f5 !important;
    box-shadow: 0 4px 20px rgba(120,80,200,0.06) !important;
    text-align: center !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #a78bfa !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Nunito', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #4c1d95 !important;
}

.stSuccess > div {
    background: linear-gradient(135deg, #ecfdf5, #f0fdf9) !important;
    border: 1px solid #a7f3d0 !important;
    border-radius: 14px !important;
    color: #065f46 !important;
    font-weight: 600 !important;
}
.stError > div {
    background: linear-gradient(135deg, #fef2f2, #fff5f5) !important;
    border: 1px solid #fecaca !important;
    border-radius: 14px !important;
    color: #991b1b !important;
}

[data-testid="stExpander"] {
    background: white !important;
    border: 1px solid #ede8f5 !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 12px rgba(120,80,200,0.04) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #7c3aed !important;
    font-size: 0.9rem !important;
}

hr { border: none !important; border-top: 1px solid #ede8f5 !important; margin: 24px 0 !important; }
.stSpinner > div { border-top-color: #7c3aed !important; }
.stJson { border-radius: 12px !important; border: 1px solid #ede8f5 !important; }

.timestamp-tag {
    display: inline-block;
    background: #f5f3ff;
    color: #7c3aed;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    margin-top: 16px;
    border: 1px solid #ddd6fe;
}
.section-heading {
    font-family: 'Nunito', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #4c1d95;
    margin-bottom: 16px;
}
.sidebar-brand {
    font-family: 'Nunito', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    background: linear-gradient(135deg, #7c3aed, #059669);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}
.sidebar-tip { font-size: 0.72rem; color: #c4b5fd; margin-bottom: 20px; font-weight: 500; }
.sidebar-broker-pill {
    background: #f5f3ff;
    border: 1px solid #ddd6fe;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 0.75rem;
    color: #7c3aed;
    margin-bottom: 6px;
    font-weight: 500;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #ddd6fe; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #a78bfa; }
</style>
""", unsafe_allow_html=True)

if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'connected' not in st.session_state:
    st.session_state.connected = False

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

with st.sidebar:
    st.markdown('<div class="sidebar-brand"> Sensor Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tip">Configura tu conexión MQTT</div>', unsafe_allow_html=True)
    broker    = st.text_input('Broker', value='broker.mqttdashboard.com')
    port      = st.number_input('Puerto', value=1883, min_value=1, max_value=65535)
    topic     = st.text_input('Tópico', value='Sensor/THP2')
    client_id = st.text_input('ID del cliente', value='streamlit_client')
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Brokers de prueba**")
    for b in ['broker.mqttdashboard.com', 'test.mosquitto.org', 'broker.hivemq.com']:
        st.markdown(f'<div class="sidebar-broker-pill">› {b}</div>', unsafe_allow_html=True)

st.markdown('<div class="hero-title">Monitor de Sensor</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Lee y visualiza datos de cualquier sensor MQTT al instante.</div>', unsafe_allow_html=True)

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
3. Los valores del sensor aparecen como tarjetas bonitas
4. Espera hasta **5 segundos** para que llegue el mensaje
    """)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("✨  Obtener datos del sensor", use_container_width=True):
    with st.spinner("Conectando... espera un momento 🌐"):
        data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = data
        st.session_state.last_update = time.strftime('%d/%m/%Y — %H:%M:%S')
        st.session_state.connected = not (isinstance(data, dict) and 'error' in data)
    st.rerun()

if st.session_state.sensor_data:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)
    data = st.session_state.sensor_data

    if isinstance(data, dict) and 'error' in data:
        st.error(f"No se pudo conectar: {data['error']}")
        st.markdown("Verifica que el broker esté activo y el puerto sea correcto.")
    else:
        st.success("¡Datos recibidos correctamente! 🎉")
        st.markdown('<div class="section-heading">📊 Valores del sensor</div>', unsafe_allow_html=True)

        if isinstance(data, dict):
            cols = st.columns(max(len(data), 1))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key, value=value)

            st.markdown(f'<div class="timestamp-tag">🕐 {st.session_state.last_update}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("Ver datos en formato JSON"):
                st.json(data)
        else:
            st.code(data, language=None)
