import abc
import typing
import pandas as pd
from pathlib import Path
from src.training_sessions.domain.models import Set
import re

class InvalidCSVFormat(Exception):
    pass

class AbstractTrainingDataParser(abc.ABC):
    
    @abc.abstractmethod
    def from_file_to_dataframe(self, file_path: Path) -> pd.DataFrame:
        pass
    
    @abc.abstractmethod
    def isvalid(self, raw_data: pd.DataFrame) -> bool:
        pass

    @abc.abstractmethod
    def parse_to_sets(self, raw_data: pd.DataFrame) -> typing.Set[typing.Set]:
        pass



class CSVParser(AbstractTrainingDataParser):
    def from_file_to_dataframe(self, file_path):
        try:
            training_dataframe = pd.read_csv(file_path)
            return training_dataframe
        except Exception:
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
            raise InvalidCSVFormat