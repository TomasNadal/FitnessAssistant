import pytest
from src.training_sessions.domain import models as model
import pandas as pd
import typing
import re
from src.training_sessions.domain import sets_parser
from src.training_sessions.adapters import transcriber
from src.training_sessions.domain import openai_schemas
from openai import OpenAI


'''
Test mapping correctly
'''
def test_map_dataframe_row_adr_to_set(valid_csv_adrencoder_path):
    training_dataframe = pd.read_csv(valid_csv_adrencoder_path)
    parser = sets_parser.CSVFileParser()

    list_of_sets_expected = set()

    for index, row in training_dataframe.iterrows():
        if row["SERIE"] != "-":
            serie = int( re.search(r'S(\d+)',row['SERIE']).group(1) ) 
            rep = int( re.search(r'R(\d+)',row['SERIE']).group(1) ) 
            kg=float(row['KG'])
            d=float(row['D'])
            vm=float(row['VM'])
            vmp=float(row['VMP'])
            rm=float(row['RM'])
            p_w=float(row['P(W)'])
            ejercicio=row["Ejer."]

            expected_set = model.Set(exercise= ejercicio,
                                    series = serie,
                                    repetition= rep,
                                    kg = kg, 
                                    distance=d,
                                    mean_velocity=vm,
                                    peak_velocity=vmp,
                                    power=p_w)
        
        list_of_sets_expected.add(expected_set)

    obtained_set = parser.parse(valid_csv_adrencoder_path)


    assert list_of_sets_expected == obtained_set


def test_map_invalid_dataframe_row_adr_to_set(invalid_csv_adrencoder_path):
    parser = sets_parser.CSVFileParser()

    with pytest.raises(sets_parser.InvalidCSV):
        parser.parse(invalid_csv_adrencoder_path)



''' 

    We will need to define function to get from 

'''


def create_sets_from_json(training_json: dict) -> typing.Set[model.Set]:
    set_of_training_sets = set()

    for i in range(1,training_json["repetition"]+1):
        new_set = model.Set(
                    exercise=training_json["exercise"],
                    series=training_json["series"],
                    repetition=i,
                    kg=training_json["kg"],
                    rir=training_json["rir"])
        set_of_training_sets.add(new_set)

    return set_of_training_sets

def test_extract_text_data_valid_data():
   openai_client = OpenAI()
   parser = sets_parser.TextParser(openai_client)
   input_text = ["primera serie 2 repeticiones de press de banca con 100 kg al fallo",
    "5 repeticiones de prensa horizontal con 5 kg a dos del fallo es mi tercera serie",
    "12 repeticiones segunda serie de peso muerto rumano con 40 kg a tres del fallo"]

   json_expected = [{'exercise':'press banca', 'series': 1, 'repetition': 2, 'kg': 100.0, 'rir': 0},
                    {'exercise':'prensa horizontal', 'series': 3, 'repetition': 5, 'kg': 5.0, 'rir':2},
                    {'exercise':'peso muerto rumano', 'series': 2, 'repetition': 12, 'kg': 40.0, 'rir': 3}]
   
   for i in range(len(input_text)):
       response = parser.extract_text_data(input_text[i])
       expected = json_expected[i]
       
       assert response == expected


def test_extract_text_data_handles_missing_fields():
   openai_client = OpenAI()
   parser = sets_parser.TextParser(openai_client)
   input_text = ["quinta serie cinco repeticiones con 244 kg al fallo",
    "curl de biceps con 5 kg a cuatro del fallo es mi tercera serie",
    "veinte repeticiones de dominadas con 0 kg a una del fallo"]

   json_expected = [{'exercise': "", 'series': 5, 'repetition': 5, 'kg': 244.0, 'rir': 0},
                    {'exercise':'curl biceps', 'series': 3, 'repetition': -1, 'kg': 5.0, 'rir':4},
                    {'exercise':'dominadas', 'series': -1, 'repetition': 20, 'kg': 0.0, 'rir': 1}]
   
   for i in range(len(input_text)):
       response = parser.extract_text_data(input_text[i])
       expected = json_expected[i]
       
       assert response == expected
    

# Cambiar esto para que sean distintos
def test_is_valid_with_valid_data():
    openai_client = OpenAI()
    parser = sets_parser.TextParser(openai_client)
    input_text = ["prensa quinta serie cinco repeticiones con 244 kg al fallo",
    "curl biceps con 5 kg tres repeticiones a cuatro del fallo es mi tercera serie",
    "primera serie veinte repeticiones de dominadas con 0 kg a una del fallo"]

    json_expected = [{'exercise': "prensa", 'series': 5, 'repetition': 5, 'kg': 244.0, 'rir': 0},
                    {'exercise':'curl biceps', 'series': 3, 'repetition': 3, 'kg': 5.0, 'rir':4},
                    {'exercise':'dominadas', 'series': 1, 'repetition': 20, 'kg': 0.0, 'rir': 1}]
    
    for i in range(len(input_text)):
        sets_obtained = parser.parse(input_text[i])
        sets_expected = create_sets_from_json(json_expected[i])
        
        
        assert sets_obtained == sets_expected


# Cambiar esto para que sean distintos
def test_missing_rir_creates_valid_set():
    openai_client = OpenAI()
    parser = sets_parser.TextParser(openai_client)
    input_text = ["elevacion lateral con mancuerna sexta serie ocho repeticiones con 10 kg",
    "tercera serie de curl predicador con 5 kg 12 repeticiones",
    "veinte repeticiones de face pull con 12 kg primera serie"]

    json_expected = [{'exercise': "elevacion lateral mancuernas", 'series': 6, 'repetition': 8, 'kg': 10.0, 'rir': -1},
                    {'exercise':'curl predicador', 'series': 3, 'repetition': 12, 'kg': 5.0, 'rir':-1},
                    {'exercise':'face pull', 'series': 1, 'repetition': 20, 'kg': 12, 'rir': -1}]
    
    for i in range(len(input_text)):
        sets_obtained = parser.parse(input_text[i])
        sets_expected = create_sets_from_json(json_expected[i])
        
        assert sets_obtained == sets_expected

# Cambiar tambien
def test_incomplete_data_raises_InvalidTrainingData_exception():
    openai_client = OpenAI()
    parser = sets_parser.TextParser(openai_client)
    input_text = ["quinta serie cinco repeticiones con 244 kg al fallo",
    "curl de biceps con 5 kg a cuatro del fallo es mi tercera serie",
    "veinte repeticiones de dominadas con 0 kg a una del fallo"]

    json_expected = [{'exercise': "", 'series': 5, 'repetition': 5, 'kg': 244.0, 'rir': 0},
                    {'exercise':'curl biceps', 'series': 3, 'repetition': -1, 'kg': 5.0, 'rir':4},
                    {'exercise':'dominadas', 'series': -1, 'repetition': 20, 'kg': 0.0, 'rir': 1}]
    
    for i in range(len(input_text)):
        with pytest.raises(sets_parser.InvalidTrainingData):
            parser.parse(input_text[i])


        
