import time
from email_env import EmailTriageEnv, Action
from tasks import get_tasks

def run_simulated_agent():
    env = EmailTriageEnv()
    obs = env.reset()
    tasks = get_tasks()
    task = tasks[0] # Spam Cleanup

    print(f"--- Simulated Run: {task.name} ---")
    print(f"Objective: {task.description}\n")

    # Step 1: List Inbox
    print("Action: ListEmails(folder='INBOX')")
    obs, reward, done, info = env.step(Action(action_type="ListEmails", args={"folder": "INBOX"}))
    print(f"Observation: Found {len(obs.emails)} emails.\n")
    time.sleep(1)

    # Step 2: Find Spam and Delete
    spam_emails = [e for e in obs.emails if "[SPAM]" in e["subject"]]
    for i, e in enumerate(spam_emails):
        print(f"Action: DeleteEmail(id='{e['id']}')")
        obs, reward, done, info = env.step(Action(action_type="DeleteEmail", args={"email_id": e["id"]}))
        print(f"Observation: {obs.message} | Reward: {reward}")
        time.sleep(0.5)

    print(f"\nFinal Task Score: {task.score(env)}")
    
    # Task 2 Demo: Urgent Reply
    task2 = tasks[1]
    print(f"\n--- Simulated Run: {task2.name} ---")
    boss_email = [e for e in env._get_email_list("INBOX") if "boss" in e["sender"]][0]
    
    print(f"Action: ReplyEmail(id='{boss_email['id']}', body='I can meet at 10 AM.')")
    obs, reward, done, info = env.step(Action(action_type="ReplyEmail", args={"email_id": boss_email["id"], "body": "I can meet at 10 AM."}))
    print(f"Observation: {obs.message} | Reward: {reward}")
    
    print(f"Final Task Score: {task2.score(env)}")

if __name__ == "__main__":
    run_simulated_agent()
