from __future__ import annotations
import abc
from src.training_sessions.adapters import repository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.training_sessions import config


class AbstractUnitOfWork(abc.ABC):
    user: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self
    
    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
    

DEFAULT_SESSION_FACTORY = sessionmaker(bind = create_engine(config.get_postgres_uri_prod()))


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self,session_factory = DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.user = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()
    
    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

