import plotly.express as px

class GestorGraficos:
    """Genera gráficos interactivos con Plotly"""

    def __init__(self, df):
        self.df = df

    def grafico_tiempo(self):
        fig = px.line(
            self.df, x="fecha", y="repostado",
            title="Evolución temporal del repostado",
            labels={"fecha": "Fecha", "repostado": "Litros repostados"},
            markers=True
        )
        return fig

    def grafico_histograma(self, columna, titulo):
        if columna not in self.df.columns:
            return None
        fig = px.histogram(
            self.df, x=columna, nbins=20, title=titulo,
            color_discrete_sequence=["#1f77b4"]
        )
        return fig

    def grafico_dispersion(self, x_col, y_col):
        if x_col not in self.df.columns or y_col not in self.df.columns:
            return None
        fig = px.scatter(
            self.df, x=x_col, y=y_col,
            title=f"Dispersión: {x_col.capitalize()} vs {y_col.capitalize()}",
            labels={x_col: x_col.capitalize(), y_col: y_col.capitalize()},
            color_discrete_sequence=["#1f77b4"]
        )
        return fig


