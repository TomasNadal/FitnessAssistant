from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Set:
    exercise: str
    set: str
    repetition: str
    kg: float
    distance: float
    mean_velocity: float
    peak_velocity: float
    power: float




class TrainingSession:
    def __init__(self, user: str, timestamp: datetime):
        self.user = user
        self.timestamp = timestamp
        self.sets = []
        self.reference = f'{user}-{timestamp}'
        self._status = 'In progress'
        

    def is_active(self):
        return self._status == 'In progress'
    
    def add_set(self, set: Set):        
        self.sets.append(set)

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
        self.training_session = []
        self.name = name
        self.surname = surname
        self.email = email
        self.password_hash = password_hash
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.height = height
        self.weight = weight