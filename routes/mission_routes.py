from database.mission_db import mission_db
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

class Mission(BaseModel):
    title: str
    description: str
    location: str
    difficulty: int
    importance: int

class MissionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    difficulty: int | None = None
    importance: int | None = None

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