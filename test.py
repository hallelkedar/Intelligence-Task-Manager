from database.agent_db import AgentDB
from database.db_connection import db_connection

db_connection.create_database()
db_connection.create_tables()

agent = AgentDB()

