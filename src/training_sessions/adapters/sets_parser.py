import abc
import typing
import pandas as pd
from pathlib import Path
from src.training_sessions.domain.models import Set
from src.training_sessions.domain.openai_schemas import TextParserResponse
import src.training_sessions.config as config
import json

import re
from openai import OpenAI

class InvalidMedia(Exception):
    pass

class MissingInformation(Exception):
    pass

class AbstractTrainingDataParser(abc.ABC):
    
    @abc.abstractmethod
    def from_raw_to_dataframe(self, file_path: typing.Optional[Path], text: typing.Optional[str]) -> pd.DataFrame:
        pass
    
    @abc.abstractmethod
    def isvalid(self, raw_data: pd.DataFrame | dict) -> bool:
        pass

    @abc.abstractmethod
    def parse_to_sets(self, raw_data: pd.DataFrame) -> typing.Set[typing.Set]:
        pass

    @abc.abstractmethod
    def parse_to_sets_from_raw(self, file_path: typing.Optional[Path], text: typing.Optional[str]) -> pd.DataFrame:
        pass


class CSVParser(AbstractTrainingDataParser):
    def from_raw_to_dataframe(self, file_path):
        
        try:
            training_dataframe = pd.read_csv(file_path)
            return training_dataframe
        except InvalidMedia:
            return None

    
    def isvalid(self, raw_data):    
        expected_columns = ["R","SERIE","KG","D","VM","VMP","RM","P(W)","Perfil","Ejer.","Atleta","Ecuacion"]

        obtained_columns = list(raw_data.columns)

        if not (expected_columns == obtained_columns):
            return False
        return True
    

    def parse_to_sets(self, raw_data):
        set_of_sets = set()
        
        if self.isvalid(raw_data):
            for index, row in raw_data.iterrows():
                # Sometimes the ADR encoder detects repetitions without actually being in a recording stage
                # in this cases since it is not recording a series the SERIE field is - 
                if row["SERIE"] != "-":
                    serie = int( re.search(r'S(\d+)', row['SERIE']).group(1) ) 
                    rep = int( re.search(r'R(\d+)', row['SERIE']).group(1) ) 
                    kg=float(row['KG'])
                    d=float(row['D'])
                    vm=float(row['VM'])
                    vmp=float(row['VMP'])
                    rm=float(row['RM'])
                    p_w=float(row['P(W)'])
                    ejercicio=row["Ejer."]

                    new_set = Set(exercise= ejercicio,
                                    series = serie,
                                    repetition= rep,
                                    kg = kg, 
                                    distance=d,
                                    mean_velocity=vm,
                                    peak_velocity=vmp,
                                    power=p_w)
                    
                    set_of_sets.add(new_set)

            return set_of_sets
        else:
            raise InvalidMedia
        
    def parse_to_sets_from_raw(self, file_path):
        
        raw_dataframe = self.from_raw_to_dataframe(file_path=file_path)
        set_of_sets = self.parse_to_sets(raw_dataframe)

        return set_of_sets
    

class TextParser:
    def __init__(self):
        self.client = OpenAI()
        self.config = config.get_text_parser_details()

    def from_text_to_json(self, text):
        completion = self.client.beta.chat.completions.parse(
            model = self.config["model"],
            messages = [
                {
                    "role": "system", 
                    "content": self.config["system_prompt"]
                },
                {
                    "role": "user", 
                    "content": text
                }
            ],
            response_format=self.config["schema"]

        )

        return json.loads(completion.choices[0].message.content)
        
        
    def isvalid(self, raw_data: dict) -> bool:
        expected_keys = [('exercise',""), ('series',-1), ('repetition',-1), ('kg',-1), ('rir',-1)]
        for key, value in expected_keys:
            if not key in raw_data:
                return False
            elif (raw_data[key] == value) and not (key == "rir"):
                return False
        return True


    def from_raw_to_dataframe(self, file_path: typing.Optional[Path], text: typing.Optional[str]) -> pd.DataFrame:
        pass

    
    def parse_to_sets(self, raw_data: pd.DataFrame) -> typing.Set[typing.Set]:
        pass

    
    def parse_to_sets_from_raw(self, file_path: typing.Optional[Path], text: typing.Optional[str]) -> pd.DataFrame:
        pass




        


