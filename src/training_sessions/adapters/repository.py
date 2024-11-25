import src.training_sessions.domain.models as model
import abc

# They mention in the book that they use Abstract class to 
# explain what the interface for the repository is, usually
# in production this ends up not-maintained and just
# rely on duck typing
class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, user: model.User):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, phone_number) -> model.User:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user):
        self.session.add(user)

    def get(self, phone_number):
        return self.session.query(model.User).filter_by(phone_number = phone_number).one()

    def list(self):
        return self.session.query(model.User).all()
