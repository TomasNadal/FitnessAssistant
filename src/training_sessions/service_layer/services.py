from __future__ import annotations
import typing
from datetime import datetime, timedelta

import src.training_sessions.domain.models as model
from src.training_sessions.adapters.repository import AbstractRepository
from src.training_sessions.adapters.whatsapp_api import WhatsappClient
from src.training_sessions.adapters.transcriber import OpenAiTranscriber
from src.training_sessions.service_layer.unit_of_work import AbstractUnitOfWork

from src.training_sessions.domain.sets_parser import CSVFileParser, TextParser, AbstractFileParser, InvalidTrainingData
from openai import OpenAI

'''
Here should go the Orchestration Logic
- Fetching objects from the domain model
- Validation
- We call a domain service
- If all is well, we save/update the state
'''

def get_or_create_user_and_training_session(phone_number: str,  uow: AbstractUnitOfWork ) -> str:
    try:

        user = uow.users.get(phone_number=phone_number)
        training_session = user.get_training_session()

    except Exception:

        user = model.User(phone_number=phone_number)
        uow.users.add(user)  
        training_session = user.get_training_session()
        uow.commit()
    return user, training_session

# I know I will need to refactor this to follow SOLID
def initialize_parser(message_type: str, training_session_id: typing.Optional[str]) -> AbstractFileParser:
    if ( message_type == 'audio') or (message_type == 'text'):
        parser = TextParser(OpenAI())

    elif message_type == 'document':
        parser = CSVFileParser(training_session_id)

    return parser

def extract_and_parse(payload: dict, api: WhatsappClient, uow: AbstractUnitOfWork):
    phone_number = payload["from"]
    message_type = payload["type"]

    with uow:
        user, training_session = get_or_create_user_and_training_session(phone_number, uow)
        parser = initialize_parser(message_type, training_session.id)

        if message_type == 'audio':
            audio = payload[message_type]
            file_path_ogg = api.download_media("audio.ogg", audio["id"])
            transcriber = OpenAiTranscriber()
            transcript = transcriber.transcribe(file_path_ogg, "mp3")

            training_sets = parser.parse(transcript)

        elif message_type == 'text':
            message_body = payload[message_type]["body"]
            training_sets = parser.parse(message_body)

        elif message_type == 'document':
            document = payload[message_type]
            file_path = api.download_media(document["filename"], document["id"])

            training_sets = parser.parse(file_path)

        return training_sets



def add_series(phone_number: str, raw_series: list, uow: AbstractUnitOfWork ) -> typing.List[str]:
    
    

    added_series = []
    with uow:
        user, training_session = get_or_create_user_and_training_session(phone_number, uow)
        
        for s in raw_series:
            exercise = training_session.get_exercise(s['exercise'])

            serie = exercise.add_series()
            
            for rep in s['repetitions']:

                serie.add_repetition(model.Repetition(**rep))
            print(f'Testing the series str {serie}')
            added_series.append(str(serie))

        uow.commit()

    return added_series



def add_sets_from_raw(payload: dict, api: WhatsappClient, uow: AbstractUnitOfWork) -> dict:
    phone_number = payload["from"]
    training_series = None  # Initialize the variable first
    
    try:
        training_series = extract_and_parse(payload, api, uow)
    except InvalidTrainingData as e:
        api.send_text_message(phone_number, f'Por favor, manda la serie incluyendo estos datos que no mencionaste: {e.parsing_errors}')
        return {}  # Return early after sending error message
    except Exception as e:
        api.send_text_message(phone_number, f'Error inesperado: {str(e)}')
        return {}  # Return early after sending error message
    
    # If we get here, training_series was successfully assigned
    if not training_series:  # Check if it's empty/None
        api.send_text_message(phone_number, f'Invalid payload: {payload}')
        return {}

    # Process valid training series
    series_str = add_series(payload["from"], training_series, uow)
    
    for serie in series_str:
        api.send_text_message(phone_number, f'Se ha añadido la serie {str(serie)}')
    
    return {"status": "success", "series": series_str}  # Return success result