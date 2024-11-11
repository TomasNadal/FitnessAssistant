import typing
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
        
    def add_set(self, set: Set):
        self.sets.append(set)

    def is_active(self):
        return self._status == 'In progress'
    
    def end(self):
        if self._status == 'Completed':
            raise ValueError('Session is completed')
        
        self._status = 'Completed'
