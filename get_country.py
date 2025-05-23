import phonenumbers
from phonenumbers import geocoder
import pycountry  


def getCountry(phone):
    """
    Recibe un número de teléfono como entrada y devuelve el nombre del país correspondiente.

    Parámetros:
    phone (str): Un número de teléfono en formato E.164 (incluyendo el prefijo internacional, por ejemplo, +1 para EE. UU.).

    Retorna:
    str: El nombre del país correspondiente al código de país del número telefónico. Si ocurre un error, 
         se retorna el valor "Telegram".
    """
    try:
        phone_parsed = phonenumbers.parse(phone)  # Analiza el número de teléfono
        country_code = phonenumbers.region_code_for_number(phone_parsed)  # Obtiene el código de región
        country = pycountry.countries.get(alpha_2=country_code)  # Busca el país usando el código de región
        country_name = country.name  # Obtiene el nombre del país
        # Si el nombre del país contiene una coma, devuelve solo lo que está antes de la coma
        if ',' in country_name:
            country_name = country_name.split(',')[0]
        return country_name  # Retorna el nombre del país
    except Exception as e:
        return "Invalid_number"  # Retorna "Invalid_number" si ocurre algún error