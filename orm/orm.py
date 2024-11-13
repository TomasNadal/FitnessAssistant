from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, Float, DateTime
from sqlalchemy.orm import registry,  relationship

import models.models as model

# This mapping style is the classical ("imperative") way

'''
Metadata contains information of the database schema
'''
mapper_registry = registry()

user = Table('user',
              mapper_registry.metadata,
              Column('id', Integer, primary_key=True, autoincrement = True),
              Column('phone_number', String(15)),
              Column('name', String(255), nullable=True),
              Column('surname', String(255), nullable=True),
              Column('email', String(255), nullable=True),
              Column('password_hash', String(255), nullable=True),
              Column('date_of_birth', Date, nullable=True),
              Column('gender', String(10), nullable=True),
              Column('height', Float, nullable=True),
              Column('weight', Float, nullable= True)
              )




training_session = Table('training_session',
                         mapper_registry.metadata,
                         Column('id', Integer, primary_key=True, autoincrement=True),
                         Column('user_id', Integer, ForeignKey('user.id')),
                         Column('reference', String),
                         Column('status', String),
                         Column('created_at',DateTime),
                         Column('modified_at',DateTime) 
                         )

sets = Table('sets', 
             mapper_registry.metadata,
             Column("id", Integer, primary_key=True, autoincrement=True),
             Column('session_id', Integer, ForeignKey('training_session.id')),
             Column('exercise', String(255)),
             Column('set', String(3)),
             Column('repetition',String(3)),
             Column('kg', Float),
             Column('distance', Float, nullable=True),
             Column('mean_velocity', Float, nullable=True),
             Column('peak_velocity', Float, nullable=True),
             Column('power', Float, nullable=True),
             Column('rir', Float, nullable = True)
             )


# Info about relationships goes in properties dict. The relationships refer to
# relationships defined in the domain class

def start_mappers():
    sets_mapper = mapper_registry.map_imperatively(model.Set, sets)

    training_session_mapper = mapper_registry.map_imperatively(model.TrainingSession,
            training_session,
            properties = {
                'sets' : relationship(sets_mapper, collection_class=set)
            }
            )
    
    mapper_registry.map_imperatively(model.User,
           user,
           properties = {
               'training_sessions' : relationship(training_session_mapper, backref='user')
           })
    


# .backref means each object should have an attribute pointing back to the parent. 