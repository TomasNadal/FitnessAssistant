import pytest
import re
import pandas as pd
from pathlib import Path
from src.training_sessions.adapters import repository
from src.training_sessions.adapters import whatsapp_api
from src.training_sessions.service_layer import services
import src.training_sessions.domain.models as model 
import src.training_sessions.config as config
import src.training_sessions.service_layer.unit_of_work as uow


class FakeRepository(repository.AbstractRepository):
    def __init__(self, users):
        self._users = set(users)

    def add(self, user):
        self._users.add(user)

    def get(self, phone_number):
        return next(u for u in self._users if u.phone_number == phone_number)
    
    def list(self):
        return list(self._users)
    


class FakeUnitOfWork(uow.AbstractUnitOfWork):
    def __init__(self):
        self.users = FakeRepository([])
        self.commited = False

    def commit(self):
        self.commited = True


    def rollback(self):
        pass

'''
Remember, in the service layer we are trying to implement the orchestration.
- Fetching objects from the domain model
- Validation
- We call a domain service
- If all is well, we save/update the state
'''

def split_df_in_series(df):
    # First split based on exercises:
    df_filtered = df[df['SERIE']!='-']
    list_of_exercises = [group for name, group in df_filtered.groupby(['Ejer.'])]
    list_of_exercises = sorted(list_of_exercises, key = lambda x: min(x['R']))

    # Now we split based on series
    series_list = []
    group_of_series = [[group for name, group in exercise_df.groupby(exercise_df['SERIE'].str.split().str[0])] for exercise_df in list_of_exercises]

    for series in group_of_series:
        series_list.extend(series)
        
    return  series_list


def from_adr_pandas_to_json(df: pd.DataFrame):
    
    list_of_series_dataframes = split_df_in_series(df)
    list_of_processed_series = []
    for serie in list_of_series_dataframes:
        serie_dict = {'exercise': serie['Ejer.'].iloc[0], 'repetitions':[]}
        for _, row in serie.iterrows():
            rep_dict = {}
            if row["SERIE"] != "-":
                rep_dict['number'] = int( re.search(r'R(\d+)', row['SERIE']).group(1) ) 
                rep_dict['kg']=float(row['KG'])
                rep_dict['distance']=float(row['D'])
                rep_dict['mean_velocity']=float(row['VM'])
                rep_dict['peak_velocity']=float(row['VMP'])
                rep_dict['power']=float(row['P(W)'])    
                serie_dict['repetitions'].append(rep_dict)
        serie_dict['repetitions'] = serie_dict['repetitions'][::-1]
        list_of_processed_series.append(serie_dict)
    
    return list_of_processed_series


'''

add_series is the function that once parsed the original data to a json, {exercise: str, repetitions: List[dict]}
will be in charge of adding the series to the user

need to check that:
- creates/gets the training_session correctly
- creates/gets the exercise correctly
- creates series + adds the reps

'''

def test_add_series_from_raw_csv(valid_csv_adrencoder_ejercicios_variados):
    uow = FakeUnitOfWork()
    phone_number = '3465849392'
    uow.users.add(model.User(phone_number=phone_number))

    series_df = pd.read_csv(valid_csv_adrencoder_ejercicios_variados)
    split_dfs = from_adr_pandas_to_json(series_df)
    expected_exercise_list = ["Sentadilla parada", "Peso muerto", "Media sentadilla", "Sentadilla a la paralela", "Sentadilla profunda", "Press militar", "Press de banca"]

    services.add_series(phone_number=phone_number, raw_series = split_dfs, uow = uow)

    
    user = uow.users.get(phone_number)
    training_session = user.training_sessions[0]

    for exercise in expected_exercise_list:
        assert exercise.lower() in training_session.exercises.keys()

        # Add some other checks of correct info added



def test_add_sets_from_raw_csv(document_message_part_2, valid_csv_adrencoder_ejercicios_variados):
    uow, api = FakeUnitOfWork(), whatsapp_api.WhatsappClient(**config.get_whatsapp_api_details())
    phone_number = '3465849392'
    series_df = pd.read_csv(valid_csv_adrencoder_ejercicios_variados)
    split_dfs = from_adr_pandas_to_json(series_df)

    expected_exercise_list = ["Sentadilla parada", "Peso muerto", "Media sentadilla", "Sentadilla a la paralela", "Sentadilla profunda", "Press militar", "Press de banca"]

    result = services.add_sets_from_raw(document_message_part_2, api, uow)

    user = uow.users.get(phone_number)
    training_session = user.training_sessions[0]

    for exercise in expected_exercise_list:
        assert exercise.lower() in training_session.exercises.keys()
    

   
    





