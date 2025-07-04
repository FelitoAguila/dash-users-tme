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

def active_subscribed_users_chart(df, view):
    fig = go.Figure()
    # Active Users
    fig.add_scatter(x=df["date"], y=df["count"], mode='lines+markers', name='Total Users', fill='tozeroy',
                    line=dict(color="#8677D8"),marker=dict(size=4, symbol='circle'))
    # New Users
    fig.add_scatter(x=df["date"], y=df["subscribed"],mode='lines+markers', name='Subscribed Users', fill='tozeroy',
                    line=dict(color="#6BC26B"), marker=dict(size=4, symbol='circle'))

    # Estética general
    fig.update_layout(title=f"{view} Total and Subscribed Active Users", yaxis_title="Users", xaxis_title="date",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def subscribed_users_percent_chart(df, view):
    # Calculate percentage of new users
    df = df.copy()
    df['subscribed_percentage'] = round((df['subscribed'] / df['count'] * 100).fillna(0), 2)
    fig = go.Figure()
    fig.add_scatter(x=df["date"], y=df["subscribed_percentage"],mode='lines+markers', name='Percentage', fill='tozeroy',
                    line=dict(color="#6BC26B"), marker=dict(size=4, symbol='circle'))
    # Estética general
    fig.update_layout(title=f'Percentage of Subscribed Users relative to Total {view} Active Users', yaxis_title="Percentage", xaxis_title="date",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def users_by_country(data, countries, view):
    # Filtrar datos por países seleccionados
    filtered = data[data["country"].isin(countries)]
    
    # Manejar caso de datos vacíos
    if filtered.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected countries",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Crear gráfico de área superpuesta
    fig = go.Figure()
    for country in countries:
        country_data = filtered[filtered['country'] == country]
        fig.add_trace(
            go.Scatter(x=country_data['date'],y=country_data['count'],name=country,mode='lines+markers',
                        line_shape='spline',  # Líneas suaves
                        marker=dict(size=4, symbol='circle'),
                        fill='tozeroy',  # Área desde y=0
                        opacity=0.5  # Transparencia para ver áreas superpuestas
            )
        )
    
    # Configurar layout
    fig.update_layout(yaxis_title="Users", xaxis_title="Date", yaxis_tickformat=',', title=f"{view} Active Users",
                        title_x=0.5, hovermode='x unified', showlegend=True)    
    return fig

def country_share(data, countries, view, selector, total_selector):
    # Crear una copia de los datos para no modificar el original
    df = data.copy()
    
    # Crear categoría 'Others' para países no seleccionados
    df['country'] = df['country'].apply(lambda x: x if x in countries else 'Others')
    
    # Agrupar por fecha y país, sumando los conteos
    grouped = df.groupby(['date', 'country'])[['count', 'subscribed']].sum().reset_index()
    grouped['free_users'] = grouped['count'] - grouped['subscribed']

    # Calcular porcentajes por día
    grouped['count_pct'] = grouped['count'] / grouped.groupby('date')['count'].transform('sum') * 100
    if total_selector == "Relative to selected category total":
        grouped['subscribed_pct'] = grouped['subscribed'] / grouped.groupby('date')['subscribed'].transform('sum') * 100
        grouped['free_users_pct'] = grouped['free_users'] / grouped.groupby('date')['free_users'].transform('sum') * 100
    elif total_selector == "Relative to total":
        grouped['subscribed_pct'] = grouped['subscribed'] / grouped.groupby('date')['count'].transform('sum') * 100
        grouped['free_users_pct'] = grouped['free_users'] / grouped.groupby('date')['count'].transform('sum') * 100
    
    # Manejar caso de datos vacíos
    if grouped.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected countries",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig

    if selector == 'Total Active Users':
        grouped['y'] = grouped['count_pct']
    elif selector == 'Subscribed Users':
        grouped['y'] = grouped['subscribed_pct']
    elif selector == 'Free Users':
        grouped['y'] = grouped['free_users_pct']
    else:
        raise ValueError("Selector inválido")
    grouped['y'] = grouped['y'].round(2)  #para redondear porcentajes
    
    # Crear figura
    fig = go.Figure()

    # Agregar una traza por país
    for country in grouped['country'].unique():
        country_data = grouped[grouped['country'] == country]
        fig.add_trace(go.Bar(x=country_data['date'], y=country_data['y'], name=country))

    # Configurar layout
    fig.update_layout(
        barmode='stack',
        yaxis_title="Country Share (%)",
        xaxis_title="Date",
        title=f"{view} Country Share",
        title_x=0.5,
        hovermode='x unified',
        yaxis=dict(tickvals=[0, 25, 50, 75, 100], ticktext=['0%', '25%', '50%', '75%', '100%']),
        height=500,
        legend_title="Country"
    )

    return fig

def interactions_by_country_chart(data, countries, view, selector):
    # Filtrar datos por países seleccionados
    filtered = data[data["country"].isin(countries)]
    
    # Manejar caso de datos vacíos
    if filtered.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected countries",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Crear gráfico de área superpuesta
    fig = go.Figure()
    for country in countries:
        country_data = filtered[filtered['country'] == country]
        if selector == 'Total Interactions':
            y_data = country_data['interactions']
        elif selector == 'Audio':
            y_data = country_data['audio']
        elif selector == 'Text':
            y_data = country_data['text']

        fig.add_trace(
            go.Scatter(x=country_data['date'],y=y_data,name=country,mode='lines+markers',
                        line_shape='spline',  # Líneas suaves
                        marker=dict(size=4, symbol='circle'),
                        fill='tozeroy',  # Área desde y=0
                        opacity=0.5  # Transparencia para ver áreas superpuestas
            )
        )
    
    # Configurar layout
    fig.update_layout(yaxis_title="Users", xaxis_title="Date", yaxis_tickformat=',', title=f"{view} Active Users",
                        title_x=0.5, hovermode='x unified', showlegend=True)    
    return fig

def new_users_by_country(data, countries, view):
    # Filtrar datos por países seleccionados
    filtered = data[data["country"].isin(countries)]
    
    # Manejar caso de datos vacíos
    if filtered.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected countries",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Crear gráfico de área superpuesta
    fig = go.Figure()
    for country in countries:
        country_data = filtered[filtered['country'] == country]
        fig.add_trace(
            go.Scatter(x=country_data['date'],y=country_data['new_users'],name=country,mode='lines+markers',
                        line_shape='spline',  # Líneas suaves
                        marker=dict(size=4, symbol='circle'),
                        fill='tozeroy',  # Área desde y=0
                        opacity=0.5  # Transparencia para ver áreas superpuestas
            )
        )
    
    # Configurar layout
    fig.update_layout(yaxis_title="Users", xaxis_title="Date", yaxis_tickformat=',', title=f"{view} New Users",
                        title_x=0.5, hovermode='x unified', showlegend=True)    
    return fig

def subs_by_country_chart(data, countries, view):
    # Filtrar datos por países seleccionados
    filtered = data[data["country"].isin(countries)]
    
    # Manejar caso de datos vacíos
    if filtered.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected countries",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Crear gráfico de área superpuesta
    fig = go.Figure()
    for country in countries:
        country_data = filtered[filtered['country'] == country]
        fig.add_trace(
            go.Scatter(x=country_data['date'],y=country_data['subscribed'],name=country,mode='lines+markers',
                        line_shape='spline',  # Líneas suaves
                        marker=dict(size=4, symbol='circle'),
                        fill='tozeroy',  # Área desde y=0
                        opacity=0.5  # Transparencia para ver áreas superpuestas
            )
        )
    
    # Configurar layout
    fig.update_layout(yaxis_title="Users", xaxis_title="Date", yaxis_tickformat=',', title=f"{view} Subscribed Active Users",
                        title_x=0.5, hovermode='x unified', showlegend=True)    
    return fig

def free_users_by_country(data, countries, view):
    # Filtrar datos por países seleccionados
    filtered = data[data["country"].isin(countries)]
    
    # Manejar caso de datos vacíos
    if filtered.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected countries",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Crear gráfico de área superpuesta
    fig = go.Figure()
    for country in countries:
        country_data = filtered[filtered['country'] == country]
        country_data['free'] = country_data['count'] - country_data['subscribed']
        fig.add_trace(
            go.Scatter(x=country_data['date'],y=country_data['free'],name=country,mode='lines+markers',
                        line_shape='spline',  # Líneas suaves
                        marker=dict(size=4, symbol='circle'),
                        fill='tozeroy',  # Área desde y=0
                        opacity=0.5  # Transparencia para ver áreas superpuestas
            )
        )
    
    # Configurar layout
    fig.update_layout(yaxis_title="Users", xaxis_title="Date", yaxis_tickformat=',', title=f"{view} Free Active Users",
                        title_x=0.5, hovermode='x unified', showlegend=True)    
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
    fig.update_layout(xaxis_title="Mes", yaxis_title="Ratio DAU/MAU", yaxis_tickformat=',', title_x=0.5) 
    return fig

def heat_map_users_by_country(total_users_by_country, title = 'Includes All Historic Free Users'):
    fig = go.Figure(data=go.Choropleth(
        locations=total_users_by_country['country'],
        locationmode='country names',
        z=total_users_by_country['Users'],
        text=total_users_by_country['country'],
        colorscale=[
            [0.0, 'rgb(220, 255, 220)'],
            [0.02, 'rgb(180, 240, 180)'],
            [0.1, 'rgb(140, 220, 140)'],
            [0.3, 'rgb(100, 200, 100)'],
            [0.6, 'rgb(60, 160, 60)'],
            [1.0, 'rgb(0, 100, 0)']
        ],
        autocolorscale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        #colorbar_title='Users',
        hovertemplate='%{text}: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title_text=title,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        margin={"r":0, "t":50, "l":0, "b":0},
        title_x=0.5
    )
    
    return fig

def tree_map_users_by_country(df_treemap, title = 'Includes All Historic Free Users'):
    fig_treemap = px.treemap(
        df_treemap,
        path=['country'],
        values='Users',
        color='Share',
        color_continuous_scale=[
            [0.0, 'rgb(200, 245, 200)'],
            [0.05, 'rgb(160, 230, 160)'],
            [0.1, 'rgb(120, 210, 120)'],
            [0.3, 'rgb(80, 180, 80)'],
            [1.0, 'rgb(0, 120, 0)']
        ],
        title=title,
        hover_data={'Users': ':,.0f', 'Share': ':.2f%'}
    )
    fig_treemap.update_traces(
        texttemplate='%{label}<br>%{value:,} users<br>%{percentRoot:.2%}',
        textposition='middle center',
        #textfont=dict(size=14, color='black'),
        marker=dict(line=dict(color='black', width=1)),
        hovertemplate='Country: %{label}<br>Users: %{value:,.0f}<br>Share: %{customdata[1]:.2f}%'
    )
    fig_treemap.update_layout(
        margin={"r":0, "t":50, "l":0, "b":0},
        title_x=0.5,
        coloraxis_colorbar_title='Share (%)'
    )
    
    return fig_treemap

def plot_histogram_users_by_cycles(df):
    total_df = (
        df.groupby("cycles_consumed", as_index=False)["Users"]
        .sum()
        .assign(country="Total")
    )

    fig = px.bar(
        total_df,
        x="cycles_consumed",
        y="Users",
        labels={
            "cycles_consumed": "Cycles Consumed",
            "Users": "Number of Users",
        },
        title="Users by Cycles Consumed"
    )
    
    fig.update_layout(
        xaxis_title="Cycles Consumed",
        yaxis_title="Number of Users",
        title_x=0.5
    )
    
    return fig

def plot_user_histogram_faceted(df):
    fig = px.histogram(
        df,
        x='cycles_consumed',
        y='Users',
        color='last_date',
        facet_col='country',
        barmode='stack',
        nbins=21,
        title='Users by Consumed Cycles (per country and year)'
    )

    # Limpiar etiquetas "country=Argentina" → solo "Argentina"
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    # Eliminar títulos de ejes X individuales
    fig.for_each_xaxis(lambda x: x.update(title=''))

    # Mostrar el eje X solo una vez
    fig.update_xaxes(matches=None, showticklabels=True)
    fig.update_traces(marker_line_width=1, marker_line_color='white')

    fig.update_layout(
        xaxis_title='Cycles Consumed',
        yaxis_title='Free Users',
        legend_title='Year'
    )

    return fig

def errors_by_date_chart(data, errors, view):
    # Crear gráfico de área superpuesta
    fig = go.Figure()
    for error in errors:
        fig.add_trace(
            go.Scatter(x=data['localdate'],y=data[error],name=error,mode='lines+markers',
                        line_shape='spline',  # Líneas suaves
                        marker=dict(size=4, symbol='circle'),
                        fill='tozeroy',  # Área desde y=0
                        opacity=0.5  # Transparencia para ver áreas superpuestas
            )
        )
    
    # Configurar layout
    fig.update_layout(yaxis_title="Errors", xaxis_title="Date", yaxis_tickformat=',', title=f"{view} Errors from 2024-01-01 to date",
                        title_x=0.5, hovermode='x unified', showlegend=True)    
    return fig

def invalid_format_types_chart(df):
    # Calcular porcentajes
    total = df['count'].sum()
    df['percentage'] = df['count'] / total * 100

    # Separar categorías con < 5% y agruparlas en "Others"
    threshold = 5
    others_df = df[df['percentage'] < threshold]
    main_df = df[df['percentage'] >= threshold]

    # Crear el grupo "Others"
    others_count = others_df['count'].sum()
    others_types = ', '.join(others_df['type'].tolist())  # Lista de categorías en "Others"
    others_row = pd.DataFrame({
        'type': ['Others'],
        'count': [others_count],
        'percentage': [others_count / total * 100],
        'details': [f"Others ({others_types})"]  # Detalle para hover y leyenda
    })

    # Combinar DataFrames
    df_final = pd.concat([main_df, others_row], ignore_index=True)

    # Crear gráfico de donut
    fig = px.pie(df_final, values='count', names='type', 
                 title='Includes all INVALID_FORMAT Errors from 2024-01-01 to date',
                 hole=0.4,  # Tamaño del agujero
                 color_discrete_sequence=px.colors.qualitative.Pastel)  # Paleta de colores suaves

    # Personalizar las etiquetas y el hover
    fig.update_traces(
        textinfo='percent+label',  # Mostrar porcentaje y etiqueta en el gráfico
        textfont_size=12,
        marker=dict(line=dict(color='white', width=2)),  # Bordes blancos
        customdata=df_final['details'] if 'details' in df_final else None,  # Datos para hover
        hovertemplate='%{label}<br>%{percent:.1%}<br>Count: %{value}<br>%{customdata}<extra></extra>'
    )

    # Personalizar el diseño
    fig.update_layout(
        showlegend=True,  # Mostrar leyenda
        template='plotly_white',  # Tema claro
        title_x=0.5,  # Centrar título
        font=dict(size=12),
        legend=dict(
            title='Types',
            itemsizing='constant'
        )
    )

    # Actualizar la leyenda para que "Others" muestre los detalles
    for trace in fig.data:
        if trace.name == 'Others':
            trace.name = others_row['details'].iloc[0]  # Mostrar detalles en la leyenda

    return fig
