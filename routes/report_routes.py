from fastapi import APIRouter
from database.agent_db import agent_db
from database.mission_db import mission_db
from typing import Literal

router = APIRouter()

@router.get('/summary')
def get_summery():
    return {
        'active_agents_count': agent_db.count_active_agents(),
        'total_missions': mission_db.count_all_missions(),
        'open_missions': mission_db.count_open_missions(),
        'completed_missions': mission_db.count_by_status(status='COMPLETED'),
        'failed_missions': mission_db.count_by_status(status='FAILED'),
        'critical_missions': mission_db.count_critical_missions()
    }

@router.get('/missions-by-status')
def get_mission_by_status(status: Literal['NEW', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED']):
    return {
        'open': mission_db.count_open_missions(),
        'in_progress': mission_db.count_by_status(status='IN_PROGRESS'),
        'completed': mission_db.count_by_status(status='COMPLETED'),
        'failed': mission_db.count_by_status(status='FAILED'),
        'critical': mission_db.count_critical_missions()
    }

@router.get('/top-agent')
def get_top_agent():
    return mission_db.get_top_agent()
