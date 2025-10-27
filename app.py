import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

# ====== Config general ======
st.set_page_config(page_title="Explorador de Repostajes", layout="wide")

# ====== Carga de datos ======
st.title("Explorador de Repostajes")

st.sidebar.header("Datos de entrada")
modo = st.sidebar.radio("Fuente de datos", ["Subir archivo", "Ruta local"])

df = None
if modo == "Subir archivo":
    up = st.sidebar.file_uploader("Sube un Excel (.xlsx)", type=["xlsx"])
    if up:
        df = pd.read_excel(up)
else:
    ruta = st.sidebar.text_input("Ruta local a Excel", "datos/Ejemplo_Repostajes.xlsx")
    if ruta:
        try:
            df = pd.read_excel(ruta)
        except Exception as e:
            st.sidebar.error(f"No se pudo leer: {e}")

if df is None:
    st.info("🗂️ Carga un archivo para empezar.")
    st.stop()

# Normaliza tipos mínimos
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
for c in ["repostado", "distancia", "consumo", "precio_litro"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ====== Filtros (sidebar) ======
st.sidebar.header("Filtros")
comb_opts = sorted([x for x in df.get("tipo_combustible", pd.Series()).dropna().unique()])
vehic_opts = sorted([x for x in df.get("tipo_vehiculo", pd.Series()).dropna().unique()])

sel_comb = st.sidebar.multiselect("Tipo de combustible", comb_opts)
sel_vehic = st.sidebar.multiselect("Tipo de vehículo", vehic_opts)
lugar_txt = st.sidebar.text_input("Lugar (busca en 'direccion')", "")

parametro = st.sidebar.selectbox("Parámetro a analizar", ["repostado", "distancia", "consumo"])
# Rango dinámico del parámetro
pmin, pmax = float(df[parametro].min(skipna=True)), float(df[parametro].max(skipna=True))
rango_val = st.sidebar.slider("Rango de valores", pmin, pmax, (pmin, pmax))

# Rango de fechas
fmin = df["fecha"].min()
fmax = df["fecha"].max()
fechas = st.sidebar.date_input("Rango de fechas", (fmin.date() if pd.notna(fmin) else date.today(),
                                                   fmax.date() if pd.notna(fmax) else date.today()))

aplicar = st.sidebar.button("Aplicar filtro")

# ====== Función de filtrado ======
def filtrar_datos(
    df,
    tipos_combustible=None,
    tipos_vehiculo=None,
    lugar=None,
    parametro=None,
    rango=None,
    fecha_inicio=None,
    fecha_fin=None
):
    out = df.copy()

    if tipos_combustible:
        out = out[out["tipo_combustible"].isin(tipos_combustible)]
    if tipos_vehiculo:
        out = out[out["tipo_vehiculo"].isin(tipos_vehiculo)]
    if lugar:
        out = out[out["direccion"].astype(str).str.contains(lugar, case=False, na=False)]

    if fecha_inicio:
        out = out[out["fecha"] >= pd.to_datetime(fecha_inicio)]
    if fecha_fin:
        out = out[out["fecha"] <= pd.to_datetime(fecha_fin)]

    if parametro and rango:
        lo, hi = rango
        out = out[(out[parametro] >= lo) & (out[parametro] <= hi)]

    # Agrupación por matrícula (vehiculo) para el listado principal
    agrupado = (
        out.groupby("vehiculo", dropna=False)
           .agg({
               "tipo_vehiculo": "first",
               "tipo_combustible": "first",
               "repostado": "count"
           })
           .rename(columns={"repostado": "n_repostajes"})
           .reset_index()
           .sort_values("n_repostajes", ascending=False)
    )
    return out, agrupado

# ====== Ejecutar filtrado ======
if aplicar:
    fecha_ini, fecha_fin = None, None
    if isinstance(fechas, tuple) and len(fechas) == 2:
        fecha_ini, fecha_fin = fechas[0], fechas[1]

    df_filtrado, agrupado = filtrar_datos(
        df,
        tipos_combustible=sel_comb,
        tipos_vehiculo=sel_vehic,
        lugar=lugar_txt.strip() or None,
        parametro=parametro,
        rango=rango_val,
        fecha_inicio=fecha_ini,
        fecha_fin=fecha_fin
    )

    st.subheader("Listado de vehículos (agrupado)")
    st.dataframe(agrupado, use_container_width=True)

    # Selector de matrícula
    matriculas = agrupado["vehiculo"].astype(str).tolist()
    if len(matriculas) == 0:
        st.warning("No hay resultados con los filtros actuales.")
        st.stop()

    sel_mat = st.selectbox("Selecciona matrícula para detalle", matriculas)
    detalle = df_filtrado[df_filtrado["vehiculo"].astype(str) == sel_mat].sort_values("fecha")

    st.markdown(f"### Evolución temporal · {sel_mat}")
    # Línea temporal
    fig1, ax1 = plt.subplots(figsize=(8, 3))
    ax1.plot(detalle["fecha"], detalle["repostado"])
    ax1.set_xlabel("Fecha")
    ax1.set_ylabel("Litros repostados")
    ax1.set_title("Repostado a lo largo del tiempo")
    st.pyplot(fig1)

    # Histogramas
    st.markdown("### Histogramas (repostado / distancia / consumo)")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig_h1, axh1 = plt.subplots(figsize=(4,3))
        axh1.hist(detalle["repostado"].dropna(), bins=20, color="#1f77b4")
        axh1.set_title("Repostado")
        st.pyplot(fig_h1)

    with col2:
        if "distancia" in detalle:
            fig_h2, axh2 = plt.subplots(figsize=(4,3))
            axh2.hist(detalle["distancia"].dropna(), bins=20, color="#1f77b4")
            axh2.set_title("Distancia")
            st.pyplot(fig_h2)

    with col3:
        if "consumo" in detalle:
            fig_h3, axh3 = plt.subplots(figsize=(4,3))
            axh3.hist(detalle["consumo"].dropna(), bins=20, color="#1f77b4")
            axh3.set_title("Consumo")
            st.pyplot(fig_h3)

    # Dispersión distancia vs repostado
    st.markdown("### Dispersión Distancia vs Repostado")
    if "distancia" in detalle:
        fig_s, axs = plt.subplots(figsize=(6,4))
        axs.scatter(detalle["distancia"], detalle["repostado"], color="#1f77b4", alpha=0.75, s=22)
        axs.set_xlabel("Distancia (km)")
        axs.set_ylabel("Litros repostados")
        st.pyplot(fig_s)

else:
    st.info("Ajusta filtros en la barra lateral y pulsa **Aplicar filtro**.")
