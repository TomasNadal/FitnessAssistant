from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, Float, DateTime
from sqlalchemy.orm import registry,  relationship, attribute_keyed_dict

import src.training_sessions.domain.models as model

# This mapping style is the classical ("imperative") way

'''
Metadata contains information of the database schema
'''
mapper_registry = registry()

user = Table('user',
              mapper_registry.metadata,
              Column('id', String(36), primary_key=True),
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
                         Column('id', String(36), primary_key=True),
                         Column('user_id', String(36), ForeignKey('user.id')),
                         Column('status', String),
                         Column('started_at',DateTime),
                         Column('modified_at',DateTime) 
                         )


exercises = Table('exercises',
                    mapper_registry.metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('session_id', String(36), ForeignKey('training_session.id')),  
                    Column('name', String(100))
                 )


series = Table('series',
               mapper_registry.metadata,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('exercise_id', Integer, ForeignKey('exercises.id')),
               Column('number', Integer)
               )



repetitions = Table('repetitions', 
             mapper_registry.metadata,
             Column("id", Integer, primary_key=True, autoincrement=True),
             Column('series_id', Integer, ForeignKey('series.id')),
             Column('number',Integer),
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
    

    repetitions_mapper = mapper_registry.map_imperatively(model.Repetition, repetitions)
    
    series_mapper = mapper_registry.map_imperatively(model.Series ,
            series,
            properties = {

                'repetitions' : relationship(repetitions_mapper, collection_class= list)

            })

    exercise_mapper = mapper_registry.map_imperatively(model.Exercise ,
            exercises,
            properties = {

                'series' : relationship(series_mapper, collection_class = list)

            })

    training_session_mapper = mapper_registry.map_imperatively(model.TrainingSession,
            training_session,
            properties = {
                'exercises' : relationship(exercise_mapper, collection_class=attribute_keyed_dict("name"),)
            }
            )
    
    mapper_registry.map_imperatively(model.User,
           user,
           properties = {
               'training_sessions' : relationship(training_session_mapper, collection_class=list)
           })
    


# .backref means each object should have an attribute pointing back to the parent. 