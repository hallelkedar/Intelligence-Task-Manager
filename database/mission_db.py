from database.base_db import BaseRepo, ResourceNotFoundError, BusinessValidationError
from database.agent_db import agent_db
from logs.logger_config import logger

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
        if not (1 <= diff <= 10) or not (1 <= imp <= 10):
            raise BusinessValidationError('difficulty and importance must be between 1 - 10') # Rule no. 2
        
        mission['risk_level'] = self.calculate_risk_level(diff, imp) # Rule no. 3
        logger.info('Generate new mission')
        new_id = super().create(mission)
        return self.get_mission_by_id(new_id)
    
    def get_all_missions(self):
        logger.info('Getting all missions')
        return super().get_all()

    def get_mission_by_id(self, id: int):
        logger.info(f'Getting agent by id: {id}')
        return super().get_by_id(id)

    def assign_mission(self, m_id: int, a_id: int) -> str:
        agent = agent_db.get_agent_by_id(a_id)
        
        if not agent.get('is_active'):
            raise BusinessValidationError('Agent not active') # Rule no. 4
        
        if len(self.get_open_missions_by_agent(a_id)) >= 3:
            raise BusinessValidationError('You can not assign more than 3 mission to an agent.') # Rule no. 5
        
        mission = self.get_mission_by_id(m_id)

        if not mission.get('status') == 'NEW':
            raise BusinessValidationError('You can only assign new missions') # Rule no. 7
        if mission.get('risk_level') == 'CRITICAL' and agent.get('agent_rank') != 'Commander':
            raise BusinessValidationError('You can give "critical" - risk level mission, only to commander.') # Rule no. 6
        logger.info(f'Assigning mission ({m_id}) to agent ({a_id})')
        updated = super().update(
            m_id,
            {'assigned_agent_id': a_id,
            'status': 'ASSIGNED'}
            )
        if not updated:
            return f'Mission ({m_id}) assign failed. (agent id: {a_id})'
        return f'Mission ({m_id}) (agent id: {a_id}) successfully assign.'
        

    def update_mission_status(self, id: int, status: str) -> str:
        mission = self.get_mission_by_id(id)
        old_status = mission.get('status')

        increment = 'not yet'

        if status == 'IN_PROGRESS' and old_status != 'ASSIGNED':
            raise BusinessValidationError('You can only start mission that assigned to agent') # Rule no. 8
        
        if status == 'CANCELLED' and old_status not in ['NEW', 'ASSIGNED']:
            raise BusinessValidationError('You can only cancel mission that did not start') # Rule no. 10
        
        if old_status == 'IN_PROGRESS':
            if status not in ['COMPLETED', 'FAILED']:
                raise BusinessValidationError('You can only finish mission in progress') # Rule no. 9
            else:
                if status == 'COMPLETED':
                    increment = agent_db.increment_completed(mission.get('assigned_agent_id'))
                else:
                    increment = agent_db.increment_failed(mission.get('assigned_agent_id'))
        logger.info(f'Updating status - {old_status} to {status} (id: {id})')
        updated = super().update(
            id,
            {'status': status}
            )
        if not updated:
            return f'Mission status ({id}-{status}) update failed.'
        return f'Mission status ({id}-{status}) updated successfully. (Finished: {increment})'

    def get_open_missions_by_agent(self, id: int) -> list[dict] | list[None]:
        query = f'''
        SELECT * FROM {self.table_name}
        WHERE assigned_agent_id = %s AND status IN ('ASSIGNED', 'IN_PROGRESS')
        '''
        result = self.execute_query(query, (id,))
        return result

    def count_all_missions(self) -> int:
        query = f'''
        SELECT COUNT(*) as TOTAL
        FROM {self.table_name}
        '''
        result = self.execute_query(query, fetch_all=False)
        return result['TOTAL'] or 0

    def count_by_status(self, status) -> int:
        query = f'''
        SELECT COUNT(*) AS STATUS
        FROM {self.table_name}
        WHERE status = %s
        '''
        result = self.execute_query(query, (status,), fetch_all=False)
        return result['STATUS'] or 0

    def count_open_missions(self) -> int:
        query = f'''
        SELECT COUNT(*) as open_missions
        FROM {self.table_name}
        WHERE status IN ('ASSIGNED', 'IN_PROGRESS')
        '''
        result = self.execute_query(query, fetch_all=False)
        return result['open_missions'] or 0

    def count_critical_missions(self) -> int:
        query = f'''
        SELECT COUNT(*) as critical
        FROM {self.table_name}
        WHERE risk_level = 'CRITICAL'
        '''
        result = self.execute_query(query, fetch_all=False)
        return result['critical'] or 0

    def get_top_agent(self) -> dict:
        query = f'''
        SELECT * FROM {agent_db.table_name}
        ORDER BY completed_missions DESC
        LIMIT 1
        '''
        result = self.execute_query(query, fetch_all=False)
        return result or 0


mission_db = MissionDB()