from database.mission_db import mission_db
from database.agent_db import agent_db
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.base_db import BusinessValidationError
from utils import service

router = APIRouter()

class Mission(BaseModel):
    title: str
    description: str
    location: str
    difficulty: int
    importance: int

@router.post('', status_code=201)
def create_mission(data: Mission):
    mission = data.model_dump()
    new_id = service.handle_create_mission(mission)
    return {'detail': f'Mission created successfully. (id: {new_id})'}

@router.get('')
def get_all_missions():
    return mission_db.get_all_missions()

@router.get('/{id}')
def get_mission(id: int):
    mission = service.get_mission(id)
    return mission

@router.put('/{id}/assign/{agent_id}')
def assign_mission(id: int, agent_id: int):
    assign_msg = service.handle_assign_mission(id, agent_id)
    return {'detail': assign_msg}

@router.put('/{id}/start')
def start_mission(id: int):
    mission = service.get_mission(id)

    if mission['status'] != 'ASSIGNED':
        raise HTTPException(400, 'You can only start mission that assigned to agent') # Rule no. 8
        
    update_msg = mission_db.update_mission_status(id, status='IN_PROGRESS')
    return {'detail': update_msg}

@router.put('/{id}/complete')
def mission_complete(id: int):
    mission = service.get_mission(id)

    if mission['status'] != 'IN_PROGRESS':
        raise HTTPException(400, 'You can only finish mission in progress')
    
    update_msg = mission_db.update_mission_status(id, status='COMPLETED')
    return {'detail': update_msg}

@router.put('/{id}/fail')
def mission_failed(id: int):
    mission = service.get_mission(id)
    
    if mission['status'] != 'IN_PROGRESS':
        raise HTTPException(400, 'You can only finish mission in progress')
    
    update_msg = mission_db.update_mission_status(id, status='FAILED')
    return {'detail': update_msg}

@router.put('/{id}/cancel')
def mission_canceled(id: int):
    mission = service.get_mission(id)
    
    if mission['status'] not in ['NEW', 'ASSIGNED']:
        raise HTTPException(400, 'You can only cancel mission that did not start')
    
    update_msg = mission_db.update_mission_status(id, status='CANCELLED')
    return {'detail': update_msg}