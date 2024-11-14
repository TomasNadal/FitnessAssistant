from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


class NotActiveSessions(Exception):
    pass



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
    def __init__(self, id: int, user_id: int, started_at: datetime):
        self.id = id
        self.user_id = user_id
        self.started_at = started_at
        self.sets = set()
        self.reference = f'{user_id}-{started_at}'
        self._status = 'In progress'
        self._modified_at = started_at
        
    def __eq__(self,other):
        if not isinstance(other, TrainingSession):
            return False
        
        return (self.id, self.user_id)  == (other.id, other.user_id)
    
    def __hash__(self):
        return hash(self.id, self.user_id)
    

    def __gt__(self, other):
        return self.started_at > other.started_at

    def is_active(self):
        return self._status == 'In progress'
    
    def add_set(self, set: Set):        
        self.sets.add(set)

    def end(self):
        if self._status == 'Completed':
            raise ValueError('Session is completed')
        
        self._status = 'Completed'


        
class User:
    def __init__(self,
    id: int,
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
        self.id = id
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
        return other.id == self.id
    
    def __hash__(self):
        return hash(self.id)