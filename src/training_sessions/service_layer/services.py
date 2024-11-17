from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta

import src.training_sessions.domain.models as model
from src.training_sessions.adapters.repository import AbstractRepository

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

def add_set(phone_number: str, set_data: dict, repo: AbstractRepository, session, ):
    for set_info in set_data:
        set = model.Set(**set_info)
    user = get_or_create_user(phone_number,repo,session)
    user, new_training_session = get_or_create_training_session(phone_number, repo, session)
    training_session_id = model.add_set(set, user.training_sessions)
    session.commit()

    return training_session_id