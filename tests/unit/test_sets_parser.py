import pytest
from src.training_sessions.domain import models as model
import pandas as pd
import re
from src.training_sessions.adapters import sets_parser
from src.training_sessions.adapters import transcriber
from src.training_sessions.domain import openai_schemas

'''
Test from_raw_to_dataframe

'''
def test_from_raw_to_dataframe(valid_csv_adrencoder_path):
    parser = sets_parser.CSVParser()
    training_dataframe = parser.from_raw_to_dataframe(valid_csv_adrencoder_path)
    
    assert isinstance(training_dataframe, pd.DataFrame)
    


'''
Test csv isvalid()
'''

def test_isvalid_adrcsv_returns_true(valid_csv_adrencoder_path):
    training_dataframe = pd.read_csv(valid_csv_adrencoder_path)
    parser = sets_parser.CSVParser()

    assert True == parser.isvalid(training_dataframe)

def test_not_valid_adrcsv_returns_false(invalid_csv_adrencoder_path):
    training_dataframe = pd.read_csv(invalid_csv_adrencoder_path)
    parser = sets_parser.CSVParser()

    assert parser.isvalid(training_dataframe) == False
        


'''
Test mapping correctly
'''
def test_map_dataframe_row_adr_to_set(valid_csv_adrencoder_path):
    training_dataframe = pd.read_csv(valid_csv_adrencoder_path)
    parser = sets_parser.CSVParser()

    list_of_sets_expected = set()
    list_of_sets_obtained = set()

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

    obtained_set = parser.parse_to_sets(training_dataframe)


    assert list_of_sets_expected == obtained_set


def test_map_invalid_dataframe_row_adr_to_set(invalid_csv_adrencoder_path):
    training_dataframe = pd.read_csv(invalid_csv_adrencoder_path)
    parser = sets_parser.CSVParser()

    with pytest.raises(sets_parser.InvalidMedia):
        parser.parse_to_sets(training_dataframe)



''' Now we test the audio to set parser 

    Need to create Fake Transcriber to test against

    We need extra step when using OpenAI transcription. 

    We will need to define function to get from 

'''
def test_from_text_to_json_valid_data():
   parser = sets_parser.TextParser()
   input_text = ["primera serie 2 repeticiones de press de banca con 100 kg al fallo",
    "5 repeticiones de prensa horizontal con 5 kg a dos del fallo es mi tercera serie",
    "12 repeticiones segunda serie de peso muerto rumano con 40 kg a tres del fallo"]

   json_expected = [{'exercise':'press banca', 'series': 1, 'repetition': 2, 'kg': 100.0, 'rir': 0},
                    {'exercise':'prensa horizontal', 'series': 3, 'repetition': 5, 'kg': 5.0, 'rir':2},
                    {'exercise':'peso muerto rumano', 'series': 2, 'repetition': 12, 'kg': 40.0, 'rir': 3}]
   
   for i in range(len(input_text)):
       response = parser.from_text_to_json(input_text[i])
       expected = json_expected[i]
       
       assert response == expected


def test_from_text_to_json_valid_incomplete_data():
   parser = sets_parser.TextParser()
   input_text = ["quinta serie cinco repeticiones con 244 kg al fallo",
    "curl de biceps con 5 kg a cuatro del fallo es mi tercera serie",
    "veinte repeticiones de dominadas con 0 kg a una del fallo"]

   json_expected = [{'exercise': "", 'series': 5, 'repetition': 5, 'kg': 244.0, 'rir': 0},
                    {'exercise':'curl biceps', 'series': 3, 'repetition': -1, 'kg': 5.0, 'rir':4},
                    {'exercise':'dominadas', 'series': -1, 'repetition': 20, 'kg': 0.0, 'rir': 1}]
   
   for i in range(len(input_text)):
       response = parser.from_text_to_json(input_text[i])
       expected = json_expected[i]
       
       assert response == expected
    

# Cambiar esto para que sean distintos
def test_is_valid_with_valid_data():
    parser = sets_parser.TextParser()
    input_text = ["prensa quinta serie cinco repeticiones con 244 kg al fallo",
    "curl biceps con 5 kg tres repeticiones a cuatro del fallo es mi tercera serie",
    "primera serie veinte repeticiones de dominadas con 0 kg a una del fallo"]

    json_expected = [{'exercise': "prensa", 'series': 5, 'repetition': 5, 'kg': 244.0, 'rir': 0},
                    {'exercise':'curl biceps', 'series': 3, 'repetition': 3, 'kg': 5.0, 'rir':4},
                    {'exercise':'dominadas', 'series': 1, 'repetition': 20, 'kg': 0.0, 'rir': 1}]
    
    for i in range(len(input_text)):
        response = parser.from_text_to_json(input_text[i])
        expected = json_expected[i]
        
        assert response == expected
        assert parser.isvalid(response) == True


# Cambiar esto para que sean distintos
def test_is_valid_returns_true_with_valid_data_no_rir():
    parser = sets_parser.TextParser()
    input_text = ["quinta serie cinco repeticiones con 244 kg",
    "curl de biceps con 5 kg es mi tercera serie",
    "veinte repeticiones de dominadas con 0 kg"]

    json_expected = [{'exercise': "", 'series': 5, 'repetition': 5, 'kg': 244.0, 'rir': -1},
                    {'exercise':'curl biceps', 'series': 3, 'repetition': -1, 'kg': 5.0, 'rir':-1},
                    {'exercise':'dominadas', 'series': -1, 'repetition': 20, 'kg': 0.0, 'rir': -1}]
    
    for i in range(len(input_text)):
        response = parser.from_text_to_json(input_text[i])
        expected = json_expected[i]
        
        assert response == expected
        assert parser.isvalid(response) == True

# Cambiar tambien
def test_is_valid_returns_false_with_incomplete_data():
    parser = sets_parser.TextParser()
    input_text = ["quinta serie cinco repeticiones con 244 kg al fallo",
    "curl de biceps con 5 kg a cuatro del fallo es mi tercera serie",
    "veinte repeticiones de dominadas con 0 kg a una del fallo"]

    json_expected = [{'exercise': "", 'series': 5, 'repetition': 5, 'kg': 244.0, 'rir': 0},
                    {'exercise':'curl biceps', 'series': 3, 'repetition': -1, 'kg': 5.0, 'rir':4},
                    {'exercise':'dominadas', 'series': -1, 'repetition': 20, 'kg': 0.0, 'rir': 1}]
    
    for i in range(len(input_text)):
        response = parser.from_text_to_json(input_text[i])
        expected = json_expected[i]
        
        assert response == expected
        assert parser.isvalid(response) == False


def test_from_json_to_dataframe_complete_data():

    json_input = [{'exercise':'press banca', 'series': 1, 'repetition': 2, 'kg': 100.0, 'rir': 0},
                        {'exercise':'prensa horizontal', 'series': 3, 'repetition': 5, 'kg': 5.0, 'rir':2},
                        {'exercise':'peso muerto rumano', 'series': 2, 'repetition': 12, 'kg': 40.0, 'rir': 3}]
    

    dfs = []
    for exercise in json_input:
        df = pd.DataFrame([{
            'exercise': exercise['exercise'],
            'series': exercise['series'],
            'kg': exercise['kg'],
            'rir': exercise['rir']
        } for _ in range(exercise['repetition'])])
        dfs.append(df)
    

    parser = sets_parser.TextParser()

    for i in range(len(json_input)):
        response = parser.from_raw_to_dataframe(json_input[i])
        expected = dfs[i]

        
        assert parser.isvalid(response) == expected

'''
def  test_from_json_to_dataframe_complete_data_no_rir():
'''


# Unrelated audio gives error
def test_from_invalid_raw_audio_text_to_dataframe():
    input_file = ("Me gusta comer lechugas","audio_path_lechuga.mp3")

    parser = sets_parser.TextParser()

    with pytest.raises(sets_parser.InvalidMedia):
        training_dataframe = parser.from_raw_to_dataframe(input_file[1])

# Missing key information 
def test_valid_raw_audio_missing_information():

    input_files = [("segunda serie 2 repeticiones de press de banca","audio_path1.mp3","kg"),
     ("primera serie press de banca con 5 kg","audio_path2.mp3", "repetition"),
     ("cuarta serie 12 repeticiones con 40 kg","audio_path1.mp3", "exercise"),
     ("10 repeticiones con 40 kg prensa horizontal", "audio_path4.mp3", "series")]
    
    parser = sets_parser.AudioParser(transcriber)

    for input_file in input_files:
        with pytest.raises(sets_parser.MissingInformation) as exc_info:
            training_dataframe = parser.from_raw_to_dataframe(input_file[1])
            assert False == training_dataframe.isvalid()
            
        assert str(exc_info.value)
    

# Correctly parses to sets
def test_from_raw_audio_text_to_sets():

    input_files = [("segunda serie 2 repeticiones de press de banca con 100 kg","audio_path1.mp3",[model.Set(exercise= "Press de banca", series=2, repetition=i, kg = 100) for i in range(1,3)]),
     ("primera serie 5 repeticiones de sentadilla con 5 kg","audio_path2.mp3", [model.Set(exercise= "Sentadilla", series=1, repetition=i, kg = 5) for i in range(1,6)]),
     ("tercera serie 8 repeticiones de banco tumbado con 40 kg","audio_path1.mp3",[model.Set(exercise= "Banco tumbado", series=3, repetition=i, kg = 100) for i in range(1,9)])]
    




        
