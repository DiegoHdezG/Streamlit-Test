import streamlit as st
from modulos.carga_datos import CargadorDatos
from modulos.filtros import GestorFiltros
from modulos.graficos import GestorGraficos
from modulos.utilidades import boton_descarga_csv

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
st.set_page_config(page_title="Explorador de Repostajes", layout="wide")
st.title("🚗 Explorador de Repostajes")

# ==============================
# CARGA DE DATOS
# ==============================
st.sidebar.header("Datos de entrada")
modo = st.sidebar.radio("Fuente de datos", ["Subir archivo", "Ruta local"])

cargador = CargadorDatos()

if modo == "Subir archivo":
    archivo = st.sidebar.file_uploader("Sube un Excel (.xlsx)", type=["xlsx"])
    if archivo:
        df = cargador.cargar_desde_subida(archivo)
    else:
        st.info("📎 Sube un archivo para comenzar.")
        st.stop()
else:
    ruta = st.sidebar.text_input("Ruta local del Excel", "datos/Ejemplo_Repostajes.xlsx")
    df = cargador.cargar_desde_ruta(ruta)

if df is None or df.empty:
    st.error("No se pudo cargar el dataset.")
    st.stop()

# ==============================
# FILTROS
# ==============================
st.sidebar.header("Filtros de análisis")

gestor_filtros = GestorFiltros(df)
filtros = gestor_filtros.mostrar_filtros()

df_filtrado, agrupado = gestor_filtros.aplicar_filtros(**filtros)

# ==============================
# RESULTADOS Y VISUALIZACIÓN
# ==============================
st.subheader("📊 Vehículos agrupados por número de repostajes")
st.dataframe(agrupado, use_container_width=True)

if agrupado.empty:
    st.warning("No hay resultados con los filtros actuales.")
    st.stop()

matriculas = agrupado["vehiculo"].astype(str).tolist()
matricula_seleccionada = st.selectbox("Selecciona matrícula para detalle", matriculas)
detalle = df_filtrado[df_filtrado["vehiculo"].astype(str) == matricula_seleccionada].sort_values("fecha")

gestor_graficos = GestorGraficos(detalle)

st.plotly_chart(gestor_graficos.grafico_tiempo(), use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.plotly_chart(gestor_graficos.grafico_histograma("repostado", "Repostado"), use_container_width=True)
col2.plotly_chart(gestor_graficos.grafico_histograma("distancia", "Distancia"), use_container_width=True)
col3.plotly_chart(gestor_graficos.grafico_histograma("consumo", "Consumo"), use_container_width=True)

st.plotly_chart(gestor_graficos.grafico_dispersion("distancia", "repostado"), use_container_width=True)

# ==============================
# DESCARGA DE DATOS
# ==============================
boton_descarga_csv(df_filtrado, nombre_archivo="repostajes_filtrados.csv", etiqueta="⬇️ Descargar CSV filtrado")


