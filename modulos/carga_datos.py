import pandas as pd
import streamlit as st

class CargadorDatos:
    """Gestiona la carga y limpieza inicial de los datos"""

    @staticmethod
    def cargar_desde_subida(archivo):
        try:
            df = pd.read_excel(archivo)
            return CargadorDatos.limpiar(df)
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return None

    @staticmethod
    def cargar_desde_ruta(ruta):
        try:
            df = pd.read_excel(ruta)
            return CargadorDatos.limpiar(df)
        except FileNotFoundError:
            st.warning("No se encontró el archivo en la ruta especificada.")
            return None
        except Exception as e:
            st.error(f"Error al cargar desde la ruta: {e}")
            return None

    @staticmethod
    def limpiar(df):
        df.columns = df.columns.str.lower().str.strip()
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

        for c in ["repostado", "distancia", "consumo", "precio_litro"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        return df


