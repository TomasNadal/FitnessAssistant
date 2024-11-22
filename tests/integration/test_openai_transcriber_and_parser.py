from src.training_sessions.adapters.transcriber import OpenAiTranscriber
from src.training_sessions.domain import sets_parser
from openai import OpenAI
import typing
from src.training_sessions.domain import models as model
import re


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

def test_audio_transcriber_returns_expected_text(test_data_folder):
    test_audios = [("2 repeticiones de press de banca con 100 kg primera serie",test_data_folder / "audio_test1.mp3"),
     ("segunda serie 5 repeticiones de sentadilla con 120 kg",test_data_folder / "audio_test2.mp3"),
     ("12 repeticiones tercera serie de remo con barra con 40 kg",test_data_folder / "audio_test3.mp3")]
    
    json_expected = [{'exercise': "press banca", 'series': 1, 'repetition': 2, 'kg': 100.0, 'rir': -1},
                {'exercise':'sentadilla', 'series': 2, 'repetition': 5, 'kg': 120.0, 'rir':-1},
                {'exercise':'remo barra', 'series': 3, 'repetition': 12, 'kg': 40, 'rir': -1}]
    
    
    
    transcriber = OpenAiTranscriber()

    openai_client = OpenAI()
    parser = sets_parser.TextParser(openai_client=openai_client)

    for i in range(len(test_audios)):
        transcript = transcriber.transcribe(test_audios[i][1], "mp3")
        sets_obtained = parser.parse(transcript)
        sets_expected = create_sets_from_json(json_expected[i])

        assert sets_obtained == sets_expected

        