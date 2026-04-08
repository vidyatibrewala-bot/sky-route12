import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from email_env import EmailTriageEnv, Action, ListEmails, GetEmail, ReplyEmail, DeleteEmail, MoveEmail
from tasks import get_tasks

load_dotenv()

# Pre-defined system prompt to guide the LLM
SYSTEM_PROMPT = """
You are an AI assistant managing a user's email inbox. 
Your goal is to complete the task provided.
You can perform the following actions:
- ListEmails(folder="INBOX"|"SPAM"|"ARCHIVE")
- GetEmail(email_id="...")
- ReplyEmail(email_id="...", body="...")
- DeleteEmail(email_id="...")
- MoveEmail(email_id="...", destination_folder="...")

IMPORTANT: You must respond in valid JSON format only.
Example Response:
{ "action_type": "ListEmails", "args": { "folder": "INBOX" } }
"""

def map_action(json_data):
    a_type = json_data.get("action_type")
    args = json_data.get("args", {})
    
    if a_type == "ListEmails":
        return Action(action=ListEmails(**args))
    elif a_type == "GetEmail":
        return Action(action=GetEmail(**args))
    elif a_type == "ReplyEmail":
        return Action(action=ReplyEmail(**args))
    elif a_type == "DeleteEmail":
        return Action(action=DeleteEmail(**args))
    elif a_type == "MoveEmail":
        return Action(action=MoveEmail(**args))
    return None

def run_task(task_obj):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    env = EmailTriageEnv()
    obs = env.reset()
    
    print(f"\n--- Starting Task: {task_obj.name} ---")
    print(f"Objective: {task_obj.description}")
    
    total_reward = 0
    for step in range(5): # Limit steps for baseline demo
        prompt = f"Objective: {task_obj.description}\nCurrent Observation: {obs.model_dump_json()}\nAction? (JSON only)"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            action_data = json.loads(response.choices[0].message.content)
            print(f"Step {step+1} Action: {action_data}")
            action = map_action(action_data)
            
            if not action:
                print("Invalid action parsed.")
                break
                
            obs, reward, done, info = env.step(action)
            total_reward += reward
            print(f"Observation: {obs.message} | Reward: {reward}")
            
            if done: break
        except Exception as e:
            print(f"Error in step: {e}")
            break
            
    final_score = task_obj.score(env)
    print(f"Task Completed. Final Score: {final_score}")
    return final_score

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        exit(1)
        
    tasks = get_tasks()
    results = {}
    for task in tasks:
        score = run_task(task)
        results[task.name] = score
        
    print("\n--- Final Results ---")
    for name, score in results.items():
        print(f"{name}: {score}")
