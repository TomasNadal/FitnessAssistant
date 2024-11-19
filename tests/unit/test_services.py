import pytest
import pandas
from pathlib import Path
from src.training_sessions.adapters import repository
from src.training_sessions.adapters import whatsapp_api
from src.training_sessions.service_layer import services
import src.training_sessions.domain.models as model 
import src.training_sessions.config as config


class FakeRepository(repository.AbstractRepository):
    def __init__(self, users):
        self._users = set(users)

    def add(self, user):
        self._users.add(user)

    def get(self, phone_number):
        return next(u for u in self._users if u.phone_number == phone_number)
    
    def list(self):
        return list(self._users)
    

class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


'''
Remember, in the service layer we are trying to implement the orchestration.
- Fetching objects from the domain model
- Validation
- We call a domain service
- If all is well, we save/update the state
'''


def test_get_or_create_user_creates_new_user():
    repo, session = FakeRepository([]), FakeSession()
    user = services.get_or_create_user('+34646383712',repo,session)
    
    assert repo.get('+34646383712') is not None
    assert isinstance(user, model.User)
    assert session.committed

def test_add_or_create_training_session_adds_when_no_sessions():
    repo, session = FakeRepository([]), FakeSession()
    services.get_or_create_training_session('+34646383712',repo,session)
    user = repo.get('+34646383712')

    assert user.training_sessions is not None
    assert next(iter(user.training_sessions)).status == "In progress"
    assert session.committed
    
def test_add_or_create_training_session_uses_existing_session():
    repo, session = FakeRepository([]), FakeSession()
    user,training_session = services.get_or_create_training_session('+34646383712',repo,session)
    
    last_training_session = sorted(user.training_sessions)[0]
    
    assert isinstance(last_training_session, model.TrainingSession)
    services.get_or_create_training_session('+34646383712',repo,session)
    
    newer_training_session = sorted(user.training_sessions)[0]
    assert last_training_session == newer_training_session

def test_add_set(sample_json_payload):
    repo, session = FakeRepository([]), FakeSession()

    services.get_or_create_training_session('+34646383712', repo, session)
    result = services.add_sets(sample_json_payload['from'], sample_json_payload['set'], repo, session)
    assert next(iter(repo.get(sample_json_payload['from']).training_sessions)).id == result


# From raw_csv, should accept fi
def test_add_sets_from_raw(document_message_part):
    repo, session, api = FakeRepository([]), FakeSession(), whatsapp_api.WhatsappClient(**config.get_whatsapp_api_details())

    result = services.add_sets_from_raw(document_message_part, repo, api, session)
    assert next(iter(repo.get(document_message_part['from']).training_sessions)).id == result


'''
Should this functionality go in domain or service? Probs service
since we need to check against commited sets, then decide and then commit (or not commit)
5. See if the sets are already in training session
6. If not, add them. If yes, pass

'''

