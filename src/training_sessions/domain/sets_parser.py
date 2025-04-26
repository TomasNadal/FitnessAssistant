import abc
import typing
import pandas as pd
from pathlib import Path
import src.training_sessions.utils.adrcsv_utils as utils
from src.training_sessions.domain.models import MissingSetInformation, Repetition
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
    def parse(self, file_path: Path) :
        pass

class AbstractTextParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, text: str):
        pass



class CSVFileParser(AbstractFileParser):
    def __init__(self, training_session_id):
        self.training_session_id = training_session_id
        self.tmp_path = config.get_tmp_folder() / f"{training_session_id}.csv"
        
        if not self.tmp_path.exists():
            # Create empty DataFrame with expected columns
            self.data = pd.DataFrame(columns=["R","SERIE","KG","D","VM","VMP","RM","P(W)","Perfil","Ejer.","Atleta","Ecuacion"])
            # Save empty DataFrame to create the file
            self.data.to_csv(self.tmp_path, index=False)
        else:
            # Load existing data if file exists
            try:
                self.data = pd.read_csv(self.tmp_path)
            except Exception as e:
                raise RuntimeError(f"Failed to load training session data: {e}")
        
        # Ensure parent directory exists
        self.tmp_path.parent.mkdir(parents=True, exist_ok=True)
    
    
    def parse(self, file_path):
        training_dataframe = pd.read_csv(file_path)
        expected_columns = ["R","SERIE","KG","D","VM","VMP","RM","P(W)","Perfil","Ejer.","Atleta","Ecuacion"]
        
        obtained_columns = list(training_dataframe.columns)
        if not (expected_columns == obtained_columns):
            raise InvalidCSV
        
        # Initialize self.data if it doesn't exist
        if not hasattr(self, 'data') or self.data.empty:
            self.data = pd.DataFrame(columns=expected_columns)
        
        # Find only the new rows (not in self.data)
        new_rows = pd.merge(training_dataframe, self.data, how='left', indicator=True)
        new_rows = new_rows[new_rows['_merge'] == 'left_only'].drop('_merge', axis=1)
        
        if not new_rows.empty:
            # Add new rows to processed data
            self.data = pd.concat([self.data, new_rows], ignore_index=True)
            # Save the updated data
            self.data.to_csv(self.tmp_path, index=False)
            
            # Process only the new rows using your utility functions
            processed_series = utils.from_adr_pandas_to_json(new_rows)
            
            return processed_series


    

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
    
    def parse(self, text: str) -> Repetition:
        extracted_data = self.extract_text_data(text)
        
        # Parser-level validation
        parsing_errors = []
        for field, default_value in [("exercise", ""), ("repetition", -1), ("kg", -1)]:
            if extracted_data[field] == default_value:
                parsing_errors.append(field)
        
        if parsing_errors:
            raise InvalidTrainingData(parsing_errors)
            
        # If we get here, try to create domain objects
        output = [{'exercise':extracted_data['exercise'], 'repetitions': [{'number': i, 'kg': extracted_data['kg'], 'rir': extracted_data['rir']} for i in range(1, extracted_data['repetition'] + 1)]}]
        
        
        return output




        


