from fastapi import FastAPI, Request, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

from src.training_sessions.domain.sets_parser import InvalidTrainingData
import src.training_sessions.adapters.orm as orm
import src.training_sessions.adapters.repository as repository
import src.training_sessions.adapters.whatsapp_api as whastapp_api
import src.training_sessions.service_layer.services as services
import src.training_sessions.config as config
import src.training_sessions.service_layer.unit_of_work as unit_of_work

# Initialize database
orm.start_mappers()
engine = create_engine(config.get_postgres_uri())
orm.mapper_registry.metadata.create_all(engine)
get_session = sessionmaker(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Fitness Assistant API")
api = whastapp_api.WhatsappClient(**config.get_whatsapp_api_details())

# Define request model
class TrainingSessionRequest(BaseModel):
    phone_number: str

@app.post("/get_training_session", status_code=201)
async def add_training_session(request: TrainingSessionRequest):
    try:
        training_session = services.get_or_create_user(
            request.phone_number, 
            unit_of_work.SqlAlchemyUnitOfWork(get_session)
        )
        return {"session_id": training_session.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 