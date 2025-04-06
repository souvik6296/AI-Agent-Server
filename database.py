import json
from supabase import create_client, Client

# Supabase configuration
DB_URL = "https://adsnebivksfdycwmejeh.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkc25lYml2a3NmZHljd21lamVoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMzMjQwNjEsImV4cCI6MjA1ODkwMDA2MX0.h7iJPsHKx8DB4M8fig9EVwiUG8X4eQpHuzhLbxv5mgU"

# Initialize Supabase client
supabase: Client = create_client(DB_URL, KEY)

# Table definitions
table_dict = {
    "users": """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);""",
    
    "tasks": """
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INT,  -- No foreign key constraint to avoid dependency errors
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INT CHECK (priority BETWEEN 1 AND 5),
    estimated_time INTERVAL,
    task_day VARCHAR(10) CHECK (task_day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    created_at TIMESTAMP DEFAULT NOW()
);""",
    
    "schedule": """
CREATE TABLE schedule (
    id SERIAL PRIMARY KEY,
    user_id INT,  -- No foreign key constraint
    task_id INT,  -- No foreign key constraint to avoid dependency errors
    day VARCHAR(10) CHECK (day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    priority INT NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pending', 'in-progress', 'completed'))
);"""
}
# Helper functions
def table_exists(table_name):
    try:
        response = supabase.table(table_name).select("*").limit(1).execute()
        return True
    except Exception:
        return False

def create_table(tablename):
    query = table_dict.get(tablename)
    if not query:
        return False
    response = supabase.postgrest.execute_sql(query)
    return bool(response)

# User operations
def create_user(params):
    response = supabase.table("users").insert({
        "name": params.get('name'),
        "email": params.get('email'),
        "phone_number": params.get('phone_number')
    }).execute()
    return bool(response)

def get_user(user_id):
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None

# Task operations
def insert_task(params):
    response = supabase.table("tasks").insert({
        "user_id": params.get('user_id'),
        "title": params.get('title'),
        "description": params.get('description'),
        "priority": params.get('priority'),
        "estimated_time": params.get('estimated_time'),
        "task_day": params.get('task_day')
    }).execute()
    return bool(response)

def get_user_tasks(user_id):
    response = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    return response.data

# Schedule operations
def insert_schedule(params):
    response = supabase.table("schedule").insert({
        "user_id": params.get('user_id'),
        "task_id": params.get('task_id'),
        "day": params.get('day'),
        "start_time": params.get('start_time'),
        "end_time": params.get('end_time'),
        "priority": params.get('priority'),
        "status": params.get('status')
    }).execute()
    return bool(response)

def get_user_schedule(params):
    query = supabase.table("schedule").select("*").eq("user_id", params.get('user_id'))
    if 'day' in params:
        query = query.eq("day", params.get('day'))
    response = query.execute()
    return response.data

def insert_multiple_tasks(params):
    tasks_list = params.get('tasks_list', [])
    try:
        for task in tasks_list:
            if not all(key in task for key in ['user_id', 'title']):
                raise ValueError("Each task must have user_id and title")
        response = supabase.table("tasks").insert(tasks_list).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error inserting multiple tasks: {e}")
        return False

def insert_multiple_schedule(params):
    schedules_list = params.get('schedules_list', [])
    try:
        for schedule in schedules_list:
            required = ['user_id', 'task_id', 'day', 'start_time', 'end_time']
            if not all(key in schedule for key in required):
                raise ValueError(f"Each schedule must have {required}")
        response = supabase.table("schedule").insert(schedules_list).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error inserting multiple schedules: {e}")
        return False

# Combined operations
def get_user_tasks_with_schedule(params):
    tasks = get_user_tasks(params.get('user_id'))
    schedule = get_user_schedule(params)
    for task in tasks:
        task['schedules'] = [s for s in schedule if s['task_id'] == task['id']]
    return tasks

def delete_task(params):
    response = supabase.table("tasks").delete() \
        .eq("user_id", params.get('user_id')) \
        .eq("id", params.get('task_id')).execute()
    return bool(response)

def update_schedule_status(params):
    response = supabase.table("schedule").update({
        "status": params.get('new_status')
    }).eq("user_id", params.get('user_id')) \
      .eq("id", params.get('schedule_id')).execute()
    return bool(response)

# Initialize database
def initialize_database():
    for table_name in table_dict.keys():
        if not table_exists(table_name):
            create_table(table_name)

# Initialize the database when this module is imported
initialize_database()