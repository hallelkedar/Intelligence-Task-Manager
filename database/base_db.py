from database.db_connection import db_connection

class ResourceNotFoundError(Exception):
    pass

class BusinessValidationError(Exception):
    pass

class BaseRepo:
    def __init__(self, table_name):
        self.table_name = table_name
        self.db = db_connection

    def execute_query(self, query: str, params: tuple = None, is_change: bool = False, fetch_all: bool = True):
        conn = self.db.get_connection()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, params or ())

            if is_change:
                conn.commit()
                return {
                    'row_count': cursor.rowcount,
                    'last_id': cursor.lastrowid
                }
            
            if fetch_all:
                return cursor.fetchall() or []
            return cursor.fetchone()
        
    def get_all(self) -> list[dict] | list[None]:
        query = f'SELECT * FROM {self.table_name}'
        result = self.execute_query(query)
        return result
            
        
    def get_by_id(self, item_id: int) -> dict | None:

        query = f'''
            SELECT * FROM {self.table_name}
            WHERE id = %s
            '''
        result = self.execute_query(query, (item_id,), fetch_all=False)
        return result
        
    def create(self, data: dict) -> int:
        keys = ', '.join(data)
        placeholders = ', '.join(['%s'] * len(data))

        query = f'''
        INSERT INTO {self.table_name}
        ({keys}) VALUES ({placeholders})
        '''
        params = tuple(data.values())

        result = self.execute_query(query, params, is_change=True)
        return result['last_id']
        
    def update(self, item_id: int, data: dict) -> bool:
        
        set_clause = ', '.join([f'{key} = %s' for key in data.keys()])

        query = f'''
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE id = %s
            '''
        params = list(data.values()) + [item_id]
        result = self.execute_query(query, params, is_change=True)
        
        return result['row_count'] > 0