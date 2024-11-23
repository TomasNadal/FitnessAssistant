from __future__ import annotations
import typing
from datetime import datetime, timedelta

import src.training_sessions.domain.models as model
from src.training_sessions.adapters.repository import AbstractRepository
from src.training_sessions.adapters.whatsapp_api import WhatsappClient
from src.training_sessions.adapters.transcriber import OpenAiTranscriber

from src.training_sessions.domain.sets_parser import CSVFileParser, TextParser, InvalidTrainingData
from openai import OpenAI

'''
Here should go the Orchestration Logic
- Fetching objects from the domain model
- Validation
- We call a domain service
- If all is well, we save/update the state
'''

def get_or_create_user(phone_number: str , repo: AbstractRepository, session,) -> str:
    
    
    try:
        user = repo.get(phone_number=phone_number)
    except Exception:
        user = model.User(phone_number=phone_number)
        repo.add(user)  
        session.commit()
    return user

def get_or_create_training_session(phone_number: str, repo: AbstractRepository, session) -> None:
    user = get_or_create_user(phone_number, repo, session)
    
    try:
        # Domain logic for finding valid active session
        return user,model.get_current_training_session(user.training_sessions)
    
    except model.NotActiveSessions:
        # Orchestration for creating new session
        new_training_session = model.TrainingSession(started_at=datetime.now())
        user.add_training_session(new_training_session)
        session.commit()
        return user,new_training_session


def add_sets(phone_number: str, set_data: typing.Set[model.Set], repo: AbstractRepository, session, ):
    user = get_or_create_user(phone_number,repo,session)
    user, training_session = get_or_create_training_session(phone_number, repo, session)

    sorted_sets = sorted(set_data, key = lambda x: (x.series, x.repetition))

    for set in sorted_sets:
        training_session.sets
        training_session_id = model.add_set(set, user.training_sessions)


    series_info = {'exercise': sorted_sets[-1].exercise,
                   'series': sorted_sets[-1].series,
                   'repetition':sorted_sets[-1].repetition,
                   'kg': sorted_sets[-1].kg, 
                   'rir':sorted_sets[-1].rir}
    
    session.commit()

    return training_session_id, series_info


def add_sets_from_raw(payload: dict, repo: AbstractRepository, api: WhatsappClient, session) -> dict:
    

    phone_number = payload["from"]
    message_type = payload["type"]
    print(f'This is the message type {message_type}')
    if message_type=="document":
        parser = CSVFileParser()
        document = payload[message_type]
        file_path = api.download_media(document["filename"], document["id"])
        training_sets = parser.parse(file_path)

        training_session_id, series_info = add_sets(phone_number, training_sets, repo, session)

        api.send_text_message(phone_number, f'Se ha añadido la serie {series_info["series"]} de {series_info["exercise"]}, {series_info["repetition"]} repeticiones con {series_info["kg"]} kg')
        return training_session_id, series_info
    
    elif message_type=="audio":
        audio = payload[message_type]
        file_path_ogg = api.download_media("audio.ogg", audio["id"])

        transcriber = OpenAiTranscriber()
        parser = TextParser(OpenAI())

        transcript = transcriber.transcribe(file_path_ogg, "mp3")

        training_sets = parser.parse(transcript)

        training_session_id, series_info = add_sets(phone_number, training_sets, repo, session)

        api.send_text_message(phone_number, f'Se ha añadido la serie {series_info["series"]} de {series_info["exercise"]}, {series_info["repetition"]} repeticiones con {series_info["kg"]} kg')
    
        return training_session_id, series_info
    
    elif message_type=="text":
        parser = TextParser(OpenAI())
        message_body = payload[message_type]["body"]

        try:
            training_sets = parser.parse(message_body)
            training_session_id, series_info = add_sets(phone_number, training_sets, repo, session)

            api.send_text_message(phone_number, f'Se ha añadido la serie {series_info["series"]} de {series_info["exercise"]}, {series_info["repetition"]} repeticiones con {series_info["kg"]} kg')
        
            return training_session_id, series_info
        except InvalidTrainingData:
            raise
    else:
        pass