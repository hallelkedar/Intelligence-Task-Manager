from database.agent_db import agent_db
from database.mission_db import mission_db
from fastapi import HTTPException

def get_agent(id: int) -> dict:
    agent = agent_db.get_agent_by_id(id)
    if not agent:
        raise HTTPException(404, detail={
            'detail': 'Agent not found',
            'detail_id': id,
        }
        )
    return agent

def get_mission(id: int) -> dict:
    mission = mission_db.get_mission_by_id(id)
    if not mission:
        raise HTTPException(404, detail={
            'detail': 'Mission not found',
            'detail_id': id,
        }
        )
    return mission

def handle_create_agent(data: dict):
    ranks = ['Junior', 'Senior', 'Commander']
    if data.get('agent_rank') not in ranks:
        raise HTTPException(400, 'Agent rank must be - Junior / Senior / Commander')
    return agent_db.create_agent(data)

def handle_create_mission(data: dict) -> dict:
    mission = data.copy()
    diff = mission.get('difficulty')
    imp = mission.get('importance')
    if not (1 <= diff <= 10) or not (1 <= imp <= 10):
        raise HTTPException(400, 'difficulty and importance must be between 1 - 10')
    new_mission = mission_db.create_mission(mission)
    return new_mission

def handle_assign_mission(m_id: int, a_id: int):
    mission = get_mission(m_id)
    agent = get_agent(a_id)
    
    if not mission.get('status') == 'NEW':
        raise HTTPException(404,
                             f'Mission not available: (id: {m_id}'
        )
    if not agent.get('is_active'):
        raise HTTPException(404,
                             f'Agent is not active: (id: {a_id}'
        )
    
    if len(mission_db.get_open_missions_by_agent(a_id)) >= 3:
        raise HTTPException(404,
                             f'Agent has reached maximum missions: (id: {a_id}'
        )
    if mission.get('risk_level') == 'CRITICAL' and agent.get('agent_rank') != 'Commander':
        raise HTTPException(404,
                             f'Only Commander can handle critical missions: (id: {a_id}'
        )

    return mission_db.assign_mission(m_id, a_id)