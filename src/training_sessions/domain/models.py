from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
import logging

class NotActiveSessions(Exception):
    pass


def get_current_training_session(training_sessions: List[TrainingSession]) -> TrainingSession:
    try:
        latest_session = next(t for t in sorted(training_sessions, reverse=True) 
                            if t.is_active() and 
                            (datetime.now() - t.modified_at) < timedelta(hours=4))
        return latest_session
    except StopIteration:
        raise NotActiveSessions



def add_set(set: Set, training_sessions: List[TrainingSession]) -> int:
    try:
        training_session = next(t for t in sorted(training_sessions, reverse=True) if t.is_active())
        training_session.add_set(set) 

        return training_session.id
    except StopIteration:
        raise NotActiveSessions 



@dataclass(unsafe_hash=True)
class Set:
    exercise: str
    series: int
    repetition: int
    kg: float
    distance: Optional[float] = None
    mean_velocity: Optional[float]= None
    peak_velocity: Optional[float]= None
    power: Optional[float]= None
    rir: Optional[float]= None



#Check this, maybe I should just store user_id, not the whole object
class TrainingSession:
    def __init__(self, started_at: datetime):
        self.id = str(uuid.uuid4())  
        self.started_at = started_at
        self.sets = set()
        self.status = 'In progress'
        self.modified_at = self.started_at
        
    def __eq__(self,other):
        if not isinstance(other, TrainingSession):
            return False
        
        return ((self.id, self.started_at)  == (other.id, other.started_at))
    
    def __hash__(self):
        return hash(self.id, self.started_at)
    

    def __gt__(self, other):
        return self.started_at > other.started_at

    def is_active(self):
        return self.status == 'In progress'
    
    def add_set(self, set: Set):        
        self.sets.add(set)
        self.modified_at = datetime.now()

    def end(self):
        if self.status == 'Completed':
            raise ValueError('Session is completed')
        
        self.status = 'Completed'
        self.modified_at = datetime.now()

    def __str__(self):
        return f'{self.id}-{self.started_at}-{self.modified_at}-{self.sets}'

        
class User:
    def __init__(self,
    phone_number: str,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
    password_hash: Optional[str] = None,
    date_of_birth: Optional[datetime] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None
    ):
        self.id = str(uuid.uuid4())  
        self.phone_number = phone_number
        self.training_sessions = []
        self.name = name
        self.surname = surname
        self.email = email
        self.password_hash = password_hash
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.height = height
        self.weight = weight



    def __eq__(self, other):
        if not isinstance(other,User):
            return False
        return (other.id == self.id) and (other.phone_number == self.phone_number)
    
    def __hash__(self):
        return hash(self.id)
    
    # Temporally I will add here logic to end previous session
    def add_training_session(self, training_session: TrainingSession):
        if len(self.training_sessions) > 0:
            self.training_sessions[-1].end()
            
        self.training_sessions.append(training_session)