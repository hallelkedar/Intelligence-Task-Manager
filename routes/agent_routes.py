from database.agent_db import agent_db
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

class Agent(BaseModel):
    name: str
    specialty: str
    agent_rank: Literal['Junior', 'Senior', 'Commander']

class UpdateAgent(BaseModel):
    name: str | None = None
    specialty: str | None = None
    agent_rank: Literal['Junior', 'Senior', 'Commander'] | None = None


router = APIRouter()


@router.post('')
def create_agent(data: Agent):
    agent = data.model_dump()
    return agent_db.create_agent(agent)

@router.get('')
def get_all_agents():
    return agent_db.get_all_agents()

@router.get('/{id}')
def get_agent(id: int):
    return agent_db.get_agent_by_id(id)

@router.put('/{id}')
def update_agent(id: int, data: UpdateAgent):
    update = data.model_dump(exclude_unset=True)
    return agent_db.update_agent(id, update)

@router.put('/{id}/deactivate')
def deactivate_agent(id: int):
    return agent_db.deactivate_agent(id)

@router.get('/{id}/performance')
def get_agent_performance(id: int):
    return agent_db.get_agent_performance(id)