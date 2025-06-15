from datetime import datetime, timedelta
import pandas as pd

def get_daily_data(collection, start_date, end_date):
    """
    Extrae documentos de TranscribeMe-charts.dau-by-country en un rango de fechas y los convierte en un DataFrame.
    
    Args:
        collection (Collection): Objeto de colección de pymongo.
        start_date (str): Fecha inicial en formato 'yyyy-mm-dd'.
        end_date (str): Fecha final en formato 'yyyy-mm-dd'.
    
    Returns:
        pd.DataFrame: DataFrame con las columnas date, country, dau, new_users, interactions, audio, text.
    """
    try:
        # Validar formato de fechas
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                raise ValueError("start_date no puede ser mayor que end_date")
        except ValueError as e:
            raise ValueError(f"Error en el formato de las fechas: {e}. Use 'yyyy-mm-dd'.")

        # Definir el filtro de fechas
        query = {
            'date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }

        # Definir los campos a extraer
        projection = {
            '_id': 0,  # Excluir el campo _id
            'date': 1,
            'country': 1,
            'dau': 1,
            'new_users': 1,
            'subscribed':1,
            'interactions': 1,
            'audio': 1,
            'text': 1
        }

        # Extraer documentos
        documentos = list(collection.find(query, projection))

        # Verificar si se encontraron documentos
        if not documentos:
            print(f"No se encontraron documentos en la colección '{collection.name}' entre {start_date} y {end_date}.")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed','interactions', 'audio', 'text'])

        # Convertir a DataFrame
        df = pd.DataFrame(documentos)

        # Cambiar nombre
        df = df.rename(columns={'dau': 'count'})

        # Convertir 'date' a datetime
        df['date'] = pd.to_datetime(df['date'])

        # Ordenar por 'date'
        df = df.sort_values(by='date', ascending=True)
        
        # Asegurar que la columna 'date' esté en formato string 'yyyy-mm-dd'
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        return df
    
    except Exception as e:
        print(f"Error al extraer datos: {e}")
        return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed','interactions', 'audio', 'text'])

def get_monthly_data(collection, start_date, end_date):
    """
    Extrae documentos de TranscribeMe-charts.dau-by-country en un rango de fechas y los convierte en un DataFrame.
    
    Args:
        collection (Collection): Objeto de colección de pymongo.
        start_date (str): Fecha inicial en formato 'yyyy-mm-dd'.
        end_date (str): Fecha final en formato 'yyyy-mm-dd'.
    
    Returns:
        pd.DataFrame: DataFrame con las columnas date, country, dau, new_users, interactions, audio, text.
    """
    try:
        # Validar formato de fechas
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                raise ValueError("start_date no puede ser mayor que end_date")
        except ValueError as e:
            raise ValueError(f"Error en el formato de las fechas: {e}. Use 'yyyy-mm-dd'.")

        # Definir el filtro de fechas
        query = {
            'month': {
                '$gte': start_date,
                '$lte': end_date
            }
        }

        # Definir los campos a extraer
        projection = {
            '_id': 0,  # Excluir el campo _id
            'month': 1,
            'country': 1,
            'mau': 1,
            'new_users': 1,
            'subscribed': 1,
            'interactions': 1,
            'audio': 1,
            'text': 1
        }

        # Extraer documentos
        documentos = list(collection.find(query, projection))

        # Verificar si se encontraron documentos
        if not documentos:
            print(f"No se encontraron documentos en la colección '{collection.name}' entre {start_date} y {end_date}.")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

        # Convertir a DataFrame
        df = pd.DataFrame(documentos)

        # Cambiar nombre
        df = df.rename(columns={'mau': 'count'})
        df = df.rename(columns={'month': 'date'})
        # Asegurar que la columna 'date' esté en formato string 'yyyy-mm-dd'
        #df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        return df
    
    except Exception as e:
        print(f"Error al extraer datos: {e}")
        return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed','interactions', 'audio', 'text'])

def add_total_per_date (df):
    # Calcular totales por fecha
    total_por_fecha = df.groupby('date', as_index=False)[['count', 'new_users', 'interactions', 'audio', 'text', 'subscribed']].sum()
    total_por_fecha['country'] = 'Total'

    # Reordenar columnas para que coincidan
    total_por_fecha = total_por_fecha[df.columns]

    # Concatenar al DataFrame original
    df = pd.concat([df, total_por_fecha], ignore_index=True)
    return df


# Para formatear los datos históricos
def format_number_smart(number):
    """Formato inteligente: compacto para números muy grandes, completo para otros"""
    if isinstance(number, (int, float)):
        if number >= 10000000:  # 10M o más -> formato compacto
            if number >= 1000000000:
                return f"{number/1000000000:.1f}B"
            elif number >= 1000000:
                return f"{number/1000000:.1f}M"
        else:  # Menos de 10M -> formato completo con puntos
            return f"{number:,.0f}".replace(',', '.')
    return str(number)

def get_total_users_by_country (collection):
    data = list(collection.find({}, {'_id': 0}))
    data_df = pd.DataFrame(data)
    return data_df

# MÉTRICAS TOTALES FIJAS - Se calculan una sola vez al iniciar la app
def calculate_total_metrics(collection_dau_by_country, collection_mau_by_country):
    """Calcula métricas totales desde 2023-01-01 hasta hoy - SOLO SE EJECUTA UNA VEZ"""
    start_date = "2023-01-01"
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Calculando métricas totales desde {start_date} hasta {end_date}...")
    
    # Obtener datos completos
    daily_data = get_daily_data(collection_dau_by_country, start_date, end_date)
    monthly_data = get_monthly_data(collection_mau_by_country, start_date, end_date)
    
    # Calcular métricas totales
    total_new_users = int(daily_data['new_users'].sum())
    average_dau = int(daily_data['count'].sum() / len(daily_data.groupby('date')))
    average_mau = int(monthly_data['count'].sum() / len(monthly_data.groupby('date')))
    total_interactions = int (daily_data['interactions'].sum())
    total_audio = int(daily_data['audio'].sum())
    total_text = int(daily_data['text'].sum())
    
    print("Métricas totales calculadas exitosamente")
    
    return {
        'total_new_users': format_number_smart(total_new_users),
        'average_dau': format_number_smart(average_dau),
        'average_mau': format_number_smart(average_mau),
        'total_interactions': format_number_smart(total_interactions),
        'total_audio': format_number_smart(total_audio),
        'total_text': format_number_smart(total_text)
    }

def get_dau_mau_ratio_data(dau_data, mau_data, countries=None):
    """
    Obtiene datos combinados de DAU y MAU para calcular el ratio DAU/MAU
    
    Args:
        collection_dau: Colección de datos diarios
        collection_mau: Colección de datos mensuales  
        start_date: Fecha inicio (YYYY-MM-DD)
        end_date: Fecha fin (YYYY-MM-DD)
        countries: Lista de países a filtrar (opcional)
    
    Returns:
        DataFrame con columnas: year_month, country, avg_dau, mau, dau_mau_ratio
    """
    dau_data = dau_data.copy()
    mau_data = mau_data.copy()

    # 3. Filtrar por países si se especifica
    if countries:
        dau_data = dau_data[dau_data['country'].isin(countries)]
        mau_data = mau_data[mau_data['country'].isin(countries)]
    
    # 4. Crear year_month para DAU (agregar por mes)
    dau_data['date'] = pd.to_datetime(dau_data['date'])
    dau_data['year_month'] = dau_data['date'].dt.to_period('M').astype(str)
    
    # 5. Calcular DAU promedio por mes y país
    avg_dau_monthly = dau_data.groupby(['year_month', 'country'])['count'].mean().reset_index()
    avg_dau_monthly.rename(columns={'count': 'avg_dau'}, inplace=True)
    
    # 6. Preparar MAU data
    mau_data['date'] = pd.to_datetime(mau_data['date'])
    mau_data['year_month'] = mau_data['date'].dt.to_period('M').astype(str)
    mau_monthly = mau_data.groupby(['year_month', 'country'])['count'].sum().reset_index()
    mau_monthly.rename(columns={'count': 'mau'}, inplace=True)
    
    # 7. Combinar DAU y MAU
    ratio_data = pd.merge(avg_dau_monthly, mau_monthly, on=['year_month', 'country'], how='inner')
    
    # 8. Calcular ratio DAU/MAU
    ratio_data['dau_mau_ratio'] = ratio_data['avg_dau'] / ratio_data['mau']
    
    # 9. Ordenar por fecha
    ratio_data = ratio_data.sort_values('year_month')
    
    return ratio_data
