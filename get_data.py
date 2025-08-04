from datetime import datetime, timedelta
import pandas as pd

from datetime import datetime, timedelta
import pandas as pd

def get_daily_data(collection_dau, collection_new_users, start_date, end_date):
    """
    Extrae documentos de TranscribeMe-charts.dau-by-country en un rango de fechas y los convierte en un DataFrame.
    
    Args:
        collection_dau (Collection): Objeto de colección de pymongo para DAU.
        collection_new_users (Collection): Objeto de colección de pymongo para nuevos usuarios.
        start_date (str): Fecha inicial en formato 'yyyy-mm-dd'.
        end_date (str): Fecha final en formato 'yyyy-mm-dd'.
    
    Returns:
        pd.DataFrame: DataFrame con las columnas date, country, count, new_users, subscribed, interactions, audio, text.
    """
    try:
        # Validar formato de fechas
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                raise ValueError("start_date no puede ser mayor que end_date")
        except ValueError as e:
            print(f"Error en el formato de las fechas: {e}. Use 'yyyy-mm-dd'.")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

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
            'subscribed': 1,
            'interactions': 1,
            'audio': 1,
            'text': 1
        }

        # Extraer documentos
        documentos = list(collection_dau.find(query, projection))
        print(f"Documentos extraídos de collection_dau: {len(documentos)}")  # Depuración

        proj = {"_id": 0, "date": 1, "country": 1, "new_users": 1}
        docs = list(collection_new_users.find(query, proj))
        print(f"Documentos extraídos de collection_new_users: {len(docs)}")  # Depuración

        # Verificar si se encontraron documentos
        if not documentos:
            print(f"No se encontraron documentos en la colección '{collection_dau.name}' entre {start_date} y {end_date}.")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

        # Convertir a DataFrame
        df = pd.DataFrame(documentos)
        df2 = pd.DataFrame(docs)
        
        # Depuración: Verificar contenido de los DataFrames
        print("Columnas en df:", df.columns.tolist())
        print("Columnas en df2:", df2.columns.tolist())
        print("Primeros registros de df:", df.head().to_dict())
        print("Primeros registros de df2:", df2.head().to_dict())

        # Cambiar nombre
        df = df.rename(columns={'dau': 'count'})

        # Convertir 'date' a datetime en ambos DataFrames
        try:
            df['date'] = pd.to_datetime(df['date'])
            df2['date'] = pd.to_datetime(df2['date'])
        except Exception as e:
            print(f"Error al convertir 'date' a datetime: {e}")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

        # Asegurar que la columna 'date' esté en formato string 'yyyy-mm-dd'
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df2['date'] = df2['date'].dt.strftime('%Y-%m-%d')

        # Unir los DataFrames por 'date' y 'country'
        df = df.merge(df2[['date', 'country', 'new_users']], 
                      on=['date', 'country'], 
                      how='left')

        # Ordenar por 'date'
        df = df.sort_values(by='date', ascending=True)

        # Rellenar posibles valores NaN o None en 'new_users' con 0
        df['new_users'] = df['new_users'].replace([None], 0).fillna(0).astype(int)

        return df
    
    except Exception as e:
        print(f"Error al extraer datos: {e}")
        return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

def get_monthly_data(collection, collection_new_users, start_date, end_date):
    """
    Extrae documentos de TranscribeMe-charts.dau-by-country en un rango de fechas y los convierte en un DataFrame.
    
    Args:
        collection (Collection): Objeto de colección de pymongo para datos mensuales.
        collection_new_users (Collection): Objeto de colección de pymongo para nuevos usuarios.
        start_date (str): Fecha inicial en formato 'yyyy-mm-dd'.
        end_date (str): Fecha final en formato 'yyyy-mm-dd'.
    
    Returns:
        pd.DataFrame: DataFrame con las columnas date, country, count, new_users, subscribed, interactions, audio, text.
    """
    try:
        # Validar formato de fechas
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                raise ValueError("start_date no puede ser mayor que end_date")
        except ValueError as e:
            print(f"Error en el formato de las fechas: {e}. Use 'yyyy-mm-dd'.")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

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
            'subscribed': 1,
            'interactions': 1,
            'audio': 1,
            'text': 1
        }

        # Extraer documentos
        documentos = list(collection.find(query, projection))
        print(f"Documentos extraídos de collection: {len(documentos)}")  # Depuración
        if documentos:
            print("Ejemplo de documento:", documentos[0])  # Mostrar un documento

        proj = {"_id": 0, "date": 1, "country": 1, "new_users": 1}
        docs = list(collection_new_users.find({'date': {'$gte': start_date, '$lte': end_date}}, proj))
        print(f"Documentos extraídos de collection_new_users: {len(docs)}")  # Depuración
        if docs:
            print("Ejemplo de documento new_users:", docs[0])  # Mostrar un documento

        # Verificar si se encontraron documentos
        if not documentos:
            print(f"No se encontraron documentos en la colección '{collection.name}' entre {start_date} y {end_date}.")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

        # Convertir a DataFrame
        df = pd.DataFrame(documentos)
        df2 = pd.DataFrame(docs)

        # Depuración: Verificar columnas
        print("Columnas en df:", df.columns.tolist())
        print("Columnas en df2:", df2.columns.tolist())

        # Verificar si 'month' existe en df
        if 'month' not in df.columns:
            print("Error: La columna 'month' no está presente en los datos de la colección")
            return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

        # Cambiar nombre
        df = df.rename(columns={'mau': 'count', 'month': 'date'})

        # Convertir 'date' en df a formato 'yyyy-mm' para compatibilidad
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)

        # Crear una columna 'month' en df2 para el año-mes
        if not df2.empty and 'date' in df2.columns:
            df2['month'] = pd.to_datetime(df2['date'], errors='coerce').dt.to_period('M').astype(str)
        else:
            print("Advertencia: df2 está vacío o no contiene la columna 'date'")
            df2['month'] = None

        # Agrupar por month y country para calcular new_users
        new_users_df = df2.groupby(['month', 'country']).agg(
            new_users=('new_users', 'sum')
        ).reset_index()

        # Unir los DataFrames por 'month' y 'country'
        df = df.merge(new_users_df[['month', 'country', 'new_users']], 
                      on=['month', 'country'], 
                      how='left')

        # Ordenar por 'month'
        df = df.sort_values(by='month', ascending=True)

        # Rellenar posibles valores NaN o None en 'new_users' con 0
        df['new_users'] = df['new_users'].replace([None], 0).fillna(0).astype(int)

        # Seleccionar columnas finales
        df = df[['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text']]

        return df
    
    except Exception as e:
        print(f"Error al extraer datos: {e}")
        return pd.DataFrame(columns=['date', 'country', 'count', 'new_users', 'subscribed', 'interactions', 'audio', 'text'])

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

def get_total_free_users(collection):
    # Pipeline de agregación
    pipeline = [
        # 1. Agrupar por país y contar usuarios únicos
        {
            "$group": {
                "_id": "$country",
                "Users": {"$addToSet": "$user_id"}  # Conjunto de user_id únicos
            }
        },
        # 2. Contar el número de usuarios por país
        {
            "$project": {
                "country": "$_id",
                "Users": {"$size": "$Users"},  # Tamaño del conjunto de usuarios
                "_id": 0
            }
        },
        # 3. Ordenar por país
        {"$sort": {"country": 1}}
    ]
    
    # Ejecutar el pipeline
    results = list(collection.aggregate(pipeline))
    
    # Convertir a DataFrame
    df = pd.DataFrame(results)
    
    # Calcular el total de usuarios
    total_users = df['Users'].sum() if not df.empty else 1  # Evitar división por 0
    
    # Calcular el Share (%)
    df['Share'] = (df['Users'] / total_users * 100).round(2)
    
    # Reordenar columnas
    df = df[['country', 'Users', 'Share']]
    
    return df

def get_heavy_free_users(collection):
    # Pipeline de agregación
    pipeline = [
        # 1. Filtrar usuarios donde cycles_consumed >= max_cycles
        {"$match": {"$expr": {"$gte": ["$cycles_consumed", "$max_cycles"]}}},
        # 2. Agrupar por país y contar usuarios únicos
        {
            "$group": {
                "_id": "$country",
                "Users": {"$addToSet": "$user_id"}  # Conjunto de user_id únicos
            }
        },
        # 3. Contar el número de usuarios por país
        {
            "$project": {
                "country": "$_id",
                "Users": {"$size": "$Users"},  # Tamaño del conjunto de usuarios
                "_id": 0
            }
        },
        # 4. Ordenar por país
        {"$sort": {"country": 1}}
    ]
    
    # Ejecutar el pipeline
    results = list(collection.aggregate(pipeline))
    
    # Convertir a DataFrame
    df = pd.DataFrame(results)
    
    # Calcular el total de heavy_free_users
    total_users = df['Users'].sum() if not df.empty else 1  # Evitar división por 0
    
    # Calcular el Share (%)
    df['Share'] = (df['Users'] / total_users * 100).round(2)
    
    # Reordenar columnas
    df = df[['country', 'Users', 'Share']]
    
    return df

def get_users_by_country_and_cycles(collection):
    pipeline = [
        {
            "$group": {
                "_id": {
                    "country": "$country",
                    "cycles_consumed": "$cycles_consumed"
                },
                "Users": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "country": "$_id.country",
                "cycles_consumed": "$_id.cycles_consumed",
                "Users": 1
            }
        },
        {
            "$sort": {
                "country": 1,
                "cycles_consumed": 1
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    # Convertir a DataFrame
    df = pd.DataFrame(results)
    
    return df

def aggregate_user_cycles(collection):
    pipeline = [
        {
            '$project': {
                'cycles_consumed': 1,
                'country': 1,
                'year': {'$year': {'$dateFromString': {'dateString': '$last_date'}}}
            }
        },
        {
            '$group': {
                '_id': {
                    'cycles_consumed': '$cycles_consumed',
                    'country': '$country',
                    'year': '$year'
                },
                'Users': {'$sum': 1}
            }
        },
        {
            '$project': {
                '_id': 0,
                'cycles_consumed': '$_id.cycles_consumed',
                'country': '$_id.country',
                'last_date': '$_id.year',
                'Users': 1
            }
        }
    ]
    
    result = list(collection.aggregate(pipeline))
    df = pd.DataFrame(result)
    return df

def add_total_as_country (df):
    total_df = df.groupby(['cycles_consumed', 'last_date'])['Users'].sum().reset_index()
    total_df['country'] = 'Total'
    result = pd.concat([df, total_df])
    return result

def filter_user_cycles(df, countries, year_range):
    start_year, end_year = year_range
    filtered_df = df[
        df['country'].isin(countries) &
        df['last_date'].between(start_year, end_year)
    ]
    return filtered_df

# MÉTRICAS TOTALES FIJAS - Se calculan una sola vez al iniciar la app
def calculate_total_metrics(collection_dau_by_country, collection_mau_by_country, collection_new_users):
    """Calcula métricas totales desde 2023-01-01 hasta hoy - SOLO SE EJECUTA UNA VEZ"""
    start_date = "2023-01-01"
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Calculando métricas totales desde {start_date} hasta {end_date}...")
    
    # Obtener datos completos
    daily_data = get_daily_data(collection_dau_by_country, collection_new_users, start_date, end_date)
    monthly_data = get_monthly_data(collection_mau_by_country, collection_new_users, start_date, end_date)
    
    # Realizar la agregación para sumar 'new_users'
    pipeline = [
            {
                "$group": {
                    "_id": None,  # Agrupar todos los documentos (sin clave específica)
                    "total_new_users": {"$sum": "$new_users"}  # Sumar el campo 'new_users'
                }
            }
        ]
    result = list(collection_new_users.aggregate(pipeline))
    
    # Calcular métricas totales
    total_new_users = result[0]['total_new_users']
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

def get_errors_by_date (collection, view):
    results = list(collection.find({}, {'_id': 0}))
    df = pd.DataFrame(results)

    if view == 'Monthly':
        df['localdate'] = pd.to_datetime(df['localdate']).dt.strftime("%Y-%m")
        # Agrupar por mes y sumar las columnas numéricas
        df = df.groupby('localdate').sum().reset_index()

    df = df.sort_values('localdate')
    return df

def get_invalid_format_types (collection, start, end):
    # Definir el filtro de fechas
    query = {'localdate': {'$gte': start,'$lte': end}}
    results = list(collection.find(query, {'_id': 0, 'localdate': 0}))
    df = pd.DataFrame(results)
    new_df = pd.DataFrame({'type': df.columns,'count': df.sum()}).reset_index(drop=True)
    return new_df
