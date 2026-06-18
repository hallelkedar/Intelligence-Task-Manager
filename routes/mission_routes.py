from database.mission_db import mission_db
from database.agent_db import agent_db
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Mission(BaseModel):
    title: str
    description: str
    location: str
    difficulty: int
    importance: int

@router.post('')
def create_mission(data: Mission):
    mission = data.model_dump()
    return mission_db.create_mission(mission)

@router.get('')
def get_all_missions():
    return mission_db.get_all_missions()

@router.get('/{id}')
def get_mission(id: int):
    return mission_db.get_mission_by_id(id)

@router.put('/{id}/assign/{agent_id}')
def assign_mission(id: int, agent_id: int):
    
    mission = mission_db.get_mission_by_id(id)
    agent = agent_db.get_agent_by_id(id)
    
    if not mission:
        raise HTTPException(404, 'Mission not found')
    if not agent:
        raise HTTPException(404, 'Agent not found')
    if not mission.get('status') == 'NEW':
        raise HTTPException(400, 'Mission not available')
    if not agent.get('is_active'):
        raise HTTPException(400, 'Agent is not active')
    if len(mission_db.get_open_missions_by_agent(agent_id)) >= 3:
        raise HTTPException(400, 'Agent has reached maximum missions')
    if mission.get('risk_level') == 'CRITICAL' and agent.get('agent_rank') != 'Commander':
        raise HTTPException(400, 'Only Commander can handle critical missions')
    
    return mission_db.assign_mission(id, agent_id)

@router.put('/{id}/start')
def start_mission(id: int):
    return mission_db.update_mission_status(id, status='IN_PROGRESS')

@router.put('/{id}/complete')
def mission_complete(id: int):
    return mission_db.update_mission_status(id, status='COMPLETED')

@router.put('/{id}/fail')
def mission_failed(id: int):
    return mission_db.update_mission_status(id, status='FAILED')

@router.put('/{id}/cancel')
def mission_canceled(id: int):
    return mission_db.update_mission_status(id, status='CANCELLED')