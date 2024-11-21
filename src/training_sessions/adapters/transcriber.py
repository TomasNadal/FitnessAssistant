from openai import OpenAI
from abc import ABC, abstractmethod
from pathlib import Path
from pydub import AudioSegment

class AbstractTranscriber(ABC): 
    @abstractmethod
    def transcribe(self, audio_path: Path, desired_file_extension: str) -> str:
        pass


class FakeTranscriber:
    def __init__(self, transcriptions_dict: dict):
        self.transcriptions_dict = transcriptions_dict

    def transcribe(self, audio_path, desired_file_extension):
        return self.transcriptions_dict.get(audio_path)




class OpenAiTranscriber:
    def __init__(self):
        self.client = OpenAI()


    def transcribe(self, audio_path, desired_file_extension):
        
        # Convert to desired_file_extension just in case
        if not audio_path.suffix == desired_file_extension:
            sound = AudioSegment.from_file(audio_path)
            audio_path = audio_path.with_suffix('.mp3')
            sound.export(audio_path, format="mp3")
        
        audio_file= open(audio_path, "rb")

        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            prompt = "Transcribe usando siempre números (1,2,3) para cantidades, nunca palabras numéricas. Usa 'kg' para kilogramos. Ejemplo: '5 repeticiones con 60 kg'. Algunas palabras comunes son Press, Curl, Squat (Por ejemplo en Press de banca). " 
            
            )
        return transcription.text

