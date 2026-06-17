from base_db import BaseRepo, ItemNotExists, InvalidField
from pydantic import BaseModel

class MissionNotFound(ItemNotExists):
    pass

class Mission(BaseModel):
    title: str
    description: str
    location: str
    difficulty: int
    importance: int

class MissionDB(BaseRepo):
    def __init__(self):
        super().__init__(table_name='missions')

    def create_mission(self, data: Mission):
        mission = data.model_dump()
        if 1 > mission['difficulty'] > 10:
            raise InvalidField('difficulty must be between 1 - 10')

    def get_all_missions(self):
        pass

    def get_mission_by_id(self, id):
        pass

    def assign_mission(self, m_id, a_id):
        pass

    def update_mission_status(self, id, status):
        pass

    def get_open_missions_by_agent(self, id):
        pass

    def count_all_missions(self):
        pass

    def count_by_status(self, status):
        pass

    def count_open_missions(self):
        pass

    def count_critical_missions(self):
        pass

    def get_top_agent(self):
        pass
