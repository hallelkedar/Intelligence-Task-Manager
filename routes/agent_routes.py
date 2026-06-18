from database.agent_db import agent_db
from database.base_db import BusinessValidationError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from logs.logger_config import logger

class Agent(BaseModel):
    name: str
    specialty: str
    agent_rank: str

class UpdateAgent(BaseModel):
    name: str | None = None
    specialty: str | None = None
    agent_rank: Literal['Junior', 'Senior', 'Commander'] | None = None


router = APIRouter()


@router.post('', status_code=201)
def create_agent(data: Agent):
    try:
        agent = data.model_dump()
        return agent_db.create_agent(agent)
    except BusinessValidationError:
        raise HTTPException(400, 'Agent rank must be - Junior / Senior / Commander')

@router.get('')
def get_all_agents():
    return agent_db.get_all_agents()

@router.get('/{id}')
def get_agent(id: int):
    if not agent_db.get_agent_by_id(id):
        raise HTTPException(404, f'Agent not found: {id}')
    return agent_db.get_agent_by_id(id)

@router.put('/{id}')
def update_agent(id: int, data: UpdateAgent):
    if not agent_db.get_agent_by_id(id):
        raise HTTPException(404, f'Agent not found: {id}')
    
    data_dict = data.model_dump(exclude_unset=True)
    if not data_dict:
        raise HTTPException(422, 'Your body request is empty.')
    updated = agent_db.update_agent(id, data_dict)
    if not updated:
        raise HTTPException(500, 'Internal server error')
    return {'detail': updated}

@router.put('/{id}/deactivate')
def deactivate_agent(id: int):
    if not agent_db.get_agent_by_id(id):
        raise HTTPException(404, f'Agent not found: {id}')
    return agent_db.deactivate_agent(id)

@router.get('/{id}/performance')
def get_agent_performance(id: int):
    if not agent_db.get_agent_by_id(id):
        raise HTTPException(404, f'Agent not found: {id}')
    
    return agent_db.get_agent_performance(id)