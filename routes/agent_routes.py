from database.agent_db import agent_db
from database.base_db import BusinessValidationError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from logs.logger_config import logger
from utils import service

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
    agent = data.model_dump()
    new_agent = service.handle_create_agent(agent)
    created_msg = f'New agent created successfully. (id: {new_agent['id']})'
    logger.info(created_msg)
    return {'message': created_msg, 
            'data': new_agent
    }

@router.get('')
def get_all_agents():
    logger.info('Return all agents to user successfully.')
    return {'message': 'Return all agents',
            'data': agent_db.get_all_agents()
    }

@router.get('/{id}')
def get_agent(id: int):
    agent = service.get_agent(id)
    logger.info(f'Agent (id: {id} return to user succeffully.)')
    return {'message': f'Return agent (id: {id})',
            'data': agent
    }

@router.put('/{id}')
def update_agent(id: int, data: UpdateAgent):
    service.get_agent(id)

    data_dict = data.model_dump(exclude_unset=True)
    
    if not data_dict:
        raise HTTPException(422, 'Your body request is empty.')
    
    update_msg = agent_db.update_agent(id, data_dict)
    
    if not update_msg:
        raise HTTPException(500, 'Internal server error')
    logger.info(update_msg)
    return {'message': update_msg,
            'data': None
            }

@router.put('/{id}/deactivate')
def deactivate_agent(id: int):
    service.get_agent(id)
    update_msg = agent_db.deactivate_agent(id)
    logger.info(update_msg)
    
    return {'message': update_msg,
            'data': None
            }
    

@router.get('/{id}/performance')
def get_agent_performance(id: int):
    service.get_agent(id)
    update_msg = agent_db.get_agent_performance(id)
    logger.info(update_msg)
    
    return {'message': update_msg,
            'data': None
            }