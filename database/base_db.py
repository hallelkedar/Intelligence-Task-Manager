from database.db_connection import db_connection

class ItemNotExists(Exception):
    pass

class InvalidField(Exception):
    pass

class BaseRepo:
    def __init__(self, table_name):
        self.table_name = table_name
        self.conn = db_connection

    def get_all(self) -> list[dict] | list[None]:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(f'SELECT * FROM {self.table_name}')
            return cursor.fetchall() or []
            
        
    def get_by_id(self, item_id: int) -> dict | None:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            query = f'''
                SELECT * FROM {self.table_name}
                WHERE id = %s
                '''
            cursor.execute(query, (item_id,))
            return cursor.fetchone()
        
    def create(self, data: dict) -> int:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            keys = ', '.join(data)
            placeholders = ', '.join(['%s'] * len(data))

            query = f'''
            INSERT INTO {self.table_name}
            ({keys}) VALUES ({placeholders})
            '''
            params = tuple(data.values())

            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        
    def update(self, item_id: int, data: dict) -> bool:
        conn = self.conn.get_connection
        with conn.cursor(dictionary=True) as cursor:
            set_clause = ', '.join([f'{key} = %s' for key in data.keys()])

            query = f'''
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE id = %s
                '''
            params = list(data.values()) + [item_id]
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0