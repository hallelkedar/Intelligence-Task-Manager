from database.base_db import BaseRepo
from database.agent_db import agent_db

class MissionDB(BaseRepo):
    def __init__(self):
        super().__init__(table_name='missions')

    def calculate_risk_level(self, diff: int, imp: int) -> str:
        score = diff * 2 + imp
        if score < 10:
            return 'LOW'
        elif score < 18: 
            return 'MEDIUM'
        elif score < 25:
            return 'HIGH'
        else: return 'CRITICAL'

    def create_mission(self, data: dict) -> dict:
        
        mission = data.copy()
        diff = mission.get('difficulty')
        imp = mission.get('importance')
        if not (1 < diff < 10) or not (1 < imp < 10):
            raise ValueError('difficulty and importance must be between 1 - 10') # Rule no. 2
        
        mission['risk_level'] = self.calculate_risk_level(diff, imp) # Rule no. 3
        new_id = super().create(mission)
        return self.get_mission_by_id(new_id)
    
    def get_all_missions(self):
        return super().get_all()

    def get_mission_by_id(self, id: int):
        return super().get_by_id(id)

    def assign_mission(self, m_id: int, a_id: int) -> str:
        agent = agent_db.get_agent_by_id(a_id)
        
        if not agent.get('is_active'):
            raise ValueError('Agent not active') # Rule no. 4
        
        if len(self.get_open_missions_by_agent(a_id)) > 3:
            raise ValueError('You can assign more than 3 mission to an agent.') # Rule no. 5
        
        mission = self.get_mission_by_id(m_id)
        if not mission.get('status') == 'NEW':
            raise ValueError('You can only assign new missions') # Rule no. 7
        if mission.get('risk_level') == 'CRITICAL' and agent.get('agent_rank') != 'Commander':
            raise ValueError('You can give critical risk level mission only to commander') # Rule no. 6
        
        updated = super().update(
            m_id,
            {'assigned_agent_id': a_id}
            )
        if not updated:
            return f'Mission ({m_id}) assign failed. (agent id: {a_id})'
        return f'Mission ({m_id}) (agent id: {a_id}) successfully assign.'
        

    def update_mission_status(self, id: int, status: str) -> str:
        mission = self.get_mission_by_id(id)
        old_status = mission.get('status')

        if status == 'IN_PROGRESS' and old_status != 'ASSIGNED':
            raise ValueError('You can only start mission that assigned to agent') # Rule no. 8
        
        if status == 'CANCELLED' and old_status not in ['NEW', 'ASSIGNED']:
            raise ValueError('You can only cancel mission that did not start') # Rule no. 10
        
        if old_status == 'IN_PROGRESS':
            if status not in ['COMPLETED', 'FAILED']:
                raise ValueError('You can only finish mission in progress') # Rule no. 9
            else:
                if status == 'COMPLETED':
                    increment = agent_db.increment_completed(mission.get('assigned_agent_id'))
                else:
                    increment = agent_db.increment_failed(mission.get('assigned_agent_id'))
        
        updated = super().update(
            id,
            {'status': status}
            )
        if not updated:
            return f'Mission status ({id}-{status}) update failed.'
        return f'Mission status ({id}-{status}) updated successfully. (complete: {increment})'

    def get_open_missions_by_agent(self, id: int) -> list[dict] | list[None]:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
            SELECT * FROM {self.table_name}
            WHERE id = %s AND status IN ('ASSIGNED', 'IN_PROGRESS')
            '''
            cursor.execute(query, (id,))
            return cursor.fetchall() or []

    def count_all_missions(self) -> int:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
            SELECT COUNT(*)
            FROM {self.table_name}
            '''
            cursor.execute(query)
            return cursor.fetchall()[0]['COUNT(*)'] or 0

    def count_by_status(self, status) -> int:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
            SELECT COUNT(*)
            FROM {self.table_name}
            WHERE status = %s
            '''
            cursor.execute(query, (status,))
            return cursor.fetchall()[0]['COUNT(*)'] or 0

    def count_open_missions(self) -> int:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
            SELECT COUNT(*)
            FROM {self.table_name}
            WHERE status IN ('ASSIGNED', 'IN_PROGRESS')
            '''
            cursor.execute(query)
            return cursor.fetchall()[0]['COUNT(*)'] or 0

    def count_critical_missions(self) -> int:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
            SELECT COUNT(*)
            FROM {self.table_name}
            WHERE status = 'CRITICAL'
            '''
            cursor.execute(query)
            return cursor.fetchall()[0]['COUNT(*)'] or 0

    def get_top_agent(self) -> dict:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
            SELECT * FROM {agent_db.table_name}
            ORDER BY completed_missions DESC
            LIMIT 1
            '''
            cursor.execute(query)
            return cursor.fetchall()[0] or 0


mission_db = MissionDB()