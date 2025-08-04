import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import pytz

def get_image_data(collection, start_date, end_date):
    """
    Busca la data de uso de la feature de imagen
    Args:
    collection: 
    start_date:
    end_date:
    Returns
    df: pandas DataFrame con la info
    """
    query_img = {"localdate": {"$gte": start_date, "$lte": end_date }, "type": "image"}
    projection_img = {"_id":0, "localdate":1, "user_id":1, "source":1, "extras":1, "result":1, "error":1}
    documentos_img = list(collection.find(query_img, projection_img))
    image_data_df = pd.DataFrame(documentos_img)
    return image_data_df

def get_documents_data(collection, start_date, end_date):
    """
    """
    # Búsqueda y extracción de la data DOCUMENTS
    query_doc = {"localdate": {"$gte": start_date, "$lte": end_date }, "type": "document", "event_type": 'document_transcription'}
    projection_doc = {"_id":0, "localdate":1, "user_id":1, "source":1, "extras":1, "result":1, "error":1}
    documentos_doc = list(collection.find(query_doc, projection_doc))
    pdf_data_df = pd.DataFrame(documentos_doc)
    return pdf_data_df

def get_video_data(collection, start_date, end_date):
    """
    Busca la data de uso de la feature de video
    Args:
    collection: 
    start_date:
    end_date:
    Returns
    df: pandas DataFrame con la info
    """
    query_video = {"localdate": {"$gte": start_date, "$lte": end_date }, "type": "video"}
    projection_video = {"_id":0, "localdate":1, "user_id":1, "source":1, "extras":1, "result":1, "error":1}
    documentos_video = list(collection.find(query_video, projection_video))
    video_data_df = pd.DataFrame(documentos_video)
    return video_data_df

def get_features_df (image_data_df, pdf_data_df, video_data_df, youtube_data_df, rme_data, list_data):
    dau_image = image_data_df.groupby('localdate').size().reset_index(name='dau_image')
    dau_video = video_data_df.groupby('localdate').size().reset_index(name='dau_video')
    dau_youtube = youtube_data_df.groupby('localdate').size().reset_index(name='dau_youtube')
    dau_docs = pdf_data_df.groupby('localdate').size().reset_index(name='dau_documentos')

    # Merge the DataFrames on 'localdate' using an outer join to keep all dates
    df_final = (dau_image[['localdate', 'dau_image']]
            .merge(dau_youtube[['localdate', 'dau_youtube']], on='localdate', how='outer')
            .merge(dau_video[['localdate', 'dau_video']], on='localdate', how='outer')
            .merge(dau_docs[['localdate', 'dau_documentos']], on='localdate', how='outer')
            .merge(rme_data[['localdate', 'dau_reminds']], on='localdate', how='outer')
            .merge(list_data[['localdate', 'dau_lists']], on='localdate', how='outer'))
    
    return df_final

def get_youtube_data(collection, start_date, end_date):
    """
    Busca la data de uso de la feature de YouTube
    Args:
    collection: 
    start_date:
    end_date:
    Returns
    df: pandas DataFrame con la info
    """
    query_youtube = {"localdate": {"$gte": start_date, "$lte": end_date }, "result.type": "youtube_transcription"}
    projection_youtube = {"_id":0, "localdate":1, "user_id":1, "source":1, "extras":1, "result":1, "error":1}
    documentos_youtube = list(collection.find(query_youtube, projection_youtube))
    youtube_data_df = pd.DataFrame(documentos_youtube)
    return youtube_data_df


def plot_dau_lines(df):
    """
    Creates a line plot of DAU by category using Plotly.
    
    Parameters:
    df (pandas.DataFrame): DataFrame with 'localdate' and DAU columns ('dau_image', 
                          'dau_youtube', 'dau_video', 'dau_documentos')
    
    Returns:
    plotly.graph_objects.Figure: The Plotly figure object
    """
    # Ensure 'localdate' is in datetime format
    df = df.copy()  # Avoid modifying the input DataFrame
    df['localdate'] = pd.to_datetime(df['localdate'])
    
    # Sort by date to ensure chronological order
    df = df.sort_values('localdate')
    
    # Create the Plotly figure
    fig = go.Figure()
    
    # Add a line for each DAU column
    fig.add_trace(
        go.Scatter(x=df['localdate'], y=df['dau_image'], mode='lines+markers', name='DAU Image', line=dict(width=2),marker=dict(size=8)
        ))
    fig.add_trace(
        go.Scatter(x=df['localdate'], y=df['dau_youtube'], mode='lines+markers', name='DAU YouTube', line=dict(width=2),marker=dict(size=8)
        ))
    fig.add_trace(go.Scatter(
        x=df['localdate'], 
        y=df['dau_video'], 
        mode='lines+markers', 
        name='DAU Video',
        line=dict(width=2),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=df['localdate'], 
        y=df['dau_documentos'], 
        mode='lines+markers', 
        name='DAU Documents',
        line=dict(width=2),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=df['localdate'], 
        y=df['dau_reminds'], 
        mode='lines+markers', 
        name='DAU Reminds',
        line=dict(width=2),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=df['localdate'], 
        y=df['dau_lists'], 
        mode='lines+markers', 
        name='DAU Lists',
        line=dict(width=2),
        marker=dict(size=8)
    ))
    
    # Customize the layout
    fig.update_layout(
        yaxis_title='DAU Count',
        xaxis_title='Date',
        yaxis_tickformat=',',
        title='Actividad de cada Feature',
        title_x = 0.5,
        hovermode='x unified', 
        showlegend=True
    ) 
    return fig

def get_lists_data(collection, start_date_str, end_date_str):
    # Tu zona horaria de trabajo
    tz = pytz.timezone('America/Argentina/Buenos_Aires')
    # Convertimos a date (sin hora aún)
    start_date_raw = datetime.fromisoformat(start_date_str).date()
    end_date_raw = datetime.fromisoformat(end_date_str).date()
    start_dt = datetime.combine(start_date_raw, time.min, tz)
    end_dt = datetime.combine(end_date_raw, time.max, tz)
    # Hacer end_date inclusivo sumando un día
    end_date_inclusive = end_dt + timedelta(days=1)

    # Convertir start_date y end_date a Unix timestamp en segundos
    start_timestamp = start_dt.timestamp()
    end_timestamp = end_date_inclusive.timestamp()

    pipeline = [
        # 1. Filtrar por rango de fechas en created_at (Unix timestamp)
        {
            "$match": {
                "created_at": {
                    "$gte": start_timestamp,
                    "$lte": end_timestamp
                }
            }
        },
        # 2. Agrupar por día (convirtiendo created_at a fecha)
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {"$toDate": {"$multiply": ["$created_at", 1000]}},  # Convertir segundos a milisegundos
                        "timezone": "America/Argentina/Buenos_Aires"
                    }
                },
                # Conteos de listas
                "dau_lists": {"$sum": 1},
            }
        },
        # 3. Project
        {
            "$project": {
                "localdate": "$_id",
                "dau_lists": 1,
                "_id": 0
            }
        },
        # 4. Ordenar por fecha
        {
            "$sort": {"localdate": 1}
        }
    ]
    # Ejecutar el pipeline y obtener resultados
    results = list(collection.aggregate(pipeline))

    # Convertir a DataFrame
    df = pd.DataFrame(results)

    # Si no hay resultados, devolver DataFrame vacío con columnas correctas
    if df.empty:
        return pd.DataFrame(columns=["localdate", "dau_lists"])
    
    # Asegurar que las columnas estén en el orden correcto
    df = df[["localdate", "dau_lists"]]
    return df

def get_reminders_data(collection, start_date_str, end_date_str):
    # Tu zona horaria de trabajo
    tz = pytz.timezone('America/Argentina/Buenos_Aires')
    # Convertimos a date (sin hora aún)
    start_date_raw = datetime.fromisoformat(start_date_str).date()
    end_date_raw = datetime.fromisoformat(end_date_str).date()
    start_dt = datetime.combine(start_date_raw, time.min, tz)
    end_dt = datetime.combine(end_date_raw, time.max, tz)
    # Hacer end_date inclusivo sumando un día
    end_date_inclusive = end_dt + timedelta(days=1)

    # Convertir start_date y end_date a Unix timestamp en segundos
    start_timestamp = start_dt.timestamp()
    end_timestamp = end_date_inclusive.timestamp()

    pipeline = [
        # 1. Filtrar por rango de fechas en created_at (Unix timestamp)
        {
            "$match": {
                "created_at": {
                    "$gte": start_timestamp,
                    "$lte": end_timestamp
                }
            }
        },
        # 2. Agrupar por día (convirtiendo created_at a fecha)
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {"$toDate": {"$multiply": ["$created_at", 1000]}},  # Convertir segundos a milisegundos
                        "timezone": "America/Argentina/Buenos_Aires"
                    }
                },
                # Conteos de listas
                "dau_reminds": {"$sum": 1},
            }
        },
        # 3. Project
        {
            "$project": {
                "localdate": "$_id",
                "dau_reminds": 1,
                "_id": 0
            }
        },
        # 4. Ordenar por fecha
        {
            "$sort": {"localdate": 1}
        }
    ]
    # Ejecutar el pipeline y obtener resultados
    results = list(collection.aggregate(pipeline))

    # Convertir a DataFrame
    df = pd.DataFrame(results)

    # Si no hay resultados, devolver DataFrame vacío con columnas correctas
    if df.empty:
        return pd.DataFrame(columns=["localdate", "dau_reminds"])
    
    # Asegurar que las columnas estén en el orden correcto
    df = df[["localdate", "dau_reminds"]]
    return df
