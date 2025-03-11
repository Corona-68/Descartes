import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(
    page_title="Análisis de Aeronaves",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-title {
        color: #2c3e50;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1em;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1em;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .warning-text {
        color: #EF553B;
        font-weight: bold;
    }
    .result-value {
        font-size: 16px;
        margin: 0.5em 0;
    }
    .highlight-red {
        color: red;
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("aeronaves.csv", encoding='latin1')
        df["LCRi"] = pd.to_numeric(df["LCRi"], errors="coerce")
        return df
    except FileNotFoundError:
        st.error("🚨 El archivo aeronaves.csv no fue encontrado")
        st.stop()
    except pd.errors.ParserError:
        st.error("❌ Error al procesar el archivo CSV")
        st.stop()

df = load_data()

# Sidebar con diseño mejorado
with st.sidebar:
    st.title("✈️ Revisión de long. pista de Aeropuertos")

    # Nombre del desarrollador en letra pequeña
    st.markdown("<small>Desarrollado por: Martín Olvera Corona incimoc@gmail.com tel 961-6622-614</small>", unsafe_allow_html=True)
    
    with st.expander("📍 Datos Generales", expanded=True):
        nombre_aeropuerto = st.text_input(
            "Nombre del Aeropuerto",
            value="Tuxtla Gutiérrez",
            help="Ingrese el nombre del aeropuerto"
        )

    with st.expander("🛫 Datos de Pista", expanded=True):
        LRP = st.number_input(
            "Longitud de pista (m)",
            min_value=0.0,
            max_value=5000.0,
            value=3102.0,
            step=10.0,
            format="%.1f"
        )
        H = st.number_input(
            "Altitud (m)",
            min_value=0.0,
            max_value=5000.0,
            value=73.0,
            step=10.0,
            format="%.1f"
        )
        TA = st.number_input(
            "Temperatura (°C)",
            min_value=-50.0,
            max_value=60.0,
            value=30.0,
            step=1.0,
            format="%.1f"
        )
        P = st.number_input(
            "Pendiente (%)",
            min_value=-10.0,
            max_value=10.0,
            value=0.65,
            step=0.01,
            format="%.2f"
        )

    procesar = st.button("🔍 Analizar", use_container_width=True)

# Contenido principal
if procesar:
    # Cálculos
    FH = 1 + (0.07 * H / 300)
    FT = 1 + 0.01 * (TA - (14.991 - 0.0065 * H))
    FC = FH * FT
    FP = 1 + 0.1 * P
    LCR = LRP / (FC * FP)

    # Nuevo expander para resultados
    with st.sidebar.expander("📊 Resultados de Cálculo", expanded=True):
        col1, col2 = st.columns(2)
        
        col1.markdown(f"<div class='result-value'>FH: {FH:.3f}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='result-value'>FT: {FT:.3f}</div>", unsafe_allow_html=True)
        
        if FC > 1.35:
            col1.markdown(f"<div class='result-value highlight-red'>FC: {FC:.2f}</div>", unsafe_allow_html=True)
        else:
            col1.markdown(f"<div class='result-value'>FC: {FC:.3f}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='result-value'>FP: {FP:.3f}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='result-value' style='font-size:20px; color:green; font-weight:bold;'>LCR(m) = {LCR:.2f}</div>", unsafe_allow_html=True)

    # Análisis de aeronaves
    df["Puede Despegar"] = df["LCRi"].apply(lambda x: "✅ Sí" if LCR > x else "❌ No")
    
    # Visualización mejorada
    st.subheader("📋 Lista de Aeronaves")
    st.dataframe(
        df.style.format({"LCRi": "{:.0f}"})
                .highlight_max(subset=["LCRi"], color="#ff9999")
                .highlight_min(subset=["LCRi"], color="#99ff99"),
        use_container_width=True,
        height=400
    )

    # Gráfico interactivo
    fig = px.bar(
        df,
        x=df.index,
        y="LCRi",
        title="Requerimientos de Pista por Aeronave",
        color="Puede Despegar",
        color_discrete_map={"✅ Sí": "#00CC96", "❌ No": "#EF553B"}
    )
    fig.add_hline(y=LCR, line_dash="dash", line_color="blue", 
                 annotation_text=f"LCR = {LCR:.0f}m")
    st.plotly_chart(fig, use_container_width=True)

    # Alertas
    if FC > 1.35:
        st.error(
            "⚠️ Factor Combinado (altitud + temperatura) (>1.35). Revisar condiciones o considerar procedimientos alternativos."
        )

# Footer
st.markdown("---")
st.caption(f"Análisis generado el {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
