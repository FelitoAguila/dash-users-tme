import pymongo
from dash import Input, Output, html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from get_data import get_daily_data, get_monthly_data, calculate_total_metrics, get_dau_mau_ratio_data
from dotenv import load_dotenv
import os
from charts import (active_users_chart, total_interactions_chart, 
                    users_by_country, new_users_by_country, 
                    new_users_percentage_chart, interactions_percentage_chart,
                    dau_mau_ratio_chart)

# MongoDB connection
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db_TME = client['TranscribeMe']
collection_freePlanCycles = db_TME['freePlanCycles']
db_TME_charts = client['TranscribeMe-charts']
collection_dau_by_country = db_TME_charts['dau-by-country']
collection_mau_by_country = db_TME_charts['mau-by-country']

# Cache para gráficos (datos que cambian según filtros)
_charts_cache = {}

# Calcular métricas una sola vez al importar el módulo
TOTAL_METRICS = calculate_total_metrics(collection_dau_by_country, collection_mau_by_country)

def get_chart_data(view, start_date, end_date):
    """Obtiene datos para gráficos con cache"""
    cache_key = f"{view}_{start_date}_{end_date}"
    
    if cache_key not in _charts_cache:
        #print(f"Obteniendo datos para gráficos: {view} desde {start_date} hasta {end_date}")
        if view == 'Daily':
            _charts_cache[cache_key] = get_daily_data(collection_dau_by_country, start_date, end_date)
        elif view == 'Monthly':
            _charts_cache[cache_key] = get_monthly_data(collection_mau_by_country, start_date, end_date)
    
    return _charts_cache[cache_key]

# Cache para datos de ratio
_ratio_cache = {}

def get_ratio_data(start_date, end_date, countries=None):
    """Obtiene datos de ratio DAU/MAU con cache"""
    cache_key = f"ratio_{start_date}_{end_date}_{str(sorted(countries) if countries else [])}"
    
    if cache_key not in _ratio_cache:
        print(f"Obteniendo datos de ratio DAU/MAU para {countries}")
        _ratio_cache[cache_key] = get_dau_mau_ratio_data(
            collection_dau_by_country, 
            collection_mau_by_country, 
            start_date, 
            end_date, 
            countries
        )
    
    return _ratio_cache[cache_key]

def register_callbacks(app):
    
    # Callback SOLO para métricas - valores fijos que NO cambian
    @app.callback(
        [
            Output('total_new_users', 'children'),
            Output('average_dau', 'children'),
            Output('average_mau', 'children'),
            Output('total_interactions', 'children'),
            Output('total_audio', 'children'),
            Output('total_text', 'children'),
        ],
        [Input('start_date_picker', 'date')]  # Solo necesitamos un trigger, pero los valores no dependen de esto
    )
    def update_total_metrics(start_date):
        """Retorna métricas totales fijas - NO cambian con los filtros"""
        return (
            TOTAL_METRICS['total_new_users'],
            TOTAL_METRICS['average_dau'], 
            TOTAL_METRICS['average_mau'],
            TOTAL_METRICS['total_interactions'], 
            TOTAL_METRICS['total_audio'], 
            TOTAL_METRICS['total_text']
        )
    
    # Callback para el contenido de las pestañas
    @app.callback(
        Output('tab-content', 'children'),
        [Input('main-tabs', 'value'), Input('view_selector', 'value'),
         Input('start_date_picker', 'date'), Input('end_date_picker', 'date')]
    )
    def render_tab_content(active_tab, view, start_date, end_date):
        """Renderiza el contenido según la pestaña seleccionada"""
        
        if active_tab == 'general':
            return html.Div([
                # Gráficos - Vista General
                html.Div([
                    html.Div([html.H3(f"{view} Active Users", style={'textAlign': 'center'}), dcc.Graph(id='total_active_users_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} New Users Percentage", style={'textAlign': 'center'}), dcc.Graph(id='new_users_percentage_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} Interactions", style={'textAlign': 'center'}), dcc.Graph(id='total_interactions_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} Audio and Text Percentage", style={'textAlign': 'center'}), dcc.Graph(id='audio_text_percentage_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'})
            ])
        elif active_tab == 'países':
            # Obtener países disponibles para el período seleccionado
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            start_date_str = start.strftime('%Y-%m-%d')
            end_date_str = end.strftime('%Y-%m-%d')
            
            data = get_chart_data(view, start_date_str, end_date_str)
            countries = data["country"].unique() if len(data) > 0 else []
            
            return html.Div([
                html.Label("Selecciona país(es):"),
                dcc.Dropdown(
                    id="country_dropdown",
                    options=[{"label": c, "value": c} for c in countries],
                    value=["Argentina"] if "Argentina" in countries else [countries[0]] if len(countries) > 0 else [],
                    multi=True
                ),
                html.Div([html.H3(f"{view} Active Users", style={'textAlign': 'center'}), dcc.Graph(id='dau_by_country')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                html.Div([html.H3(f"{view} New Users", style={'textAlign': 'center'}), dcc.Graph(id='new_users_by_country')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                html.Div([html.H3("DAU/MAU Ratio por Mes", style={'textAlign': 'center'}), dcc.Graph(id='dau_mau_ratio_chart')], style={'margin': '20px 10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'})
            ])
        return html.Div([html.P("Selecciona una pestaña para ver el contenido.")])
    
    # Callback para gráficos generales - SÍ cambian con filtros
    @app.callback(
        [
            Output('total_active_users_fig', 'figure'),
            Output('new_users_percentage_fig', 'figure'),
            Output('total_interactions_fig', 'figure'),
            Output('audio_text_percentage_fig', 'figure')
        ],
        [
            Input('start_date_picker', 'date'), 
            Input('end_date_picker', 'date'),
            Input('view_selector', 'value')
        ]
    )
    def update_general_charts(start_date, end_date, view):
        """Actualiza gráficos generales según filtros seleccionados"""
        # Parsear fechas
        start = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end = datetime.strptime(end_date[:10], '%Y-%m-%d')
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')
        
        # Obtener datos para el período seleccionado
        data = get_chart_data(view, start_date_str, end_date_str)
        
        # Agregar datos para gráficos
        total_active_users = data.groupby('date')[['count', 'new_users']].sum().reset_index()
        total_interactions_by_date = data.groupby('date')[['interactions', 'audio', 'text']].sum().reset_index()
        
        # Generar gráficos
        total_active_users_fig = active_users_chart(total_active_users, view)
        total_interactions_fig = total_interactions_chart(total_interactions_by_date, view)
        new_users_percentage_fig = new_users_percentage_chart(total_active_users, view)        
        audio_text_percentage_fig = interactions_percentage_chart(total_interactions_by_date, view)
        
        return total_active_users_fig, new_users_percentage_fig, total_interactions_fig, audio_text_percentage_fig
    
    # Callback para gráficos por país - SÍ cambian con filtros
    @app.callback(
        [
            Output('dau_by_country', 'figure'),
            Output('new_users_by_country', 'figure'),
        ],
        [
            Input('start_date_picker', 'date'), 
            Input('end_date_picker', 'date'),
            Input('view_selector', 'value'),
            Input("country_dropdown", "value")
        ]
    )
    def update_charts_by_country(start_date, end_date, view, countries):
        """Actualiza gráficos por país según filtros seleccionados"""
        # Parsear fechas
        start = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end = datetime.strptime(end_date[:10], '%Y-%m-%d')
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')

        # Obtener datos para el período seleccionado
        data = get_chart_data(view, start_date_str, end_date_str)

        # Generar gráficos por país
        users_by_country_fig = users_by_country(data, countries, view)
        new_users_by_country_fig = new_users_by_country(data, countries, view)
        return users_by_country_fig, new_users_by_country_fig
    
    # Nuevo callback para el gráfico DAU/MAU ratio
    @app.callback(
        Output('dau_mau_ratio_chart', 'figure'),
        [
            Input('start_date_picker', 'date'), 
            Input('end_date_picker', 'date'),
            Input("country_dropdown", "value")
        ]
    )
    def update_dau_mau_ratio_chart(start_date, end_date, countries):
        """Actualiza gráfico de ratio DAU/MAU"""
        # Parsear fechas
        start = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end = datetime.strptime(end_date[:10], '%Y-%m-%d')
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')

        # Obtener datos de ratio
        ratio_data = get_ratio_data(start_date_str, end_date_str, countries)
    
        # Generar gráfico
        return dau_mau_ratio_chart(ratio_data, countries, "DAU/MAU Ratio por Mes")
