from __future__ import annotations
import typing
from datetime import datetime, timedelta

import src.training_sessions.domain.models as model
from src.training_sessions.adapters.repository import AbstractRepository
from src.training_sessions.adapters.whatsapp_api import WhatsappClient
from src.training_sessions.adapters.sets_parser import CSVParser

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
    user, new_training_session = get_or_create_training_session(phone_number, repo, session)
    for set in sorted(set_data, key = lambda x: (x.series, x.repetition)):
        training_session_id = model.add_set(set, user.training_sessions)

    session.commit()

    return training_session_id


def add_sets_from_raw(payload: dict, repo: AbstractRepository, api: WhatsappClient, session) -> dict:
    parser = CSVParser()

    phone_number = payload["from"]
    message_type = payload["type"]

    if message_type=="document":
        document = payload[message_type]
        file_path = api.download_media(document["filename"], document["id"])
        training_dataframe = parser.from_file_to_dataframe(file_path)
        training_sets = parser.parse_to_sets(training_dataframe)

        training_session_id = add_sets(phone_number, training_sets, repo, session)

        return training_session_id
    elif message_type=="audio":
        audio = payload[message_type]
        file_path = api.download_media("audio.ogg", audio["id"])

    else:
        pass