from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

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




class TrainingSession:
    def __init__(self, id: int, user: 'User', started_at: datetime):
        self.id = id
        self.user = user
        self.started_at = started_at
        self.sets = set()
        self.reference = f'{user.id}-{started_at}'
        self._status = 'In progress'
        self._modified_at = started_at
        
    def __eq__(self,other):
        if not isinstance(other, TrainingSession):
            return False
        
        return (self.id, self.user.id)  == (other.id, other.user.id)
    
    def __hash__(self):
        return hash(self.id, self.user.id)
    

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