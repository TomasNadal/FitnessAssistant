import models.models as model
import abc

# They mention in the book that they use Abstract class to 
# explain what the interface for the repository is, usually
# in production this ends up not-maintained and just
# rely on duck typing
class UserAbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user: model.User):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id) -> model.User:
        raise NotImplementedError
    
class TrainingSessionAbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, training_session: model.TrainingSession):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, user_id: int) -> model.TrainingSession:
        raise NotImplementedError



class UserSqlAlchemyRepository(UserAbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user):
        self.session.add(user)

    def get(self, id):
        self.session.query(model.User).filter_by(id = id).one()

    def list(self):
        self.session.query(model.User).all()

class TrainingSessionSqlAlchemyRepository(TrainingSessionAbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, training_session):
        self.session.add(training_session)

    def get(self, user_id):
        self.session.query(model.TrainingSession).filter_by(user_id = user_id)