# Inteligence Task Manager
## Agents and missions system manager

Manage sql database, crud with mysql connector, help define agents and mission and have any agent his mission with full report.

### Project Structure:
```
intelligence-task-manager/
├── database/
│   ├── db_connection.py
│   ├── agent_db.py
│   └── mission_db.py
├── README.md
├── requirements.txt
└── .gitignore
```

### === Tables ===

agents:
```
FIELD              |         TYPE            |   NOTES 
id                 | INT, AUTO_INCREMENT, PK | Unique id
name               | VARCHAR(50)             | Name of agent
specialty          | VARCHAR(30)             | Specialty field
is_active          | BOOLEAN                 | DEFAULT TRUE
completed_missions | INT                     | DEFAULT 0
failed_missions    | INT                     | DEFAULT 0
agent_rank         | ENUM(Junior, Senior, Commander)
```

missions:
```
FIELD              |         TYPE            |   NOTES 
id                 | INT, AUTO_INCREMENT, PK | Unique id
name               | VARCHAR(50)             | Name of agent
specialty          | VARCHAR(30)             | Specialty field
is_active          | BOOLEAN                 | DEFAULT TRUE
completed_missions | INT                     | DEFAULT 0
failed_missions    | INT                     | DEFAULT 0
agent_rank         | ENUM(Junior, Senior, Commander)
```

### === Repo classes ===
DB_connection:
```
Create sql connection to the database.
get_connection() - Returns active sql connection
create_database() - Create database - 'Intelligence_db' (if not exsits)
create_tables() - Create the tables - agents and missions (if not exsits)
```

AgentDB:
```
Handle the contact with agents table.
create_agent(data) - Create new agent, Return his object
get_all_agents() - Return all agents
get_agent_by_id(id) - Return agent by id | None
update_agent(id, data) - Update mission by id
deactivate_agent(id) - Set agent into deactive
increment_completed(id) - Update completed agent mission 
increment_failed(id) - Update failed agent mission
get_agent_performance(id) - Return completed, failed, total, success_rate - dictionary 
count_active_agents() - Return count of active agents
```

MissionDB:
```
Handle the contact with missions table.
create_mission(data) - Create new mission, Return his object
get_all_missions() - Return all missions
get_mission_by_id(id) - Return mission by id | None
assign_mission(m_id, a_id) - Assign mission to agent
update_mission_status(id, status) - Update any status change
get_open_missions_by_agent(id) - Return ASSIGNED/IN_PROGRESS of agent
count_all_missions() - Return number of all mission
count_by_status(status) - Return number of all mission with this status
count_open_missions() - Return number of open mission
count_critical_missions() - Return number of CRITICAL mission
get_top_agent() - Return agent with highest completed_missions
```

### === Rules ===

1. rank - has to be, Junior / Senior / Commander
2. difficulty, importance - has to be between 1 - 10
3. risk_level - calculate with algorithm not from user
4. Agent with is_active=False - can't get any mission
5. Agent can't hold more than 3 open mission together
6. Mission with risk_level=CRITICAL - only assign to Commander agent
7. Mission can be assign - only if status=NEW
8. Mission can be start - only if status=ASSIGNED
9. Mission can be close - only if status=IN_PROGRESS (change to FAILED or COMPLETED)
10. Mission can be cancled - only if status=NEW/status=ASSIGNED

### === Run instructions ===
docker run - 
```
docker run -d --name intelligence-mysql -e MYSQL_ROOT_PASSWORD=1234 -e MYSQL_DATABASE=Intelligence_db -p 3306:3306 mysql:8.0
```

```
pip install requirements.txt
```