from openai import OpenAI
import speech_recognition as sr
import json
from database import *
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import json

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_whisper(audio)  # Using Whisper for better accuracy
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand.")
        return None




API_KEY1 = "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"


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=API_KEY1,
)

client._custom_headers = {
    "HTTP-Referer": "https://your-app-url.vercel.app",  # Required
    "X-Title": "AI Agent Scheduler",  # Optional but recommended
}

switch = {
    "table_exists": table_exists,
    "create_table": create_table,
    "create_user": create_user,
    "get_user": get_user,
    "insert_task": insert_task,
    "insert_schedule": insert_schedule,
    "insert_multiple_tasks": insert_multiple_tasks,
    "insert_multiple_schedule": insert_multiple_schedule,
    "get_user_tasks": get_user_tasks,
    "get_user_schedule": get_user_schedule,
    "get_user_tasks_with_schedule": get_user_tasks_with_schedule,
    "delete_task": delete_task,
    "update_schedule_status": update_schedule_status
}

SYSTEM_PROMPT = """You are an AI assistant with Start, Plan, Action, Observation and output state.
Wait for the user prompt and first plan using available tools.
After planning call the appropiate function or tool based on avaibility and wait for the response.
Once you get the observation, return the AI response based on start prompt and observation.

Do not insert the day as today, tomorrow only day input is allowed as Monday, Tuesday and also dont write 30 minutes for estimated time insted of 30 minutes use 0.5 hours. Strictly follow this or it may lead to error in CURD opertaion.

 ***This is a wrong input format never use a back slash with input params insted use single quote for it and follow this strictly.

You are a JSON-only API assistant. You must follow these rules strictly:
1. Respond with exactly ONE JSON object per message
2. Never include any explanatory text, comments, or Markdown formatting
3. Never concatenate multiple JSON objects
4. Your response must be parseable with json.loads() directly

Example of VALID response:
{"type": "output", "output": "Hello"}

Example of INVALID response:
First I'll greet the user
{"type": "output", "output": "Hello"}
Then I'll ask how to help

***stricly follow the format in examlple dont write one line twice dont give something in mark down or dont use \boxed or anything extra stricly

*** only give json output only



only valid response:
    {"type": "output", "output": "Hello! How can I help?"}

invalid response:
    ```Here's your response:
{"type": "output", "output": "Hello!"}
Or maybe you wanted this?```


Available tools:

-def table_exists(table_name: str) : bool  
table_exists this function takes the table name as an input parameter and checks if the table exists or not.  
Returns a boolean response: True if the table exists, False otherwise.  

-def create_table(tablename: str) : bool  
create_table is a function that is used to create a table if it does not exist.  
It takes the table name as a string and returns a boolean response indicating whether the table was created.  
We mainly have three tables: users, tasks, and schedule.  

-def create_user({"name": str, "email": str, "phone_number": str}) : boolean  
create_user creates a new user in the users table.  
Takes dictionary of name, email, and phone_number as input parameters.  
Returns boolean if created or not.  

-def get_user(user_id: int) : dict  
get_user retrieves user information from the users table.  
Takes user_id as input parameter.  
Returns user details as dictionary.  

-def insert_task({"user_id": int, "title": str, "description": str, "priority": int, "estimated_time": str, "task_day": str}) : boolean  
insert_task inserts a new task into the tasks table for specific user.  
Takes dictionary of user_id, title, description, priority, estimated_time, and task_day as input parameters.  
Returns boolean if inserted or not.  

-def insert_schedule({"user_id": int, "task_id": int, "day": str, "start_time": str, "end_time": str, "priority": int, "status": str}) : boolean  
insert_schedule inserts a new task schedule into the schedule table for specific user.  
Takes dictionary of user_id, task_id, day, start_time, end_time, priority, and status as input parameters.  
Returns boolean if inserted or not.  

-def insert_multiple_tasks({tasks_list: list}) : boolean  
insert_multiple_tasks inserts multiple task records at once into the tasks table.  
Takes a list of task dictionaries (each containing user_id) as input.  
Each task dictionary should contain: user_id, title, description, priority, estimated_time, task_day.  
Returns True if successful, False otherwise.  

-def insert_multiple_schedule({schedules_list: list}) : boolean  
insert_multiple_schedule inserts multiple schedule records at once into the schedule table.  
Takes a list of schedule dictionaries (each containing user_id) as input.  
Each schedule dictionary should contain: user_id, task_id, day, start_time, end_time, priority, status.  
Returns True if successful, False otherwise.  

-def get_user_tasks(user_id: int) : list  
get_user_tasks retrieves all tasks for a specific user.  
Takes user_id as input parameter.  
Returns list of tasks.  

-def get_user_schedule({user_id: int, day: str = None}) : list  
get_user_schedule retrieves schedule for a specific user (optionally filtered by day).  
Takes user_id and optional day as input parameters.  
Returns list of scheduled tasks.  

-def get_user_tasks_with_schedule({user_id: int, task_id: int}) : list  
get_user_tasks_with_schedule retrieves all tasks with their schedules for a specific user.  
Takes user_id and optional task_id as input parameters.  
Returns combined list of tasks with their schedules.  

-def delete_task({user_id: int, task_id: int}) : boolean  
delete_task removes a task and its schedules for a specific user.  
Takes user_id and task_id as input parameters.  
Returns boolean if deleted or not.  

-def update_schedule_status({user_id: int, schedule_id: int, new_status: str}) : boolean  
update_schedule_status updates status of a scheduled task for a specific user.  
Takes user_id, schedule_id and new_status as input parameters.  
Returns boolean if updated or not.  

Stricty follow the json output format as in example

if you got observation like this "[{'id': 3, 'user_id': 1, 'task_id': 3, 'start_time': '2025-04-01 09:00:00', 'end_time': '2025-04-01 11:00:00', 'priority': 1, 'status': 'pending'}]"
then analyze it don't stop the process and extract the required data and give the required output.

The timestamp should be like this "2025-04-01 09:00:00" for end and start time and the progress status start all in lower-case.



insert_task, insert_schedule, insert_multiple_tasks, insert_multiple_schedule, update_schedule_status for these function only input is dictionary not a string don't use quote before curly braces of dictionary.***

***check the input formats and fields properly for all function you are doing it wrong


Example:

{"type": "user", "user": "Hey I have to complete my practical report that is very much important and also have to call my girlfriend which is less important by today monday please add this tasks to my tasklist and schedule it according to priority. My user ID is 1."}

{"type": "plan", "plan": "First I need to verify if the user exists by calling get_user with user_id 1."}

{"type": "action", "function": "get_user", "input": "1"}

{"type": "observation", "observation": "{'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'phone_number': '1234567890'}"}

{"type": "plan", "plan": "User exists. Now I will check if required tables exist by calling table_exists for 'tasks' and 'schedule' tables."}

{"type": "action", "function": "table_exists", "input": "tasks"}

{"type": "observation", "observation": "True"}

{"type": "plan", "plan": "Tasks table exists. Now checking schedule table."}

{"type": "action", "function": "table_exists", "input": "schedule"}

{"type": "observation", "observation": "True"}

{"type": "plan", "plan": "Both tables exist. Now I will add the tasks using insert_multiple_tasks with user_id included."}

{"type": "action", "function": "insert_multiple_tasks", "input": 
"[
    {'user_id': 1, 'title': 'Completing Practical Report', 'description': 'Complete the Practical Report which is very important', 'priority': 1, 'estimated_time': '1 hour', 'task_day': 'Monday'},
    {'user_id': 1, 'title': 'Talking to Girlfriend', 'description': 'Talk to your lovely one', 'priority': 2, 'estimated_time': '1.5 hours', 'task_day': 'Monday'}
]"}

{"type": "observation", "observation": "True"}

{"type": "plan", "plan": "Tasks added successfully. Now checking existing schedules for user 1 on Monday using get_user_schedule."}

{"type": "action", "function": "get_user_schedule", "input": {"user_id": 1, "day": "Monday"}}

{"type": "observation", "observation": "[{'id': 3, 'user_id': 1, 'task_id': 3, 'start_time': '2025-04-01 09:00:00', 'end_time': '2025-04-01 11:00:00', 'priority': 1, 'status': 'pending'}, {'id': 4, 'user_id': 1, 'task_id': 4, 'start_time': '2025-04-01 11:15:00', 'end_time': '2025-04-01 12:00:00', 'priority': 3, 'status': 'pending'}]"}

{"type": "plan", "plan": "There are two existing schedules. I will reschedule lower priority task (ID 4) to make room for new tasks by calling update_schedule_status."}

{"type": "action", "function": "update_schedule_status", "input": {"user_id": 1, "schedule_id": 4, "new_status": "rescheduled"}}

{"type": "observation", "observation": "True"}

{"type": "plan", "plan": "Now I will schedule the new tasks using insert_multiple_schedule with user_id included."}

{"type": "action", "function": "insert_multiple_schedule", "input": 
"[
    {'user_id': 1, 'task_id': 5, 'day': 'Monday', 'start_time': '2025-04-01 11:00:00', 'end_time': '2025-04-01 12:00:00', 'priority': 1, 'status': 'pending'},
    {'user_id': 1, 'task_id': 6, 'day': 'Monday', 'start_time': '2025-04-01 12:00:00', 'end_time': '2025-04-01 13:30:00', 'priority': 2, 'status': 'pending'}
]"}

{"type": "observation", "observation": "True"}

{"type": "output", "output": "Your tasks have been successfully scheduled. Your practical report is scheduled from 11:00 to 12:00 (high priority) and calling your girlfriend is scheduled from 12:00 to 13:30 (medium priority). The previously scheduled low-priority task has been rescheduled."}


"""

message=[{"role":"system","content":SYSTEM_PROMPT}]


import re

def clean_ai_response(raw_response):
    """Removes Markdown/boxed formatting and extracts pure JSON."""
    # Case 1: If response is already clean JSON, return as-is
    if raw_response.strip().startswith("{") and raw_response.strip().endswith("}"):
        return raw_response.strip()
    
    # Case 2: Remove ```json ``` wrapper
    cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_response, flags=re.IGNORECASE)
    
    # Case 3: Remove \boxed{} wrapper
    cleaned = re.sub(r'^\\boxed$', '', cleaned)
    
    # Case 4: Extract first valid JSON block
    json_match = re.search(r'\{.*\}', cleaned, flags=re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    raise ValueError("No valid JSON found in AI response")


app = Flask(__name__)
CORS(app)
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.get_json()
        if not data or 'usermsg' not in data:
            return jsonify({"error": "Invalid request format"}), 400
            
        usermsg = data.get('usermsg', '')
        query = {"type": "user", "user": usermsg}
        message.append({"role": "user", "content": json.dumps(query)})
        
        while True:
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=message,
                    response_format={"type": "json_object"}
                )
                
                if not completion or not completion.choices:
                    return jsonify({"error": "Empty response from AI"}), 500
                    
                raw_response = completion.choices[0].message.content
                print("Raw Response:", raw_response)  # Debug logging
                
                raw_response = re.sub(r'^```json|```$', '', raw_response, flags=re.IGNORECASE)
                print(raw_response)

                
                response = json.loads(raw_response)
                message.append({"role": "assistant", "content": json.dumps(response)})
                
                if response.get("type") == "output":
                    return jsonify({
                        "response": response.get("output"),
                        "status": "complete"
                    })
                elif response.get("type") == "action":
                    func = switch.get(response.get("function"))
                    if not func:
                        return jsonify({"error": f"Unknown function: {response.get('function')}"}), 400
                    observation = func(response.get("input"))
                    obs = {"type": "observation", "observation": observation}
                    message.append({"role": "developer", "content": json.dumps(obs)})

                    
            except Exception as e:
                return jsonify({
                    "error": "Failed to parse AI response",
                    "details": str(e),
                    "raw_response": raw_response
                }), 500
            except Exception as e:
                return jsonify({"error": "AI service error", "details": str(e)}), 503
                
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500
if __name__ == '__main__':
    app.run(port=7000)
