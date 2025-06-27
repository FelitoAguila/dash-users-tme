import pymongo
from dash import Input, Output, html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from dotenv import load_dotenv
import pytz
import os
from get_data import (get_daily_data, get_monthly_data, add_total_per_date, get_total_free_users,
                      get_heavy_free_users, aggregate_user_cycles, add_total_as_country, filter_user_cycles,
                      calculate_total_metrics, get_dau_mau_ratio_data, get_errors_by_date, get_invalid_format_types)
from charts import (active_users_chart, total_interactions_chart, heat_map_users_by_country, plot_user_histogram_faceted,
                    users_by_country, new_users_by_country, tree_map_users_by_country, interactions_by_country_chart,
                    new_users_percentage_chart, interactions_percentage_chart, subs_by_country_chart, free_users_by_country,
                    dau_mau_ratio_chart, active_subscribed_users_chart, subscribed_users_percent_chart, country_share,
                    errors_by_date_chart, invalid_format_types_chart)

# MongoDB connection
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db_TME = client['TranscribeMe']
collection_freePlanCycles = db_TME['freePlanCycles']
db_TME_charts = client['TranscribeMe-charts']
collection_dau_by_country = db_TME_charts['dau-by-country']
collection_mau_by_country = db_TME_charts['mau-by-country']
collection_free_cycles_by_country = db_TME_charts['free-cycles-by-country']
collection_errors_by_date = db_TME_charts['errors_by_date']
collection_invalid_format_types = db_TME_charts['invalid-format-types']

# Calcular métricas una sola vez al importar el módulo
TOTAL_METRICS = calculate_total_metrics(collection_dau_by_country, collection_mau_by_country)

# Cache para data de DAU
_dau_chart_cache = {}

def get_dau_chart(data, dau_selector, countries, view):
    cache_key = f'{view}_{dau_selector}_{str(sorted(countries) if countries else [])}'

    if cache_key not in _dau_chart_cache:
        print(f"Obteniendo los datos para graficar {view} {dau_selector} para los países {countries}")
        if dau_selector == 'Total Active Users':
            _dau_chart_cache[cache_key] = users_by_country(data, countries, view)
        elif dau_selector == 'Free Users':
            _dau_chart_cache[cache_key] = free_users_by_country(data, countries, view)
        elif dau_selector == 'Subscribed Users':
            _dau_chart_cache[cache_key] = subs_by_country_chart(data, countries, view)
    return _dau_chart_cache[cache_key]


# Cache para gráficos (datos que cambian según filtros)
_charts_cache = {}

def get_chart_data(view, start_date, end_date):
    """Obtiene datos para gráficos con cache"""
    cache_key = f"{view}_{start_date}_{end_date}"
    
    if cache_key not in _charts_cache:
        print(f"Obteniendo datos para gráficos: {view} desde {start_date} hasta {end_date}")
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
        dau_data = get_chart_data(view='Daily', start_date = start_date, end_date = end_date)
        mau_data = get_chart_data(view='Monthly', start_date = start_date, end_date = end_date)
        dau_and_total_data = add_total_per_date(dau_data)
        mau_and_total_data = add_total_per_date(mau_data)
        _ratio_cache[cache_key] = get_dau_mau_ratio_data(dau_and_total_data, mau_and_total_data, countries)
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
        [
            Input('main-tabs', 'value'), 
            Input('view_selector', 'value'),
            Input('start_date_picker', 'date'), 
            Input('end_date_picker', 'date')
        ]
    )
    def render_tab_content(active_tab, view, start_date, end_date):
        """Renderiza el contenido según la pestaña seleccionada"""
        
        if active_tab == 'general':
            usage_free_users = aggregate_user_cycles(collection_free_cycles_by_country)
            usage_free_users = add_total_as_country(usage_free_users)
            countries = list(usage_free_users['country'].unique())
            countries = sorted([c for c in countries if c != 'Total']) + ['Total']
            
            # Errors
            errors_by_date = get_errors_by_date(collection_errors_by_date, view)
            errors = [col for col in errors_by_date.columns if col != 'localdate']
            return html.Div([
                # Gráficos - Vista General
                html.Div([
                    html.Div([html.H3(f"{view} Active Users", style={'textAlign': 'center'}), 
                              dcc.Graph(id='total_active_users_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} New Users Percentage", style={'textAlign': 'center'}), 
                              dcc.Graph(id='new_users_percentage_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} Interactions", style={'textAlign': 'center'}), 
                              #dcc.RadioItems(id = 'interactions_selector', options = ['Total Active Users', 'Free Users', 'Subscribed_Users'], value = 'Total Active Users',inline=True, labelStyle={'margin-right': '20px'}, style={'marginTop': '10px', 'textAlign': 'center'}), 
                              dcc.Graph(id='total_interactions_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} Audio and Text Percentage", style={'textAlign': 'center'}), 
                              dcc.Graph(id='audio_text_percentage_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} Active Subscribed Users", style={'textAlign': 'center'}), 
                              dcc.Graph(id='total_active_subscribed_users_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3(f"{view} Subscribed Users Percentage", style={'textAlign': 'center'}), 
                              dcc.Graph(id='subscribed_users_percent_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    # Errors charts
                    html.Div([
                        html.H3(f"{view} Errors", style={'textAlign': 'center'}), 
                        html.Label("Select the error:"),
                        dcc.Dropdown(id="errors_dropdown", options=errors,
                                    value=['total_errors', 'INVALID_FORMAT'],
                                    multi=True),
                        dcc.Graph(id='errors_dau')], 
                    style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([
                        html.H3("Types in INVALID_FORMAT Errors", style={'textAlign': 'center'}), 
                        html.Label("Start date", style={'marginRight': '10px'}),
                        dcc.DatePickerSingle(id='start_date_invalid_format_types', 
                                             display_format='YYYY-MM-DD',
                                             initial_visible_month=datetime(2025, 1, 1),
                                             date=datetime(2025, 1, 1),  # Fecha inicial: enero-2025
                                             min_date_allowed=datetime(2024, 1, 1),
                                             style={'marginRight': '20px'}),
                        html.Label("End date", style={'marginRight': '10px'}),
                        dcc.DatePickerSingle(id='end_date_invalid_format_types', 
                                             display_format='YYYY-MM-DD',
                                             initial_visible_month=datetime(2025, 6, 1),
                                             date=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')),
                                             min_date_allowed=datetime(2024, 1, 1),
                                             style={'marginRight': '20px'}),
                        dcc.Graph(id='invalid_format_types')], 
                    style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),

                    # Free Users Charts
                    html.Div([html.H3("Free Users by Country", style={'textAlign': 'center'}), 
                              dcc.RadioItems(id = 'free_users_data', options = ['Total Free Users', 'Heavy Free Users'], value = 'Total Free Users',inline=True, labelStyle={'margin-right': '20px'}, style={'marginTop': '10px', 'textAlign': 'center'}), 
                              dcc.Graph(id='heat_map_free_users_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3("Country Share of Free Users", style={'textAlign': 'center'}), 
                              dcc.Graph(id='tree_map_free_users_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                    html.Div([html.H3("Free Users Usage", style={'textAlign': 'center'}),
                              html.Label("Select countries", style={'marginBottom': '10px'}),
                              dcc.Dropdown(id ='countries_free_usage', options = countries, value = ['Argentina','Total'], multi=True, style={'marginBottom': '20px'}),
                              html.Label("Select years range", style={'marginBottom': '10px'}),
                              dcc.RangeSlider(id = 'years', min=2023, max=2025, step =1, marks={2023: '2023', 2024:'2024', 2025:'2025'},value=[2023, 2025]), 
                              dcc.Graph(id='free_users_usage_fig')], style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),                              
                ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'})
            ])
        elif active_tab == 'países':
            # Obtener países disponibles para el período seleccionado
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            start_date_str = start.strftime('%Y-%m-%d')
            end_date_str = end.strftime('%Y-%m-%d')
            
            data = get_chart_data(view, start_date_str, end_date_str)
            data_with_total = add_total_per_date(data)
            countries = data_with_total["country"].unique() if len(data_with_total) > 0 else []
            
            return html.Div([
                # ACTIVE USERS CHART
                html.Div([
                        html.Label("Selecciona país(es):"),
                        dcc.Dropdown(id="country_dropdown_dau", options=[{"label": c, "value": c} for c in countries],
                                    value=data_with_total.groupby('country')['count'].sum().sort_values(ascending=False).head(15).index.tolist(),
                                    multi=True),
                        html.H3(f"{view} Active Users", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'dau_selector', options = ['Total Active Users', 'Free Users', 'Subscribed Users'], value = 'Total Active Users',inline=True, labelStyle={'margin-right': '20px'}, style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(id='dau_by_country')], 
                    style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                # COUNTRY SHARES CHART
                html.Div([
                        html.Label("Selecciona país(es):"),
                        dcc.Dropdown(id="country_shares_dropdown", options=[{"label": c, "value": c} for c in countries],
                                    value=data_with_total.groupby('country')['count'].sum().sort_values(ascending=False).head(15).index.tolist(),
                                    multi=True),
                        html.H3(f"Country Shares of {view} Active Users", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'dau_selector_share', options = ['Total Active Users', 'Free Users', 'Subscribed Users'], value = 'Total Active Users',inline=True, labelStyle={'margin-right': '20px'}, style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'total_category_selector', options = ["Relative to selected category total", "Relative to total"], value = "Relative to selected category total",inline=True, labelStyle={'margin-right': '20px'}, style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(id='country_share_by_country')], 
                    style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                # New users chart
                html.Div([
                        html.Label("Selecciona país(es):"),
                        dcc.Dropdown(id="country_dropdown_new_users", options=[{"label": c, "value": c} for c in countries],
                                    value=data_with_total.groupby('country')['new_users'].sum().sort_values(ascending=False).head(15).index.tolist(),
                                    multi=True),
                        html.H3(f"{view} New Users", style={'textAlign': 'center'}), 
                        dcc.Graph(id='new_users_by_country')], 
                    style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                # Interactions chart
                html.Div([
                        html.Label("Selecciona país(es):"),
                        dcc.Dropdown(id="country_dropdown_interactions", options=[{"label": c, "value": c} for c in countries],
                                    value=data_with_total.groupby('country')['interactions'].sum().sort_values(ascending=False).head(15).index.tolist(),
                                    multi=True),
                        html.H3(f"{view} Interactions", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'interaction_selector', options = ['Total Interactions', 'Audio', 'Text'], value = 'Total Interactions',inline=True, labelStyle={'margin-right': '20px'}, style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(id='interactions_by_country')], 
                    style={'flex': '1', 'minWidth': '45%', 'margin': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'}),
                # DAU/MAU ratio chart
                html.Div([
                        html.Label("Selecciona país(es):"),
                        dcc.Dropdown(id="country_dropdown_DAU/MAU_ratio", options=[{"label": c, "value": c} for c in countries],
                                    value=data_with_total.groupby('country')['count'].sum().sort_values(ascending=False).head(15).index.tolist(),
                                    multi=True),
                        html.H3("DAU/MAU Ratio por Mes", style={'textAlign': 'center'}), 
                        dcc.Graph(id='dau_mau_ratio_chart')], 
                    style={'margin': '20px 10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'padding': '10px'})
            ])
        return html.Div([html.P("Selecciona una pestaña para ver el contenido.")])
    
    # Callback para gráficos generales - SÍ cambian con filtros
    @app.callback(
        [
            Output('total_active_users_fig', 'figure'),
            Output('new_users_percentage_fig', 'figure'),
            Output('total_interactions_fig', 'figure'),
            Output('audio_text_percentage_fig', 'figure'),
            Output('total_active_subscribed_users_fig', 'figure'),
            Output('subscribed_users_percent_fig', 'figure')
        ],
        [
            Input('start_date_picker', 'date'), 
            Input('end_date_picker', 'date'),
            Input('view_selector', 'value'),
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
        total_active_subscribed_users = data.groupby('date')[['count', 'subscribed']].sum().reset_index()
        
        # Generar gráficos
        total_active_users_fig = active_users_chart(total_active_users, view)
        total_interactions_fig = total_interactions_chart(total_interactions_by_date, view)
        new_users_percentage_fig = new_users_percentage_chart(total_active_users, view)        
        audio_text_percentage_fig = interactions_percentage_chart(total_interactions_by_date, view)
        total_active_subscribed_users_fig = active_subscribed_users_chart(total_active_subscribed_users, view)
        subscribed_users_percent_fig = subscribed_users_percent_chart(total_active_subscribed_users, view)

        return (total_active_users_fig, new_users_percentage_fig, 
                total_interactions_fig, audio_text_percentage_fig, 
                total_active_subscribed_users_fig, subscribed_users_percent_fig)
    
    # Callback para los gráficos de errores
    @app.callback(
        
        [   Output('errors_dau', 'figure'),
            Output('invalid_format_types', 'figure')
        ],
        [
            Input('errors_dropdown', 'value'),
            Input('view_selector', 'value'),
            Input('start_date_invalid_format_types', 'date'),
            Input('end_date_invalid_format_types', 'date')
        ]
    )
    def update_errors_charts(errors, view, start, end):
        errors_data = get_errors_by_date(collection_errors_by_date, view)
        errors_by_date_fig = errors_by_date_chart(errors_data, errors, view)
        
        invalid_format_types = get_invalid_format_types(collection_invalid_format_types, start, end)
        invalid_format_types_fig = invalid_format_types_chart(invalid_format_types)
        return errors_by_date_fig, invalid_format_types_fig
    
    # Callback para gráficos generales de Free Users
    @app.callback(
        [
            Output('heat_map_free_users_fig', 'figure'),
            Output('tree_map_free_users_fig', 'figure'), 
            Output('free_users_usage_fig', 'figure')
        ],
        [
            Input('free_users_data', 'value'),
            Input('countries_free_usage', 'value'),
            Input('years', 'value'),
        ]
    )
    def update_general_free_users_charts(free_users_data_selector,countries_list, year_range):
        # Total Free Users
        if free_users_data_selector == 'Total Free Users':
            free_users_data = get_total_free_users(collection_free_cycles_by_country)
        elif free_users_data_selector == 'Heavy Free Users':
            free_users_data = get_heavy_free_users(collection_free_cycles_by_country)

        usage_free_users = aggregate_user_cycles(collection_free_cycles_by_country)
        usage_free_users = add_total_as_country(usage_free_users)
        filtered_df = filter_user_cycles(usage_free_users, countries_list, year_range)
        
        # # Graficos 
        heat_map_users_fig = heat_map_users_by_country(free_users_data, title = 'Heavy User condition: cycles_consumed >= max_cycles')
        tree_map_users_fig = tree_map_users_by_country(free_users_data, title = 'Heavy User condition: cycles_consumed >= max_cycles')
        free_users_usage_fig = plot_user_histogram_faceted (filtered_df)
        return heat_map_users_fig, tree_map_users_fig,free_users_usage_fig


    # Callback para gráficos por país - SÍ cambian con filtros
    @app.callback(
        [
            Output('dau_by_country', 'figure'),
            Output('country_share_by_country', 'figure'),
            Output('new_users_by_country', 'figure'),
            Output('interactions_by_country', 'figure')
        ],
        [
            Input('start_date_picker', 'date'), 
            Input('end_date_picker', 'date'),
            Input('view_selector', 'value'),
            Input("country_dropdown_dau", "value"),
            Input("country_dropdown_new_users", "value"),
            Input("country_dropdown_interactions", "value"),
            Input ('country_shares_dropdown', 'value'),
            Input('dau_selector', 'value'),
            Input('dau_selector_share', 'value'),
            Input ('total_category_selector', 'value'),
            Input('interaction_selector', 'value')
        ]
    )
    def update_charts_by_country(start_date, end_date, view, 
                                 country_dropdown_dau, country_dropdown_new_users, 
                                 country_dropdown_interactions, country_shares_dropdown,
                                 dau_selector, dau_selector_share, total_category_selector, interaction_selector):
        """Actualiza gráficos por país según filtros seleccionados"""
        # Parsear fechas
        start = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end = datetime.strptime(end_date[:10], '%Y-%m-%d')
        start_date_str = start.strftime('%Y-%m-%d')
        end_date_str = end.strftime('%Y-%m-%d')

        # Obtener datos para el período seleccionado
        data = get_chart_data(view, start_date_str, end_date_str)
        data_with_total = add_total_per_date(data)

        # Generar gráficos por país
        users_by_country_fig = get_dau_chart(data_with_total, dau_selector, country_dropdown_dau, view)
        country_share_by_country = country_share(data, country_shares_dropdown, view, dau_selector_share, total_category_selector)
        new_users_by_country_fig = new_users_by_country(data_with_total, country_dropdown_new_users, view)
        interactions_by_country_fig = interactions_by_country_chart(data_with_total, country_dropdown_interactions, view, interaction_selector)
        return users_by_country_fig, country_share_by_country, new_users_by_country_fig, interactions_by_country_fig
    
    # Nuevo callback para el gráfico DAU/MAU ratio
    @app.callback(
        Output('dau_mau_ratio_chart', 'figure'),
        [
            Input('start_date_picker', 'date'), 
            Input('end_date_picker', 'date'),
            Input("country_dropdown_DAU/MAU_ratio", "value")
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
