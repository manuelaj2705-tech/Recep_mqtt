import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MQTT Sensor Monitor",
    page_icon="📡",
    layout="wide"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
}

.stApp {
    background-color: #0a0e14;
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(0, 255, 136, 0.04) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 180, 255, 0.04) 0%, transparent 60%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #1e2d3d !important;
}

[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background-color: #0a0e14 !important;
    border: 1px solid #1e3a2f !important;
    color: #00ff88 !important;
    font-family: 'Share Tech Mono', monospace !important;
    border-radius: 4px !important;
}

[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stNumberInput input:focus {
    border-color: #00ff88 !important;
    box-shadow: 0 0 0 1px #00ff88, 0 0 12px rgba(0,255,136,0.2) !important;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #7a8fa6 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* ── Main Title ── */
.main-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2rem;
    color: #00ff88;
    text-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
    letter-spacing: 0.05em;
    margin-bottom: 0;
    line-height: 1.2;
}

.main-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #3a5a45;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 2px;
    margin-bottom: 24px;
}

/* ── Status Bar ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #0d1117;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    padding: 10px 18px;
    margin-bottom: 24px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #4a6a5a;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #1e3a2f;
    display: inline-block;
    flex-shrink: 0;
}

.status-dot.active {
    background: #00ff88;
    box-shadow: 0 0 8px #00ff88;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.status-label { color: #7a8fa6; }
.status-value {
    color: #00ff88;
    font-weight: 600;
}

/* ── Config Panel (sidebar header) ── */
.sidebar-section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: #3a5a45;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2d3d;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #001a0f 0%, #00331f 100%) !important;
    border: 1px solid #00ff88 !important;
    color: #00ff88 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    padding: 12px 24px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(0,255,136,0.1) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #003020 0%, #005030 100%) !important;
    box-shadow: 0 0 30px rgba(0,255,136,0.3) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: #0d1117 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 6px !important;
    padding: 20px !important;
    position: relative;
    overflow: hidden;
}

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00ff88, transparent);
}

[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #4a6a5a !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.6rem !important;
    color: #00ff88 !important;
    text-shadow: 0 0 15px rgba(0,255,136,0.3) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background-color: #0d1117 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 6px !important;
}

[data-testid="stExpander"] summary {
    color: #7a8fa6 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
}

/* ── Alerts ── */
.stSuccess {
    background-color: #001a0f !important;
    border: 1px solid #00ff88 !important;
    border-radius: 4px !important;
    color: #00ff88 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

.stError {
    background-color: #1a0005 !important;
    border: 1px solid #ff0044 !important;
    border-radius: 4px !important;
    color: #ff4466 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── JSON viewer ── */
.stJson {
    background-color: #060a0e !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 4px !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* ── Divider ── */
hr {
    border-color: #1e2d3d !important;
    margin: 20px 0 !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #00ff88 !important;
}

/* ── Section labels ── */
.section-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #3a5a45;
    margin-bottom: 12px;
}

.data-panel {
    background: #0d1117;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    padding: 24px;
    margin-top: 16px;
}

.data-panel-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #3a5a45;
    border-bottom: 1px solid #1e2d3d;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.timestamp {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #3a5a45;
    text-align: right;
    margin-top: 12px;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0e14; }
::-webkit-scrollbar-thumb { background: #1e3a2f; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00ff88; }
</style>
""", unsafe_allow_html=True)

# ─── State ─────────────────────────────────────────────────────────────────────
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'connected' not in st.session_state:
    st.session_state.connected = False

# ─── MQTT Logic ────────────────────────────────────────────────────────────────
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

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section-title">// Configuración de Conexión</div>', unsafe_allow_html=True)

    broker = st.text_input(
        'Broker MQTT',
        value='broker.mqttdashboard.com',
        help='Dirección IP o dominio del broker'
    )
    port = st.number_input(
        'Puerto',
        value=1883, min_value=1, max_value=65535,
        help='Puerto TCP del broker'
    )
    topic = st.text_input(
        'Tópico',
        value='Sensor/THP2',
        help='Canal MQTT a suscribirse'
    )
    client_id = st.text_input(
        'ID del Cliente',
        value='streamlit_client',
        help='Identificador único de este cliente'
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">// Brokers Públicos</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; color: #4a6a5a; line-height: 1.8;">
› broker.mqttdashboard.com<br>
› test.mosquitto.org<br>
› broker.hivemq.com
</div>
""", unsafe_allow_html=True)

# ─── Main Layout ───────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])

with col_title:
    st.markdown('<div class="main-header">📡 MQTT SENSOR MONITOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Real-time data acquisition interface</div>', unsafe_allow_html=True)

# Status bar
dot_class = "active" if st.session_state.connected else ""
last_ts = st.session_state.last_update if st.session_state.last_update else "—"
st.markdown(f"""
<div class="status-bar">
    <span class="status-dot {dot_class}"></span>
    <span class="status-label">BROKER:</span>
    <span class="status-value">{broker}</span>
    <span style="color:#1e2d3d;">│</span>
    <span class="status-label">TÓPICO:</span>
    <span class="status-value">{topic}</span>
    <span style="color:#1e2d3d;">│</span>
    <span class="status-label">PUERTO:</span>
    <span class="status-value">{int(port)}</span>
    <span style="color:#1e2d3d; margin-left:auto;">ÚLTIMA LECTURA: </span>
    <span class="status-value">{last_ts}</span>
</div>
""", unsafe_allow_html=True)

# Info expander
with st.expander('ℹ️  Instrucciones de uso'):
    st.markdown("""
<div style="font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; color: #4a6a5a; line-height: 2;">
<span style="color:#00ff88;">01.</span> Configura el broker en el panel lateral<br>
<span style="color:#00ff88;">02.</span> Ingresa el tópico al que deseas suscribirte<br>
<span style="color:#00ff88;">03.</span> Asigna un ID de cliente único<br>
<span style="color:#00ff88;">04.</span> Presiona <span style="color:#00ff88;">OBTENER DATOS</span> — espera hasta 5 segundos<br>
<span style="color:#00ff88;">05.</span> Los valores del sensor aparecerán como métricas
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Fetch Button ──────────────────────────────────────────────────────────────
if st.button('⟳  OBTENER DATOS DEL SENSOR', use_container_width=True):
    with st.spinner('Conectando al broker MQTT...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data
        st.session_state.last_update = time.strftime('%Y-%m-%d  %H:%M:%S')
        st.session_state.connected = not (isinstance(sensor_data, dict) and 'error' in sensor_data)
    st.rerun()

# ─── Results ───────────────────────────────────────────────────────────────────
if st.session_state.sensor_data:
    data = st.session_state.sensor_data

    if isinstance(data, dict) and 'error' in data:
        st.error(f"⚠  Error de conexión: {data['error']}")
        st.markdown("""
<div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#4a4040; margin-top:8px;">
Verifica que el broker esté disponible y el puerto sea correcto.
</div>
""", unsafe_allow_html=True)

    else:
        st.markdown('<div class="section-label">// Telemetría recibida</div>', unsafe_allow_html=True)
        st.success('✓  Paquete recibido correctamente')

        if isinstance(data, dict):
            # Metric cards
            cols = st.columns(max(len(data), 1))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key.upper(), value=value)

            # Raw JSON
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander('{ }  Ver payload JSON completo'):
                st.json(data)
        else:
            st.markdown(f"""
<div style="
    background:#060a0e;
    border:1px solid #1e2d3d;
    border-radius:4px;
    padding:16px;
    font-family:'Share Tech Mono',monospace;
    font-size:0.85rem;
    color:#00ff88;
    letter-spacing:0.05em;
">{data}</div>
""", unsafe_allow_html=True)

        st.markdown(f'<div class="timestamp">// TIMESTAMP: {st.session_state.last_update}</div>',
                    unsafe_allow_html=True)
