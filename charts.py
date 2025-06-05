import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

def active_users_chart(df, view):
    fig = go.Figure()
    # Active Users
    fig.add_scatter(x=df["date"], y=df["count"], mode='lines+markers', name='Total Users', fill='tozeroy',
                    line=dict(color="#8677D8"),marker=dict(size=4, symbol='circle'))
    # New Users
    fig.add_scatter(x=df["date"], y=df["new_users"],mode='lines+markers', name='New Users', fill='tozeroy',
                    line=dict(color="#6BC26B"), marker=dict(size=4, symbol='circle'))

    # Estética general
    fig.update_layout(title=f"{view} New and Total Active Users", yaxis_title="Users", xaxis_title="date",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def new_users_percentage_chart(df, view):
    # Calculate percentage of new users
    df = df.copy()
    df['new_users_percentage'] = round((df['new_users'] / df['count'] * 100).fillna(0), 2)
    fig = go.Figure()
    fig.add_scatter(x=df["date"], y=df["new_users_percentage"],mode='lines+markers', name='Percentage', fill='tozeroy',
                    line=dict(color="#6BC26B"), marker=dict(size=4, symbol='circle'))
    # Estética general
    fig.update_layout(title=f'Percentage of New Users relative to Total {view} Active Users', yaxis_title="Percentage", xaxis_title="date",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def total_interactions_chart(df, view):
    fig = go.Figure()
    # Interactions
    fig.add_scatter(x=df["date"], y=df["interactions"], mode='lines+markers', name='Interactions', fill='tozeroy',
                    line=dict(color="#8677D8"),marker=dict(size=4, symbol='circle'))

    # Audio (relleno sobre interactions)
    fig.add_scatter(x=df["date"], y=df["audio"],mode='lines+markers', name='Audio', fill='tozeroy',
                    line=dict(color="#6BC26B"), marker=dict(size=4, symbol='circle'))

    # Text (relleno sobre audio)
    fig.add_scatter(x=df["date"], y=df["text"], mode='lines+markers',name='Text',fill='tozeroy',
                    line=dict(color="#B87B7B"),marker=dict(size=4, symbol='circle'))

    # Estética general
    fig.update_layout(title=f"Total {view} Interactions", yaxis_title="Interactions", xaxis_title="date",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def interactions_percentage_chart(df, view):
    # Calculate percentage of new users
    df = df.copy()
    df['audio_percentage'] = round((df['audio'] / df['interactions'] * 100).fillna(0), 2)
    df['text_percentage'] = round((df['text'] / df['interactions'] * 100).fillna(0), 2)

    fig = go.Figure()
    # Interactions
    fig.add_scatter(x=df["date"], y=df["audio_percentage"], mode='lines+markers', name='Audio', fill='tozeroy',
                    line=dict(color="#6BC26B"),marker=dict(size=4, symbol='circle'))

    # Text (relleno sobre audio)
    fig.add_scatter(x=df["date"], y=df["text_percentage"], mode='lines+markers',name='Text',fill='tozeroy',
                    line=dict(color="#B87B7B"),marker=dict(size=4, symbol='circle'))
    
    # Estética general
    fig.update_layout(title=f'Percentage of Audio and Text relative to Total {view} Interactions', yaxis_title="Percentage", xaxis_title="date",
                        yaxis_tickformat=',', title_x=0.5)
    return fig


def users_by_country (data, countries, view):
    filtered = data[data["country"].isin(countries)]
    fig = px.area(filtered, x="date", y="count", color="country", title=f"{view} Active Users")
    fig.update_traces(mode='lines+markers', marker=dict(size=4, symbol='circle'))
    fig.update_layout(yaxis_title="Users", xaxis_title="date", yaxis_tickformat=',', title_x=0.5)
    return fig

def new_users_by_country (data, countries, view):
    filtered = data[data["country"].isin(countries)]
    fig = px.area(filtered, x="date", y="new_users", color="country", title=f"{view} Active Users")
    fig.update_traces(mode='lines+markers', marker=dict(size=4, symbol='circle'))
    fig.update_layout(yaxis_title="Users", xaxis_title="date", yaxis_tickformat=',', title_x=0.5)
    return fig

def dau_mau_ratio_chart(data, countries, title="DAU/MAU Ratio"):
    """
    Crea gráfico de línea para el ratio DAU/MAU por país
    
    Args:
        data: DataFrame con columnas year_month, country, dau_mau_ratio
        countries: Lista de países seleccionados
        title: Título del gráfico
    """
    
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos disponibles para el período seleccionado", xref="paper", yref="paper",
                            x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Filtrar por países seleccionados
    if countries:
        data_filtered = data[data['country'].isin(countries)]
    else:
        data_filtered = data
    
    if data_filtered.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos para los países seleccionados", xref="paper", yref="paper",
                            x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Crear gráfico de líneas
    fig = px.line(data_filtered, x='year_month', y='dau_mau_ratio', color='country', title=title,
                labels={'year_month': 'Mes', 'dau_mau_ratio': 'Ratio DAU/MAU', 'country': 'País'}, markers=True)
    
    # Configurar layout
    fig.update_layout(xaxis_title="Mes", yaxis_title="Ratio DAU/MAU", hovermode='x unified', 
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    
    # Formato del hover
    fig.update_traces(
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Mes: %{x}<br>' +
                      'Ratio DAU/MAU: %{y:.3f}<br>' +
                      '<extra></extra>'
    )    
    return fig
