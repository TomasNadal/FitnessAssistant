import abc
import typing
import pandas as pd
from pathlib import Path
from src.training_sessions.domain.models import Set, MissingSetInformation
from src.training_sessions.domain.openai_schemas import TextParserResponse
import src.training_sessions.config as config
import json

import re


class InvalidCSV(Exception):
    pass


class InvalidTrainingData(Exception):
    def __init__(self, parsing_errors: list[str]):
        self.parsing_errors = parsing_errors
        super().__init__(f"Could not parse training data: {', '.join(parsing_errors)}")

class AbstractFileParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, file_path: Path) -> typing.Set[Set]:
        pass

class AbstractTextParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, text: str) -> typing.Set[Set]:
        pass



class CSVFileParser(AbstractFileParser):
    def parse(self, file_path):
        
        training_dataframe = pd.read_csv(file_path)
        expected_columns = ["R","SERIE","KG","D","VM","VMP","RM","P(W)","Perfil","Ejer.","Atleta","Ecuacion"]
        
        obtained_columns = list(training_dataframe.columns)
        if not (expected_columns == obtained_columns):
            raise InvalidCSV
        
        set_of_sets = set()
        for index, row in training_dataframe.iterrows():
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
                
                new_set.validate()
                set_of_sets.add(new_set)

        return set_of_sets


    

class TextParser(AbstractTextParser):
    def __init__(self, openai_client):
        self.client = openai_client
        self.config = config.get_text_parser_details()

    def extract_text_data(self, text: str) -> dict:
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
        response_json = json.loads(completion.choices[0].message.content)
        return response_json
    
    def parse(self, text: str) -> typing.Set[Set]:
        training_data_dict = self.extract_text_data(text)
        
        # Parser-level validation
        parsing_errors = []
        for field, default_value in [("exercise", ""), ("series", -1), ("repetition", -1), ("kg", -1)]:
            if training_data_dict[field] == default_value:
                parsing_errors.append(field)
        
        if parsing_errors:
            raise InvalidTrainingData(parsing_errors)
            
        # If we get here, try to create domain objects
        set_of_sets = set()
        try:
            new_sets = [
                Set(
                    exercise=training_data_dict["exercise"],
                    series=training_data_dict["series"],
                    repetition=i,
                    kg=training_data_dict["kg"],
                    rir=training_data_dict["rir"]
                ) for i in range(1, training_data_dict["repetition"] + 1)
            ]
            
            for training_set in new_sets:
                training_set.validate()  # This might raise MissingSetInformation
                set_of_sets.add(training_set)
                
        except MissingSetInformation as e:
            # Let domain exceptions bubble up
            raise
            
        return set_of_sets

        
        





        


