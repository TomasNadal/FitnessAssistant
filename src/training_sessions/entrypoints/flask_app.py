from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.training_sessions.domain.sets_parser import InvalidTrainingData
import src.training_sessions.adapters.orm as orm
import src.training_sessions.adapters.repository as repository
import src.training_sessions.adapters.whatsapp_api as whastapp_api
import src.training_sessions.service_layer.services as services
import src.training_sessions.config as config

orm.start_mappers()
engine = create_engine(config.get_postgres_uri())
get_session = sessionmaker(bind = engine)
app = Flask(__name__)
api = whastapp_api.WhatsappClient(**config.get_whatsapp_api_details())




@app.route("/get_training_session", methods=["POST"])
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

    r = request.get_json()
    
    messages = r["entry"][0]["changes"][0]["value"].get("messages")
    print(messages)
    if messages:
        message = messages[0]
        print(f'This is the message {message}')
    else:
        return "OK", 201

    message_type = message["type"]

    if message_type == "document" or message_type == "audio" or message_type == "text":
        try:
            training_session_id = services.add_sets_from_raw(message, repo=repo, api=api, session=session)
        except InvalidTrainingData:
            return "NOT OK", 200



    
    return {"session_id": training_session_id}, 201



@app.route("/webhook", methods=["GET"])
def webhook_get():
    return api.verify()

@app.route("/webhook", methods=["POST"])
@api.signature_required
def webhook_post():

    return add_set()
