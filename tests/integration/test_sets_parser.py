import pytest
from src.training_sessions.domain import models as model
import pandas as pd
import re
from src.training_sessions.adapters import sets_parser

'''
Test_extract_sets_from_csv.
1. Read CSV + name is adrencoder
2. Check expected format (isvalid? i.e fixed column structure)
3. Read rows

This is another function:
    Map data to set object

'''

'''
Test from_raw_to_dataframe

'''
def test_from_raw_to_dataframe(valid_csv_adrencoder_path):
    parser = sets_parser.CSVParser()
    training_dataframe = parser.from_file_to_dataframe(valid_csv_adrencoder_path)
    
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


def map_invalid_dataframe_row_adr_to_set(invalid_csv_adrencoder_path):
    training_dataframe = pd.read_csv(invalid_csv_adrencoder_path)
    parser = sets_parser.CSVParser()

    with pytest.raises(sets_parser.InvalidCSVFormat):
        parser.parse_to_sets(invalid_csv_adrencoder_path)

