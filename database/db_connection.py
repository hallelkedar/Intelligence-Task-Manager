import mysql.connector

class DB_connection:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

        self._connection = None
        self.connect()
    
    def connect(self):
        self._connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )

    @property
    def get_connection(self):
        if self._connection is None or not self._connection.is_connected():
            self.connect()
        return self._connection
    
    def create_database(self):
        with self._connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE IF NOT EXISTS Intelligence_db')
            cursor.execute('USE Intelligence_db')

    def create_tables(self):
        with self._connection.cursor() as cursor:
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS agents (
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           name VARCHAR(50) NOT NULL,
                           specialty VARCHAR(30) NOT NULL,
                           is_active BOOLEAN DEFAULT TRUE,
                           completed_missions INT DEFAULT 0,
                           failed_missions INT DEFAULT 0,
                           agent_rank ENUM('Junior', 'Senior', 'Commander')
                           )
                           ''')
            
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS missions (
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           title VARCHAR(50) NOT NULL,
                           description TEXT NOT NULL,
                           location VARCHAR(30) NOT NULL,
                           difficulty INT NOT NULL,
                           importance INT NOT NULL,
                           status ENUM('NEW', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'NEW',
                           risk_level VARCHAR(50) NOT NULL,
                           assigned_agent_id INT DEFAULT NULL
                           )
                           ''')
            

    def close(self):
        if self._connection:
            self._connection.close()

db_connection = DB_connection(
    host='localhost',
    user='root',
    password='1234'
)
