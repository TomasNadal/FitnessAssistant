from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
import logging

class NotActiveSessions(Exception):
    pass


class InvalidSeries(Exception):
    pass

class MissingSetInformation(Exception):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(f"Missing required fields: {', '.join(missing_fields)}")


@dataclass(unsafe_hash=True)
class Repetition:
    number: int
    kg: float
    distance: Optional[float] = None
    mean_velocity: Optional[float]= None
    peak_velocity: Optional[float]= None
    power: Optional[float]= None
    rir: Optional[int]= None
    _series: Optional[Series]= None

    def validate(self) -> None:
        missing_fields = []
        required_fields = ['number', 'kg']

        # Weird validation because of how openai API handles None values
        for field in required_fields:
            value = getattr(self, field)
            if (value is None or 
                (isinstance(value, str) and value == "") or
                (isinstance(value, (int, float)) and value == -1)):
                missing_fields.append(field)
            
        if missing_fields:
            raise MissingSetInformation(missing_fields)
        


class Series:
    def __init__(self, number: int):
        self.number = number
        self.repetitions = []
        self._exercise: Optional[Exercise] = None


    # Verify incremental Order
    def add_repetition(self, repetition: Repetition):
        
        last_rep_number = self.repetitions[-1].number if self.repetitions else 0

        if repetition.number == last_rep_number + 1:
            self.repetitions.append(repetition)
        else:
            raise InvalidSeries

    def __str__(self):
        return f'Serie: {self.number} : \n Reps: {max([repetition.number for repetition in self.repetitions])} \n Kg: {self.repetitions[0].kg}'
    
    

class Exercise:
    def __init__(self, name: str):
        self.name = name.lower()
        self.series = []
        self._training_session: Optional[TrainingSession] = None

    def add_series(self) -> Series:
        if self.series:
            last_series = self.series[-1]
            next_series_number = last_series.number + 1
            new_series = Series(number = next_series_number)

            self.series.append(new_series)
            return new_series
        
        else:
            new_series = Series(number = 1)
            self.series.append(new_series)
            return new_series

    def __eq__(self,other):
        if not isinstance(other, Exercise):
            return False
        else:
            return self.name.lower() == other.name.lower()
        
    def __hash__(self):
        return hash(self.name)

#Check this, maybe I should just store user_id, not the whole object
class TrainingSession:
    def __init__(self, started_at: datetime):
        self.id = str(uuid.uuid4())  
        self.started_at = started_at
        self.exercises = dict()
        self.status = 'In progress'
        self.modified_at = self.started_at
        self._user: Optional[User] = None

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
    
    def get_user(self):
        return self._user
    
    def _add_exercise(self, exercise: Exercise):        
        if not exercise.name in self.exercises:
            self.exercises[exercise.name] = exercise
        self.modified_at = datetime.now()

    def get_exercise(self, exercise_name: str) -> Exercise:
        if not exercise_name.lower() in self.exercises:
            self._add_exercise(Exercise(name=exercise_name))

        return self.exercises[exercise_name.lower()]
    
    def end(self):
        if self.status == 'Completed':
            pass
        
        self.status = 'Completed'
        self.modified_at = datetime.now()

    def __str__(self):
        return f'{self.id}-{self.started_at}-{self.modified_at}-{self.exercises}'



### Things I will need to query easily:
'''

- User by telephone
- Session by day
- Exercise by name
- Series by number


Functions I will need to define in models:

- user.get_training_session: gets or creates training session 
- user.add_series(exercise_name: ... , series(list_of_dicts))
    - I receive series info, no rep by rep. Makes sense to add the complete series
    - The add_series function manages creating a new series object.
    - It adds the repetitions
    - Returns the data added. 


'''


    
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
    

    # Adds the new training session and ends previous
    def add_training_session(self, training_session: TrainingSession) -> None:
        if len(self.training_sessions) > 0:
            self.training_sessions[-1].end()
            
        self.training_sessions.append(training_session)
    
    # Gets active session or creates new one
    def get_training_session(self) -> TrainingSession:
        try:
            latest_session = next(t for t in sorted(self.training_sessions, reverse=True) 
                                if t.is_active() and 
                                (datetime.now() - t.modified_at) < timedelta(hours=4))
            return latest_session
        except StopIteration:
            new_session = TrainingSession(started_at=datetime.now())
            self.add_training_session(new_session)
            return new_session    
    

    def add_series(self, exercise_name: str, repetitions: List[Repetition]) -> str:
        
        training_session = self.get_training_session()
        exercise = training_session.get_exercise(exercise_name=exercise_name)
        series = exercise.add_series()

        for rep in repetitions:
            series.add_repetition(rep)

        return series

        
        