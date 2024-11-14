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


class SqlAlchemyRepository(UserAbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, user):
        self.session.add(user)

    def get(self, id):
        self.session.query(model.User).filter_by(id = id).one()

    def list(self):
        self.session.query(model.User).all()
