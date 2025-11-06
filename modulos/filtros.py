import streamlit as st
import pandas as pd

class GestorFiltros:
    """Maneja los filtros dinámicos y agrupaciones"""

    def __init__(self, df):
        self.df = df

    def mostrar_filtros(self):
        df = self.df

        tipos_comb = sorted(df.get("tipo_combustible", pd.Series()).dropna().unique())
        tipos_veh = sorted(df.get("tipo_vehiculo", pd.Series()).dropna().unique())

        seleccion_comb = st.sidebar.multiselect("Tipo de combustible", tipos_comb)
        seleccion_veh = st.sidebar.multiselect("Tipo de vehículo", tipos_veh)
        texto_lugar = st.sidebar.text_input("Lugar (buscar en columna 'direccion')", "")

        parametro = st.sidebar.selectbox("Parámetro de análisis", ["repostado", "distancia", "consumo"])

        # Rango dinámico
        pmin, pmax = float(df[parametro].min(skipna=True)), float(df[parametro].max(skipna=True))
        rango = st.sidebar.slider("Rango de valores", pmin, pmax, (pmin, pmax))

        fmin, fmax = df["fecha"].min(), df["fecha"].max()
        fechas = st.sidebar.date_input("Rango de fechas", (fmin.date(), fmax.date()))

        return {
            "tipos_combustible": seleccion_comb,
            "tipos_vehiculo": seleccion_veh,
            "lugar": texto_lugar.strip() or None,
            "parametro": parametro,
            "rango": rango,
            "fecha_inicio": fechas[0],
            "fecha_fin": fechas[1]
        }

    def aplicar_filtros(self, tipos_combustible=None, tipos_vehiculo=None, lugar=None,
                        parametro=None, rango=None, fecha_inicio=None, fecha_fin=None):
        df = self.df.copy()

        if tipos_combustible:
            df = df[df["tipo_combustible"].isin(tipos_combustible)]
        if tipos_vehiculo:
            df = df[df["tipo_vehiculo"].isin(tipos_vehiculo)]
        if lugar:
            df = df[df["direccion"].astype(str).str.contains(lugar, case=False, na=False)]

        if fecha_inicio:
            df = df[df["fecha"] >= pd.to_datetime(fecha_inicio)]
        if fecha_fin:
            df = df[df["fecha"] <= pd.to_datetime(fecha_fin)]

        if parametro and rango:
            lo, hi = rango
            if parametro in df.columns:
                df = df[(df[parametro] >= lo) & (df[parametro] <= hi)]

        # Agrupación
        agg_dict = {}
        if "tipo_vehiculo" in df.columns:
            agg_dict["tipo_vehiculo"] = "first"
        if "tipo_combustible" in df.columns:
            agg_dict["tipo_combustible"] = "first"
        if "repostado" in df.columns:
            agg_dict["repostado"] = "count"

        agrupado = (
            df.groupby("vehiculo", dropna=False)
              .agg(agg_dict)
              .rename(columns={"repostado": "n_repostajes"})
              .reset_index()
              .sort_values("n_repostajes", ascending=False)
        )

        return df, agrupado


