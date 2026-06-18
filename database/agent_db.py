from database.base_db import BaseRepo, BusinessValidationError
from logs.logger_config import logger

class AgentDB(BaseRepo):
    def __init__(self):
        super().__init__(table_name='agents')

    def create_agent(self, data: dict):
        ranks = ['Junior', 'Senior', 'Commander']
        if data.get('agent_rank') not in ranks:
            raise BusinessValidationError('Agent rank must be - Junior / Senior / Commander') # Rule no. 1
        logger.info('Generating new agent')
        new_id = super().create(data)
        return self.get_agent_by_id(new_id)
    
    def get_all_agents(self):
        logger.info('Getting all agents')
        all_agents = super().get_all()
        for agent in all_agents.copy():
            agent['is_active'] = bool(agent['is_active'])
        return all_agents
    
    def get_agent_by_id(self, id: int):
        logger.info(f'Getting user by id: {id}')
        agent = super().get_by_id(id)
        if not agent:
            return None
        agent['is_active'] = bool(agent['is_active'])
        return agent

    def update_agent(self, id: int, data: dict) -> str:
        self.get_agent_by_id(id)
        logger.info(f'Updating user: {id}')
        updated = super().update(id, data)
        
        if not updated:
            return f'Agent ({id}) update failed.'
        return f'Agent ({id}) update successfully.'
    
    def deactivate_agent(self, id: int) -> str:
        agent = self.get_agent_by_id(id)
        if not agent['is_active']:
            return f'Agent ({id}) is already not active.'
        logger.info(f'Deactive user: {id}')
        updated = super().update(id, {'is_active': False})
        
        if not updated:
            return f'Agent ({id}) deactivate failed.'
        return f'Agent ({id}) deactive successfully.'

    def increment_completed(self, id: int) -> str:
        self.get_agent_by_id(id)
        logger.info(f'Up agent mission completed +1: {id}')
        query = f'''
            UPDATE {self.table_name}
            SET completed_missions = completed_missions + 1
            WHERE id = %s
            '''
        result = self.execute_query(query, (id,), is_change=True)
        changed = result['row_count'] > 0
        
        if not changed:
            return f'Agent ({id}) completed missions increment failed.'
        return f'Agent ({id}) completed missions successfully increase.'

    def increment_failed(self, id) -> str:
        self.get_agent_by_id(id)
        logger.info(f'Up agent mission failed +1: {id}')
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
        sucess_rate = (agent_performance['completed'] / agent_performance['total']) * 100 if agent_performance['total'] else 0.0
        agent_performance['success_rate'] = float("{:.2f}".format(round(sucess_rate, 2)))
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