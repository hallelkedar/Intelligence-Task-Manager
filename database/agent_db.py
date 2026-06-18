from database.base_db import BaseRepo, ResourceNotFoundError, BusinessValidationError

class AgentDB(BaseRepo):
    def __init__(self):
        super().__init__(table_name='agents')

    def create_agent(self, data: dict):
        ranks = ['Junior', 'Senior', 'Commander']
        if data.get('agent_rank') not in ranks:
            raise BusinessValidationError('Agent rank must be - Junior / Senior / Commander') # Rule no. 1
        new_id = super().create(data)
        return self.get_agent_by_id(new_id)
    
    def get_all_agents(self):
        return super().get_all()

    def get_agent_by_id(self, id: int):
        agent = super().get_by_id(id)
        if not agent:
            return None
        agent['is_active'] = bool(agent['is_active'])
        return agent

    def update_agent(self, id: int, data: dict) -> str:
        self.get_agent_by_id(id)
        
        updated = super().update(id, data)
        
        if not updated:
            return f'Agent ({id}) update failed.'
        return f'Agent ({id}) update successfully.'
    
    def deactivate_agent(self, id: int) -> str:
        self.get_agent_by_id(id)
        updated = super().update(id, {'is_active': False})
        
        if not updated:
            return f'Agent ({id}) deactivate failed.'
        return f'Agent ({id}) deactive successfully.'

    def increment_completed(self, id: int) -> str:
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
            return f'Agent ({id}) completed missions increment failed.'
        return f'Agent ({id}) completed missions successfully increase.'

    def increment_failed(self, id) -> str:
        self.get_agent_by_id(id)
        
        query = f'''
            UPDATE {self.table_name}
            SET failed_missions = failed_missions + 1
            WHERE id = %s
            '''
        result = self.execute_query(query, (id,), is_change=True)
        changed = result['row_count']
        
        if not changed:
            return f'Agent ({id}) failed missions increment failed.'
        return f'Agent ({id}) failed missions successfully increase.'

    def get_agent_performance(self, id) -> dict:
        agent = self.get_agent_by_id(id)
        agent_performance = {
            'completed': agent['completed_missions'],
            'failed': agent['failed_missions'],
            'total': agent['completed_missions'] + agent['failed_missions'], 
        }
        agent_performance['success_rate'] = (agent_performance['completed'] / agent_performance['total']) * 100 if agent_performance['total'] else 0.0
        return agent_performance
    
    def count_active_agents(self) -> int:
        query = f'''
        SELECT COUNT(*) AS ACTIVE
        FROM {self.table_name}
        WHERE is_active = TRUE
        '''
        result = self.execute_query(query, fetch_all=False)
        active_agents = result['ACTIVE']
        return active_agents if active_agents else 0
        
agent_db = AgentDB()