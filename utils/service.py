from database.agent_db import agent_db
from database.mission_db import mission_db
from fastapi import HTTPException

def get_agent(id: int) -> dict:
    agent = agent_db.get_agent_by_id(id)
    if not agent:
        raise HTTPException(404, f'Agent not found: {id}')
    return agent

def get_mission(id: int) -> dict:
    mission = mission_db.get_mission_by_id(id)
    if not mission:
        raise HTTPException(404, f'Mission not found: {id}')
    return mission

def handle_create_agent(data: dict):
    ranks = ['Junior', 'Senior', 'Commander']
    if data.get('agent_rank') not in ranks:
        raise HTTPException(400, 'Agent rank must be - Junior / Senior / Commander')
    return agent_db.create_agent(data)

def handle_create_mission(data: dict) -> int:
    mission = data.copy()
    diff = mission.get('difficulty')
    imp = mission.get('importance')
    if not (1 <= diff <= 10) or not (1 <= imp <= 10):
        raise HTTPException(400, 'difficulty and importance must be between 1 - 10')
    new_mission = mission_db.create_mission(mission)
    return new_mission['id']

def handle_assign_mission(m_id: int, a_id: int):
    mission = get_mission(m_id)
    agent = get_agent(a_id)
    
    if not mission:
        raise HTTPException(404, f'Mission not found: {m_id}')
    if not agent:
        raise HTTPException(404, f'Agent not found: {a_id}')
    
    if not mission.get('status') == 'NEW':
        raise HTTPException(400, f'Mission not available: {m_id}')
    if not agent.get('is_active'):
        raise HTTPException(400, f'Agent is not active: {a_id}')
    if len(mission_db.get_open_missions_by_agent(a_id)) >= 3:
        raise HTTPException(400, f'Agent has reached maximum missions: {a_id}')
    if mission.get('risk_level') == 'CRITICAL' and agent.get('agent_rank') != 'Commander':
        raise HTTPException(400, f'Only Commander can handle critical missions: {a_id}')
    
    return mission_db.assign_mission(m_id, a_id)