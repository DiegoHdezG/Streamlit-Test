import streamlit as st

def boton_descarga_csv(df, nombre_archivo="datos.csv", etiqueta="⬇️ Descargar CSV"):
    """Botón para descargar el dataframe como CSV"""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=etiqueta,
        data=csv,
        file_name=nombre_archivo,
        mime="text/csv"
    )


