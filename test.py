from database.db_connection import db_connection
from database.agent_db import agent_db
from database.mission_db import mission_db

db_connection.create_database()
db_connection.create_tables()

