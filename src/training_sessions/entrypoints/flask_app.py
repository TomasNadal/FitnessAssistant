from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


import src.training_sessions.adapters.orm as orm
import src.training_sessions.adapters.repository as repository
import src.training_sessions.service_layer.services as services
import src.training_sessions.config as config

orm.start_mappers()
engine = create_engine(config.get_postgres_uri())
get_session = sessionmaker(bind = engine)
app = Flask(__name__)


@app.route("/new_training_session", methods=["POST"])
def add_training_session():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    r = request.json

    user,training_session = services.get_or_create_training_session(r["phone_number"], repo, session)


    return {"session_id":training_session.id}, 201

@app.route("/add_set", methods=["POST"])
def add_set():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    r = request.json

    training_session_id = services.add_set(phone_number=r["from"], set_data = r["set"], repo=repo, session=session)
    
    return {"session_id": training_session_id}, 201
