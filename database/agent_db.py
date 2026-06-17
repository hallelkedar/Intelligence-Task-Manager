from database.base_db import BaseRepo, ItemNotExists
from pydantic import BaseModel
from typing import Literal

class AgentNotExists(ItemNotExists):
    pass

class AgentDB(BaseRepo):
    def __init__(self):
        super().__init__(table_name='agents')

    def create_agent(self, data: dict):
        ranks = ['Junior', 'Senior', 'Commander']
        if data.get('agent_rank') not in ranks:
            raise ValueError('Agent rank must be - Junior / Senior / Commander')
        new_id = super().create(data)
        return self.get_agent_by_id(new_id)
    
    def get_all_agents(self):
        return super().get_all()

    def get_agent_by_id(self, id: int):
        agent = super().get_by_id(id)
        agent['is_active'] = bool(agent['is_active'])
        return agent

    def update_agent(self, id: int, data: dict):
        self.get_agent_by_id(id)
        
        updated = super().update(id, data)
        
        if not updated:
            return {'msg': f'Agent ({id}) update failed.'}
        return {'msg': f'Agent ({id}) update successfully.'}
    
    def deactivate_agent(self, id: int):
        self.get_agent_by_id(id)
        updated = super().update(id, {'is_active': False})
        
        if not updated:
            return {'msg': f'Agent ({id}) deactivate failed.'}
        return {'msg': f'Agent ({id}) deactive successfully.'}

    def increment_completed(self, id: int):
        self.get_agent_by_id(id)
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
                UPDATE {self.table_name}
                SET completed_missions = completed_missions + 1
                WHERE id = %s
                '''
            cursor.execute(query, (id,))
            conn.commit()
            changed = cursor.rowcount > 0
        if not changed:
            return {'msg': f'Agent ({id}) completed missions increment failed.'}
        return {'msg': f'Agent ({id}) completed missions successfully increase.'}

    def increment_failed(self, id):
        self.get_agent_by_id(id)
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
                UPDATE {self.table_name}
                SET failed_missions = failed_missions + 1
                WHERE id = %s
                '''
            cursor.execute(query, (id,))
            conn.commit()
            changed = cursor.rowcount > 0
        if not changed:
            return {'msg': f'Agent ({id}) failed missions increment failed.'}
        return {'msg': f'Agent ({id}) failed missions successfully increase.'}

    def get_agent_performance(self, id):
        agent = self.get_agent_by_id(id)
        agent_performance = {
            'completed': agent['completed_missions'],
            'failed': agent['failed_missions'],
            'total': agent['completed_missions'] + agent['failed_missions'], 
        }
        agent_performance['success_rate'] = (agent_performance['completed'] / agent_performance['total']) * 100 if agent_performance['total'] else 0.0
        return agent_performance
    
    def count_active_agents(self):
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
            SELECT COUNT(*) AS ACTIVE
            FROM {self.table_name}
            WHERE is_active = TRUE
            '''
            cursor.execute(query)
            active_agents = cursor.fetchone()['ACTIVE']
            return active_agents if active_agents else 0