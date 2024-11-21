import pytest
from src.training_sessions.adapters.transcriber import OpenAiTranscriber
import re

''' 

Will need to create a set of audios to test this against.

Problem is every test will cost money.

'''
    


def test_audio_transcriber_returns_expected_text(test_data_folder):
    test_audios = [(["2 repeticiones de press de banca con 100 kg", "Dos repeticiones de press de banca con 100 kg"],test_data_folder / "audio_test1.ogg"),
     (["5 repeticiones de press de banca con 5 kg", "Cinco repeticiones de press de banca con cinco kg"],test_data_folder / "audio_test2.ogg"),
     (["12 repeticiones de remo con barra con 40 kg", "Doce repeticiones de remo con barra con cuarenta kg"],test_data_folder / "audio_test3.ogg")]
    
    transcriber = OpenAiTranscriber()

    for audio in test_audios:
        transcript = transcriber.transcribe(audio[1], "mp3")

        # normalise and avoid punctuation
        transcript = re.sub(r'[^\w\s]', '', transcript.lower())
        expected_transcripts = [re.sub(r'[^\w\s]', '', text.lower()) for text in audio[0]]
        
        assert transcript in expected_transcripts