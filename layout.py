from dash import dcc, html
from datetime import datetime
import pytz
from get_data import get_daily_data

timezone = pytz.timezone('America/Argentina/Buenos_Aires')



def serve_layout():
    # Layout
    return html.Div([
        # Agregar el logo de la empresa
        html.Img(
            src='/assets/TME_LOGO_BOT_2.png',
            style={'height': '50px','width': 'auto','margin': '10px'}
        ),
        # Header
        html.Div([
            html.H1("Dashboard de Usuarios", 
                    style={"color": "#0AB84D", "marginBottom": "10px"}),
            html.Hr(style={"margin": "0 0 20px 0"}),
        ], style={"textAlign": "center", "paddingTop": "20px"}),

        # Selector de fechas
        html.Div([
            html.Div([
                html.Label("Fecha de inicio:"),
                dcc.DatePickerSingle(
                    id='start_date_picker',
                    date=datetime(2025, 1, 1),
                    display_format='YYYY-MM-DD',
                    min_date_allowed=datetime(2023, 12, 1).date(),
                    max_date_allowed=datetime.now(timezone).date(),
                    style={'marginBottom': '10px'}
                ),
            ], style={'margin': '10px', 'flex': '1'}),

            html.Div([
                html.Label("Fecha de fin:"),
                dcc.DatePickerSingle(
                    id='end_date_picker',
                    date=datetime.now(timezone),
                    display_format='YYYY-MM-DD',
                    min_date_allowed=datetime(2023, 12, 1).date(),
                    max_date_allowed=datetime.now(timezone).date(),
                    style={'marginBottom': '10px'}
                ),
            ], style={'margin': '10px', 'flex': '1'}),

            html.Div([
                html.Label("Vista:"),
                dcc.RadioItems(
                    id='view_selector',
                    options=[
                        {'label': 'Diario', 'value': 'Daily'},
                        {'label': 'Mensual', 'value': 'Monthly'}
                    ],
                    value='Daily',
                    style={'display': 'flex', 'gap': '10px'}
                ),
            ], style={'margin': '10px', 'flex': '1'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '20px'}),

        # Tarjetas de métricas
        html.Div([
            html.Div([html.H3("Total Users"), html.H2(id='total_new_users', children='0')], className='metric-card'),
            html.Div([html.H3("Average DAU"), html.H2(id='average_dau', children='0')], className='metric-card'),
            html.Div([html.H3("Average MAU"), html.H2(id='average_mau', children='0')], className='metric-card'),
            html.Div([html.H3("Total Interactions"), html.H2(id='total_interactions', children='0')], className='metric-card'),
            html.Div([html.H3("Total Audios"), html.H2(id='total_audio', children='0')], className='metric-card'),
            html.Div([html.H3("Total Texts"), html.H2(id='total_text', children='0')], className='metric-card'),
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'gap': '15px', 'margin': '20px'}),

        # Pestañas para las vistas
        html.Div([
            dcc.Tabs(id="main-tabs", value="general", children=[
                dcc.Tab(label="Vista General", value="general"),
                dcc.Tab(label="Análisis por países", value="países"),
            ], style={'marginBottom': '20px'}),

            # Contenido de las pestañas
            html.Div(id="tab-content")
        ], style={'margin': '20px'}),
], style={'fontFamily': 'Arial, sans-serif', 'margin': '0 auto', 'maxWidth': '1400px', 'padding': '20px'})
