import os

def get_postgres_uri():
    host = os.environ.get("DB_HOST", "172.30.48.1")
    port = 34526 if host == "172.30.48.1" else 5432
    password = os.environ.get("DB_PASSWORD", "training")
    user, db_name = "training_session_user", "training_sessions_dev"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

def get_whatsapp_api_details():
    access_token = os.environ.get("ACCESS_TOKEN", "")
    api_version = os.environ.get("VERSION", "")
    app_secret = os.environ.get("APP_SECRET", "")
    phone_number_id = os.environ.get("PHONE_NUMBER_ID", "")
    verify_token = os.environ.get("VERIFY_TOKEN", "")

    return {"access_token":access_token,
            "api_version":api_version,
            "app_secret":app_secret,
            "phone_number_id":phone_number_id,
            "verify_token":verify_token}

def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5000 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_text_parser_details():
    system_prompt = '''
Eres un analizador de transcripciones de ejercicios. Extrae información estructurada de descripciones de ejercicios en español según estas especificaciones:

Formato de Salida:
{
   "exercise": texto,     // Nombre normalizado del ejercicio, "" si no se encuentra
   "series": entero,     // Número de serie, -1 si no se encuentra
   "repetition": entero, // Repeticiones por serie, -1 si no se encuentra
   "kg": decimal,        // Peso en kg, -1.0 si no se encuentra 
   "rir": entero        // Repeticiones en reserva (0 = al fallo), -1 si no se encuentra
}

Reglas:
- Normalizar nombres de ejercicios (ej: "press banca" no "press de banca")
- No utilizar acentuación
- "Al fallo" significa RIR 0. A tres del fallo significa RIR 3.
- Series pueden ser ordinales ("primera", "1era") o explícitas ("3 series")
- Usar valores por defecto si no se encuentra información:
 * exercise: ""  
 * series/repetition/rir: -1
 * kg: -1.0

Ejemplos:

"press cuarta serie con 80kg al fallo"
{
   "exercise": "press banca",
   "series": 4,
   "repetition": 12,
   "kg": 80.0,
   "rir": 0
}

"tercera serie de dominadas rir 2"
{
   "exercise": "dominadas",
   "series": 3,
   "repetition": -1,
   "kg": -1.0,
   "rir": 2
}
'''
    model = "gpt-4o-mini"

    schema = {
   "type": "json_schema",
   "json_schema": {
       "name": "parser_respuesta_ejercicio",
       "schema": {
           "type": "object",
           "properties": {
               "exercise": {
                   "type": "string",
                   "description": "Nombre normalizado del ejercicio, nulo si no se encuentra"
               },
               "series": {
                   "type": "number",
                   "description": "Número de series, nulo si no se encuentra"
               },
               "repetition": {
                   "type": "number",
                   "description": "Repeticiones por serie, nulo si no se encuentra"
               },
               "kg": {
                   "type": "number",
                   "description": "Peso en kilogramos, nulo si no se encuentra"
               },
               "rir": {
                   "type": "number",
                   "description": "Repeticiones en reserva (0 = al fallo), nulo si no se encuentra"
               }
           },
           "required": ["exercise", "series", "repetition", "kg", "rir"],
           "additionalProperties": False
       },
       "strict": True
   }
}

    return {"model":model, "system_prompt":system_prompt, "schema":schema}

